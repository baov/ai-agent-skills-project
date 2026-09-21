# Block A — Executable invariants

Loaded by `codebase-harness` only if this block was retained in the scoping multiple-choice question (step 2). The other blocks live in the neighbouring `block-*.md` files.

---

## 3.1 — Extracting the candidate rules

The agent re-reads (where they exist):
- `docs/technical/architecture.md`, section "Structural constraints"
- Every ADR under `docs/technical/adr/*.md` — the "Decision" section above all
- The root `README.md`, for hints of conventions ("no direct DB calls in handlers", and the like)

If the cartographer documentation never ran, the agent asks the user directly:

> "Which code or architecture rules would you like to make testable? For instance: isolated layers, a ban on I/O imports inside a layer, file naming conventions, mandatory return types on public functions, and so on."

The question is asked in the target project's language, like everything this block writes into that project.

## 3.1 bis — Shape thresholds are invariants like any other

On top of the rules drawn from the ADRs, always add one family of candidates that gets forgotten because it passes for cosmetic: **function size, file size, cyclomatic complexity, nesting depth, number of parameters**.

The justification is not aesthetic, and it has to be put to the user as such: **tangled code degrades agent productivity**. An agent reworking a 300-line function with high complexity makes repeated passes at it, produces wide diffs, breaks adjacent things, and sometimes fails to untangle its own knots — a human then has to take over, which cancels out the gain of delegating. Constraining shape up front is cheaper than untangling downstream.

That is a measurable argument, not a principle: if the user is doubtful, offer to start in `warn` and to watch, over two weeks, the correlation between violations and the number of agent turns needed.

Reasonable starting thresholds, to be tuned to the project rather than imposed:

| Metric | `warn` threshold | Typical tool |
|----------|--------------|---------------|
| Lines per function | 40 | Checkstyle/Detekt (JVM), ESLint `max-lines-per-function` (JS/TS) |
| Cyclomatic complexity | 10 | PMD/Detekt, ESLint `complexity` |
| Nesting depth | 4 | Detekt, ESLint `max-depth` |
| Parameters per function | 5 | Detekt, ESLint `max-params` |

Do not reinvent these checks: when the stack's standard linter already knows how to do it, the invariant amounts to **turning on and configuring the existing rule**, and `invariants.md` documents the threshold and why it is there. Write a custom script in `tools/harness/` only when no tool in the stack covers the rule.

## 3.1 ter — Consolidation

The agent consolidates a list of **candidate rules** (5-15 max), each one carrying:
- A one-sentence statement
- Its source (ADR-XXXX, a section of architecture.md, or "stated by the user")
- The proposed check mechanism (Python AST, custom ESLint, ArchUnit, dependency-cruiser, custom test)
- A complexity estimate (low / medium / high)

## 3.2 — Selection multiple-choice question

```
I extracted N candidate rules:

INV-CANDIDATE-1: "The `src/domain/` layer imports no I/O module"
    Source: ADR-0003 (hexagonal architecture)
    Proposed check: custom Python AST (low complexity)

INV-CANDIDATE-2: "Every REST endpoint has a Pydantic response schema"
    Source: architecture.md, "Structural constraints" section
    Proposed check: custom Python AST (medium)

INV-CANDIDATE-3: "No TODO in main code"
    Source: team convention (stated by the user)
    Proposed check: grep + regex (low)

...
```

Multiple-choice question: "Which ones do you want to make executable?". Options: all / a selection / none. The wording reaches the user in the target project's language; the example above is written in English only because this file is.

For each validated rule, a second multiple-choice question: "Severity? `error` (blocking CI) or `warn` (signal only)?". Default recommendation: start in `warn` for one or two weeks, then move to `error` once existing violations are down to zero.

## 3.3 — Producing the artifacts

For each validated invariant, the agent produces:

**a) An entry in `docs/technical/invariants.md`** following the template (see `references/templates.md` section 1):
- An `INV-NNN` id (immutable numbering, never renumbered)
- Status `active`
- Statement, source, link to the script, severity, actionable remediation, an example violation and its fix

This file is documentation of the target project: it is written in that project's language, not necessarily in English.

**b) A check script in `tools/harness/check_<subject>.{py,js,kt,go}`** following the conventions:
- Output format `path:line: [INV-NNN] message — remediation`
- An `--explain` mode that describes the rule without checking anything
- A `--root <path>` mode so it can be tested locally
- Exit codes: 0 OK, 1 `error` violation, 2 `warn` violations
- See `references/harness-starters/README.md` for the contract every script has to honor, and `references/templates.md` § 6 for message conventions

**c) A feedback loop into the ADRs concerned**: if the rule comes from an ADR, the agent offers to add an "Associated executable invariants: INV-NNN" field to that ADR. Always through a multiple-choice question before any change.

## 3.4 — Integration proposal

The agent shows the user the snippet to add to pre-commit / CI, and asks explicitly for permission to write it:

```yaml
# pre-commit example
- id: harness-invariants
  name: Harness — invariant check
  entry: python tools/harness/check_layer_isolation.py
  language: system
  pass_filenames: false
```

```yaml
# GitHub Actions example
- name: Harness checks
  run: |
    python tools/harness/check_layer_isolation.py
    python tools/harness/check_api_typing.py
```

The skill does not touch these files without validation. If the user says no, the scripts exist in `tools/harness/` all the same — they can be run by hand.

---
