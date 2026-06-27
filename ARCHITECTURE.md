# Architecture: The Big Picture

## One-Paragraph Flow

The harness reads ~500 official IFEval prompts (instruction-following tasks) and sends each to three open-weight LLMs via OpenAI-compatible endpoints (Groq, OpenRouter, Google AI Studio). For each model, we save the prompt-response pairs as JSONL. Then, for each model's responses, we run the official IFEval instruction checkers—which evaluate whether each response correctly follows the instruction in both strict (exact match) and loose (after text normalization) modes—producing four accuracy metrics: instruction-level and prompt-level, each in strict and loose. Finally, we aggregate the metrics into a single comparison table showing which model follows instructions best.

## Why This Design?

### Use Official Checkers, Not Reimplemented Ones
The IFEval checkers handle subtle edge cases:
- Strict evaluation expects exact text matches; loose applies 8 transformations (lowercase, punctuation removal, etc.).
- Instruction types range from "contains the phrase X" to "word count in range [a, b]" to "URL pattern matching."
- Off-by-one errors or missed edge cases would make scores non-comparable to the official benchmark.

Solution: Import the checkers directly from `instruction_following_eval.evaluation.eval_utils`.

### Separate Generation and Scoring
API calls are expensive and slow; checkers are fast. If a run crashes during scoring, we don't re-call the APIs—we just re-run the scoring code.

Solution: `generate.py` → JSONL files → `score.py`. Cache already-generated responses in JSONL so resuming a partial run is free.

### Parameterized Model List
Want to add Mixtral or swap OpenRouter for Together.ai? Don't edit scripts—edit `config.py`. Each model is one dict with name, endpoint, API key env var, and model ID.

Solution: All three models go through identical code paths (OpenAI-compatible client), so swapping is one-line in config.

### Rate Limiting and Backoff
Free tiers enforce strict rate limits (Groq ~10 req/min, OpenRouter similar). A naive loop will hit 429 errors and fail. We need exponential backoff with jitter to retry intelligently.

Solution: Catch `RateLimitError`, exponential backoff (base 2, max 120s), sleep per-request based on configured RPM.

### CSV Output
The table is useful on screen but also as a CSV for email, spreadsheet import, or further analysis.

Solution: `compare.py` prints to terminal *and* saves to CSV.

## Data Flow Diagram

```
                        config.py (models, rate limits)
                              ↓
            ┌──────────────────────────────────────────┐
            │         generate.py                      │
            │ For each model in MODELS:               │
            │   - Check API key env var               │
            │   - Load 500 IFEval prompts             │
            │   - For each prompt:                    │
            │     * Call OpenAI-compatible endpoint   │
            │     * Retry on 429 with backoff        │
            │     * Append response to JSONL file     │
            │   - Cache: skip already-done prompts   │
            └──────────────────────────────────────────┘
                              ↓
            responses/llama_3.3_70b_responses.jsonl
            responses/qwen_100b_variant_responses.jsonl
            responses/gemma_3_27b_responses.jsonl
                    (each: instruction_id, response)
                              ↓
            ┌──────────────────────────────────────────┐
            │         score.py                         │
            │ For each model's response file:          │
            │   - Load responses from JSONL            │
            │   - Load original prompts + instructions │
            │   - Import official eval_utils checkers │
            │   - For each response:                  │
            │     * Check each instruction            │
            │     * Record strict/loose pass          │
            │   - Compute 4 metrics (prompt/instr     │
            │     × strict/loose)                     │
            │   - Save to scores.json                 │
            └──────────────────────────────────────────┘
                              ↓
            scores/scores.json
            {
              "name": "Llama 3.3 70B",
              "prompt_level_strict": 42.3,
              ...
            }
                              ↓
            ┌──────────────────────────────────────────┐
            │         compare.py                       │
            │ - Load scores.json                       │
            │ - Format as ASCII table                  │
            │ - Print to terminal                      │
            │ - Save as comparison.csv                 │
            └──────────────────────────────────────────┘
                              ↓
            Terminal:                    scores/comparison.csv
            Model            | P Strict % | ... |
            Llama 3.3 70B   | 42.3       | ... |
            ...
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Use official IFEval checkers | Reimplement → bugs, non-comparable results. Official code is subtle. |
| OpenAI-compatible endpoints | All three models use same API shape; easy to add more models. |
| JSONL for intermediate data | Structured, line-delimited, resumable, human-readable. |
| Config as a list of dicts | Swapping/adding models is one-line: edit `config.py`, add env var to `.env`. |
| Exponential backoff for 429s | Free tier APIs are rate-limited. Naive retries fail. Backoff + jitter works. |
| Cache by instruction_id | Long-running generation can crash. Resume without re-calling APIs. |
| Four separate metrics | Two levels (prompt, instruction) × two modes (strict, loose) = comprehensive picture of model ability. |

## Files at a Glance

| File | Lines | Purpose |
|------|-------|---------|
| config.py | ~30 | Model list + rate limits. Edit here to add models. |
| generate.py | ~180 | Call models, save JSONL, backoff on 429. |
| score.py | ~150 | Run official checkers, compute metrics. |
| compare.py | ~70 | Read scores, print table, save CSV. |
| download_ifeval.sh | ~20 | Clone official repo (one-time setup). |
| requirements.txt | ~10 | Python dependencies. |

Total: ~450 lines of user-facing code (excluding IFEval's ~2000 lines of checkers).

## Extending the Project

**Add a model:** Edit `config.py`, add env var to `.env`, re-run `generate.py`.

**Change metrics:** Edit the `metrics` list in `compare.py` to show different columns.

**Analyze by instruction type:** Modify `score.py` to bucket results by constraint type (e.g., "word count" vs. "contains phrase") and see which types the model struggles with.

**Hyperparameter sweep:** Edit the prompt (e.g., temperature, max_tokens in `generate.py`) and re-generate.

## Known Limitations

- **Official IFEval integration** is based on the expected structure of the repo (as of early 2024). If the official code layout changes significantly, `score.py` will fail; adjust imports and data access paths as needed.
- **Rate limits** are configured conservatively for free tiers. Paid accounts may allow higher RPM; update `config.py` accordingly.
- **No fault tolerance for failed scoring.** If `score.py` crashes mid-evaluation, you have to re-run it (it will re-evaluate all responses). Add checkpointing if evaluating 10k+ prompts.
- **No model-side rate limiting (token budget).** If generating long responses with low max_tokens, you may hit budget limits; adjust in `generate.py`.
