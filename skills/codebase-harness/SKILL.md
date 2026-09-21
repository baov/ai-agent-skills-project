---
name: codebase-harness
description: Deterministic enforcement layer that keeps a codebase coherent while AI agents contribute to it. Four optional blocks offered through multiple-choice questions: (A) executable invariants — ADRs, architecture rules and shape thresholds (size, complexity) turned into custom pre-commit/CI linters; (B) test-case bridge to real tests — YAML front-matter + a coverage script; (D) mutation testing — checks that unreviewed tests would really catch a bug; tool detected from the stack, scope calibrated by criticality; (C) doc-gardening — a scheduled task (CI or the host's scheduler) that reports drift. Artifacts in `tools/harness/` and `docs/technical/invariants.md`. Use when the user wants an "agent harness", to "make ADRs executable", "custom linters", "architecture enforcement" (ArchUnit, dependency-cruiser), "mutation testing", or says "my tests don't test anything". Works best after `codebase-cartographer`, also runs in degraded mode.
compatibility: Requires git and a shell. Block C additionally assumes a scheduler — scheduled CI (GitHub Actions, GitLab pipeline), a scheduled task of the host agent, or cron.
---

# Codebase Harness

Sets up a deterministic enforcement layer so a codebase stays coherent while AI agents (or humans in a hurry) contribute to it. Documentation alone is not enough: it takes mechanical checks that stop drift before it lands on main.

## Doctrine

**The harness does not exist to compensate for how fast agents go. It exists to frame it.** When a machine writes the code, the control loop gets stricter, not looser — it is precisely because throughput rises that the guardrails have to be mechanical rather than declarative. A harness treated as just another lint tool misses its point.

Three consequences govern everything that follows:

1. **A check that never runs is not a check.** A rule written in an ADR or in an AGENTS.md is an intention; a script that exits with code 1 is a constraint. This skill's job is to turn the former into the latter.
2. **What is not reviewed must be verified some other way.** The rarer human review gets on an artifact, the stronger the mechanical verification of that artifact has to be. That is block D's reason to exist: tests nobody reviews need a check that is not review.
3. **Depth is calibrated on criticality, not on whether the tool happens to be available.** Stacking every check onto every task is easy to automate and rarely justified. Every block must be restrictable to a scope.

> **Companion skill**: this skill works best after [`codebase-cartographer`](#), which produces the ADRs, the documented architecture and the test-cases. But it can also run in degraded mode on a project without that documentation — it adapts to what it finds and asks the missing questions directly.

## The four blocks

The skill offers four independent blocks. The user can enable one, several, all or none of them. Each is offered through a multiple-choice question at the start of the run.

| Block | Produces | Drawn from |
|--------|---------|----------------------|
| **A — Executable invariants** | `docs/technical/invariants.md` + linters in `tools/harness/` + pre-commit/CI integration | ADRs, architecture constraints, shape thresholds, team conventions |
| **B — Test-case bridge to real tests** | YAML front-matter in every test-case.md + `tools/harness/check_test_coverage.*` | Existing test-cases + the automated test suite |
| **D — Mutation testing** | Config for the detected tool + `tools/harness/run_mutation.*` + per-scope thresholds in `invariants.md` | Existing test suite, critical scopes of the domain |
| **C — Automated doc-gardening** | Scheduled task (configurable cadence) producing a report without modifying anything | Existing documentation + the A, B and D checks |

**Blocks B and D answer two different questions.** B checks that a test *exists* for a documented behavior. D checks that a test *would catch a bug* if there were one. A test-case can be `covered` in B's sense and still be guarded by a test that asserts nothing — only D sees that case. Enabling both is the nominal case; enabling B alone leaves a known blind spot.

---

## Workflow overview

```
[First run]
1. Context detection (has cartographer run? which artifacts are there?)
2. Scoping question: which blocks to enable among A, B, D, C?
3. For each enabled block:
   a. Analysis + targeted multiple-choice question
   b. Artifact production (md, scripts, config, scheduled task)
   c. Integration proposal (pre-commit, CI) — NEVER applied without approval
4. Update of the "Harness" section in AGENTS.md (with a multiple-choice question)

[Re-run: update mode]
1. Inventory of the blocks already installed (presence of tools/harness/, invariants.md, mutation config, scheduled task)
2. For each block: run the existing checks + analyze the delta
3. Consolidated report (new violations, obsolete invariants, drifted test-cases, mutation score regression)
4. Grouped multiple-choice question to propose the adjustments (nothing automatic, ever)
```

**Core principle**: this skill never modifies application code. It only produces documentation files, scripts in `tools/harness/`, and integration configs (proposed, not written). Detected violations are reported back to the human, never fixed silently.

---

## Step 1 — Context detection

First of all, the agent inspects the project to understand what it has at hand. In parallel:

- Does `docs/technical/architecture.md` exist? Does it contain a "Structural constraints" section?
- Do `docs/technical/adr.md` and `docs/technical/adr/*.md` exist? If so, read every ADR to extract the structuring decisions.
- Does `docs/business/test-cases/**/*.md` exist? Count them, and note whether YAML front-matter is already present.
- Does `tools/harness/` already exist? (signature: this skill has already run)
- Does `docs/technical/invariants.md` exist? (same)
- Inspect the stack to pick the right kind of linter: Python (AST), JS/TS (custom ESLint or dependency-cruiser), JVM (ArchUnit), Go (custom analyzer), Rust (clippy + custom lints), and so on.
- Spot the mutation tooling already in place, by searching the manifests and configs of the detected stack (e.g. `pitest` in `pom.xml`/`build.gradle(.kts)`, `@stryker-mutator/*` in `package.json`, `stryker.conf.*`, `infection.json`, `setup.cfg`/`pyproject.toml` for mutmut) as well as report directories already committed. Note the test runner too and, if possible, how long a full run of the suite takes — that is the number block D hinges on.
- Inspect the CI: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, etc. to know where to propose the integration.
- Inspect pre-commit: `.pre-commit-config.yaml`, `lefthook.yml`, `.husky/`, `package.json` (husky), etc.

If the skill detects that `tools/harness/` or `invariants.md` already exist, it switches to **update mode** (see the dedicated section). This is idempotent.

If the cartographer documentation was never produced (no ADRs, no test-cases), the agent announces it and explains:

> "I can set up a harness layer anyway, but I will have to ask you about the architecture rules directly. If you prefer, run `codebase-cartographer` first to structure the documentation, then come back here. Which one do you pick?"

Multiple-choice question with two options: "continue in degraded mode" / "stop, I will run cartographer first".

---

## Step 2 — Scoping question

The agent presents the four blocks with a one-sentence summary each and asks which ones to enable. Typical format:

```
Four blocks available:

A — Executable invariants
    Turns your architecture rules and your ADRs into custom linters that run
    in pre-commit/CI. Setup cost: medium (1 script per rule). Maintenance
    cost: low. Recommended if there are > 2 developers or if AI agents
    contribute.

B — Test-case bridge to real tests
    Adds YAML front-matter to your business test-cases and produces a script
    that checks they point at tests that really exist. Setup cost: low.
    Maintenance cost: none. Recommended if you already have test-cases under
    docs/business/test-cases/.

D — Mutation testing
    Injects artificial bugs into the code and checks that your tests catch
    them. It is the only check that measures *assertion quality* rather than
    line execution. Setup cost: low (config). Run cost: HIGH — a full run
    takes tens of minutes. Maintenance cost: low. Recommended if agents write
    tests nobody reviews line by line.

C — Automated doc-gardening
    Creates a weekly (or other cadence) scheduled task that re-checks the
    documentation and the checks as time goes by, and reports back to you.
    No file modified without approval. Recommended if the project changes
    regularly.
```

Multi-select multiple-choice question (doctrine in `clarify-with-choices`): "Which ones to enable? A / B / D / C / all / none". If "none" → the skill ends with the message "Understood, nothing to do.".

The execution order is fixed: **A → B → D → C**. B may rely on the stack detected in A; D relies on B to target the critical scopes (the test-cases marked `priority: critical` are the best starting candidates); C relies on A, B and D to know what to monitor.

If the user enables D without B, say so once: the mutation scope will have to be defined by hand for lack of prioritized test-cases. This is not blocking.

---

## Steps 3 to 6 — The blocks

Each block kept at the scoping question runs in its own file.
**Read only the ones that were enabled**: the fixed execution order stays
A → B → D → C.

| Block | Detailed procedure |
|---|---|
| A — Executable invariants | [`references/block-a-invariants.md`](references/block-a-invariants.md) |
| B — Test-case bridge to real tests | [`references/block-b-test-case-bridge.md`](references/block-b-test-case-bridge.md) |
| D — Mutation testing | [`references/block-d-mutation.md`](references/block-d-mutation.md) |
| C — Automated doc-gardening | [`references/block-c-doc-gardening.md`](references/block-c-doc-gardening.md) |

Every file follows the same structure: prerequisites and cost trade-off,
artifact production, pre-commit/CI integration proposal. None of them writes
anything without explicit approval.

## Step 7 — Updating AGENTS.md

The agent adds (or updates) a section in `AGENTS.md`. **Always with a multiple-choice question before writing**.

**Claude Code compatibility.** `AGENTS.md` is read natively by most agents, but not by Claude Code, which looks for `CLAUDE.md`. If the project has no `CLAUDE.md`, or has one that does not import `AGENTS.md`, offer through a multiple-choice question to add the import line to it:

```markdown
@AGENTS.md
```

A single source of truth, readable by all. Never duplicate the content across both files: two copies drift apart.


### Section content

```markdown
## Harness

This project has a deterministic enforcement layer generated by the `codebase-harness` skill. Agents must comply with these rules.

### Executable invariants

The architecture rules are made executable by scripts in `tools/harness/`. Full list and statuses in [docs/technical/invariants.md](docs/technical/invariants.md).

- Before any commit, run: `bash tools/harness/run_all.sh` (or the individual scripts)
- Each linter's error messages include the remediation to apply — read them before looking elsewhere
- To understand an invariant without checking it: `python tools/harness/check_<subject>.py --explain`

### Test-case bridge to real tests

Every scenario under `docs/business/test-cases/` carries YAML front-matter pointing to its automated test. The `tools/harness/check_test_coverage.*` script checks the consistency.

- Adding a test-case → fill in the front-matter (`automated_test` field, or `status: pending`)
- Adding a test → check it has a matching test-case, otherwise create one

### Mutation testing

Tests written without line-by-line human review are kept in check by mutation testing. A green test is not proof: only a killed mutant is.

- Scope and thresholds: see the matching invariant in [docs/technical/invariants.md](docs/technical/invariants.md)
- Run locally: `bash tools/harness/run_mutation.sh --scope diff`
- A surviving mutant is dealt with by adding a test that expresses the unprotected **behavior** — never a test written to kill the mutant. If the mutant matches no behavior that counts, exclude it explicitly in the config with a comment justifying it
- Never lower a threshold to get CI passing: that is the signal that a behavior has lost its protection

### Doc-gardening

A scheduled task runs periodically and reports drift. When the report surfaces violations, treat that as a signal to improve the repo (add documentation, sharpen an invariant, and so on), not as noise.
```

> Which subsections appear depends on the enabled blocks. If only block B is active, include only the "Test-case bridge to real tests" subsection.

**Coexistence with `codebase-cartographer`**: the "Project documentation" section (generated by cartographer) is never touched by this skill. If only the "Harness" section is missing, add it after the Documentation section.

---

## Update mode (re-running the skill)

When the skill detects that it has already run (presence of `tools/harness/` or of `docs/technical/invariants.md`), it automatically switches to update mode.

### Inventory

- List the defined invariants (parse `invariants.md`) and their status (`active`, `deprecated`)
- List the scripts in `tools/harness/` and identify the ones tied to an invariant
- List the test-cases carrying front-matter and note their `status`
- Record the mutation baseline and the current threshold from `invariants.md`, and check that the tool config and the `run_mutation.*` wrapper are still in place and consistent with the stack
- Check whether a scheduled task exists for this project: a scheduled CI job (`.github/workflows/`, GitLab *Schedules*), a task in the host's scheduler, or a cron entry

### Running the checks

The agent runs (through bash) every script in `tools/harness/` and collects the output. For each invariant:

| Result | Action |
|----------|--------|
| Pass | Nothing to do |
| New fail (the code used to pass, no longer does) | Report it, propose a remediation |
| Already known fail | Mention it (without noise) |
| Obsolete invariant (the layer/pattern no longer exists) | Propose switching it to `deprecated` |
| Missing invariant (new ADR without an invariant) | Propose creating one |

For the test-cases:

| Result | Action |
|----------|--------|
| `pending` whose test now exists | Propose `covered` |
| `covered_broken` (test gone or failing) | Propose an investigation |
| Orphan test (new test without a test-case) | Propose creating the test-case |

For mutation testing (if block D is installed):

| Result | Action |
|----------|--------|
| Score stable or rising | Nothing to do — propose raising the threshold if the gap to the baseline exceeds 5 points |
| Score falling below the threshold | Report it, list the new surviving mutants, propose an investigation |
| New module in the critical scope, not covered by the config | Propose extending the scope |
| Run far exceeding its usual duration | Report it — often the sign of a slow test added, or of a scope that grew without anyone deciding it |

**Never propose aligning the threshold with a falling score.** A threshold lowered to get back to green turns a signal into decoration.

### Consolidated report

```
## Harness — report

INVARIANTS (5 active)
  - INV-001 (domain isolation): 2 new violations
      src/domain/checkout.py:42 import requests → remediation: move it to application/
      src/domain/checkout.py:67 import boto3 → same
  - INV-002 to INV-005: OK

  Deprecation candidate:
  - INV-003 (REST JSON status): no REST routes left in the code (ADR-0007 replaced them)

TEST-CASE COVERAGE (12 files)
  - 10 covered_ok, 1 pending → 1 covered_ok (a pending test has been implemented)
  - 1 covered_broken: cart/bulk-removal.md → test gone since commit abc1234

MUTATION (scope: critical domain)
  - score 74.1% (baseline 78.4%, threshold 75%) → BELOW THRESHOLD
  - 3 new surviving mutants, all in src/domain/cart/Discount.kt
      → introduced by branch feat/stackable-discounts

DOC-GARDENING
  - Scheduled task active (weekly, Monday 9am) — last run 3 days ago, OK
```

Consolidated multiple-choice question to approve the whole set of proposed actions.

### If nothing has changed

If every check passes and there is no delta, the agent simply says "Harness OK, nothing to do" and stops. No superfluous tool call.

---

## Cross-cutting advice

**Start small**. Do not try to make 20 rules executable at once. Start with 2-3 invariants that really hurt when they are violated (e.g. an isolated layer, a secret in clear text, a console.log in production). Extend afterwards.

**Severity `warn` at first**. A linter set to `error` on existing non-compliant code will block the whole team. Recommend `warn` for 1-2 weeks, long enough to clean up the existing violations, then switch to `error`.

**Actionable error messages**. This is the golden rule. A message saying "unauthorized import" is useless to an agent. A message saying "move this import to `src/application/` and expose a port on the domain side — see INV-001" is usable. Every starter provided follows this rule.

**No silent auto-fix**. Even when the agent is sure it knows how to fix a violation, it never does so without a multiple-choice question. The harness produces a signal; the human or the agent applies the fix in a visible commit.

**Feedback loop**. When an agent trips over an invariant, treat it as a signal: is the remediation clear enough? is the invariant too strict? is the documentation missing an example? Update `invariants.md` and the linter's error message accordingly. That is what makes the harness evolve with the project.

**Keep the trust**. A harness that produces too many false positives will be ignored. If a rule fires false positives over and over, that is a bug in the linter, not in the code. Fix the linter first.

**Run cost is a design constraint, not a detail**. A check that is right but too slow ends up disabled, which is worse than no check at all — it suggests a protection that no longer exists. For block D in particular: a demanding mutation testing run over 15% of the code that really runs beats a global run the team sets to `continue-on-error` and stops reading.

**Never stack by reflex**. Not every block is justified on every project. An internal utility with no reliability stakes does not need mutation testing; a billing calculation engine needs it more than it needs doc-gardening. When the user enables everything by default, ask about the real criticality before installing.

**What is no longer reviewed must be verified more**. When a project shifts to a mode where the agents write the code and the unit tests without line-by-line review, this is not the time to lighten the harness — this is the moment it becomes the only protection left. The signal to watch: if the invariants have been on `warn` for months and nobody reads the reports, the protection is nominal.

---

## Reference

- `references/block-a-invariants.md`, `-b-test-case-bridge`, `-c-doc-gardening`, `-d-mutation` — the detailed procedure for each block. Read only the ones kept at the scoping question: that is the whole point of the split
- `references/templates.md` — six sections: (1) `invariants.md` and its writing rules, (2) test-case front-matter, (3) a typical mutation threshold entry with its baseline, (4) the scheduled task prompt, (5) the Harness section of `AGENTS.md`, (6) script writing conventions and the golden rule for messages
- `references/harness-starters/` — reference implementations. Contains `README.md` (the contract shared by every script) and `check_test_coverage.py` (block B, complete and generic). Deliberately free of per-stack linters: the skill generates those from the conventions, which ages better than a frozen directory
- `references/harness-starters/mutation/` — optional. Block D **generates** its wrapper and its config from the detected stack (see `references/block-d-mutation.md`, sections 5.3.a and 5.3.b); this directory only freezes examples already proven internally, never a source of truth. The normalized output contract described in 5.3.b of that file takes precedence over any starter that departs from it.
