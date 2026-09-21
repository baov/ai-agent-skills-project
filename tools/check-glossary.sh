#!/usr/bin/env bash
#
# Checks that the repository holds no leftover French.
#
# Two complementary nets:
#   1. accented characters  — catches most French prose
#   2. unaccented French words from docs/glossary.md — catches the rest
#
# Two files are exempt: docs/glossary.md, which must name both languages, and
# this script, which holds the French terms it searches for.
set -uo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

failures=0

# git grep searches tracked files only: build output and vendored code are not
# ours to translate. Exit status 1 just means "no match", which is the pass case.
check() {
  local label="$1" pattern="$2"
  local hits
  hits=$(git grep -nIE "$pattern" -- . ':!docs/glossary.md' ':!tools/check-glossary.sh' || true)
  if [ -n "$hits" ]; then
    echo "FAIL — $label"
    printf '%s\n' "$hits" | sed 's/^/    /'
    failures=$((failures + 1))
  else
    echo "ok   — $label"
  fi
}

check "no accented characters" \
  '[àâäçéèêëîïôöùûüœÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŒ]'

# Unaccented French the accent net misses. Terms spelled identically in both
# languages (gauntlet, doctrine, invariant, harness) are deliberately absent.
check "no French glossary terms" \
  '\b([Bb]rique|briques|QCM|metier|relecteur|signalement|declencheur|dette|tactique|strategique|perimetre|symptome|degrade|agregat|anemique)\b'

check "no renamed paths" \
  'docs/metier|docs/technique|clarify-with-qcm|brique-[a-d]-'

echo
if [ "$failures" -gt 0 ]; then
  echo "$failures check(s) failed." >&2
  exit 1
fi
echo "Repository is English."
