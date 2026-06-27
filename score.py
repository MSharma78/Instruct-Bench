#!/usr/bin/env python3
"""
Score model responses using the official IFEval evaluation code.

For each model's saved responses (JSONL file):
  1. Load the prompt-response pairs from the JSONL file.
  2. Load the original prompts and instruction lists.
  3. Use the official evaluation_lib to compute strict and loose scores.
  4. Extract four metrics per model:
     - prompt_level_strict: Fraction of prompts all instructions pass (strict).
     - instruction_level_strict: Fraction of instructions that pass (strict).
     - prompt_level_loose: Fraction of prompts all instructions pass (loose).
     - instruction_level_loose: Fraction of instructions that pass (loose).
  5. Save the scores for each model to a JSON file.

The official IFEval evaluation_lib handles all the complexity:
  - Strict mode: response as-is
  - Loose mode: 8 text transformations (remove first/last line, remove asterisks, etc.)
"""

import json
import logging
from pathlib import Path
import sys

from dotenv import load_dotenv
from config import MODELS, RESPONSES_DIR, SCORES_DIR

# Load API keys from .env file (not used in score.py, but good practice).
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def score_model(model_config: dict) -> dict:
    """
    Evaluate a single model's responses and return the four scores.

    Args:
        model_config: One entry from config.MODELS

    Returns:
        A dict with keys:
          - name: model name
          - skipped: True if API key was missing (the model was not run)
          - prompt_level_strict, instruction_level_strict,
            prompt_level_loose, instruction_level_loose (0-100, percentages)
    """

    # Construct the path to this model's response file.
    response_file = Path(RESPONSES_DIR) / f"{model_config['name'].replace(' ', '_').lower()}_responses.jsonl"

    # If the file doesn't exist, the model was skipped during generation.
    if not response_file.exists():
        logger.info(f"{model_config['name']}: No response file found (skipped during generation)")
        return {
            "name": model_config["name"],
            "skipped": True,
        }

    logger.info(f"Scoring {model_config['name']}...")

    # Import the official IFEval evaluation code.
    ifeval_root = Path("instruction_following_eval")
    if not ifeval_root.exists():
        raise FileNotFoundError(
            "Official IFEval code not found at instruction_following_eval/. "
            "Did you run download_ifeval.sh?"
        )

    sys.path.insert(0, str(ifeval_root.parent))
    from instruction_following_eval import evaluation_lib

    # Load the prompts and instruction lists.
    prompts_file = ifeval_root / "data" / "input_data.jsonl"
    if not prompts_file.exists():
        raise FileNotFoundError(
            f"Prompts file not found at {prompts_file}. "
            "Did you run download_ifeval.sh?"
        )

    inputs = evaluation_lib.read_prompt_list(str(prompts_file))
    logger.info(f"Loaded {len(inputs)} prompts")

    # Load the model's responses.
    prompt_to_response = evaluation_lib.read_prompt_to_response_dict(str(response_file))
    logger.info(f"Loaded {len(prompt_to_response)} responses")

    # Evaluate in strict mode.
    logger.info("Evaluating strict mode...")
    outputs_strict = []
    for inp in inputs:
        # Skip if we don't have a response for this prompt or if response is None.
        if inp.prompt not in prompt_to_response or prompt_to_response[inp.prompt] is None:
            continue
        output = evaluation_lib.test_instruction_following_strict(inp, prompt_to_response)
        outputs_strict.append(output)

    # Evaluate in loose mode.
    logger.info("Evaluating loose mode...")
    outputs_loose = []
    for inp in inputs:
        # Skip if we don't have a response for this prompt or if response is None.
        if inp.prompt not in prompt_to_response or prompt_to_response[inp.prompt] is None:
            continue
        output = evaluation_lib.test_instruction_following_loose(inp, prompt_to_response)
        outputs_loose.append(output)

    # Compute metrics.
    # Strict metrics.
    num_prompts_strict = len(outputs_strict)
    prompts_all_pass_strict = sum(1 for o in outputs_strict if o.follow_all_instructions)
    instructions_pass_strict = sum(sum(o.follow_instruction_list) for o in outputs_strict)
    instructions_total_strict = sum(len(o.follow_instruction_list) for o in outputs_strict)

    # Loose metrics.
    num_prompts_loose = len(outputs_loose)
    prompts_all_pass_loose = sum(1 for o in outputs_loose if o.follow_all_instructions)
    instructions_pass_loose = sum(sum(o.follow_instruction_list) for o in outputs_loose)
    instructions_total_loose = sum(len(o.follow_instruction_list) for o in outputs_loose)

    # Convert to percentages.
    prompt_level_strict = (prompts_all_pass_strict / num_prompts_strict * 100
                          if num_prompts_strict > 0 else 0.0)
    instruction_level_strict = (instructions_pass_strict / instructions_total_strict * 100
                               if instructions_total_strict > 0 else 0.0)
    prompt_level_loose = (prompts_all_pass_loose / num_prompts_loose * 100
                         if num_prompts_loose > 0 else 0.0)
    instruction_level_loose = (instructions_pass_loose / instructions_total_loose * 100
                              if instructions_total_loose > 0 else 0.0)

    logger.info(
        f"{model_config['name']}: "
        f"prompt_strict={prompt_level_strict:.1f}%, "
        f"instruction_strict={instruction_level_strict:.1f}%, "
        f"prompt_loose={prompt_level_loose:.1f}%, "
        f"instruction_loose={instruction_level_loose:.1f}%"
    )

    return {
        "name": model_config["name"],
        "skipped": False,
        "prompt_level_strict": round(prompt_level_strict, 2),
        "instruction_level_strict": round(instruction_level_strict, 2),
        "prompt_level_loose": round(prompt_level_loose, 2),
        "instruction_level_loose": round(instruction_level_loose, 2),
    }


def main():
    # Score all models.
    Path(SCORES_DIR).mkdir(parents=True, exist_ok=True)

    scores = []
    for model_config in MODELS:
        score = score_model(model_config)
        scores.append(score)

    # Save scores to JSON.
    scores_file = Path(SCORES_DIR) / "scores.json"
    with open(scores_file, "w") as f:
        json.dump(scores, f, indent=2)

    logger.info(f"Scores saved to {scores_file}")


if __name__ == "__main__":
    main()
