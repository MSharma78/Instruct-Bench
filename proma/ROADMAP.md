# ROADMAP — IFEval-Stack

**Terminal goal:** A publishable instruction-density × model-size scaling study: a 2D phase diagram (model × k → fraction of instructions followed) and a fitted instruction-capacity law k*(N), built on the IFEval verifiable-checker harness. Pilot tier first.

**Plan of record:** docs/plans/2026-06-28-feat-ifeval-stack-scaling-study-pilot-plan.md
**Origin brainstorm:** docs/brainstorms/2026-06-28-instruction-density-scaling-study-brainstorm.md

---

### EPIC-01 — Foundations: Synthetic Instruction Composer & Dataset
- **status:** active
- **created:** 2026-06-28
- **closed:** (empty)
- **exit_criteria:**
  - [ ] Official `INSTRUCTION_CONFLICTS` + 2 implicit edges loaded; conflict unit test passes
  - [ ] `compose.py` emits valid IFEval-schema records; 1,000-set reference-response test passes (no impossible sets); solo atoms never at k>1
  - [ ] `build_dataset.py` produces `datasets/ifeval_stack_pilot.jsonl` deterministically; max-k ceiling logged
  - [ ] ≥60 fresh non-IFEval topics in `topics.py`
- **blocked_by:** (none)
- **blocks:** EPIC-02, EPIC-03

---

### EPIC-02 — Grid Generation & Scoring
- **status:** planned
- **created:** 2026-06-28
- **closed:** (empty)
- **exit_criteria:**
  - [ ] `generate.py` records failure_class/finish_reason/usage; scales max_tokens with k; resumes from cache
  - [ ] `score.py` emits per-instruction rows incl. gen_failure + position_index; langdetect seeded
  - [ ] Pilot grid run complete (10 models × k∈{1,2,3,5,8,13} × 50 prompts)
  - [ ] Synthetic k≤3 agrees with native IFEval within pre-registered margin; failure rates reported per model
- **blocked_by:** EPIC-01
- **blocks:** EPIC-03

---

### EPIC-03 — Analysis, Figures & Scale-Up Decision
- **status:** planned
- **created:** 2026-06-28
- **closed:** (empty)
- **exit_criteria:**
  - [ ] `analyze.py` outputs cells.csv (Wilson CI + clustered SE) and capacity.csv (k* per model w/ CI)
  - [ ] `figures.py` produces phase-diagram heatmap, open-weight scaling curves, k*(N) law, frontier overlay, serial-position
  - [ ] Draft phase diagram shows degradation-in-k + visible size effect with CIs
  - [ ] Go/no-go decision recorded on scaling to Mid/Full
- **blocked_by:** EPIC-02
- **blocks:** (paper draft — future)

---

## Closed Epics

_(Epics move here on closure.)_

## Deferred Epics

_(Epics move here when deferred via human approval.)_
