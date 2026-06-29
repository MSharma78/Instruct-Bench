# ADR-007 — Separate generation-failure taxonomy from instruction failures

- **Date:** 2026-06-28
- **Status:** accepted
- **Related:** TASK-008, TASK-009

## Context
The repo's own corrected report showed Qwen returned `None` for ~40% of prompts; scoring only valid responses inflated its rank. Generation failures and instruction failures are different phenomena and must not be conflated.

## Decision
`generate.py` records a `failure_class` per call ∈ {ok, empty_none, refusal, truncated, api_error} plus finish_reason and token usage. `score.py` tags a failed-generation response's instructions as failed **but flagged**, enabling dual reporting: "IF on valid responses" vs "real-world incl. failures".

## Rationale
Prevents the exact measurement trap that corrupted the prior report; surfaces reliability as a first-class result.

## Consequences
Scoring tolerates None/truncated without crashing. `max_tokens` scales with k so truncation doesn't fail length constraints spuriously (clamp 512–4096).
