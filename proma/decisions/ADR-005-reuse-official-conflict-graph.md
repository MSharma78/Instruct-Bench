# ADR-005 — Reuse official IFEval INSTRUCTION_CONFLICTS (+2 implicit edges)

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** TASK-003

## Context
Stacking arbitrary IFEval atoms can produce logically impossible constraint sets (e.g. english_lowercase + english_capital; constrained_response with anything). A conflict graph is required. IFEval already ships `INSTRUCTION_CONFLICTS` in `instructions_registry.py`.

## Decision
**Reuse** the official conflict graph (after its `conflict_make` symmetry closure) rather than hand-building one. Add two implicit edges research found missing: `startend:end_checker ↔ detectable_content:postscript` and `change_case:english_lowercase ↔ detectable_format:multiple_sections`. Treat `constrained_response`, `json_format`, `two_responses`, `repeat_prompt` as solo-only (never at k>1).

## Rationale
The official graph encodes subtle, authoritative conflicts; reimplementing invites bugs and non-comparability. Far less work, far more trustworthy.

## Consequences
Max feasible k is bounded by the graph's largest compatible clique — must be measured (TASK-007), likely ~12–18 before forced conflicts. Also set `langdetect.DetectorFactory.seed=0` for deterministic language/case checks.
