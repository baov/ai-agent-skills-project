# Changelog

Notable changes to this repository. Format based on [Keep a Changelog](https://keepachangelog.com/1.1.0/), versioning follows [semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No skill changed: all ten `SKILL.md` files are still identical to 0.1.0. What
follows corrects the repository's own documentation and one overstated claim —
it concerns contributors, not anyone installing the skills, which is why it
carries no version of its own.

### Changed

- `docs/glossary.md` is now indexed on the English term rather than on the French
  one it replaced. The French column was migration scaffolding — it forced ten
  parallel translators onto one word per term — and it pointed at the wrong risk
  once the translation was done: the plausible slip is no longer a leftover
  French word, it is writing "module B" for "block B". Each term now lists the
  synonyms it displaces, and the "Renamed paths" table moved out, migration
  information belonging to the commit that performed the renames.
- `tools/check-glossary.sh` no longer exempts `docs/glossary.md`, which is now
  entirely English and checked like every other file.

### Fixed

- 0.1.0 described the glossary as "mechanically enforced" and the check as
  catching "off-glossary vocabulary". Both overstated it. The script catches
  leftover French — the mechanically checkable half. It does not catch rejected
  synonyms, and deliberately so: "module", "rule" and "framework" are ordinary
  English words elsewhere, so matching on them would raise false alarms far more
  often than real ones. One word per concept binds the writer and is caught in
  review. `AGENTS.md` and `README.md` now say so.

## [0.1.0] — 2026-09-21

First public version. Ten skills conformant to the [Agent Skills specification](https://agentskills.io/specification), the tooling that keeps them consistent, and the documentation that chains them.

### Skills

Entry points, triggered by a user request:

- `codebase-cartographer` — maps a project into business and technical documentation
- `codebase-harness` — the enforcement layer: executable invariants, test-case bridge, mutation testing, doc-gardening
- `plan-driven-dev` — implementation workflow: validated plan, behavior-driven TDD, invariants inside the loop
- `premerge-review` — pre-merge review: mechanical gauntlet, four angles, GO/NO-GO verdict
- `systematic-debugging` — diagnosis down to a proven root cause, no fix
- `ai-code-remediation` — cold audit of an AI-generated codebase, eight symptoms, Mikado plan
- `code-assimilation-quiz` — assimilation quiz on the diff, never automatic

Supporting skills, loaded by another skill:

- `behavior-driven-testing` — test doctrine: behaviors rather than classes
- `ddd-advisor` — Domain-Driven Design audit and guidance
- `clarify-with-choices` — multiple-choice validation doctrine, and its degraded mode per host agent

### Tooling

- `tools/validate-skills.py` — checks the specification rules and the 500-line cap on a `SKILL.md`; `--explain` describes each rule without checking anything
- `tools/check-glossary.sh` — catches leftover French and off-glossary vocabulary
- Both run in pre-commit and in CI, with no dependency to install
- `install.sh` — symlink or copy install, user or project scope, every conformant client
- `setup-repo.sh` — publishes your own copy to a private GitHub repository

### Documentation

- `README.md` — the ten skills, their installation, the conventions they share
- `workflows.md` — which skill to use when, how artifacts circulate, the common chaining mistakes
- `docs/glossary.md` — the binding vocabulary, mechanically enforced
- `AGENTS.md` — the contribution conventions

[0.1.0]: https://github.com/baov/proof-over-vibes/releases/tag/v0.1.0
