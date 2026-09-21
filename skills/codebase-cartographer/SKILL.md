---
name: codebase-cartographer
description: Maps an existing or brand-new codebase to produce structured business + technical documentation. Creates a `docs/` folder split into `docs/business/` (glossary, core features, test cases — one .md per case, grouped by feature) and `docs/technical/` (architecture, stack, test strategy, ADRs backed by git history analysis), validates every section with the user through multiple-choice questions, refactors to remove redundancy, and links it all from `AGENTS.md`. Use AS SOON AS the user asks to "document the project", "map the codebase", "generate the docs", "write a business glossary", "document the architecture", "write ADRs", "produce a test strategy", or mentions wanting to capture a project's knowledge in a structured way — even when the word "skill" never comes up. Use it as well when the user calls this skill by name.
---

# Codebase Cartographer

Generates complete, structured project documentation, validated step by step with the user.

## Workflow at a glance

```
[First run]
1. Initial project analysis
2. For each doc to generate (7 files):
   a. Validation round of multiple-choice questions (what the agent understood + what it is unsure about)
   b. Writing the .md file
3. Global anti-redundancy refactor
4. Approval request before touching AGENTS.md
5. AGENTS.md update (creation or patch)

[Re-run: switches to update mode automatically]
1. Inventory of the existing docs
2. Delta analysis between code and docs (new/obsolete/changed/unchanged)
3. Consolidated multiple-choice round per doc type to validate the changes
4. Applying the changes (archiving deletions, preserving manual edits)
5. Global refactor across the whole set
6. AGENTS.md update if needed
```

**Core principle**: the agent NEVER writes a doc file without first showing the user what it understood and getting the uncertain points settled. The multiple-choice round is mandatory before every write.

**Idempotence**: re-running the skill does not damage the docs. Update mode is designed to be triggered regularly as the code evolves.

---

## Step 1 — Initial analysis

Before asking the user anything, the agent inspects the project to form a picture. Tasks to run in parallel whenever possible:

- List the root and the first-level folders
- Read `README.md` if it exists
- Spot the manifest files (`package.json`, `pyproject.toml`, `pom.xml`, `Cargo.toml`, `go.mod`, `Gemfile`, etc.) to infer the stack
- Spot the CI/CD, Docker and infra config files (`docker-compose.yml`, `Dockerfile`, `.github/workflows/`, `terraform/`, etc.)
- Spot the test folder and identify the test framework
- Spot the main source folders and how they are organized
- Check whether `docs/` or `AGENTS.md` already exists (so nothing gets blindly overwritten)
- If the project is under git, inspect `git log --oneline -200` and the tags to spot past structural decisions (useful for the ADR phase)

If a `docs/` produced by this skill already exists (the expected files are there: `docs/business/glossary.md`, `docs/technical/architecture.md`, etc.), the agent switches to **update mode** — see the dedicated section below. The skill is idempotent: re-run, it updates intelligently instead of regenerating everything.

If a `docs/` exists but does not look like output from this skill (different structure, unknown files), the agent flags the ambiguity and asks the user: complete it / start over with a backup / cancel.

If an `AGENTS.md` already exists, note it for the final step — and above all, do not touch it yet.

**Keep in mind** (or in a scratch file if the session runs long): what is clear, what is ambiguous, what is missing. This map feeds the multiple-choice questions.

---

## Step 2 — Doc-by-doc generation with multiple-choice validation

For each of the 7 files, the agent follows the same cycle: **analyze → ask → write**.

The recommended order is business first (it sets the vocabulary), then technical:

| # | File(s) | Location |
|---|---------|----------|
| 1 | `glossary.md` | `docs/business/` |
| 2 | `core-features.md` | `docs/business/` |
| 3 | one `.md` per test case, grouped by feature | `docs/business/test-cases/[feature]/` |
| 4 | `architecture.md` | `docs/technical/` |
| 5 | `tech-stack.md` | `docs/technical/` |
| 6 | `test-strategy.md` | `docs/technical/` |
| 7 | `adr.md` (index) + one `.md` per ADR | `docs/technical/` + `docs/technical/adr/` |

### Shape of the multiple-choice round

For each section, present to the user, in this order:

1. **What I understood**: a short bullet-point summary of what the agent inferred
2. **What I am unsure about**: 1 to 3 multiple-choice questions

The full doctrine — how to word the questions, how many options, degraded mode when the host agent exposes no multiple-choice question tool — lives in the `clarify-with-choices` skill. Load it before the first round.

If the agent has no uncertainty at all about a section (rare), it still asks for a simple confirmation: "Here is what I am about to write in X — shall I go ahead?"

### Per-file detail

Each file follows a specific template. See `references/templates.md` for the detailed structures and the typical questions per section.

### Writing the file

Once the questions are answered, the agent writes the `.md` file straight into `docs/business/` or `docs/technical/`. The content must:
- Follow the matching template (see `references/templates.md`)
- Stay factual and concise (no filler)
- Use the glossary vocabulary (consistency)
- Include relative links to the other docs where relevant

After writing, the agent **briefly announces** what it just produced and moves on to the next file, without waiting for confirmation (the user already validated through the questions).

---

## Step 3 — Anti-redundancy refactor

Once the 7 files are generated, the agent rereads the whole set in one pass and looks for:

1. **Duplicated definitions**: a term defined in the glossary AND re-explained in another doc → keep it in the glossary, replace it with a link in the other doc
2. **Redundant feature lists**: `core-features.md` and `architecture.md` describing the same flows → the feature stays on the business side, the architecture links back to it
3. **Repeated stack**: `tech-stack.md` and `architecture.md` listing the same tools → the exhaustive list stays in `tech-stack.md`, the architecture mentions only what is structural
4. **Test strategy vs test cases**: `test-strategy.md` describes the HOW (pyramid, tools, coverage target), `test-cases.md` describes the WHAT (business scenarios) — no mixing
5. **Technical decisions**: if a decision sits in `architecture.md` AND deserves an ADR, create/move it into the ADR and link

For each redundancy found, the agent briefly shows the user the proposed diff in a single pass (bullet list), then applies the fixes once approved as a whole.

If there is nothing to refactor (the ideal case), the agent says so and moves to the next step.

---

## Step 4 — AGENTS.md update (with validation)

**Strict rule**: before any change to `AGENTS.md`, the agent explicitly asks the user for permission, showing:
- If `AGENTS.md` does not exist: the full content it proposes to create
- If `AGENTS.md` exists: the exact diff it proposes to apply (section appended at the end by default)

### Content of the section to add / create

```markdown
## Project documentation

This project has structured documentation under `docs/`. Read these files before any significant change.

### Business
- [Glossary](docs/business/glossary.md) — domain vocabulary
- [Core features](docs/business/core-features.md) — main capabilities
- [Test cases](docs/business/test-cases/) — business test scenarios (one file per case, grouped by feature)

### Technical
- [Architecture](docs/technical/architecture.md) — overview and components
- [Tech stack](docs/technical/tech-stack.md) — technologies and tools
- [Test strategy](docs/technical/test-strategy.md) — testing approach
- [ADR](docs/technical/adr.md) — architecture decisions
```

If `AGENTS.md` already existed with other sections, add this one without touching the rest. If a "Documentation" section already existed, propose a merge rather than an overwrite.

**Claude Code compatibility.** `AGENTS.md` is read natively by most agents, but not by Claude Code, which looks for `CLAUDE.md`. If the project has no `CLAUDE.md`, or has one that does not import `AGENTS.md`, offer through a multiple-choice question to add the import line:

```markdown
@AGENTS.md
```

One single source of truth, readable by everyone. Never duplicate the content across both files: two copies drift apart.


---

## Update mode (re-running the skill)

When the skill detects a `docs/` it generated itself (signature: `docs/business/glossary.md`, `docs/business/core-features.md` and `docs/technical/architecture.md` present at minimum), it switches to update mode automatically. **This is the default behavior, not an option** — the skill is built to be re-run at every significant evolution of the project.

### Principle

The skill produces a **doc diff**, not a new set of docs. It compares the current state of the code against what is recorded in `docs/`, and offers the user the relevant adjustments — never losing human content added by hand.

### Detailed procedure

**1. Inventory of what exists**

First, the agent reads every file under `docs/` and builds an internal representation of them. It notes in particular:
- The list of glossary terms
- The list of features
- The list of existing test cases (per feature) with their title and file identifier
- The list of existing ADRs with their number and status
- Any comment or section that looks hand-edited (presence of `> TODO`, very specific wording, content absent from the code)

**2. Delta analysis**

The agent redoes the full project analysis (step 1 of the normal workflow) and compares it to the snapshot from the previous step. For each doc type, it sorts the items into 4 categories:

| Category | Default action |
|----------|----------------|
| **Unchanged** (present on both sides, consistent content) | Do nothing |
| **New** (present in the code, missing from the docs) | Propose an addition through a multiple-choice question |
| **Obsolete** (present in the docs, gone from the code) | Propose a deletion through a multiple-choice question, with context |
| **Changed** (present on both sides but diverging) | Propose an update through a multiple-choice question, showing the diff |

**3. Consolidated question round**

Instead of one round per file as on the first run, the agent presents a structured recap in a single pass (per doc type):

```
## Glossary — 3 proposed changes

NEW (1):
- "Idempotence" — spotted in src/api/handlers.py (new central concept)

OBSOLETE (1):
- "LegacyAuth" — no reference left in the code (removed in commit abc1234)

CHANGED (1):
- "Cart" — the current definition talks about "session", but the code now uses
  DB persistence. Update it?
```

Then a multiple-choice question to validate the whole thing: accept all / reject all / pick individually (see `clarify-with-choices`).

**4. Applying the changes**

Once validated:
- **Additions** are inserted following the existing order (alphabetical for the glossary, by feature for the test cases, continuous numbering for the ADRs)
- **Deletions** move the file to `docs/.archive/[date]/` rather than deleting it for good (recovery stays possible)
- **Changes** preserve any hand-marked sections (comments, handwritten notes) — the agent updates only the auto-generated part and reports what it preserved

### Per-doc specifics

**Test cases**: sequential numbering is avoided precisely to prevent conflicts on re-runs (descriptive kebab-case names). If an existing test case was renamed by hand, do not recreate it under the old name — use the current name as the reference.

**ADRs**: numbering is continuous and **immutable**. An existing ADR is never renumbered. New ADRs take the next free number. An obsolete ADR is not deleted — its status becomes `deprecated` or `superseded by ADR-XXXX` (to be validated through a multiple-choice question).

**AGENTS.md**: if the "Project documentation" section already exists and points at the right structure, leave it alone. Otherwise propose a targeted patch.

### Refactor in update mode

The anti-redundancy refactor (step 3 of the normal workflow) runs in update mode too, but over the **whole** set of files (existing + changed + added), not just the changes. That catches redundancies that survived the previous run.

### If nothing changed

If the analysis reveals no significant delta, the agent says so plainly ("The docs are up to date, nothing to change") and stops without a single superfluous tool call. That is a happy case, not an error.

---

## Cross-cutting advice

**Language**: follow the language of the existing project. If the project is in French (README, comments, business variable names), generate the docs in French. Otherwise in English. If it is a mix, ask the user.

**Level of detail**: aim for files people can use, not exhaustive ones. A 200-line glossary will not be read. 30 precise entries beat 100 vague ones.

**Honesty about uncertainty**: if the agent cannot find the information in the code and the user has no answer, mark the section with a `> TODO: to be completed — [precise question]` rather than making something up.

**ADRs**: do not invent them retroactively from the code. Ask the user which structural decisions deserve an ADR. If there are none, create a minimal `adr.md` explaining the format to use for future ADRs (template included).

**No over-engineering**: if the project is small (a single script, ~500 lines), offer a condensed version (one single `docs/README.md` rather than 7 files). Ask the user whether they prefer the full or the condensed version.

---

## Reference

- `references/templates.md` — detailed templates for the 7 files + typical multiple-choice questions per section
