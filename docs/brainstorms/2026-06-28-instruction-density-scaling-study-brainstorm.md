---
date: 2026-06-28
topic: instruction-density-scaling-study
---

# IFEval-Stack: Instruction-Density × Model-Size Scaling Study

## What We're Building

A controlled study measuring how well LLMs follow instructions as a function of
two axes — **instruction density** (number of simultaneous constraints `k` in a
prompt) and **model size** (parameter count) — to produce a scaling "phase
diagram" of instruction-following capacity. Aimed at a publishable paper.

The key enabler: IFEval instructions are *programmatically verifiable*. We compose
them into prompts with a controlled count `k`, then auto-score the fraction
satisfied — no LLM judge, no human raters. This makes the study rigorous,
deterministic, and cheap enough to run at scale.

**Axes / the headline figure (the "index"):**
- **X = instruction density:** `k ∈ {1,2,3,5,8,13,20,30}`. Native IFEval prompts
  cover k≤3 (used as a cross-check); synthetic stacking extends k above 3.
- **Y = model size:** dense ladder 1B → 3B → 8B → 14B → 24/27B → 32B → 70B → 405B.
- **Cell value:** fraction of the k instructions satisfied (instruction-level),
  plus all-pass rate (prompt-level).

**Two figures (open-weight and frontier analyzed separately):**
- **Fig 1:** clean open-weight scaling curves (true param x-axis).
- **Fig 2:** frontier models (GPT-5.x, Claude Opus 4.x, Gemini 3.x, Grok 4.x,
  DeepSeek V4) overlaid as a band — sizes undisclosed, so not point estimates.

## Why This Approach

Considered three framings for the instruction axis: (a) bucket native IFEval
prompts by their 1–3 instructions — too narrow for a scaling claim; (b) pure
synthetic stacking — loses comparability to the established benchmark;
(c) **hybrid** — validate synthetic prompts against native IFEval at k≤3, then
extend with synthetic stacking to high k. Chose (c) for rigor + range.

Model scope: open-weight gives a clean, reproducible size axis; frontier models
are topical but size-unknown. Chose to analyze **both separately** rather than
forcing closed models onto a parameter x-axis.

## Key Decisions

- **Instruction-conflict matrix (critical):** randomly stacking instructions can
  produce logically impossible sets (e.g., "all lowercase" + "title case").
  Build a compatibility graph; sample only mutually-satisfiable constraint sets.
- **Within-family size ladders preferred:** Llama (1/3/8/70/405B) and Qwen3
  (8/14/32B) isolate *size* with training held roughly constant. Cross-family
  points are confounded. Report dense params; for MoE note total vs active.
- **Separate generation failures from instruction failures:** prior corrected
  report shows Qwen returned `None` for ~40% of prompts. Log empty/refused/
  truncated as a distinct category; never count silently as instruction misses.
- **Scale `max_tokens` with k:** a fixed 1024 cap artificially fails length
  constraints at high k.
- **Variance via fresh topics, not temperature:** keep temp=0 (deterministic),
  get "seeds" by re-instantiating each constraint set over different base topics.
  Also mitigates training-data contamination (stacked prompts are novel).
- **Metric emphasis:** at high k, prompt-level all-pass → 0 quickly; the
  informative quantity is the instruction-level satisfied-fraction and the
  "instruction capacity" — the k at which a model drops below a threshold
  (e.g., 50% all-pass).

## Scale / Cost Tiers (OpenRouter, live pricing 2026-06-28)

| Tier  | Models                | k-levels | prompts × inst. | calls    | est. cost |
|-------|-----------------------|----------|-----------------|----------|-----------|
| Pilot | 10 (8 open + 2 front) | 6        | 50 × 1          | ~3,000   | $5–15     |
| Mid   | 16 (10 open + 6 front)| 8        | 100 × 2         | ~25,600  | $60–150   |
| Full  | 24 (12 open + 12 front)| 8       | 200 × 3         | ~115,000 | $300–800  |

Cost driver: reasoning models (o3, gpt-5-pro) bill hidden reasoning tokens
(3–5× multiplier) and dominate the upper end of each range.

## Decided Scope

- **Scale: Pilot first** — 10 models (8 open-weight dense ladder + 2 frontier),
  k ∈ {1,2,3,5,8,13}, 50 prompts/level × 1 instantiation (~3,000 calls, $5–15).
  Goal: prove the conflict matrix + synthetic generator + scoring end-to-end and
  produce a draft heatmap before scaling to Mid/Full.
- **Reasoning models: mixed into the frontier band** — DeepSeek-R1, o3,
  gpt-5-pro, Qwen-thinking appear as additional points on Fig 2 (frontier), not a
  separate sub-study. Caveat to handle in analysis: this confounds the size axis
  and adds hidden-reasoning-token cost; flag in figure captions + cost tracking.

## Open Questions (for planning)

- **Literature positioning:** multi-constraint IF benchmarks already exist
  (ManyIFEval, InFoBench, ComplexBench). Novelty here = the *scaling-law* framing.
  Do a focused lit-check so the contribution is unmistakable before investing.
- Statistical plan: Wilson CIs on proportions; mixed-effects model with
  instruction-type as a random effect.
- Serial-position analysis: do models drop *late* instructions ("lost in the
  middle")? Optional secondary result.

## Next Steps
→ `/workflows:plan` for the implementation plan (conflict matrix, synthetic
  prompt generator, harness refactor for the k × model grid, scoring, analysis,
  and figure generation).
