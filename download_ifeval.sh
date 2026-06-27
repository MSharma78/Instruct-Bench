#!/bin/bash
# Download the official IFEval code and data from Google Research.
# Run this once before generating responses or scoring.
#
# Downloads the repo as a zip file, extracts it, and copies out just the
# instruction_following_eval folder. This avoids Windows-illegal filenames
# in other directories.
#
# Requires: curl, unzip (both available in Git Bash on Windows)

set -e

REPO_ZIP="google-research-master.zip"
REPO_EXTRACTED="google-research-master"

echo "Downloading google-research as zip..."

if [ ! -d "instruction_following_eval" ]; then
    # Download the repo as a zip file.
    if [ ! -f "$REPO_ZIP" ]; then
        echo "Fetching $REPO_ZIP from GitHub..."
        curl -L -o "$REPO_ZIP" \
            https://github.com/google-research/google-research/archive/refs/heads/master.zip
        echo "✓ Downloaded $REPO_ZIP"
    else
        echo "✓ $REPO_ZIP already downloaded"
    fi

    # Extract the zip file.
    if [ ! -d "$REPO_EXTRACTED" ]; then
        echo "Extracting $REPO_ZIP..."
        unzip -q "$REPO_ZIP"
        echo "✓ Extracted to $REPO_EXTRACTED/"
    fi

    # Copy the instruction_following_eval folder from the extracted archive.
    echo "Copying instruction_following_eval/ to project root..."
    cp -r "$REPO_EXTRACTED/instruction_following_eval" .
    echo "✓ Copied instruction_following_eval/"

    # Clean up temp files.
    echo "Cleaning up temporary files..."
    rm -rf "$REPO_ZIP" "$REPO_EXTRACTED"
    echo "✓ Cleaned up"
else
    echo "instruction_following_eval/ already exists, skipping download"
fi

# Verify the critical file exists.
if [ -f "instruction_following_eval/data/input_data.jsonl" ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║ ✓ Setup complete! All files in place.                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Key files ready:"
    echo "  • instruction_following_eval/data/input_data.jsonl"
    echo "    → ~540 IFEval prompts"
    echo "  • instruction_following_eval/evaluation/eval_utils.py"
    echo "    → Official instruction checkers"
    echo ""
else
    echo ""
    echo "✗ ERROR: Expected file not found."
    echo "  Looked for: instruction_following_eval/data/input_data.jsonl"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check that the download completed (look for google-research-master.zip)"
    echo "  2. Try again: bash download_ifeval.sh"
    exit 1
fi
