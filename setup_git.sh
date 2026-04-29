#!/usr/bin/env bash
# Initialize this project as a fresh git repository with a logical
# commit history (rather than one giant "initial commit" of all files).
#
# Run this ONCE, after extracting the project and configuring your
# git user.name and user.email. After it finishes, follow the
# instructions in PUSH_TO_GITHUB.md to push to GitHub.
#
# Usage:
#     bash setup_git.sh

set -euo pipefail

# --- Sanity checks --------------------------------------------------------

if [ -d .git ]; then
    echo "Error: a .git/ directory already exists in $(pwd)."
    echo "Delete it first if you want to re-run this script:  rm -rf .git"
    exit 1
fi

if ! command -v git >/dev/null 2>&1; then
    echo "Error: git is not installed."
    exit 1
fi

if ! git config user.name >/dev/null 2>&1 || ! git config user.email >/dev/null 2>&1; then
    echo "Error: git user.name and user.email are not configured."
    echo
    echo "Run these once, with your real name and email:"
    echo "  git config --global user.name  \"Your Name\""
    echo "  git config --global user.email \"your.email@example.com\""
    echo
    echo "Then re-run this script."
    exit 1
fi

NAME="$(git config user.name)"
EMAIL="$(git config user.email)"
echo "Initializing repository as: $NAME <$EMAIL>"
echo

# --- Initialize -----------------------------------------------------------

git init -q -b main

# --- Commit 1: project skeleton ------------------------------------------
git add .gitignore LICENSE requirements.txt
git commit -q -m "Initial commit: license, gitignore, dependencies"

# --- Commit 2: data structure --------------------------------------------
git add data/README.md data/raw/.gitkeep data/processed/.gitkeep
git commit -q -m "Add data folder structure and dataset documentation"

# --- Commit 3: data loading ----------------------------------------------
git add src/__init__.py src/data.py scripts/load_data.py
git commit -q -m "Load NASA .mat files, aggregate to one row per cycle, compute SOH"

# --- Commit 4: feature engineering ---------------------------------------
git add src/features.py
git commit -q -m "Feature engineering: raw, rolling, and physics-derived groups"

# --- Commit 5: models and evaluation -------------------------------------
git add src/models.py src/evaluate.py
git commit -q -m "Random Forest and XGBoost training, metrics, and diagnostic plots"

# --- Commit 6: training script -------------------------------------------
git add scripts/train.py models/.gitkeep results/.gitkeep
git commit -q -m "Training script with --model and --features flags"

# --- Commit 7: ablation study (the experimental core) --------------------
git add scripts/ablation.py
git commit -q -m "Ablation study comparing the three feature groups"

# --- Commit 8: EDA notebook ----------------------------------------------
git add notebooks/01_explore_data.ipynb
git commit -q -m "EDA notebook with capacity-fade plot and observation prompts"

# --- Commit 9: report template -------------------------------------------
git add docs/report_template.md
git commit -q -m "Four-page report template with section prompts"

# --- Commit 10: README ---------------------------------------------------
git add README.md
git commit -q -m "Project README with motivation, methodology, and how to reproduce"

# Catch anything we missed (PUSH_TO_GITHUB.md, this script itself, etc.)
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -q -m "Add push-to-github guide and setup script"
fi

echo "Done. Commit history:"
echo
git log --oneline
echo
echo "Next: open PUSH_TO_GITHUB.md for the steps to push this to GitHub."
