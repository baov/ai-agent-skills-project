---
name: premerge-review
description: Defect-oriented pre-merge code review — first runs the branch through a gauntlet of mechanical checks (tests, lint, harness invariants, test-case bridge, mutation on the diff), then analyzes the diff against main at a depth calibrated on criticality, and produces a structured report with a GO/NO-GO verdict. A red gauntlet stops the review: no point hand-reading a diff that is about to change. Use SYSTEMATICALLY when the user asks for a "code review", "review my branch", "check my diff before merge", "is my PR ready", "review what I did", or before any merge inside an agentic pipeline (pre-merge checkpoint). Covers four angles — bugs/regressions, security, ADR/architecture compliance, debt/readability. Not to be confused with code-assimilation-quiz (developer learning, not defect hunting) or ai-code-remediation (cold audit of a whole codebase, not of a diff).
---

# Premerge Review

Defect-oriented code review on a branch diff, before merge. The goal is to play the demanding but fair reviewer: find what has to be fixed before the code reaches `main`, without drowning the signal in stylistic noise.

**First cardinal principle: the review is read-only.** Never modify code during a review. If the user then wants the findings fixed, that is the job of `plan-driven-dev` (or of the pipeline in progress) — the review report becomes the input of the fix plan.

**Second cardinal principle: attention is spent after the machine, not before.** Anything a mechanical check can settle must be settled before the review starts. Hand-reading a diff the harness already rejects wastes time twice over: the fix will change the diff, and everything will have to be read again. Hence the imposed order — gauntlet, then review. The review exists for what no machine can see: an intent that does not match the need, a broken implicit contract, a complexity that will cost dearly in six months.

## Phase 0 — Establish the diff

Before any analysis, pin down exactly what is under review:

1. Identify the target branch (`main` by default, otherwise `master`, otherwise ask).
2. Compute the comparison base with `git merge-base`, so that only the branch's own changes are reviewed, not the commits that landed on main in the meantime:
   ```bash
   git fetch origin
   BASE=$(git merge-base HEAD origin/main)
   git diff --stat $BASE..HEAD
   git log --oneline $BASE..HEAD
   ```
3. Announce the scope to the user: number of files, size of the diff, list of commits. If the diff is very large (>~2000 lines), offer to split the review into coherent subsets rather than skimming all of it superficially — a diluted review misses the real defects.

Do not stop at the raw diff: for every modified file, read enough context around the changes (the whole function, the class, the callers when relevant). Many bugs are only visible from the unmodified code that depends on the modified code.

## Phase 1 — Load the project context

The quality of the review depends on what is known about the project. Look, in this order, for:

- `AGENTS.md` — the project's conventions.
- `docs/technical/` — architecture, ADRs, test strategy. ADRs are the reference for the compliance angle: a change that contradicts a recorded decision is a major finding at the very least.
- `docs/technical/invariants.md` and `tools/harness/` — take stock of what exists (documented invariants, available scripts, mutation threshold and its baseline). The invariants serve as the reading grid for the compliance angle; **running** them happens in phase 3, not here.
- `docs/business/` — glossary and test-cases, to judge whether the diff respects the language of the domain and whether the modified behaviors are covered.

**Degraded mode**: if all or part of this documentation is missing, carry the review through in full on the three remaining angles, and handle the compliance angle from the conventions observable in the existing code (consistency with the patterns already in place). State explicitly in the report what could not be checked for lack of reference material — an absence of verification is not an absence of problems.

## Phase 2 — Calibrate depth against criticality

Not every branch deserves the same rigor, and pretending otherwise produces either diluted reviews everywhere or an unsustainable cost. Criticality is the variable that governs depth — it is settled before reading, from what the diff touches.

Criticality signals, in order of weight:

- The diff touches code exercised by test-cases marked `priority: critical` (front-matter of harness block B).
- It touches the domain layer, or a module designated as critical by an ADR.
- It touches authentication, authorization, a payment flow, a data migration, or a publicly exposed boundary (API, webhook, persisted format).
- It changes a contract consumed elsewhere: public signature, schema, event.

| Level | When | Review depth |
|--------|-------|---------------------|
| **Critical** | At least one strong signal above | Four angles in depth, context reading widened to the callers, mutation testing on the diff in phase 3 |
| **Standard** | The common case | Four angles, context read around the changes |
| **Low** | Docs, comments, tests alone, mechanical renaming, a version bump with no behavior change | Angles 1 and 2 as a targeted skim, angles 3 and 4 only if a signal shows up |

Announce the level retained and the signal that triggered it, in one line. The user can correct it; with no answer, carry on at the announced level — the checkpoint has to stay predictable for a pipeline.

**Two guardrails.** Criticality modulates depth, never scope: even at low level, a diff is read in full. And it never drops below "standard" when the diff touches security, whatever its size — a one-line fix in an access control is not a small diff.

## Phase 3 — The gauntlet

Before any reading, run the branch through what the machine can check on its own. The order is not a preference: it is what makes the review pay off.

### What the gauntlet is made of

Run, in this order, whatever exists in the project:

1. **The test suite** on the branch. A red suite makes everything else moot.
2. **The project's linter and formatter**, in their versioned configuration.
3. **The harness invariants** — `bash tools/harness/run_all.sh`, or the individual scripts in `tools/harness/`.
4. **The test-case bridge** — `check_test_coverage.*`, which flags documented behaviors whose test has disappeared.
5. **Mutation testing on the diff** — `run_mutation.* --scope diff` — at **critical** criticality only, and only if block D is installed. It is the one gauntlet check whose cost justifies being conditional.

Report for each of them: run / not available / failed, with the useful output.

### The stop rule

**If a gauntlet check fails at `error` severity, the review stops there.** Immediate NO-GO verdict, report limited to the Gauntlet section, no four-angle review.

The justification comes down to two points, and is worth stating to a user who would find this brutal: the fix is going to change the diff, so any reading done now will have to be redone; and the attention spent on code the machine already rejects is taken from the attention that will be missing later, on what the machine cannot see.

Two caveats:

- Failures at `warn` severity stop nothing. They are carried over as major or minor findings in phase 5, depending on their nature.
- If the user explicitly asks for the full review despite a red gauntlet, do it — flagging at the top of the report that the diff is about to change.

### Degraded mode — and why it makes the review heavier

If the project has neither a harness nor a usable test suite, say so clearly and carry on. But **the absence of a gauntlet raises the depth of the review instead of lowering it**: what the machine does not check, nobody checks. Concretely, a project without a harness moves up to the depth level immediately above the one settled in phase 2, and the "Checks not performed" section of the report becomes the most important part of the document.

This is also the right moment to mention that `codebase-harness` exists — once, without insisting, and never in place of the review that was asked for.

## Phase 4 — Four-angle review

Go through the diff with four distinct readings. A single pass that "looks at everything" misses things; four targeted passes with a precise question in mind are more reliable.

### Reading order: the what before the how

At **critical** criticality, first read the test-cases in `docs/business/test-cases/` that the diff touches — through the front-matter's `automated_test` field, which points at the modified tests. The code afterwards.

The reason: these files describe the expected behavior (context, action, expected result), and they are the only layer the review can validate against the real need. The code itself can only be validated against those files. Reading them after reading the code means reading them looking to confirm what has just been understood.

At standard criticality, skim them. At low criticality, ignore them unless the diff modifies them.

### Angle 1 — Bugs and regressions
The question: *what is going to break?*
- Unhandled edge cases (null/empty/zero, bounds, concurrency, encoding, time zones).
- Contract changes: signature, return format, error behavior — check the existing callers.
- Inverted logic, incomplete conditions, off-by-one, shared state mutated.
- Tests: are the added or modified behaviors covered by tests that test the behavior (and not the structure)? A modified behavior with no modified test is suspicious.

### Angle 2 — Security
The question: *what would an attacker, or hostile data, make of this?*
- Unvalidated inputs, injections (SQL, command, path, template), deserialization.
- Hardcoded secrets, verbose logs on sensitive data, widened permissions.
- AuthN/AuthZ: does every new entry point check who is calling, and with what right?
- Added dependencies: provenance and surface.

### Angle 3 — ADR / architecture compliance
The question: *does this change respect the recorded decisions?*
- Weigh every structural change against the ADRs and invariants loaded in Phase 1.
- Boundaries: dependencies between layers/modules that violate the allowed direction, domain logic leaking into the infrastructure or the UI.
- In degraded mode: consistency with the dominant patterns of the codebase (a third error-handling style is not an improvement).
- **Is the described behavior the right one?** Does a test-case the diff modifies, or adds, describe what the business really expects? A test-case that describes the wrong behavior is a **blocking** finding even if the code implements it perfectly and every test passes — it is the one error no mechanical check can catch. Weigh it against the `docs/business/` glossary and flag any vocabulary drift: a test-case that invents a term absent from the glossary often signals a misunderstanding of the need.

### Angle 4 — Debt and readability
The question: *will the next developer understand, and at what price?*
- Duplication introduced, accidental complexity, naming that betrays the intent or the business glossary.
- Dead code, TODOs with no ticket, comments that lie.
- Only flag here what carries a real maintenance cost — purely stylistic preferences a linter already handles do not deserve a finding.

## Phase 5 — Classify the findings

Every finding gets a severity. The definitions matter: they are what makes the verdict objective.

- **Blocking** — a defect that will cause an incident, an exploitable vulnerability, data corruption, or a head-on violation of an ADR. Merged as it stands, it will mean coming back in a hurry.
- **Major** — a real defect that degrades reliability, security or architecture, but with no immediate danger: a plausible edge case left unhandled, a modified behavior with no test, notable structural debt.
- **Minor** — a desirable improvement with no risk: readability, naming, small duplication.

When hesitating between two levels, retain the lower one but say so in the finding — the credibility of the review rests on blocking findings that really block. A review that cries wolf ends up ignored.

## Phase 6 — Report and verdict

### Verdict rule

- **NO-GO** if a gauntlet check fails at `error` severity (phase 3), OR if there is at least one **blocking** finding, OR if there are at least three **major** findings.
- **GO** otherwise. The remaining major findings (≤2) and minor ones are listed as debt to be dealt with, without blocking the merge.

A red gauntlet is a NO-GO **whatever the criticality**. Criticality modulates what gets read, never what gets waved through.

Apply the rule mechanically — judgment is exercised in the classification (phase 5), not in the verdict. That is what makes the checkpoint predictable for a pipeline.

### Report structure

Write the report to `.reviews/<branch>-<YYYY-MM-DD>.md` (create the folder if needed), then present its summary in conversation. **The report and the findings are written in the language of the target project**, not necessarily English: a project documented in French gets a review in French. The template below fixes the structure, not the wording. ALWAYS follow this structure:

```markdown
# Pre-merge review — <branch>
**Verdict: GO | NO-GO**
**Date**: … · **Base**: <base sha>..<head sha> · **Scope**: N files, ±N lines
**Criticality**: critical | standard | low — <signal that triggered it>

## Summary
2-4 sentences: nature of the change, general state, reason for the verdict.

## Gauntlet
| Check | Result |
|-------|----------|
| Test suite | OK / FAILED / not available |
| Lint / format | … |
| Harness invariants | … (failing INV-NNN, where applicable) |
| Test-case bridge | … |
| Mutation (diff) | … (score, threshold) — or "not applicable: criticality <level>" |
| Test-cases touched | N read / N skimmed / not applicable — list the files |

When stopping on a red gauntlet, stop after this section and say so explicitly: "Four-angle review not performed — the diff is about to change."

## Findings
### Blocking
- **[B1] <title>** — `file:line` · angle: <bugs|security|compliance|debt>
  Observation, concrete consequence, recommendation.
### Major
- **[M1] …** (same format)
### Minor
- **[m1] …** (same format, one-line recommendation)

## Checks not performed
Missing reference material (ADRs, invariants, business test-cases) and its impact on the review.

## Positive notes
1-3 notable points — an honest review also names what is well done.
```

Every finding cites the exact spot (`file:line`) and offers an actionable recommendation. A finding with neither a location nor a recommendation helps nobody.

### After the verdict

- **NO-GO on the gauntlet**: offer to move straight on to the fix through `plan-driven-dev`, then **restart the review from phase 3** — the diff having changed, the previous review no longer holds.
- **NO-GO on findings**: offer to move straight on to fixing the blocking and major findings through `plan-driven-dev`, with the report as input.
- **GO**: recall the remaining major findings, if any, so that they get tracked (ticket, `.plans/FEEDBACK.md`, or backlog depending on the project's practices).
