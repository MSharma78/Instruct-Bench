# INBOX — Human Work Queue

Agent writes IN-NNN items. Human fills the `#### Answer` section.
Agent consumes answers on next session start.

---

## Open

### IN-001 — API access & pilot budget approval
- **Date opened:** 2026-06-28
- **Gate type:** resource
- **Status:** pending
- **Blocking:** TASK-001 | TASK-010
- **Informs:** all generation work
- **Flag:** (empty)

#### Context
The pilot runs ~3,000 OpenRouter calls (10 models × 6 k-levels × 50 prompts), estimated $5–15. Reasoning/frontier models are the main cost swing. Foundation work (EPIC-01) needs no API and can proceed now.

#### Question
(1) Is an `OPENROUTER_API_KEY` available to put in `.env`? (2) Do you approve the ~$5–15 pilot spend? (3) Any hard ceiling I should enforce in code (e.g., abort at $X)?

#### Answer
<!-- Fill in your answer here -->

---

### IN-002 — Confirm the 2 frontier models for the pilot
- **Date opened:** 2026-06-28
- **Gate type:** scope
- **Status:** pending
- **Blocking:** TASK-010 | TASK-014
- **Informs:** frontier overlay (Fig 2)
- **Flag:** (empty)

#### Context
The pilot uses 8 open-weight models (fixed: Llama 3.2 1B/3B, Llama 3.1 8B, Llama 3.3 70B, Hermes-3 405B, Qwen3 14B/32B, Gemma 3 27B) + 2 frontier. Plan default: `openai/gpt-5.1` + `anthropic/claude-opus-4.8`. Reasoning models are folded into the frontier band per ADR-004.

#### Question
Keep `gpt-5.1` + `claude-opus-4.8`, or swap (e.g., `google/gemini-3.1-pro-preview`, `x-ai/grok-4.3`, `deepseek/deepseek-v4-pro`, or a reasoning model like `openai/o3`)? Pick exactly 2 for the pilot.

#### Answer
<!-- Fill in your answer here -->

---

### IN-003 — Pre-registration of validity thresholds
- **Date opened:** 2026-06-28
- **Gate type:** methodology
- **Status:** pending
- **Blocking:** TASK-007 | TASK-011
- **Informs:** validity gates, paper credibility
- **Flag:** (empty)

#### Context
To avoid post-hoc tuning, fix these before running: (a) the acceptable margin for synthetic-vs-native IFEval agreement at k≤3, (b) the capacity threshold τ defining k*, (c) the pilot k-levels.

#### Question
Confirm or adjust: (a) margin = ±5 percentage points; (b) τ = 0.5 (prompt-level all-pass); (c) k-levels = {1,2,3,5,8,13}. OK as-is, or change any?

#### Answer
<!-- Fill in your answer here -->

---

## Resolved

_(Resolved items stay here until the daily sweep archives them.)_
