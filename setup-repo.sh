#!/usr/bin/env bash
#
# Creates the private GitHub repository and pushes this folder's contents.
#
#   ./setup-repo.sh [repo-name]
#
# Uses YOUR gh authentication — no token is written or stored here.
# Requires: gh (https://cli.github.com) and git.
#
set -euo pipefail

# Defaults to the current folder's name.
REPO_NAME="${1:-$(basename "$PWD")}"

# --- checks ---------------------------------------------------------------
command -v git >/dev/null || { echo "git not found."; exit 1; }
command -v gh  >/dev/null || {
  echo "gh not found. Install GitHub CLI: https://cli.github.com"
  exit 1
}

if ! gh auth status >/dev/null 2>&1; then
  echo "You are not authenticated with GitHub. Run this first:"
  echo "    gh auth login"
  exit 1
fi

OWNER=$(gh api user --jq .login)

if gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
  echo "Repository $OWNER/$REPO_NAME already exists."
  echo "Pick another name: ./setup-repo.sh <name>"
  exit 1
fi

# --- confirmation ---------------------------------------------------------
echo
echo "  Repository : $OWNER/$REPO_NAME"
echo "  Visibility : private"
echo "  Files      : $(find . -type f -not -path './.git/*' | wc -l | tr -d ' ')"
echo
read -r -p "Create and push? [y/N] " answer
[[ "$answer" =~ ^[yY]$ ]] || { echo "Canceled."; exit 0; }

# --- init + commit --------------------------------------------------------
if [ ! -d .git ]; then
  git init -q
  git branch -M main
fi

git add .
git diff --cached --quiet || git commit -q -m "Software development skills for AI agents"

# --- create + push --------------------------------------------------------
gh repo create "$REPO_NAME" \
  --private \
  --source=. \
  --remote=origin \
  --description "Proof Over Vibes — agent skills: documentation, enforcement, review" \
  --push

echo
echo "Done: $(gh repo view "$OWNER/$REPO_NAME" --json url --jq .url)"
