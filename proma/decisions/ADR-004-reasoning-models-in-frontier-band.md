# ADR-004 — Reasoning models mixed into the frontier band

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** IN-002, TASK-013

## Context
Reasoning models (o3, gpt-5-pro, DeepSeek-R1, Qwen-thinking) bill hidden reasoning tokens and may follow more constraints via test-time compute. They could be a separate sub-study or folded into the frontier band.

## Decision
**Mix them into the frontier band** (Fig 2) rather than running a separate sub-study, for the pilot.

## Rationale
Simplest path to a first result; keeps pilot scope contained. User's explicit choice.

## Consequences
Confounds the size interpretation of the frontier band and inflates cost. Mitigation: mark reasoning models distinctly in figures, log reasoning-token usage, and caveat in captions. Revisit as a dedicated overlay at Mid/Full.
