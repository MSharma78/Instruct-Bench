# ADR-008 — Variance via fresh topics, not temperature

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** TASK-005, TASK-008

## Context
We need replication/variance across prompts at each k. Options: sample at temperature>0 (nondeterministic), or re-instantiate the same constraint set over different base topics at temperature=0.

## Decision
Keep **temperature=0** and obtain variance by **re-instantiating constraint sets over fresh base topics** (≥60 topics, none drawn from IFEval).

## Rationale
Deterministic and reproducible; fresh non-IFEval topics also reduce training-data contamination (stacked prompts are novel). Avoids conflating sampling noise with instruction-following ability.

## Consequences
Requires a curated topic bank (TASK-005). Caveat (arXiv:2408.04667): served models aren't perfectly deterministic at temp=0 even so — note in reporting; consider 3× repeats for headline cells at Mid/Full.
