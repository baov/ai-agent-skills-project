# Harness script starters

This folder holds reference implementations of the scripts the skill generates. **They are examples, not a library.** The skill always generates the script that fits the detected stack; these files are here to show the contract in action and to save it from being reinvented.

**Where they diverge, the contract wins over the starter.** A starter drifting from the conventions of `templates.md` § 6 is to be fixed, not imitated.

## Contents

| File | Block | Reach |
|---------|--------|--------|
| `check_test_coverage.py` | B | Generic — reads nothing but markdown and paths, works whatever the project's stack |

## What this folder deliberately does not hold

**Per-stack linters (block A).** A layer isolation check is written in ArchUnit on the JVM, in dependency-cruiser on JS/TS, in AST on Python — three implementations with no code in common. Freezing them here would produce a folder that ages faster than the stacks do. The skill generates them from the conventions of `templates.md` § 6.

**Mutation configs (block D).** See SKILL.md § 5.3.a: the five-point specification is the source of truth, the tooling is detected at run time.

If you freeze a starter here that has proven itself internally, add it to the table above and note the stack it targets. An undocumented starter is a starter nobody will reuse.

## The contract, in short

Every script in `tools/harness/`, whatever the block:

- accepts `--explain` (describes without checking) and `--root <path>`
- writes one line per violation: `path:line: [INV-NNN] message — remediation`
- exits `0` (OK), `1` (`error` violation), `2` (`warn` violations only)
- fixes nothing, changes neither its config nor its threshold
- requires no dependency to be installed for the documentation checks
