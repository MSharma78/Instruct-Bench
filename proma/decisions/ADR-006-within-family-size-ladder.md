# ADR-006 — Within-family dense ladder as primary size axis

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** TASK-010, TASK-013

## Context
Cross-family model comparisons confound size with training data, recipe, and tokenizer. A clean size effect needs architecture/training held roughly constant.

## Decision
Anchor the size axis with a **within-family dense ladder** — Llama 3.x: 1B, 3B, 8B, 70B, 405B (Hermes-3 finetune at 405B). Add Qwen3 (14B/32B) and Gemma 3 (27B) as cross-family breadth, plotted but secondary.

## Rationale
The within-family line isolates parameter count as the variable; cross-family points show generality. Reviewers expect this control.

## Consequences
Hermes-3-405B is an instruction finetune of Llama-3.1-405B (Meta-Instruct not on the cheap OR tier) — a minor confound to flag, or swap if Meta-Instruct becomes available. MoE models (total vs active params) deferred to Mid/Full.
