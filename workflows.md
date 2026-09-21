# Workflows — chaining the skills

Ten skills, two families, and one rule: artifacts circulate, and skills are never called into a vacuum.

## Two families

**Entry points** — invoked by a user request.

| Skill | Trigger | Produces |
|---|---|---|
| `codebase-cartographer` | "document the project" | `docs/business/`, `docs/technical/`, a section in `AGENTS.md` |
| `codebase-harness` | "set up the guardrails" | `tools/harness/`, `docs/technical/invariants.md` |
| `ai-code-remediation` | "audit this codebase" | `.audit/<project>-<date>.md` + a remediation plan |
| `systematic-debugging` | "why does this crash" | A proven root cause (no file) |
| `plan-driven-dev` | "implement", "fix" | `.plans/done/<slug>.md`, `.plans/FEEDBACK.md` |
| `premerge-review` | "review my branch" | `.reviews/<branch>-<date>.md` + a verdict |
| `code-assimilation-quiz` | "quiz me" — **never automatic** | Nothing (learning) |

**Supporting skills** — loaded by another skill, rarely requested directly.

| Skill | Loaded by | Role |
|---|---|---|
| `behavior-driven-testing` | `plan-driven-dev` (steps 5-6), `ai-code-remediation` (S3) | Test doctrine |
| `ddd-advisor` | `ai-code-remediation` (when S8 dominates) | Design qualification |
| `clarify-with-choices` | `codebase-cartographer`, `codebase-harness`, `ddd-advisor` | Shapes the validation multiple-choice questions, and the degraded mode when the host agent has no question tool |

---

## Scenario 1 — A new feature on a tooled project

The nominal case, the one the chain was designed for.

```
plan-driven-dev
  step 1    reads invariants.md + tools/harness/ + .plans/FEEDBACK.md
  step 3    plan validated, applicable invariants noted in section 3
  step 5    TDD; the invariants run on every return to green
            └─ loads behavior-driven-testing for the test boundaries
  step 6    full suite + run_all.sh + check_test_coverage
       ↓
premerge-review
  phase 2   criticality determined
  phase 3   gauntlet — green by construction if step 6 was done
  phase 4   test-cases first (if critical), then the four angles
  phase 6   GO/NO-GO verdict
       ↓
code-assimilation-quiz   (optional, on explicit request)
```

**The point that matters**: step 6 of `plan-driven-dev` replays exactly the gauntlet of phase 3 of `premerge-review`. A review stopped by a mechanical check means step 6 was rushed.

---

## Scenario 2 — A production bug

```
systematic-debugging      diagnosis only, up to the proven cause
       ↓                  never fix here
plan-driven-dev           the root cause becomes the input to step 2
       ↓
premerge-review           criticality raised automatically if the bug touches security
```

**The classic mistake**: fixing during the diagnosis. The separation exists because a fix applied before the proof usually masks the real problem.

---

## Scenario 3 — Inheriting a vibe-coded codebase

```
ai-code-remediation
  phase 1   signals measured, including a sampled mutation score
  phase 2   the eight symptoms
            └─ if S8 dominates → ddd-advisor
            └─ if S3 is suspected → the mutation score proves or disproves it
  phase 4   plan cut into worksites
       ↓
codebase-cartographer     if the missing documentation is itself a finding
       ↓
plan-driven-dev           one pass per worksite
       ↓
codebase-harness          last — the remediation decisions
                          become executable invariants
```

**Why the harness comes last**: it freezes rules. Freezing them before knowing which ones matter produces a harness everyone disables at the first red build. The audit also supplies the mutation baseline.

---

## Scenario 4 — Tooling a healthy project

```
codebase-cartographer     ADRs, architecture, test-cases
       ↓
codebase-harness
  block A    the ADRs become linters — start in `warn`
  block B    front-matter on the test-cases
  block D    mutation testing — scope calibrated on the `priority: critical` cases
  block C    doc-gardening
```

The order A → B → D → C is mandatory: D targets its scope from the test-cases prioritized by B.

**Two weeks in `warn` before switching to `error`.** A blocking linter on existing non-conformant code stops the whole team.

---

## Scenario 5 — "My tests are worthless"

```
behavior-driven-testing   doctrine diagnosis: what do they actually test?
       ↓
codebase-harness          block D alone — measure before concluding
```

A mutation score turns an impression into a number. If the tests really are hollow, the rewrite goes through `plan-driven-dev`, one behavior at a time.

---

## How the artifacts circulate

This table is what makes the whole coherent: every file one skill produces is read by another.

| Artifact | Written by | Read by |
|---|---|---|
| `docs/business/glossary.md` | cartographer | premerge-review (angle 3), ddd-advisor |
| `docs/business/test-cases/**` | cartographer | harness (B decorates), premerge-review (phase 4) |
| `docs/technical/adr/**` | cartographer | harness (A extracts), premerge-review (angle 3) |
| `docs/technical/invariants.md` | harness | plan-driven-dev (step 1), premerge-review (phase 1) |
| `tools/harness/*` | harness | plan-driven-dev (step 5), premerge-review (phase 3) |
| `.plans/FEEDBACK.md` | plan-driven-dev | plan-driven-dev (step 1, later tasks) |
| `.reviews/<branch>.md` | premerge-review | plan-driven-dev (input to the fix) |
| `.audit/<project>.md` | ai-code-remediation | plan-driven-dev (one worksite per pass) |

**Degraded mode**: every skill works without these files, but says so. In `premerge-review`, a missing reference **increases** the review depth instead of reducing it.

---

## Chaining mistakes

| What people do | Why it misses |
|---|---|
| `premerge-review` to learn the code | That is `code-assimilation-quiz`. A review hunts defects, it does not teach. |
| `premerge-review` on a whole codebase | That is `ai-code-remediation`. A review works on a diff. |
| `ai-code-remediation` on a branch | The inverse of the above. |
| `codebase-harness` before `codebase-cartographer` | It works, but the agent will have to ask every architecture question by hand. |
| Fixing during `systematic-debugging` | The skill stops at the proven cause, by construction. |
| `code-assimilation-quiz` triggering on its own | Forbidden: explicit request only. |
| Mutation testing inside the TDD loop | Too slow. Its place is the gauntlet and CI. |

---

## One principle across the board

Three skills modulate their depth on **criticality**: `systematic-debugging`, `premerge-review`, `codebase-harness` (block D).

Criticality modulates what gets looked at and how deeply — never the scope, never the blocking threshold. A diff is read in full whatever its criticality, and a red gauntlet stays a NO-GO.
