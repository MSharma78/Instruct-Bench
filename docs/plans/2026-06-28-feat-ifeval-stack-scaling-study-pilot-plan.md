---
title: "IFEval-Stack: Instruction-Density × Model-Size Scaling Study (Pilot)"
type: feat
status: active
date: 2026-06-28
origin: docs/brainstorms/2026-06-28-instruction-density-scaling-study-brainstorm.md
---

# ✨ IFEval-Stack: Instruction-Density × Model-Size Scaling Study (Pilot)

## Overview

Extend the existing IFEval harness (`Instruct-Bench`) into a controlled scaling
study that measures how instruction-following degrades as the **number of
simultaneous constraints `k`** grows, and how that degradation **scales with
model size**. The headline artifact is a 2D phase diagram (model × k → fraction
of instructions followed) plus a fitted **instruction-capacity scaling law
`k*(N)`** — the constraint count at which a model of `N` parameters collapses
below a pass-rate floor. Aimed at a publishable paper.

This plan covers the **Pilot tier** only (≈3,000 API calls, $5–15): prove the
method end-to-end and produce a draft phase diagram before committing to the Mid
/ Full tiers (see brainstorm: docs/brainstorms/2026-06-28-instruction-density-scaling-study-brainstorm.md).

## Problem Statement / Motivation

Native IFEval prompts carry only 1–3 constraints, so they cannot answer "how many
instructions can a model follow at once, and does that capacity grow with size?"
The corrected prior report in this repo also exposed a measurement trap: Qwen
returned `None` for ~40% of prompts, and naively scoring only valid responses
inflated its rank. A rigorous study must (a) push `k` well beyond 3 with
*verifiable* constraints, (b) span a clean parameter ladder, and (c) separate
**generation failures** from **instruction failures**.

### Novelty (must be defended — two close competitors exist)

- **ManyIFEval / "Curse of Instructions"** (Harada et al., ICLR 2025,
  OpenReview R6q67CDBCH): derives prompt-level accuracy `P(k) = p^k`, but caps at
  `k≤10` and **has no model-size axis** (one variant per family).
- **IFScale** (Jaroslawicz et al., 2025, arXiv:2507.11538): sweeps keyword density
  10→500 and finds three degradation patterns, but uses **frontier API models
  only** (no parameter ladder, opaque sizes), a **single keyword-only domain**,
  and derives **no capacity law**.
- **"256 LLMs"** (arXiv:2510.18892): finds size does *not* cleanly correlate with
  IF — but uses only `k=1`, so it cannot separate per-constraint failure from
  multi-constraint load.

**Our open gap:** the *joint* experiment — a dense, controlled **open-weight
parameter ladder (1B→405B)** crossed with a `k`-sweep up to 30 using the **full
IFEval-atom constraint vocabulary** (not just keywords), producing `k*(N)` as a
fitted scaling law and a frontier overlay ("how many effective parameters does a
closed model behave like?"). No published work crosses both axes.

## Proposed Solution

Reuse IFEval's official, deterministic checkers unchanged. **Compose** compatible
IFEval instruction atoms into synthetic prompts with exactly `k` constraints over
fresh (non-IFEval) topics, emit them in IFEval's native JSONL schema, generate
responses across the model grid, score with `evaluation_lib`, and analyze into a
phase diagram + scaling fit.

Key insight from research: IFEval already ships the conflict graph
(`INSTRUCTION_CONFLICTS` in `instructions_registry.py`) and each instruction's
`build_description(**kwargs)` produces the exact constraint text the checker
expects. So composition = sample a compatible `k`-subset, call each atom's
`build_description`, concatenate, and record `(instruction_id_list, kwargs)`. The
official strict/loose checkers then score it with zero reimplementation.

## Technical Approach

### Architecture

New/changed modules (each small, ≤400 lines, per repo's stated style):

```
instruct_bench/
├── config.py            # CHANGED: model grid w/ size metadata + tier presets
├── instructions/
│   ├── registry.py      # NEW: wrap IFEval atoms + per-atom param samplers
│   ├── conflict.py      # NEW: load official INSTRUCTION_CONFLICTS + 2 implicit edges
│   └── compose.py       # NEW: sample compatible k-set, render prompt, emit IFEval record
├── topics.py            # NEW: bank of ≥60 fresh base writing tasks (anti-contamination)
├── build_dataset.py     # NEW: produce datasets/ifeval_stack_<tier>.jsonl (k-grid)
├── generate.py          # CHANGED: grid loop, failure taxonomy, max_tokens(k)
├── score.py             # CHANGED: per-instruction pass lists, failure-aware
├── analyze.py           # CHANGED: per-(model,k) aggregates, Wilson CIs, k*, GLMM
├── figures.py           # NEW: heatmap, scaling curves, capacity, serial-position
└── run_pilot.py         # NEW: orchestrates build→generate→score→analyze→figures
```

Data flow:

```
build_dataset.py → datasets/ifeval_stack_pilot.jsonl   (IFEval-schema records, k-tagged)
        ↓
generate.py → responses/<model>.jsonl  (+ meta: finish_reason, usage, failure_class)
        ↓
score.py → scores/per_instruction.jsonl  (model, k, topic, instr_id, pos, strict_pass, loose_pass, gen_failure)
        ↓
analyze.py → scores/cells.csv (model×k aggregates + Wilson CI + clustered SE), scores/capacity.csv (k*(N))
        ↓
figures.py → figures/*.{png,pdf}  (phase-diagram heatmap, scaling curves, k* law, serial-position)
```

### Composition & Conflict Handling (the methodological core)

- **Reuse the official conflict graph.** Load `INSTRUCTION_CONFLICTS` from
  `instructions_registry.py` (after its `conflict_make` symmetry closure). Add the
  two implicit edges the research flagged: `startend:end_checker ↔
  detectable_content:postscript`, and `change_case:english_lowercase ↔
  detectable_format:multiple_sections`.
- **Solo/dominant atoms excluded from stacking:** `detectable_format:constrained_response`
  (conflicts with *everything*), and treat `json_format`, `combination:two_responses`,
  `combination:repeat_prompt` as solo-only (they fix the whole output). These are
  valid at `k=1` but never composed.
- **Sampling algorithm (greedy CSP):** to build a `k`-set, shuffle candidate
  atoms (seeded RNG), add one at a time, rejecting any that conflicts with the
  chosen set; also reject jointly-infeasible parameterizations (e.g.
  `number_words` lower bound vs a tiny `number_sentences` upper bound; overlapping
  `keywords`/`forbidden_words`). If a target `k` is infeasible from the
  compatibility graph's max clique, **log the achieved k and cap** — never emit an
  impossible set. (Note: max compatible `k` is bounded by the graph; verify the
  ceiling during Phase 1 — likely ~12–18 before forced conflicts.)
- **Determinism:** set `langdetect.DetectorFactory.seed = 0` before any scoring
  (3 atoms — `response_language`, `english_capital`, `english_lowercase` — depend
  on it). Fix a global RNG seed for atom/param/topic sampling.
- **Fresh topics** from `topics.py` (≥60 tasks not drawn from IFEval) → variance
  via re-instantiation across topics, not temperature. Mitigates contamination.
- **Validity cross-check (k≤3):** synthetic `k≤3` prompts must score within a
  small margin of native IFEval for the same models; a systematic gap signals a
  composition bug. This is the brainstorm's "hybrid axis" cross-check
  (see brainstorm).

### Generation: failure taxonomy + token budget

`generate.py` records per call: `finish_reason`, `usage`, and a `failure_class` ∈
`{ok, empty_none, refusal, truncated, api_error}`:
- `empty_none` — content is None/empty (the Qwen trap).
- `truncated` — `finish_reason == "length"` (don't let a small cap fail length
  constraints artificially).
- `refusal` — heuristic refusal detection (short + apology pattern).
- **`max_tokens` scales with k and any length requirement:**
  `max_tokens = clamp(512 + 256*k + words_required_headroom, 512, 4096)`.
- `temperature = 0`; resumable JSONL cache by `(model, prompt key)` (existing
  pattern preserved). Reasoning models (mixed into the frontier band per
  brainstorm) get a larger cap + usage-based cost logging.

### Scoring

`score.py` reuses `evaluation_lib.test_instruction_following_strict/loose`
unchanged on our generated records. Emits one row **per instruction** (not just
per prompt): `model, k, topic, instruction_id, position_index, strict_pass,
loose_pass, gen_failure`. A `gen_failure` response marks all its instructions
failed **but tagged**, so analysis can report both "IF on valid responses" and
"real-world incl. failures" (mirrors the corrected report).

### Statistics (grounded in research)

- **Per-cell CIs:** Wilson score interval
  (`statsmodels.stats.proportion.proportion_confint(method='wilson')`).
- **Clustered SE** for model comparisons (instructions cluster within prompt):
  Miller 2024 (arXiv:2411.00640) — `statsmodels` OLS `cov_type='cluster'`,
  `groups=prompt_id`. Report alongside naive SE.
- **GLMM** (secondary, paper-grade): `pass ~ log(size) + k + (1|instruction_type)
  + (1|topic) + (1|prompt_id)` via `bambi`/`pymc` (Bernoulli/logit). Reports which
  variance dominates (instruction type vs topic).
- **Scaling fit:** 4-param sigmoid `Acc(N) = L + (U−L)/(1+exp(−s·(logN−logN₀)))`
  via `scipy.optimize.curve_fit`; **capacity `k*`** = k where all-pass crosses
  τ=0.5, with delta-method (or bootstrap) CI.
- **Metric caution** (Schaeffer et al. 2304.15004): report the **continuous**
  instruction-level fraction as primary (avoids fake "emergence"); report binary
  all-pass as secondary and note `all_pass ≈ p^k` as an independence diagnostic
  (directly engages ManyIFEval's `P(k)=p^k`).
- **Serial-position** (Liu et al. lost-in-the-middle): normalized position
  `(j−1)/(k−1)`, bucketed; quadratic-vs-flat LR test for a U-shape. Secondary
  result.

### Figures

1. **Phase-diagram heatmap (headline):** rows = models sorted by size, cols = k,
   cell = instruction-level fraction; diverging colormap centered at 0.5.
2. **Scaling curves (Fig 1, open-weight):** fraction vs log(params), one line per
   k, Wilson CI bands; within-family Llama line emphasized.
3. **Capacity law:** `k*(N)` vs log(params) with fit + CI.
4. **Frontier overlay (Fig 2):** closed models (sizes unknown) as a band over the
   open-weight curve; reasoning models marked (confound caveat in caption).
5. **Serial-position profiles** per model size bucket.

## Pilot Model Grid (exact OpenRouter IDs, catalog snapshot 2026-06-28)

**Open-weight dense ladder (8)** — anchored by a 5-point *within-family* Llama 3.x
line (gold standard for isolating size):

| Model | OpenRouter ID | Params (dense) | $/M in–out | Role |
|-------|---------------|----------------|------------|------|
| Llama 3.2 1B | `meta-llama/llama-3.2-1b-instruct` | 1.23B | 0.027–0.201 | Llama line |
| Llama 3.2 3B | `meta-llama/llama-3.2-3b-instruct` | 3.2B | 0.051–0.335 | Llama line |
| Llama 3.1 8B | `meta-llama/llama-3.1-8b-instruct` | 8B | 0.02–0.03 | Llama line |
| Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct` | 70B | 0.1–0.32 | Llama line |
| Hermes 3 405B | `nousresearch/hermes-3-llama-3.1-405b` | 405B | 1–1 | Llama line\* |
| Qwen3 14B | `qwen/qwen3-14b` | 14B | 0.1–0.24 | cross-family |
| Qwen3 32B | `qwen/qwen3-32b` | 32B | 0.08–0.28 | cross-family |
| Gemma 3 27B | `google/gemma-3-27b-it` | 27B (dense) | 0.08–0.16 | cross-family |

\*Hermes-3 is a finetune of Llama-3.1-405B (Meta's own 405B-Instruct isn't on the
cheap OpenRouter tier). Same base/size; flag the finetune as a minor confound, or
swap if Meta-Instruct becomes available.

**Frontier (2, swappable)** — analyzed as a separate band:

| Model | OpenRouter ID | $/M in–out |
|-------|---------------|------------|
| GPT-5.1 | `openai/gpt-5.1` | 1.25–10 |
| Claude Opus 4.8 | `anthropic/claude-opus-4.8` | 5–25 |

Pilot grid: **10 models × k∈{1,2,3,5,8,13} × 50 prompts × 1 instantiation ≈ 3,000
calls**. Per-model volume is 300 calls, so even Opus stays within the $5–15 band.
MoE models (Qwen3-30B-A3B, Nemotron, gpt-oss) and the total-vs-active-param
analysis are **deferred to Mid/Full**.

## System-Wide Impact

- **Interaction graph:** `build_dataset` is the new upstream dependency; `score`
  and `analyze` now consume per-instruction rows, so `compare.py` (old 4-metric
  table) becomes a thin legacy view or is retired.
- **Error propagation:** generation failures must flow as *tagged* rows all the
  way to `analyze`, never silently dropped (the prior bug). Scoring must tolerate
  `None`/truncated responses without crashing.
- **State lifecycle:** JSONL append-cache means a crashed `generate` resumes;
  `build_dataset` must be deterministic (seeded) so resumed runs match prompts.
- **API surface parity:** the old single-axis path (`compare.py`) and the new grid
  path should share `config.MODELS`; keep one model registry.
- **Integration scenarios:** (1) synthetic k≤3 vs native IFEval agreement; (2) a
  hand-written "perfect" response passes all `k` checks (composition sanity); (3)
  a `None` response yields k tagged failures, not a crash; (4) truncated response
  is flagged, not counted as a clean instruction miss.

## Acceptance Criteria

### Functional
- [ ] `instructions/conflict.py` loads official `INSTRUCTION_CONFLICTS` + 2 implicit
  edges; unit test asserts known conflicts (e.g. `english_capital` vs `english_lowercase`).
- [ ] `compose.py` emits valid IFEval-schema records; for 1,000 sampled `k`-sets, a
  programmatically-constructed reference response passes **all** their checkers
  (proves no impossible sets). `constrained_response`/`json_format`/`two_responses`/
  `repeat_prompt` never appear at k>1.
- [ ] `build_dataset.py` produces `datasets/ifeval_stack_pilot.jsonl`, deterministic
  under fixed seed; logs the achieved max-`k` ceiling.
- [ ] `generate.py` records `failure_class`, `finish_reason`, `usage`; scales
  `max_tokens` with k; resumes from cache.
- [ ] `score.py` outputs per-instruction rows incl. `gen_failure` + `position_index`;
  `langdetect` seeded.
- [ ] `analyze.py` outputs `cells.csv` (Wilson CI + clustered SE) and `capacity.csv`
  (`k*` per model w/ CI).
- [ ] `figures.py` produces the phase-diagram heatmap, open-weight scaling curves,
  `k*(N)` plot, and frontier overlay.
- [ ] `run_pilot.py` runs the whole pipeline for the PILOT preset.

### Validity / Quality gates
- [ ] Synthetic `k≤3` pass rates agree with native IFEval within a pre-registered
  margin (e.g. ±5 pts) per model; deviations investigated.
- [ ] Generation-failure rate reported per model; no silent drops.
- [ ] Reproducible: pinned model IDs + dated OpenRouter snapshot, fixed seeds,
  `temperature=0`, `langdetect` seeded; `requirements.txt` updated
  (`statsmodels`, `scipy`, `matplotlib`/`seaborn`, optional `bambi`/`pymc`).

### Success metric for the pilot
- [ ] A draft phase diagram showing a **monotone-ish degradation in k** and a
  **visible size effect** (larger models hold higher k), with CIs — enough signal
  to justify scaling to Mid/Full.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Composition produces impossible constraint sets → artificially low scores | Reuse official conflict graph + 2 implicit edges; 1,000-set reference-response test; k≤3 native cross-check |
| Max compatible `k` ceiling < 30 | Verify ceiling in Phase 1; cap k-levels to what the graph supports; document |
| Generation failures mis-scored (Qwen `None` trap) | Failure taxonomy, tagged rows, dual reporting |
| Truncation fails length constraints spuriously | `max_tokens(k)`; flag `finish_reason=="length"` |
| `langdetect` nondeterminism | `DetectorFactory.seed = 0` |
| temp=0 ≠ deterministic on served models (arXiv:2408.04667) | Report caveat; for headline cells optionally 3× repeat at Mid/Full |
| Reviewer: "ManyIFEval/IFScale already did this" | Position on size-axis + k*(N) law + open ladder + full-atom vocab; cite & differentiate explicitly |
| Contamination (IFEval in training data) | Fresh non-IFEval topics; report native-vs-synthetic delta |
| Cost overrun from reasoning tokens | Usage logging + spend ceiling; pilot volume tiny |

## Implementation Phases

- **Phase 1 — Foundations (no API cost):** `registry.py`, `conflict.py`,
  `compose.py`, `topics.py`, `build_dataset.py`; reference-response test; determine
  max-`k` ceiling; native IFEval cross-check harness. *Gate:* 1,000-set validity
  test passes.
- **Phase 2 — Grid generation + scoring:** refactor `generate.py` (failure
  taxonomy, token budget) and `score.py` (per-instruction, failure-aware); run the
  pilot grid. *Gate:* failure rates sane, k≤3 agrees with native IFEval.
- **Phase 3 — Analysis + figures:** `analyze.py` (Wilson, clustered SE, k* fit,
  optional GLMM) + `figures.py`; produce draft phase diagram. *Gate:* decide
  Mid/Full scale-up.

## Future Considerations
- Scale to Mid/Full (more models, MoE total-vs-active analysis, 3× repeats, k→30).
- Position-controlled ablation (shuffle vs fixed instruction order).
- Per-instruction-type difficulty atlas; conflict-aware "hardest pairs".
- Paper draft (intro positions against ManyIFEval + IFScale).

## Sources & References

### Origin
- **Brainstorm:** [docs/brainstorms/2026-06-28-instruction-density-scaling-study-brainstorm.md](../brainstorms/2026-06-28-instruction-density-scaling-study-brainstorm.md)
  — carried forward: hybrid axis (native k≤3 cross-check + synthetic stacking),
  open-weight + frontier analyzed separately, Pilot-first scale, reasoning models
  mixed into frontier band, conflict-matrix + within-family + failure-taxonomy
  guardrails.

### Internal
- Existing harness: `generate.py`, `score.py`, `config.py`, `ARCHITECTURE.md`.
- Prior corrected report (failure-confound motivation): `BENCHMARK_REPORT_CORRECTED.md`.
- Official IFEval registry/conflicts: `instruction_following_eval/instructions_registry.py`
  (`INSTRUCTION_DICT`, `INSTRUCTION_CONFLICTS`), `instructions.py`, `evaluation_lib.py`.

### External — related work to cite
- IFEval — Zhou et al. 2023, arXiv:2311.07911
- FollowBench — Jiang et al. ACL 2024, arXiv:2310.20410
- InFoBench — Qin et al. 2024, arXiv:2401.03601
- ComplexBench — Wen et al. NeurIPS 2024, arXiv:2407.03978
- **ManyIFEval / Curse of Instructions** — Harada et al. ICLR 2025, OpenReview R6q67CDBCH (primary competitor)
- When Instructions Multiply — EMNLP 2025, arXiv:2509.21051
- **IFScale** — Jaroslawicz et al. 2025, arXiv:2507.11538 (primary competitor)
- SIFo — Chen et al. EMNLP 2024, arXiv:2406.19999
- Multi-IF — 2024, arXiv:2410.15553
- CELLO — He et al. 2024, arXiv:2410.13382 · CFBench — arXiv:2408.01122
- ConInstruct (conflicting constraints) — arXiv:2511.14342
- 256 LLMs — arXiv:2510.18892 · Scaling Reasoning, Losing Control — arXiv:2505.14810
- Emergent Abilities — Wei et al. arXiv:2206.07682 · Mirage? — Schaeffer et al. arXiv:2304.15004

### External — methodology
- Adding Error Bars to Evals (clustered SE) — Miller 2024, arXiv:2411.00640
- Don't Use the CLT in LLM Evals — arXiv:2503.01747
- Order Matters / position bias (CDDI) — arXiv:2502.17204
- Lost in the Middle — Liu et al. TACL 2024
- Non-Determinism of "Deterministic" LLM Settings — arXiv:2408.04667
- Wilson score interval; `statsmodels` proportion_confint; `bambi`/`pymc` GLMM
