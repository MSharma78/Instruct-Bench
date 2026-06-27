#!/usr/bin/env python3
"""
Generate model responses for all IFEval prompts.

For each model in config.MODELS:
  1. Check if the API key env var is set; skip the model if missing.
  2. Load all IFEval prompts from instruction_following_eval/data/input_data.jsonl.
  3. Loop through prompts, calling the model via OpenAI-compatible endpoint.
  4. On rate-limit (HTTP 429), retry with exponential backoff.
  5. Save responses as JSONL in the format IFEval expects:
     {"prompt": "...", "response": "..."}
  6. Cache: if the output file already exists, skip already-generated prompts.
"""

import os
import json
import time
import logging
from pathlib import Path
import random

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from config import MODELS, RATE_LIMITS, RESPONSES_DIR

# Load API keys from .env file.
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_ifeval_prompts(prompts_file: str) -> list:
    """Load IFEval prompts from the official JSON file."""
    if not Path(prompts_file).exists():
        raise FileNotFoundError(
            f"Prompts file not found: {prompts_file}\n"
            "Did you run download_ifeval.sh? It should be at: instruction_following_eval/data/input_data.jsonl"
        )

    prompts = []
    with open(prompts_file) as f:
        for line in f:
            obj = json.loads(line)
            prompts.append(obj)

    logger.info(f"Loaded {len(prompts)} prompts from {prompts_file}")
    return prompts


def load_existing_responses(output_file: str) -> set:
    """
    Return the set of prompt texts already generated and saved.
    If the output file doesn't exist, return an empty set.
    """
    if not Path(output_file).exists():
        return set()

    existing = set()
    with open(output_file) as f:
        for line in f:
            obj = json.loads(line)
            existing.add(obj["prompt"])

    return existing


def generate_for_model(model_config: dict, prompts: list) -> None:
    """
    Generate responses for a single model and save to JSONL file.

    Args:
        model_config: One entry from config.MODELS
        prompts: List of prompt objects from load_ifeval_prompts()
    """

    # Check for API key.
    api_key = os.getenv(model_config["api_key_env"])
    if not api_key:
        logger.warning(
            f"Skipping {model_config['name']}: {model_config['api_key_env']} not set"
        )
        return

    logger.info(f"Starting generation for {model_config['name']}")

    # Initialize OpenAI client with the model's base URL.
    client = OpenAI(
        api_key=api_key,
        base_url=model_config["base_url"],
    )

    # Output file for this model.
    output_file = Path(RESPONSES_DIR) / f"{model_config['name'].replace(' ', '_').lower()}_responses.jsonl"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing responses to avoid re-generating.
    existing_prompts = load_existing_responses(str(output_file))
    prompts_to_generate = [p for p in prompts if p["prompt"] not in existing_prompts]

    logger.info(
        f"{model_config['name']}: {len(existing_prompts)} already generated, "
        f"{len(prompts_to_generate)} to do"
    )

    # Rate limit: delay between requests (in seconds).
    base_url = model_config["base_url"]
    rpm_limit = RATE_LIMITS.get(base_url, 10)
    delay_per_request = 60.0 / rpm_limit
    last_request_time = time.time()

    # Generate responses with exponential backoff for rate limits.
    backoff_base = 2
    backoff_max = 120

    with open(output_file, "a") as f:
        for i, prompt_obj in enumerate(prompts_to_generate, 1):
            # Sleep to respect rate limit (measure since last request completed).
            now = time.time()
            elapsed = now - last_request_time
            if elapsed < delay_per_request:
                time.sleep(delay_per_request - elapsed)

            backoff = 1
            while True:
                try:
                    # Call the model.
                    response = client.chat.completions.create(
                        model=model_config["model_id"],
                        messages=[{"role": "user", "content": prompt_obj["prompt"]}],
                        temperature=0.0,
                        max_tokens=1024,
                    )

                    # Extract the response text.
                    response_text = response.choices[0].message.content

                    # Save in IFEval format: prompt and response.
                    output_obj = {
                        "prompt": prompt_obj["prompt"],
                        "response": response_text,
                    }
                    f.write(json.dumps(output_obj) + "\n")
                    f.flush()

                    # Update request completion time for accurate rate limiting.
                    last_request_time = time.time()

                    if i % 10 == 0:
                        logger.info(f"{model_config['name']}: {i}/{len(prompts_to_generate)}")

                    break  # Success; move to next prompt.

                except RateLimitError as e:
                    # Rate limited. Back off and retry.
                    backoff = min(backoff * backoff_base, backoff_max)
                    jitter = random.uniform(0, 0.1 * backoff)
                    sleep_time = backoff + jitter
                    logger.warning(
                        f"{model_config['name']}: Rate limited. "
                        f"Backing off {sleep_time:.1f}s..."
                    )
                    time.sleep(sleep_time)
                except Exception as e:
                    logger.error(f"{model_config['name']}: Error on prompt: {e}")
                    break

    logger.info(f"Completed generation for {model_config['name']}")


def main():
    # Path to the official IFEval prompts file.
    prompts_file = "instruction_following_eval/data/input_data.jsonl"

    # Load all prompts once.
    prompts = load_ifeval_prompts(prompts_file)

    # Generate for each model.
    for model_config in MODELS:
        generate_for_model(model_config, prompts)


if __name__ == "__main__":
    main()
