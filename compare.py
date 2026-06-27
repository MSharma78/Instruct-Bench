#!/usr/bin/env python3
"""
Compare scores across all three models.

Load the scores from SCORES_DIR/scores.json and print a comparison table.
The table has:
  - Rows: the three models
  - Columns: the four metrics (prompt_level_strict, instruction_level_strict,
             prompt_level_loose, instruction_level_loose)

Also save the table as CSV for easy import into a spreadsheet.
"""

import json
import csv
from pathlib import Path
from config import SCORES_DIR

def main():
    scores_file = Path(SCORES_DIR) / "scores.json"

    if not scores_file.exists():
        print(f"Error: {scores_file} not found. Did you run score.py?")
        return

    with open(scores_file) as f:
        scores = json.load(f)

    # Extract the metrics.
    metrics = [
        ("prompt_level_strict", "Prompt Strict %"),
        ("instruction_level_strict", "Instruction Strict %"),
        ("prompt_level_loose", "Prompt Loose %"),
        ("instruction_level_loose", "Instruction Loose %"),
    ]

    # Print table header.
    print("\n" + "=" * 80)
    print("IFEval Benchmark Results")
    print("=" * 80)
    print(f"{'Model':<30}", end="")
    for _, header in metrics:
        print(f"{header:>14}", end="")
    print()
    print("-" * 80)

    # Print each model's scores.
    for score in scores:
        model_name = score["name"]
        print(f"{model_name:<30}", end="")

        if score.get("skipped"):
            print("SKIPPED (API key not set)")
        else:
            for metric_key, _ in metrics:
                value = score.get(metric_key)
                if value is not None:
                    print(f"{value:>13.1f}%", end="")
                else:
                    print(f"{'N/A':>14}", end="")
            print()

    print("=" * 80 + "\n")

    # Save as CSV.
    csv_file = Path(SCORES_DIR) / "comparison.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)

        # Header row.
        header = ["Model"] + [header for _, header in metrics]
        writer.writerow(header)

        # Data rows.
        for score in scores:
            row = [score["name"]]
            if score.get("skipped"):
                row.append("SKIPPED")
            else:
                for metric_key, _ in metrics:
                    value = score.get(metric_key, "N/A")
                    row.append(value)
            writer.writerow(row)

    print(f"Comparison table saved to {csv_file}")


if __name__ == "__main__":
    main()
