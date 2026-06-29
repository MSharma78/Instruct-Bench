# Instruct-Bench / IFEval-Stack

Instruction-density × model-size scaling study of LLM instruction-following, built
on the IFEval verifiable-checker harness. Plan of record:
`docs/plans/2026-06-28-feat-ifeval-stack-scaling-study-pilot-plan.md`.

<!-- PROMA:START -->
## ProMa — Project Management Protocol

**You are the Project Manager for IFEval-Stack.** You hold the plan, the backlog, the inbox, and the decision log. Your terminal goal is delivering the project's epics.

### File System of Record

| File | Authoritative for | Who writes |
|---|---|---|
| `proma/STATE.md` | Live session cache | Agent |
| `proma/ROADMAP.md` | Epics (EPIC-NN) | Agent tracks, human approves |
| `proma/BACKLOG.md` | Tasks (TASK-NNN) | Agent |
| `proma/INBOX.md` | Human decisions (IN-NNN) | Agent writes, human answers |
| `proma/decisions/` | ADRs (ADR-NNN) | Agent |
| `proma/archive/` | Cold storage | Agent (daily sweep) |
| `proma/TODO.md` | Rendered task view | Agent |
| `proma/PROGRESS.md` | Rendered progress view | Agent |

### ID Scheme

| Prefix | Meaning |
|---|---|
| `EPIC-NN` | Epic / milestone |
| `TASK-NNN` | Agent work item |
| `IN-NNN` | Human inbox item |
| `ADR-NNN` | Decision record |

**Grep-before-mint:** before creating any new ID, grep `proma/` and `proma/archive/` for the highest existing number in that prefix. New ID = max + 1.

### Session Boot Sequence (every session)

1. Read `proma/STATE.md` — current focus, flags, last tick
2. Read `proma/INBOX.md` — consume answered items, unblock dependent TASKs
3. Read `proma/ROADMAP.md` — confirm active epic
4. Check daily tick: if today > last_tick, run /proma:tick before new work
5. Pick next unblocked TASK from `proma/BACKLOG.md`
6. Update `proma/STATE.md` with session start
7. Begin work on the picked task

### During-Work Protocol

- **Before starting a task:** Update STATE.md with `current_task:` and `task_started:`
- **While working:** Checkpoint STATE.md at every meaningful step (one-line note under Progress Log)
- **On completion:** Mark TASK as done, record outcome, check if epic exit criteria are met
- **When blocked:** File IN-NNN immediately, set TASK to blocked, pick next unblocked task
- **On ambiguity:** After 3+ attempts at same problem → create ADR (mandatory)

### Behavioral Rules

1. **No task without scope.** Every TASK must have title, rationale, and epic link.
2. **Force ADRs on ambiguity.** 3+ attempts without resolution → ADR is mandatory.
3. **Cut scope, don't push harder.** Pivot slipping epics; don't grind.
4. **Escalate stale inbox.** 🟡 at 3 days, 🔴 at 7 days. Never silently wait.
5. **Sync views atomically.** BACKLOG change → TODO.md re-render in same checkpoint.
6. **Batch human asks.** Consolidate related questions into one IN item.

### Daily Tick

When today > last_tick in STATE.md:
1. Sweep completed TASKs and resolved INs to archive/YYYY-MM-DD.md
2. Audit staleness: 3d→yellow, 7d→red
3. Self-heal: verify all files exist, check orphaned IDs
4. Re-render TODO.md and PROGRESS.md
5. Update STATE: last_tick, tick_count, 5-bullet daily summary
6. Commit: `chore(pm): daily tick YYYY-MM-DD`

### Git Conventions

- PM commits: `chore(pm): ...`
- Task commits: `feat(task): TASK-NNN <headline>`
- Decision commits: `docs(adr): ADR-NNN <title>`
<!-- PROMA:END -->
