#!/usr/bin/env bash
#
# Crée le dépôt GitHub privé et pousse le contenu de ce dossier.
#
#   ./setup-repo.sh [nom-du-depot]
#
# Utilise TON authentification gh — aucun token n'est écrit ni stocké ici.
# Prérequis : gh (https://cli.github.com) et git.
#
set -euo pipefail

REPO_NAME="${1:-claude-skills}"

# --- vérifications --------------------------------------------------------
command -v git >/dev/null || { echo "git introuvable."; exit 1; }
command -v gh  >/dev/null || {
  echo "gh introuvable. Installe GitHub CLI : https://cli.github.com"
  exit 1
}

if ! gh auth status >/dev/null 2>&1; then
  echo "Tu n'es pas authentifié auprès de GitHub. Lance d'abord :"
  echo "    gh auth login"
  exit 1
fi

OWNER=$(gh api user --jq .login)

if gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
  echo "Le dépôt $OWNER/$REPO_NAME existe déjà."
  echo "Choisis un autre nom : ./setup-repo.sh <nom>"
  exit 1
fi

# --- confirmation ---------------------------------------------------------
echo
echo "  Dépôt      : $OWNER/$REPO_NAME"
echo "  Visibilité : privé"
echo "  Fichiers   : $(find . -type f -not -path './.git/*' | wc -l | tr -d ' ')"
echo
read -r -p "Créer et pousser ? [o/N] " answer
[[ "$answer" =~ ^[oOyY]$ ]] || { echo "Annulé."; exit 0; }

# --- init + commit --------------------------------------------------------
if [ ! -d .git ]; then
  git init -q
  git branch -M main
fi

git add .
git diff --cached --quiet || git commit -q -m "Skills Claude pour le développement logiciel"

# --- création + push ------------------------------------------------------
gh repo create "$REPO_NAME" \
  --private \
  --source=. \
  --remote=origin \
  --description "Skills Claude — workflow de développement, enforcement, revue" \
  --push

echo
echo "Terminé : $(gh repo view "$OWNER/$REPO_NAME" --json url --jq .url)"
