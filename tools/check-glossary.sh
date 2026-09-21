#!/usr/bin/env bash
#
# Checks that the repository holds no leftover French.
#
# Two complementary nets:
#   1. accented characters  — catches most French prose
#   2. unaccented French words — catches the rest
#
# Only this script is exempt, since it holds the French terms it searches for.
# It checks what is mechanically checkable: that no French is left. The rest of
# docs/glossary.md — one English word per concept — binds the writer, not grep:
# its "Not" column lists ordinary English words that are perfectly valid
# elsewhere, so matching on them would cry wolf more often than it caught
# anything.
set -uo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

failures=0

# git grep searches tracked files only: build output and vendored code are not
# ours to translate. Exit status 1 just means "no match", which is the pass case.
check() {
  local label="$1" pattern="$2" opts="${3:-}"
  local hits
  # shellcheck disable=SC2086 -- $opts is a deliberate word-split of grep flags.
  hits=$(git grep -nIE $opts "$pattern" -- . ':!tools/check-glossary.sh' || true)
  if [ -n "$hits" ]; then
    echo "FAIL — $label"
    printf '%s\n' "$hits" | sed 's/^/    /'
    failures=$((failures + 1))
  else
    echo "ok   — $label"
  fi
}

# git grep compares bytes, not characters, whatever the locale. A bracket
# expression therefore matches individual bytes, and the UTF-8 sequences of
# "—" or "→" collide with bytes of "À", "Ô" and "Œ" — every em dash reads as
# an accent. An alternation of whole sequences has no such collision.
check "no accented characters" \
  '(à|â|ä|ç|é|è|ê|ë|î|ï|ô|ö|ù|û|ü|ÿ|œ|æ|À|Â|Ä|Ç|É|È|Ê|Ë|Î|Ï|Ô|Ö|Ù|Û|Ü|Œ|Æ)'

# Unaccented French the accent net misses. Terms spelled identically in both
# languages (gauntlet, doctrine, invariant, harness) are deliberately absent.
# git grep's ERE does not support \b: a pattern using it matches nothing at
# all, so the check would pass without testing anything. -w says "whole word".
check "no French glossary terms" \
  '(brique|briques|QCM|metier|relecteur|signalement|declencheur|dette|tactique|strategique|perimetre|symptome|degrade|agregat|anemique)' \
  '-iw'

check "no renamed paths" \
  'docs/metier|docs/technique|clarify-with-qcm|brique-[a-d]-'

echo
if [ "$failures" -gt 0 ]; then
  echo "$failures check(s) failed." >&2
  exit 1
fi
echo "Repository is English."
