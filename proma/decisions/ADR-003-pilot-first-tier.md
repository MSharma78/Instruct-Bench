# ADR-003 — Pilot-first scaling tier

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** EPIC-02

## Context
Three scale tiers were costed: Pilot (~3,000 calls, $5–15), Mid (~25,600, $60–150), Full (~115,000, $300–800). A flaw in the composer/conflict matrix or scoring wastes more money at larger scale.

## Decision
Run the **Pilot** first (10 models × k∈{1,2,3,5,8,13} × 50 prompts × 1 instantiation) to validate the method and produce a draft phase diagram, then decide on Mid/Full.

## Rationale
De-risks the method cheaply. The pilot exercises every component end-to-end.

## Consequences
A go/no-go gate (TASK-014) precedes any larger spend. Statistical power at pilot scale is limited (single instantiation, n per cell modest) — sufficient for signal, not final claims.
