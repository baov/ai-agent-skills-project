#!/usr/bin/env bash
#
# Installe les skills de ce dépôt là où les agents vont les chercher.
#
#   ./install.sh                          # portée utilisateur, tous les clients détectés
#   ./install.sh --scope project --into ~/projets/mon-app
#   ./install.sh --client claude --copy
#
# Par défaut, des liens symboliques : les mises à jour du dépôt sont prises en
# compte sans réinstaller. `--copy` produit des copies indépendantes.
set -euo pipefail

SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
SCOPE="user"
CLIENT="auto"
CIBLE=""
MODE="symlink"

usage() {
  cat <<'USAGE'
Usage : ./install.sh [options]

  --scope user|project   Portée. `user` installe pour toi sur cette machine ;
                         `project` installe dans un dépôt précis (défaut : user).
  --into <chemin>        Racine du projet. Requis avec --scope project.
  --client <nom>         agents | claude | all (défaut : auto — voir ci-dessous).
  --copy                 Copier au lieu de créer des liens symboliques.
  -h, --help             Cette aide.

Répertoires visés :

  agents   ~/.agents/skills/        ou  <projet>/.agents/skills/
           Répertoire interopérable, lu par Codex, Cursor, Gemini CLI,
           Copilot et les autres clients conformes à la spécification.
  claude   ~/.claude/skills/        ou  <projet>/.claude/skills/
           Claude Code, qui a conservé son propre répertoire.

`auto` installe pour les clients dont le répertoire parent existe déjà, et
retombe sur `agents` si aucun n'est détecté.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --scope)  SCOPE="${2:?--scope attend une valeur}"; shift 2 ;;
    --into)   CIBLE="${2:?--into attend un chemin}"; shift 2 ;;
    --client) CLIENT="${2:?--client attend une valeur}"; shift 2 ;;
    --copy)   MODE="copy"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Option inconnue : $1" >&2; usage >&2; exit 1 ;;
  esac
done

[ -d "$SOURCE" ] || { echo "Dossier skills/ introuvable à côté du script." >&2; exit 1; }

case "$SCOPE" in
  user)    RACINE="$HOME" ;;
  project)
    [ -n "$CIBLE" ] || { echo "--scope project exige --into <chemin>." >&2; exit 1; }
    [ -d "$CIBLE" ] || { echo "Projet introuvable : $CIBLE" >&2; exit 1; }
    RACINE="$(cd "$CIBLE" && pwd)" ;;
  *) echo "--scope attend 'user' ou 'project'." >&2; exit 1 ;;
esac

# Détection : on ne crée pas un répertoire client que l'utilisateur n'utilise pas.
DESTINATIONS=()
case "$CLIENT" in
  agents) DESTINATIONS=("$RACINE/.agents/skills") ;;
  claude) DESTINATIONS=("$RACINE/.claude/skills") ;;
  all)    DESTINATIONS=("$RACINE/.agents/skills" "$RACINE/.claude/skills") ;;
  auto)
    [ -d "$RACINE/.agents" ] && DESTINATIONS+=("$RACINE/.agents/skills")
    [ -d "$RACINE/.claude" ] && DESTINATIONS+=("$RACINE/.claude/skills")
    [ ${#DESTINATIONS[@]} -eq 0 ] && DESTINATIONS=("$RACINE/.agents/skills")
    ;;
  *) echo "--client attend 'agents', 'claude', 'all' ou 'auto'." >&2; exit 1 ;;
esac

echo "Source      : $SOURCE"
echo "Mode        : $MODE"
printf 'Destination : %s\n' "${DESTINATIONS[@]}"
echo

for destination in "${DESTINATIONS[@]}"; do
  mkdir -p "$destination"
  for skill in "$SOURCE"/*/; do
    nom="$(basename "$skill")"
    lien="$destination/$nom"

    # Un skill préexistant qui n'est pas à nous : on ne l'écrase jamais en silence.
    if [ -e "$lien" ] && [ ! -L "$lien" ]; then
      echo "  ~ $nom déjà présent dans $destination (copie, pas un lien) — ignoré"
      continue
    fi

    rm -f "$lien"
    if [ "$MODE" = "symlink" ]; then
      ln -s "${skill%/}" "$lien"
    else
      cp -R "${skill%/}" "$lien"
    fi
    echo "  + $nom"
  done
done

echo
echo "Terminé. Vérification :"
echo "    python3 tools/validate-skills.py --root ."
