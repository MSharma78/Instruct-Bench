# IFEval Evaluation Harness

A small, readable harness to test three open-weight LLMs on the [IFEval benchmark](https://github.com/google-research/google-research/tree/master/instruction_following_eval) (Zhou et al. 2023, Google).

The harness generates responses from three models via OpenAI-compatible endpoints, then scores them using the official IFEval checkers, producing a single comparison table.

## Overview: How It Works

```
1. IFEval Prompts (500 official instructions from Google Research)
           ↓
2. generate.py → Calls each model (Groq, OpenRouter) → Saves JSONL responses
           ↓
3. score.py → Runs official IFEval checkers → Produces four metrics per model
           ↓
4. compare.py → Aggregates scores → Prints table + saves CSV
```

**The Four Metrics:**
- **Prompt-level strict**: Fraction of prompts where the model's response satisfies *all* instructions exactly (case-sensitive, with punctuation).
- **Instruction-level strict**: Fraction of individual instructions that the model's responses satisfy exactly.
- **Prompt-level loose**: Same as strict, but after 8 transformations (lowercase, remove punctuation, etc.) are applied to the response.
- **Instruction-level loose**: Same as strict instruction-level, but with transformations.

Loose metrics are more forgiving; strict metrics are the ground truth.

## Setup

### 1. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set API Keys

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Then edit `.env`:
```
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
```

**Where to get keys:**
- **Groq** (for Llama 3.3 70B): https://console.groq.com — free tier allows ~10 req/min
- **OpenRouter** (for Qwen and Gemma 3): https://openrouter.ai — free tier with API credits

If you don't set a key, that model is skipped with a clear message.

### 4. Download Official IFEval Code

```bash
bash download_ifeval.sh
```

This clones the official repo and extracts the evaluation code + prompts to `instruction_following_eval/`.

## Running the Evaluation

### Step 1: Generate Responses

```bash
python generate.py
```

This:
- Loads all 500 IFEval prompts.
- For each model (and each prompt), calls the OpenAI-compatible endpoint.
- Retries on rate-limit (HTTP 429) with exponential backoff.
- Saves responses to `responses/` as JSONL files (one per model).
- **Caches**: If a run crashes, re-run this command; it skips already-generated prompts.

Expected runtime: ~30–60 minutes (depends on rate limits).

### Step 2: Score Responses

```bash
python score.py
```

This:
- For each model's response file, loads all responses.
- Runs the official IFEval instruction checkers on each one.
- Computes the four metrics.
- Saves scores to `scores/scores.json`.

**Note**: `score.py` uses the official `evaluation_lib.py` module which is baked into the IFEval repo. If you get import errors, verify that `instruction_following_eval/evaluation_lib.py` exists and is importable.

### Step 3: Print Comparison

```bash
python compare.py
```

This:
- Reads scores from `scores/scores.json`.
- Prints a formatted table to the terminal.
- Saves the table as `scores/comparison.csv`.

## Output Files

After running all three scripts:

```
responses/
├── llama_3.3_70b_responses.jsonl
├── qwen_100b_variant_responses.jsonl
└── gemma_3_27b_responses.jsonl

scores/
├── scores.json                   # Raw metric values
└── comparison.csv                # Table for easy import
```

## Project Structure

- **config.py** — Model list (name, base_url, env var, model ID) and rate-limit defaults. Edit here to swap/add models.
- **generate.py** — Calls models and saves responses. Handles rate-limit backoff.
- **score.py** — Runs official IFEval checkers. Computes four metrics.
- **compare.py** — Aggregates scores and prints the table.
- **download_ifeval.sh** — One-time setup: fetches official IFEval code.
- **requirements.txt** — Python dependencies.
- **.env.example** — Template for API keys.

## Why Use the Official Checkers?

The IFEval instruction checkers are subtle:
- Strict vs. loose evaluation modes.
- 8 response transformations (lowercase, remove punctuation, etc.).
- Edge cases (e.g., checking for repeated phrases, word counts, URL patterns).

Rather than reimplement these (error-prone and unmaintainable), we import them directly from `instruction_following_eval.evaluation.eval_utils` and call them. This ensures we match the official IFEval benchmark exactly.

## Customization

### Add or Swap Models

Edit `config.py`. Example: replacing Qwen with Mixtral:

```python
{
    "name": "Mixtral 8x7B",
    "base_url": "https://api.together.xyz/v1",
    "api_key_env": "TOGETHER_API_KEY",
    "model_id": "mistralai/Mixtral-8x7B-Instruct-v0.1",
},
```

Then set the env var in `.env` and re-run `generate.py`.

### Adjust Rate Limits

In `config.py`, edit `RATE_LIMITS`:

```python
RATE_LIMITS = {
    "https://api.groq.com/openai/v1": 20,  # Increase to 20 req/min
}
```

This changes the delay between requests for that provider.

## Learning Notes

This project is designed for readability and learning:
- Every file is ~200–400 lines.
- Comments explain the "why," not the "what."
- No premature abstractions or helper functions.
- Config is separate from logic.

If you have questions about how something works, the code should be clear enough to read end-to-end in ~30 minutes.

## Troubleshooting

**"Prompts file not found"**
- Did you run `bash download_ifeval.sh`?

**"API key not set"**
- Check your `.env` file. Make sure the env var name matches `config.py`.

**"Rate limited / backing off"**
- This is expected on free tiers. The script retries automatically with exponential backoff.
- If it's too slow, consider upgrading to a paid tier or adjusting `RATE_LIMITS`.

**"No checker for constraint type: ..."**
- The official IFEval may have constraint types not in `eval_utils.INSTRUCTION_DICT`. This is rare; file an issue if you hit it.

## References

- [IFEval Paper](https://arxiv.org/abs/2311.07911) (Zhou et al. 2023)
- [Official Repo](https://github.com/google-research/google-research/tree/master/instruction_following_eval)
- [OpenAI Python Client](https://github.com/openai/openai-python)
- [Groq Console](https://console.groq.com)
- [OpenRouter](https://openrouter.ai)
