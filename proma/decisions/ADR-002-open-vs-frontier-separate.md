# ADR-002 — Open-weight and frontier models analyzed separately

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** EPIC-03, TASK-013

## Context
Open-weight models have published parameter counts; frontier (closed) models do not. Forcing closed models onto a parameter x-axis would fabricate a number.

## Decision
Two figures. **Fig 1**: open-weight scaling curves on a true param x-axis. **Fig 2**: frontier models as an overlay *band* (size unknown), positioned relative to the open-weight curve.

## Rationale
Preserves a clean, reproducible scaling axis while still answering the topical question "where do frontier models land / how many effective params do they behave like?"

## Consequences
Analysis and figures branch by `is_open_weight` / `is_frontier` flags in config. Frontier points carry no x-coordinate, only a capacity band.
