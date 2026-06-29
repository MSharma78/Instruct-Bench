# TODO — IFEval-Stack

Two-queue task system: BACKLOG (agent work) + INBOX (human decisions).

---

## Agent Queue (TASK-NNN)

| ID | Title | Priority | Status | Epic | Blocked By |
|---|---|---|---|---|---|
| TASK-001 | Environment & IFEval setup | critical | blocked | EPIC-01 | IN-001 |
| TASK-002 | Instruction registry wrapper | high | open | EPIC-01 | (none) |
| TASK-003 | Conflict graph | high | open | EPIC-01 | (none) |
| TASK-004 | Prompt composer | high | blocked | EPIC-01 | TASK-002, TASK-003 |
| TASK-005 | Fresh topic bank | normal | open | EPIC-01 | (none) |
| TASK-006 | Dataset builder | high | blocked | EPIC-01 | TASK-004, TASK-005 |
| TASK-007 | Validity gate (reference-response + k-ceiling) | high | blocked | EPIC-01 | TASK-006, IN-003 |
| TASK-008 | Refactor generate.py (grid + failure taxonomy) | high | blocked | EPIC-02 | TASK-007 |
| TASK-009 | Refactor score.py (per-instruction) | high | blocked | EPIC-02 | TASK-007 |
| TASK-010 | Run pilot grid | high | blocked | EPIC-02 | TASK-008, IN-001, IN-002 |
| TASK-011 | Native IFEval cross-check (k≤3) | normal | blocked | EPIC-02 | TASK-010, IN-003 |
| TASK-012 | Analysis (analyze.py) | high | blocked | EPIC-03 | TASK-011 |
| TASK-013 | Figures (figures.py) | high | blocked | EPIC-03 | TASK-012 |
| TASK-014 | Pilot orchestrator + scale-up decision | normal | blocked | EPIC-03 | TASK-013, IN-002 |

## Human Queue (IN-NNN)

| ID | Title | Type | Status | Blocking | Flag |
|---|---|---|---|---|---|
| IN-001 | API access & pilot budget approval | resource | pending | TASK-001, TASK-010 | |
| IN-002 | Confirm 2 frontier models | scope | pending | TASK-010, TASK-014 | |
| IN-003 | Pre-registration of validity thresholds | methodology | pending | TASK-007, TASK-011 | |
