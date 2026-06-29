# BACKLOG — Agent Work Queue

Pull from top. Priority order: critical > high > normal > low.
Within a tier, pick unblocked items first.

---

## Active

### TASK-001 — Environment & IFEval setup
- **priority:** critical
- **status:** blocked
- **epic:** EPIC-01
- **blocked_by:** IN-001
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** venv + requirements (statsmodels, scipy, matplotlib/seaborn, optional bambi/pymc); run download_ifeval.sh; set OPENROUTER_API_KEY in .env.
- **outcome:** (filled on completion)

### TASK-002 — Instruction registry wrapper (instructions/registry.py)
- **priority:** high
- **status:** open
- **epic:** EPIC-01
- **blocked_by:** (none)
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Wrap IFEval atoms with metadata + per-atom parameter samplers (seeded). Tag solo/dominant atoms (constrained_response, json_format, two_responses, repeat_prompt).
- **outcome:** (filled on completion)

### TASK-003 — Conflict graph (instructions/conflict.py)
- **priority:** high
- **status:** open
- **epic:** EPIC-01
- **blocked_by:** (none)
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Load official INSTRUCTION_CONFLICTS (after conflict_make symmetry) + add implicit edges end_checker↔postscript and english_lowercase↔multiple_sections. Unit test asserts known conflicts. (see ADR-005)
- **outcome:** (filled on completion)

### TASK-004 — Prompt composer (instructions/compose.py)
- **priority:** high
- **status:** blocked
- **epic:** EPIC-01
- **blocked_by:** TASK-002, TASK-003
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Greedy CSP sampler of compatible k-sets; render prompt via each atom's build_description; emit IFEval record (key, prompt, instruction_id_list, kwargs). Exclude solo atoms at k>1; reject jointly-infeasible params.
- **outcome:** (filled on completion)

### TASK-005 — Fresh topic bank (topics.py)
- **priority:** normal
- **status:** open
- **epic:** EPIC-01
- **blocked_by:** (none)
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** ≥60 base writing tasks NOT drawn from IFEval (anti-contamination). Variance via topic re-instantiation, not temperature. (see ADR-008)
- **outcome:** (filled on completion)

### TASK-006 — Dataset builder (build_dataset.py)
- **priority:** high
- **status:** blocked
- **epic:** EPIC-01
- **blocked_by:** TASK-004, TASK-005
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Produce datasets/ifeval_stack_pilot.jsonl over k∈{1,2,3,5,8,13} × 50 prompts; deterministic under fixed seed; log achieved max-k ceiling.
- **outcome:** (filled on completion)

### TASK-007 — Validity gate: reference-response + k-ceiling
- **priority:** high
- **status:** blocked
- **epic:** EPIC-01
- **blocked_by:** TASK-006, IN-003
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** For 1,000 sampled k-sets, programmatically construct a satisfying reference response and confirm it passes ALL checkers (proves no impossible sets). Report max feasible k. GATE for EPIC-01.
- **outcome:** (filled on completion)

### TASK-008 — Refactor generate.py to grid + failure taxonomy
- **priority:** high
- **status:** blocked
- **epic:** EPIC-02
- **blocked_by:** TASK-007
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Grid loop (model × k × prompt); record failure_class {ok,empty_none,refusal,truncated,api_error}, finish_reason, usage; max_tokens=clamp(512+256*k+headroom,512,4096); temp=0; resumable cache. (see ADR-007)
- **outcome:** (filled on completion)

### TASK-009 — Refactor score.py to per-instruction + failure-aware
- **priority:** high
- **status:** blocked
- **epic:** EPIC-02
- **blocked_by:** TASK-007
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Emit one row per instruction (model,k,topic,instr_id,position_index,strict_pass,loose_pass,gen_failure) via evaluation_lib. Set langdetect.DetectorFactory.seed=0. Tag (not drop) failures.
- **outcome:** (filled on completion)

### TASK-010 — Run pilot grid
- **priority:** high
- **status:** blocked
- **epic:** EPIC-02
- **blocked_by:** TASK-008, IN-001, IN-002
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Generate + score for 10 models × k∈{1,2,3,5,8,13} × 50 prompts (~3,000 calls). Log per-model generation-failure rate and spend.
- **outcome:** (filled on completion)

### TASK-011 — Native IFEval cross-check (k≤3) gate
- **priority:** normal
- **status:** blocked
- **epic:** EPIC-02
- **blocked_by:** TASK-010, IN-003
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Compare synthetic k≤3 pass rates vs native IFEval per model; investigate any deviation beyond pre-registered margin. GATE for EPIC-02.
- **outcome:** (filled on completion)

### TASK-012 — Analysis (analyze.py)
- **priority:** high
- **status:** blocked
- **epic:** EPIC-03
- **blocked_by:** TASK-011
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Per-(model,k) aggregates with Wilson CIs + clustered SE (cluster=prompt_id); fit 4-param sigmoid; estimate k* (τ=0.5) with delta-method CI; optional GLMM (bambi/pymc). Output cells.csv, capacity.csv.
- **outcome:** (filled on completion)

### TASK-013 — Figures (figures.py)
- **priority:** high
- **status:** blocked
- **epic:** EPIC-03
- **blocked_by:** TASK-012
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** Phase-diagram heatmap (model×k); open-weight scaling curves vs log(params) w/ CI bands; k*(N) law; frontier overlay band (reasoning models marked); serial-position profiles.
- **outcome:** (filled on completion)

### TASK-014 — Pilot orchestrator + scale-up decision
- **priority:** normal
- **status:** blocked
- **epic:** EPIC-03
- **blocked_by:** TASK-013, IN-002
- **created:** 2026-06-28
- **completed:** (empty)
- **summary:** run_pilot.py runs build→generate→score→analyze→figures for PILOT preset. Review draft phase diagram; record go/no-go on Mid/Full. GATE for EPIC-03.
- **outcome:** (filled on completion)

---

## Completed

_(Items move here temporarily; daily sweep archives them.)_
