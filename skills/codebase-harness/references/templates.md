# Harness artifact templates

The agent consults this file when it generates each of the harness artifacts. For every artifact it holds: (1) the expected structure, (2) the typical multiple-choice questions to ask during the approval phase.

**Underlying rule**: these templates fix the *form*, never the business content. An invariant, a threshold or a scope is always a user decision, approved through a multiple-choice question. The agent proposes, the user decides.

---

## 1. `docs/technical/invariants.md`

### File structure

```markdown
# Executable invariants

Architecture and shape rules made mechanically verifiable. Every invariant has an immutable ID, a script that checks it, and an actionable remediation.

Run every check: `bash tools/harness/run_all.sh`

| ID | Statement | Severity | Status |
|----|--------|----------|--------|
| INV-001 | … | error | active |
| INV-002 | … | warn | active |
| INV-003 | … | — | deprecated |

---

## INV-001 — [Short title]

- **Status**: active | deprecated
- **Statement**: the rule in one sentence, in the present tense, phrased as a property that holds true of the codebase
- **Source**: ADR-NNNN | architecture.md § Structural constraints | team convention (stated by the user)
- **Script**: `tools/harness/check_<subject>.<ext>`
- **Severity**: error | warn
- **Remediation**: what whoever breaks the rule has to do, concretely
- **Example violation**:
  ```
  <minimal excerpt>
  ```
- **Fix**:
  ```
  <the same excerpt, corrected>
  ```
```

### Writing rules

- **Numbering is immutable.** A deprecated invariant keeps its ID; nothing is ever renumbered. A new invariant takes the next number, even if gaps exist.
- **One invariant = one rule.** If the statement contains "and" or "unless", it is either two invariants or a badly framed rule.
- **The statement describes the wanted state, not the ban.** "The domain layer depends on no I/O module" rather than "do not import requests".
- **The remediation is an instruction, not an observation.** It has to be enough for an agent that never read the ADR.
- The example/fix blocks are mandatory: they are what makes the rule understandable without context.

### Typical multiple-choice questions

- "I extracted N candidate rules: [list]. Which ones should be made executable?"
- "INV-00X: severity `error` (blocking CI) or `warn` (signal only)?"
- "This rule comes from ADR-NNNN — should I add the 'Related executable invariants' cross-reference to the ADR?"
- "Invariant INV-00X no longer finds the layer it watches. Switch it to `deprecated`?"

---

## 2. Test-case front-matter (block B)

### Structure

To be inserted at the top of every `docs/business/test-cases/[feature]/[name].md`, before the title:

```yaml
---
feature: panier
type: nominal              # nominal | error | edge-case
priority: critical         # critical | important | nice-to-have
automated_test: tests/test_cart.py::test_add_product   # or null
status: covered            # covered | pending | manual
---
```

### Field semantics

| Field | Role | Automatic inference |
|-------|------|------------------------|
| `feature` | Grouping, must match the parent directory | Directory name |
| `type` | Nature of the scenario | Inferred from the title and the content |
| `priority` | **Feeds block D's scope** — the `critical` ones are the natural candidates for mutation testing | Inferred, to be approved |
| `automated_test` | Reference `<path>::<test name>` | Lookup by name, snake_case heuristic |
| `status` | State of the coverage | `covered` if a test was found, `pending` otherwise |

`status: manual` flags a scenario that will stay verified by hand (visual walkthrough, QA procedure) — it is excluded from the consistency checks, never counted as a gap.

### Typical multiple-choice questions

- "I annotated N test-cases. M of them are ambiguous: [list with options a/b/c]."
- "No automated test was found for this test-case — `pending`, or `manual` because it will never be automated?"
- "These N tests exist with no matching test-case. Create some, or ignore them (technical tests)?"

---

## 3. "Mutation threshold" invariant entry (block D)

The mutation threshold is an invariant like any other, with two extra fields: the scope and the baseline.

### Structure

```markdown
## INV-0NN — Domain mutation score ≥ 75%

- **Status**: active
- **Statement**: the mutation score over the critical scope does not fall below 75%
- **Source**: harness block D, "critical domain" scope approved on YYYY-MM-DD
- **Scope**: `<globs or modules>`
- **Script**: `tools/harness/run_mutation.* --scope critical`
- **Tool**: <detected tool> — parsable report: <format>
- **Severity**: warn (→ error planned once stabilized)
- **Baseline**: 78.4% measured on YYYY-MM-DD at <sha>
- **Remediation**: read the surviving mutants listed by the script. For each one,
  identify the unprotected behavior and add a test that expresses it. Never add
  a test whose only justification is killing a mutant — if a surviving mutant
  matches no behavior that counts, exclude it explicitly in the config with a
  comment justifying the exclusion.
```

### Writing rules

- **The initial threshold is the baseline rounded down**, never an aspirational round number. Its job is to prevent regression, not to set a goal.
- **The baseline is dated and tied to a sha.** Without that, there is no telling whether a variation comes from the code or from a change of scope.
- **A threshold is never lowered to get CI green again.** If the score drops, a behavior has lost its protection — the remediation is a test, not a number adjustment.
- The **Tool** field is filled in at detection time and not frozen in the skill: it documents what was found, so that whoever reads this six months later knows what to re-run.

### Typical multiple-choice questions

- "Mutation testing scope: critical domain / incremental on the diff / global / a combination / drop the block?"
- "These N modules carry the test-cases marked `critical`. Is the scope right?"
- "Baseline measured at X%. Should I set the threshold at <X rounded down>% as `warn`?"
- "The score has been more than 5 points above the baseline for N runs. Raise the threshold to Y%?"

---

## 4. Scheduled task prompt (block C)

Concerns only the **interpretation** variant of block C (see `block-c-doc-gardening.md`, section 6.4), the one that runs an agent. The mechanical report is a scheduled CI job and has no prompt.

### Structure

Three elements, whatever the host's scheduler — the field names themselves vary:

| Element | Value |
|---|---|
| Title | `Harness — doc-gardening [project name]` |
| Cadence | cron expression chosen through a multiple-choice question |
| Prompt | the one below, as is |

```
Re-run the codebase-harness skill in update mode on the project [path].
Do not modify any file automatically — produce only a consolidated
report: new invariant violations, obsolete invariants, drifted
test-cases (covered_broken, or a new test with no test-case),
mutation score regression against the baseline and new surviving
mutants, documentation that has drifted. If everything is green, say so and
send nothing else. Write the report in the language of the project.
```

### Writing rules

- The prompt must explicitly contain **"do not modify any file automatically"**. The task runs with no human at the keyboard; this is the only protection.
- The prompt must contain **"if everything is green, send nothing"**. A task that produces an empty report every week teaches the team to stop reading it.
- The project path is hardcoded: the task has no session context.
- The prompt must say **"write the report in the language of the project"**. This skill is written in English; the report it installs in someone else's project is not.

### Typical multiple-choice questions

- "Cadence: daily / weekly / twice monthly / monthly?"
- "Here are the prompt and the cadence. Should I create the task?"

---

## 5. The "Harness" section of `AGENTS.md`

The full structure is in SKILL.md, step 7. Two writing rules apply:

- **Include only the subsections of the blocks actually enabled.** A subsection describing a check that does not exist wastes agents' time and undermines trust in the rest of the file.
- **Never touch the "Project documentation" section** generated by `codebase-cartographer`. The two skills coexist in the same file without stepping on each other.

### Typical multiple-choice questions

- "Should I add the Harness section to AGENTS.md? Here is the proposed content."
- "AGENTS.md already has a Harness section mentioning block X, disabled since then. Should I remove it?"

---

## 6. Script writing conventions

Every script produced in `tools/harness/` respects the same contract, whatever the block and whatever the language. That contract is what lets update mode and the scheduled task aggregate them without knowing them individually.

### Interface

| Element | Rule |
|---------|------|
| `--explain` | Describes the rule and its scope without checking anything. Mandatory. |
| `--root <path>` | Allows running the script from outside the current directory. Mandatory. |
| Standard output | One line per violation, format `path:line: [INV-NNN] message — remediation` |
| Exit code 0 | No violation |
| Exit code 1 | At least one violation of severity `error` |
| Exit code 2 | Only violations of severity `warn` |

### Golden rule for messages

An error message is written **for an agent that has no context**. The test: is the message enough to fix the problem without opening another file?

```
✗  unauthorized import
✗  INV-001 violated
✓  src/domain/checkout.py:42: [INV-001] `requests` imported in the domain layer
   — move the HTTP call to `src/application/` and expose a port on the domain side
```

### Forbidden

- **No auto-fix.** Even when the fix is obvious. The harness produces a signal; the fix goes through a visible commit.
- **No modification of its own config or its own threshold.** An adjustment is a decision; it goes through a multiple-choice question and through `invariants.md`.
- **No dependency to install** for the documentation checking scripts. They run on a minimal CI; if they require a `pip install`, they will end up disabled.

### Typical multiple-choice questions

- "The check_X script fires N false positives on the existing code. Should I fix the script, or loosen the rule?"
- "Move INV-00X from `warn` to `error`? Existing violations have been at zero for N days."
