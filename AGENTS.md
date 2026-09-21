# AGENTS.md

Contribution conventions for this repository. They apply to every agent that writes here.

This repository **produces** skills; it does not consume them for itself. To know which one to use in a project, see [workflows.md](workflows.md).

## Format

Every skill is a folder under `skills/` conforming to the [Agent Skills specification](https://agentskills.io/specification): a `SKILL.md` with `name` and `description` in its frontmatter, the detail in `references/`.

Before any commit:

```bash
python3 tools/validate-skills.py --root .
tools/check-glossary.sh
```

The pre-commit hook already runs both (`pre-commit install`). What the validator checks, and why each rule exists: `python3 tools/validate-skills.py --explain`.

## Writing rules

- **English.** Bodies, descriptions, error messages, script comments and identifiers.
- **The vocabulary in [`docs/glossary.md`](docs/glossary.md) is binding.** It fixes one word per concept so that ten skills read as one system; using a listed synonym is a defect, not a variation. `tools/check-glossary.sh` catches the mechanical half — leftover French — and leaves the synonyms to the reviewer, since they are ordinary English words elsewhere.
- **No hardcoded tool names.** No `mcp__*`, no named multiple-choice tool, no agent-specific path. A skill that names its tool breaks on every other agent. For multiple-choice questions, defer to `clarify-with-choices`.
- **`AGENTS.md`, never `CLAUDE.md`.** When a skill writes to the target project's instruction file, the target is `AGENTS.md`. Claude Code compatibility comes from a one-line `CLAUDE.md` that imports `AGENTS.md`.
- **"the agent", never a product name.** A skill's narrator is whichever agent runs it.
- **A `SKILL.md` body stays under 500 lines.** It is loaded in full the moment the skill activates. Past that, move detail into `references/` — one file per branch of the workflow, so the agent reads only what concerns it.
- **A `description` is a trigger, not a summary.** It is the only text loaded at all times: it says what the skill does *and* when to use it, in the words the user will actually type. Capped at 1024 characters.

## Two languages, two scopes

The repository is English. What a skill *writes elsewhere* is not.

- **Repository language: English.** Everything versioned here.
- **Output language: the target project's.** Documentation, plans, review reports, audits, and the questions a skill asks — all follow the language of the project being worked on. A skill documenting a French codebase produces French documentation, and a Domain-Driven Design skill keeps that project's ubiquitous language intact.

Commit messages are outside both scopes: they follow the language of whoever writes them, and nothing here constrains that.

Writing the repository in English must never push English onto the projects these skills serve.

## Doctrine shared by the skills

These rules live inside the skills themselves; restating them here keeps a contribution from contradicting them.

- **Announcement** — a skill announces itself before applying, never silently.
- **Validation by multiple-choice question** — structural decisions go through the user.
- **File-backed persistence** — plans, reports and invariants live in the repository, not in the context window.
- **Explicit degraded mode** — a skill works without its reference material, but says so.
- **No silent auto-fix** — the harness reports; the correction goes through a visible commit.
