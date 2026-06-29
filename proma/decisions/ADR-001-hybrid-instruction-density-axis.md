# ADR-001 — Hybrid instruction-density axis

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** EPIC-01, TASK-011

## Context
The "number of instructions" (k) axis can be built by (a) bucketing native IFEval prompts (k≤3 only), (b) pure synthetic stacking, or (c) a hybrid. Native prompts cap at k≈3; pure synthetic loses comparability to the established benchmark.

## Decision
Use the **hybrid** axis: native IFEval (k≤3) as a validity cross-check, synthetic composition for k above 3 (pilot: k∈{1,2,3,5,8,13}).

## Rationale
Keeps comparability to IFEval where it overlaps, while extending range far enough to observe degradation and a capacity threshold. The k≤3 agreement check is a built-in correctness test for the composer.

## Consequences
Requires a synthetic composer (TASK-004) and a native cross-check gate (TASK-011). A systematic synthetic-vs-native gap signals a composition bug.
