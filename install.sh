#!/usr/bin/env bash
#
# Installs this repository's skills where agents look for them.
#
#   ./install.sh                          # user scope, every detected client
#   ./install.sh --scope project --into ~/projects/my-app
#   ./install.sh --client claude --copy
#
# Symlinks by default: repository updates are picked up without reinstalling.
# `--copy` produces independent copies.
set -euo pipefail

SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
SCOPE="user"
CLIENT="auto"
TARGET=""
MODE="symlink"

usage() {
  cat <<'USAGE'
Usage: ./install.sh [options]

  --scope user|project   Scope. `user` installs for you on this machine;
                         `project` installs into one repository (default: user).
  --into <path>          Project root. Required with --scope project.
  --client <name>        agents | claude | all (default: auto — see below).
  --copy                 Copy instead of creating symlinks.
  -h, --help             This help.

Target directories:

  agents   ~/.agents/skills/        or  <project>/.agents/skills/
           The interoperable directory, read by Codex, Cursor, Gemini CLI,
           Copilot and other clients conforming to the specification.
  claude   ~/.claude/skills/        or  <project>/.claude/skills/
           Claude Code, which kept its own directory.

`auto` installs for the clients whose parent directory already exists, and
falls back to `agents` if none is detected.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --scope)  SCOPE="${2:?--scope expects a value}"; shift 2 ;;
    --into)   TARGET="${2:?--into expects a path}"; shift 2 ;;
    --client) CLIENT="${2:?--client expects a value}"; shift 2 ;;
    --copy)   MODE="copy"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[ -d "$SOURCE" ] || { echo "No skills/ folder next to the script." >&2; exit 1; }

case "$SCOPE" in
  user)    ROOT="$HOME" ;;
  project)
    [ -n "$TARGET" ] || { echo "--scope project requires --into <path>." >&2; exit 1; }
    [ -d "$TARGET" ] || { echo "Project not found: $TARGET" >&2; exit 1; }
    ROOT="$(cd "$TARGET" && pwd)" ;;
  *) echo "--scope expects 'user' or 'project'." >&2; exit 1 ;;
esac

# Detection: we never create a client directory the user does not use.
DESTINATIONS=()
case "$CLIENT" in
  agents) DESTINATIONS=("$ROOT/.agents/skills") ;;
  claude) DESTINATIONS=("$ROOT/.claude/skills") ;;
  all)    DESTINATIONS=("$ROOT/.agents/skills" "$ROOT/.claude/skills") ;;
  auto)
    [ -d "$ROOT/.agents" ] && DESTINATIONS+=("$ROOT/.agents/skills")
    [ -d "$ROOT/.claude" ] && DESTINATIONS+=("$ROOT/.claude/skills")
    [ ${#DESTINATIONS[@]} -eq 0 ] && DESTINATIONS=("$ROOT/.agents/skills")
    ;;
  *) echo "--client expects 'agents', 'claude', 'all' or 'auto'." >&2; exit 1 ;;
esac

echo "Source      : $SOURCE"
echo "Mode        : $MODE"
printf 'Destination : %s\n' "${DESTINATIONS[@]}"
echo

for destination in "${DESTINATIONS[@]}"; do
  mkdir -p "$destination"

  # A renamed or removed skill leaves a dangling symlink behind. We only clear
  # links that point into this repository — someone else's skills are theirs.
  for link in "$destination"/*; do
    [ -L "$link" ] || continue
    [ -e "$link" ] && continue
    case "$(readlink "$link")" in
      "$SOURCE"/*) rm -f "$link"; echo "  - $(basename "$link") (dangling link removed)" ;;
    esac
  done

  for skill in "$SOURCE"/*/; do
    name="$(basename "$skill")"
    link="$destination/$name"

    # A pre-existing skill that is not ours: never overwritten silently.
    if [ -e "$link" ] && [ ! -L "$link" ]; then
      echo "  ~ $name already in $destination (a copy, not a link) — skipped"
      continue
    fi

    rm -f "$link"
    if [ "$MODE" = "symlink" ]; then
      ln -s "${skill%/}" "$link"
    else
      cp -R "${skill%/}" "$link"
    fi
    echo "  + $name"
  done
done

echo
echo "Done. To verify:"
echo "    python3 tools/validate-skills.py --root ."
