# Documentation file templates

The agent reads this file when it is about to generate each of the 7 files. For every file it holds: (1) the expected structure, (2) typical multiple-choice questions to ask the user during the validation phase.

---

## 1. `docs/business/glossary.md`

### Structure

```markdown
# Business glossary

Domain vocabulary. Each term is defined once here and referenced from the other docs.

## [Term A]
Short definition (1-3 sentences). Where useful, a concrete example in parentheses.

## [Term B]
...
```

Order: alphabetical. No more than 3 sentences per entry. If a definition needs more, it is probably a feature, not a term.

### Typical multiple-choice questions

- "I identified these candidate business terms: [list]. Which ones do we keep?"
- "The term X: I see two possible uses in the code — [A] or [B]?"
- "Are any important terms missing that I did not see in the code?"

---

## 2. `docs/business/core-features.md`

### Structure

```markdown
# Core features

The product's main capabilities, from the user's point of view.

## [Feature 1: short name]

**Description**: One to three sentences on what the feature lets you do.

**Users concerned**: [roles / personas]

**Main journey**:
1. ...
2. ...

**Key business rules**:
- ...

## [Feature 2: short name]
...
```

A feature is a user capability, not a technical endpoint. If the agent hesitates, it is probably architecture, not a feature.

### Typical multiple-choice questions

- "I identified these features: [list]. Which one is the main feature?"
- "Which users does feature X concern: [A] / [B] / both?"
- "Are there features in progress or planned that should be documented, or only what exists today?"

---

## 3. `docs/business/test-cases/[feature]/[name].md` (one file per test case)

### Sources to go through

To identify candidate test cases, the agent inspects, in this order:

1. **Existing tests in the code**: `*_test.*` and `*.spec.*` files, the `tests/`, `__tests__/`, `spec/` folders, etc. Every unit or business integration test becomes a candidate.
2. **Controllers / endpoints / handlers**: HTTP routes, event handlers, CLI commands. Every endpoint suggests at least one nominal case plus an error case.
3. **Business features already documented** in `core-features.md`: for each feature, derive the main scenarios not covered by the two previous sources.

The agent consolidates the list, removes duplicates, and presents a recap to the user as multiple-choice questions BEFORE writing the files.

### Organization

One `.md` file per test case, grouped by feature in a subfolder:

```
docs/business/test-cases/
├── authentication/
│   ├── login-succeeds.md
│   ├── login-invalid-password.md
│   └── login-locked-account.md
├── cart/
│   ├── add-product.md
│   └── ...
└── ...
```

Naming convention: kebab-case, descriptive, no numeric prefix (the ordering carries no business meaning).

### Structure of a test case file

```markdown
# [Clear one-sentence title]

**Feature**: [feature name, link to core-features.md#feature]
**Type**: nominal / error case / edge case
**Priority**: critical / important / nice-to-have

## Context
System state and preconditions before the test. Actors involved. Initial data.

## Action
What the user (or the upstream system) triggers. One clear main action.

## Expected result
What must happen. Final system state, what the user gets back, observable side effects.

## Notes (optional)
- Existing automated test: `path/to/test.py::test_xxx` (if applicable)
- Endpoint involved: `POST /api/...` (if applicable)
- Related cases: [link to other TCs]
```

### Typical multiple-choice questions

- "I found [N] tests in the code and [M] endpoints. I propose these [X] test cases (list). Which ones do we keep?"
- "For feature [X], I only found nominal cases in the code. Do you want me to propose error cases as well?"
- "Granularity: one TC per distinct scenario (verbose) / group close variants into a single TC (compact)?"
- "Include the mapping to the existing automated tests in the Notes field?"

---

## 4. `docs/technical/architecture.md`

### Structure

```markdown
# Architecture

## Overview

Diagram (ASCII or mermaid) + 2-3 paragraphs of explanation.

## Components

### [Component 1]
- **Role**: ...
- **Key technologies**: [see tech-stack.md]
- **Interfaces**: (who it talks to, how)

### [Component 2]
...

## Main flows

For the 2-3 most structural flows, walk through the path between components.

## Data

Where relevant: simplified data model, external sources, persistence.
```

No copy-paste of tech-stack.md here. Mention technologies ONLY when they are structural for the architecture.

### Typical multiple-choice questions

- "The architecture is rather: monolith / microservices / serverless / hybrid?"
- "Preferred diagram format: ASCII art / mermaid / link to an external file?"
- "Which 2-3 flows are the most critical to document?"

---

## 5. `docs/technical/tech-stack.md`

### Structure

```markdown
# Tech stack

## Languages & runtimes
- ...

## Main frameworks & libraries
- **[Name]** (version) — role in the project

## Database / persistence
- ...

## Infrastructure & deployment
- ...

## Dev tooling
- Tests: ...
- Lint / format: ...
- CI/CD: ...

## External services
- ...
```

Only the versions that matter (language, major framework, DB). No need to list every sub-dependency.

### Typical multiple-choice questions

- "For versions, do I list: all of them / only the majors / only when critical for compatibility?"
- "Include personal dev tooling (IDE config, etc.) or only the shared stack?"

---

## 6. `docs/technical/test-strategy.md`

### Structure

```markdown
# Test strategy

## Pyramid / philosophy
Describe the kind of pyramid in use (classic, trophy, ice-cream, etc.) and why.

## Types of tests
- **Unit**: framework, naming conventions, where they live, coverage target
- **Integration**: ...
- **End-to-end**: ...
- **Others** (perf, security, accessibility): ...

## Conventions
- Shape of a test (AAA, Given/When/Then in code, etc.)
- Fixtures & mocks: the approach
- Naming of test files and test functions

## Running them
- Local commands
- Running in CI
- Merge criteria (minimum coverage, tests that must pass)
```

### Typical multiple-choice questions

- "Which kind of pyramid: classic (lots of unit tests) / trophy (lots of integration) / other?"
- "Overall coverage target: [value] / no numeric target / defined per test type?"
- "E2E tests are: already there / to be set up / not planned?"

---

## 7. `docs/technical/adr.md` + `docs/technical/adr/`

### Sources to go through BEFORE the questions

To propose candidate ADRs, the agent analyzes:

1. **The code**: detectable structural technical choices (chosen framework, architecture pattern, DB choice, authentication approach, state management, caching strategy, etc.)
2. **The git history** (when available):
   - `git log --oneline` to spot commits that mention migration, refactor, choice, decision, switch, replace, introduce, remove
   - `git log --all --grep="ADR\|decision\|migrat\|refactor\|switch\|replace"` for the explicit ones
   - Tags and branches that signal major changes
   - Files deleted or renamed en masse (the signature of a structural refactor)
3. **The configuration files**: `package.json` (major deps added/removed), `Dockerfile` (base image switched), CI/CD config (pipeline changes)

The agent consolidates a list of **candidate decisions** (5-15 entries max), each with:
- The short name of the decision
- The clue that surfaced it (commit, code, etc.)
- The level of evidence (clear / likely / speculative)

That list is presented to the user as a multiple-choice question so they can select the real decisions to formalize.

### Structure of `adr.md` (index)

```markdown
# Architecture Decision Records

The project's structural decisions. Each ADR is a numbered file under `adr/`.

## Format

Use the `adr/0000-template.md` template to create a new ADR.

## Index

- [ADR-0001: Title](adr/0001-title.md) — status: accepted
- [ADR-0002: Title](adr/0002-title.md) — status: proposed
```

### Structure of an individual ADR (`adr/NNNN-title.md`)

```markdown
# ADR-NNNN: [Title]

**Status**: proposed / accepted / deprecated / superseded by ADR-XXXX
**Date**: YYYY-MM-DD
**Source**: (optional) commit abc1234, or "reconstructed after the fact"

## Context
Which problem, which constraints?

## Decision
What was decided, in one to three clear sentences.

## Consequences
- Upsides: ...
- Downsides / costs: ...
- Risks: ...

## Alternatives considered
- [Option A] — rejected because ...
- [Option B] — rejected because ...
```

### Typical multiple-choice questions

- "I detected these candidate decisions in the code and the git history: [list with level of evidence]. Which ones do we formalize as ADRs?"
- "For decision X (evidence: likely), I am missing context on the why. Can you clarify: [option A] / [option B] / I will write it out freely?"
- "Are there important decisions I did not detect that you want to add?"
- "For reconstructed ADRs, should the Source field say 'reconstructed after the fact' explicitly?"

**Important**:
- NEVER write an ADR without user validation, even when the evidence looks strong
- If the user has no decision to formalize, create only `adr.md` (an empty index) plus `adr/0000-template.md` for future ADRs
- For reconstructed decisions (no clear git context), mark the Source as "reconstructed after the fact", for transparency

---

## General notes on the question phase

The doctrine of validation through multiple-choice questions — the mechanism depending on the host agent, the shape of a round, how to word questions, edge cases — lives in the `clarify-with-choices` skill. The templates above fix *what we ask*; `clarify-with-choices` fixes *how we ask it*.
