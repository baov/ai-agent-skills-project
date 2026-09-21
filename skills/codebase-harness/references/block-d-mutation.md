# Block D — Mutation testing

Loaded by `codebase-harness` only if this block was retained in the scoping multiple-choice question (step 2). The other blocks live in the neighbouring `block-*.md` files.

---

## 5.0 — What this block solves

Blocks A and B control the code and the existence of the tests. Neither controls **the value of the tests themselves**. That is the blind spot that matters most when agents write the test suite: a test can run, be green, cover 100% of the lines and assert nothing useful.

Mutation testing answers exactly that: the tool introduces mechanical alterations of the code (flip a condition, replace a `+` with a `-`, drop a call, return `null`), runs the tests again, and checks that at least one test fails. A **killed** mutant means the tests protect that behavior. A **surviving** mutant means that line can be broken without any test noticing.

To be said to the user explicitly, because it is the most frequent confusion: **the mutation score is not an improved coverage**. Coverage measures which lines run; the mutation score measures whether the assertions are worth anything. It is the metric coverage pretends to be without ever being it — and the only one that justifies not reading a test by hand.

> Consistency with `behavior-driven-testing`: this skill sets no numeric target as an end in itself. The mutation score is a **diagnostic tool** — a surviving mutant is a question ("which behavior is unprotected here?"), not a box to tick. A threshold in CI is there to prevent a regression, not to push a number up.

## 5.1 — Prerequisites and weighing the cost

Before proposing anything, the agent checks three things:

1. **A test suite exists and passes.** Mutation testing on a red suite makes no sense. If tests are failing, say so and stop there.
2. **How long a full run of the suite takes.** That is the multiplier: a mutation run executes the suite (partially) once per mutant. Measure it if possible, otherwise ask.
3. **The candidate scope.** The global run is almost always the wrong choice.

The agent then lays out the trade-off honestly, without selling the block:

```
Your suite runs in ~4 min. A mutation run over the whole codebase
would likely take several hours — unusable in MR CI.

Three possible scopes:

1. Critical domain only (recommended)
   The packages/modules carrying the business rules. Typically
   10-20% of the code, most of the risk. Estimated run: 10-20 min.
   → nightly CI, or pre-merge on the MRs that touch this scope.

2. Incremental on the diff
   Mutates only the files the branch changed. Short, proportionate
   run, but no protection against erosion elsewhere.
   → MR CI.

3. Global
   Full coverage, long run. Reserved for a weekly or monthly
   execution.
   → scheduled task, never blocking CI.
```

Multiple-choice question: scope 1 / 2 / 3 / a combination (typically 2 on MRs + 1 nightly) / drop block D. What the user actually reads is phrased in the target project's language.

**"Drop it" is a legitimate answer and must be presented as such.** If the suite is slow or flaky, or if CI is already saturated, mutation testing is a bad investment and the agent says so plainly rather than installing a check that will be disabled on the first red build.

## 5.2 — Choosing the critical scope

If the user settles on scope 1, the agent proposes a list of modules, leaning in this order on:

- The test-cases marked `priority: critical` in block B → trace back to the modules they exercise.
- The domain layer identified by the ADRs, or by `ddd-advisor` if it ran.
- Failing that: the modules with the highest density of conditional logic, or the ones the user points at.

Present the list as a multi-select multiple-choice question. Never guess silently: the scope is the structuring decision of this block.

## 5.3 — Producing the artifacts

#### a) Configuring the mutation tool

As with blocks A and B, **the agent detects the ecosystem and generates the matching config**. What follows is the specification, valid whatever the tool — it is the specification that governs, not a list of tools that will age.

Five points to settle in any generated config, in this order of priority:

1. **Explicit scope.** Restrict the targets to the scope retained in 5.2, by globs or by named packages. Never leave the "all the code" default — that is the leading cause of an unusable run.
2. **Default mutator set on the first pass.** Extended sets multiply run time and produce equivalent mutants (semantically neutral alterations, impossible to kill). Widen only if the score plateaus artificially high.
3. **No blocking threshold on the first run.** Measure before constraining. The threshold comes in 5.3.c, after the baseline.
4. **One report a human can read and one a machine can parse.** The second feeds the harness script; without it, the block cannot surface in the consolidated report.
5. **Timeout and parallelism calibrated on the real CI**, not on the tool's defaults — and incremental mode enabled if it exists, since that is what makes the "diff" scope viable.

The config is written into the project at the tool's standard location, **not** in `tools/harness/`. The harness provides the driving and the normalisation, never the tool's config: a developer has to be able to run the tool directly without going through the harness.

Landmarks per ecosystem, to be checked at run time rather than taken at face value — tooling moves:

| Ecosystem | Usual tool | Parsable format |
|------------|-------------|-----------------|
| JVM | PIT (`pitest`), through Maven or Gradle | XML |
| JS/TS | Stryker | JSON |
| .NET | Stryker.NET | JSON |
| Python | mutmut, cosmic-ray | JSON / SQLite depending on the tool |
| Go | go-mutesting, or `gremlins` | JSON |
| Rust | `cargo-mutants` | JSON |
| PHP | Infection | JSON |

If no mature tool exists for the detected stack, **say so and propose dropping block D** rather than installing an abandoned or experimental tool. A harness resting on an unmaintained tool is debt, not protection.

#### b) `tools/harness/run_mutation.{sh,ps1}`

The wrapper is the piece that makes the block tool-agnostic: it absorbs the difference in tooling and exposes a stable contract, identical to the one the block A and B scripts follow. It is that contract that has to be honored, not any particular implementation.

**Interface** — aligned with the other harness scripts:
- `--scope critical|diff|full` (default `critical`)
- `--explain`: describes the scope, the tool in use and the threshold, without running anything
- `--root <path>`: so it can be tested locally

**Behavior in `diff` mode**: compute the base with `git merge-base HEAD origin/<target branch>` and restrict the scope to the modified files, honoring the selection format of the detected tool.

**Normalised output** — independent of the underlying tool:
```
MUTATION — scope: critical (4 modules) · tool: <detected>
score: 78.4% (312 killed / 398 generated)  threshold: 75%  → OK

Most significant surviving mutants:
  <file>:44  [NEGATE_CONDITIONS]  no test tells > from >=
  <file>:71  [MATH]               the pro-rata computation is not asserted
```

**Exit codes** identical to the other scripts: `0` OK, `1` below the `error` threshold, `2` below the `warn` threshold.

**Two prohibitions**:
- The script never writes a test. It reports; the fix goes through `plan-driven-dev` with `behavior-driven-testing` in support.
- The script never changes the tool's config or the threshold. Adjusting a threshold is a decision, it goes through a multiple-choice question and an entry in `invariants.md`.

If the project is multi-module with several stacks (typical of a back + front monorepo), generate **one wrapper per stack** with the same contract, plus a root `run_mutation.sh` that calls them and aggregates the scores. The output contract stays the same; only the `tool:` line changes.

#### c) Entries in `invariants.md`

The mutation threshold is an invariant in its own right and follows the same `INV-NNN` numbering, with one extra field:

```markdown
## INV-012 — Domain mutation score ≥ 75%

- **Status**: active
- **Source**: harness block D, "critical domain" scope
- **Scope**: `src/domain/**`
- **Script**: `tools/harness/run_mutation.sh --scope critical`
- **Severity**: warn (→ error planned once stabilised)
- **Baseline**: 78.4% measured on YYYY-MM-DD
- **Remediation**: read the surviving mutants the script lists. For each one,
  identify the unprotected behavior and add a test that expresses it. Never add
  a test whose only justification is killing a mutant — if a surviving mutant
  matches no behavior that matters, exclude it explicitly in the config with a
  comment justifying the exclusion.
```

Like every entry in `invariants.md`, this one is written in the target project's language.

**The threshold rule**: the initial threshold is set **at the measured baseline, rounded down**, never at an aspirational round number. Its role is to prevent regression. It is then raised by explicit steps, each one validated through a multiple-choice question.

## 5.4 — Integration

As with the other blocks, the agent presents the snippet and asks permission before writing.

Two rules specific to this block:

- **Never in pre-commit.** The run time is incompatible with a local hook. If the user asks for it anyway, explain why it is a bad idea before following their decision.
- **`warn` is mandatory on the first pass.** Putting a mutation threshold in blocking CI right at install time guarantees a red CI and a check disabled within the week.

```yaml
# GitHub Actions — incremental mutation on MRs
- name: Harness — mutation (diff)
  run: bash tools/harness/run_mutation.sh --scope diff
  continue-on-error: true   # remove once the threshold is stable
```

```yaml
# GitHub Actions — nightly mutation on the critical domain
on:
  schedule:
    - cron: '0 2 * * *'
jobs:
  mutation:
    steps:
      - name: Harness — mutation (critical domain)
        run: bash tools/harness/run_mutation.sh --scope critical
```

On GitLab CI, transpose with a job under `rules: - if: $CI_PIPELINE_SOURCE == "merge_request_event"` for the incremental one and a `schedule` for the nightly one.

---
