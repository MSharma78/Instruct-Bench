# Configuration for the three models.
# Each model needs a display name, OpenAI-compatible base_url, the environment
# variable holding the API key, and the model ID string used in API calls.

MODELS = [
    {
        "name": "Llama 3.3 70B",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_id": "meta-llama/llama-3.3-70b-instruct",
    },
    {
        "name": "Qwen 3.5 27B",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_id": "qwen/qwen3.5-27b",
    },
    {
        "name": "Gemma 4 26B",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_id": "google/gemma-4-26b-a4b-it",
    },
]

# Rate limit: max requests per minute per provider. Adjust based on your tier.
RATE_LIMITS = {
    "https://openrouter.ai/api/v1": 10000,   # Paid tier: let OpenRouter rate-limit via 429 backoff
}

# Output directories
RESPONSES_DIR = "responses"  # Where to save model outputs as JSONL
SCORES_DIR = "scores"        # Where to save evaluation scores
