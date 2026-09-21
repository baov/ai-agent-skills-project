---
name: ai-code-remediation
description: Cold audit of a codebase written mostly by AI, followed by a remediation plan prioritized under a strict doctrine (TDD, Mikado method, micro-iteration). Use it SYSTEMATICALLY when the user asks to "audit this codebase", "size up the debt in this AI-generated project", "clean up a vibe-coded project", "figure out what the agents produced", "remediation plan", "clean up this code", or doubts the quality of a project written largely by agents — even when the word "audit" never comes up. Covers 8 categories of symptoms typical of AI-generated code. Do not confuse it with premerge-review (a diff before merge, not a whole codebase) or with codebase-cartographer (documentation, not diagnosis). May invoke ddd-advisor when the symptoms are really about domain design.
---

# AI Code Remediation

Cold audit of a codebase produced largely by AI agents, then a disciplined remediation plan. The goal is not to pass judgement on the code but to make it maintainable: name the symptoms, prove they are real, and organize their removal without a big bang.

**Cardinal rule: the audit is read-only.** Never fix anything while auditing, not even a trivial defect — fixing as you go destroys the overall picture and blends diagnosis into treatment. Remediation comes afterwards, plan in hand, and its execution is delegated to `plan-driven-dev`.

## The remediation doctrine

All remediation obeys three disciplines, none of them negotiable:

1. **Behavior-driven TDD** — no refactoring without a safety net. When the code to remediate has no tests (the usual case for generated code), start with characterization tests that capture the current behavior, flaws and all. Lean on the `behavior-driven-testing` skill for the strategy: test behaviors, not classes.
2. **Mikado method** — every remediation goal is broken down into a graph of prerequisites. Attempt the change; when it breaks, write down what is missing, revert, and go after the leaves of the graph first. Never leave an open worksite that does not compile.
3. **Micro-iteration** — steps so small they look ridiculous: each one leaves the codebase green, committable, shippable. A refactoring you cannot stop at any moment is a badly sliced refactoring.

## Phase 0 — Scoping

1. Set the scope: the whole repo, or a subset (a module, a service)? On a large codebase (>~50k lines), offer to split the audit by area rather than skim everything.
2. Collect the minimum context from the user — ask in the language of the project: how much of the code is generated, since when, what already hurts (recurring bugs, areas nobody dares touch, slow builds)? Lived pain drives the final prioritization.
3. Take stock of the available reference material: `AGENTS.md`, `docs/technical/` (ADRs, architecture), `docs/business/` (glossary, test cases), `docs/technical/invariants.md` and `tools/harness/`. **Degraded mode**: their absence does not block the audit, but it is a finding in itself — a generated codebase with no reference material drifts faster.

## Phase 1 — Gathering signals

Before any fine-grained analysis, measure whatever can be measured. Get the facts first, interpret second.

- **Structure**: size per module, depth of the directory trees, abnormally long files.
- **Duplication**: a clone detector when one is available (jscpd, PMD/CPD, simian), otherwise targeted manual sampling.
- **Tests**: test-to-code ratio, but above all a qualitative read of a sample — what do the assertions actually check?
- **Mutation score on a sample**, if and only if three conditions hold: the suite is green, a mutation tool exists for the stack, and a module carrying business rules can be isolated. A run on that single module is enough — the point is an order of magnitude, not an exhaustive measurement. Record the score, the scope and the runtime. If any condition is missing, do not push: this is one signal more, never a prerequisite of the audit.
- **Git history**: commit rhythm and size, bursts of generic messages ("fix", "update"), files rewritten over and over in a loop — the usual signatures of unsupervised agent sessions.
- **Dependencies**: manifests (package.json, pom.xml...), unused or redundant dependencies (three HTTP libraries, two mocking frameworks).

## Phase 2 — Symptom-by-symptom analysis

Go through the codebase with eight targeted readings. As in a review, a single pass that "looks at everything" misses what matters; each category comes with its own question.

### S1 — Systemic duplication
*Is the same knowledge written down several times?* Generated code duplicates instead of factoring out, because every generation session starts from scratch. Look for exact clones, but also for semantic ones: three email validators, two home-grown HTTP clients.

### S2 — Over-abstraction and over-engineering
*Are there layers nothing justifies?* Interfaces with a single implementation, patterns pasted on (a factory of factories, a strategy with one case), speculative genericity. AI reproduces "best practice" patterns with no real need behind them.

### S3 — Cosmetic tests
*Would the tests catch a real regression?* High coverage but hollow assertions, tests that verify mocks, a mechanical 1 test ↔ 1 class mapping, happy path only. Check against the `behavior-driven-testing` skill. The decisive test: mutate a business rule — does anything go red?

**This is the only one of the eight symptoms that comes with mechanical proof.** When the Phase 1 mutation score is available, use it instead of judgement: "43% of the mutants survive in the billing module" holds up against a team that disputes the audit, where "these tests look hollow to me" only opens a debate of opinion. Quote the score, the scope and the date.

Without a real run, mental mutation still works — but the finding is then phrased as a hypothesis to verify, not as an established fact. The doctrine of this phase is to **prove** symptoms; a proven symptom and a suspected one are not prioritized alike.

### S4 — Inconsistent conventions
*How many styles live side by side?* Heterogeneous naming, three ways of handling errors, mixed paradigms — the trace of successive generation sessions with no memory of one another. Inconsistency has a price: every area has to be read through a different lens.

### S5 — Dead code and phantom paths
*What serves no purpose?* Functions never called, features half wired up, orphaned config flags, files generated then abandoned. Generated dead code is dangerous: it looks intentional.

### S6 — Facade error handling
*What happens when things fail?* try/catch blocks that swallow, generic messages, errors logged then ignored, no strategy at all (retry? propagate? compensate?). Generated code handles the shape of an error, rarely its substance.

### S7 — Lying documentation and comments
*Is what is written true?* Comments that paraphrase the code, boilerplate docstrings, a README describing a project that no longer exists, examples that do not compile. Wrong docs are worse than no docs.

### S8 — Porous architectural boundaries
*Is the domain logic where it belongs?* Domain logic scattered across controllers and infrastructure, leaking layers, tight coupling between modules meant to be independent, an anemic model. **When this category dominates, invoke the `ddd-advisor` skill** to qualify the design symptoms and propose the target split.

For every symptom observed: cite precise occurrences (`file:line`), estimate the spread (isolated case, one area, systemic), and note the concrete consequence (why it costs, not just why it is ugly).

## Phase 3 — Audit report

Classify each finding:

- **Critical** — makes confident work impossible: an untestable area, unpredictable behavior, a vulnerability, possible corruption.
- **Structural** — debt that slows down every change: systemic duplication, porous boundaries, widespread cosmetic tests.
- **Cosmetic** — a real but local cost: naming, isolated dead code, stale docs.

Write the report to `.audit/<project>-<YYYY-MM-DD>.md`, then present the summary in conversation and **have the user validate the findings before moving on to the plan** — they know constraints the code does not show. The report is written in the language of the audited project, headings included; the template below fixes the structure, not the wording. ALWAYS follow this structure:

```markdown
# Cold audit — <project>
**Date**: ... · **Scope**: ... · **Reference material available**: ...

## Summary
Overall state in 3-5 sentences, and the 2-3 worksites that would change the most.

## Measured signals
Raw numbers from Phase 1.

## Findings by symptom
### S1 — Systemic duplication: <none | local | systemic>
- **[C1|St1|c1] <title>** — `file:line` · spread · concrete consequence
(... S2 to S8, same format; call out the healthy categories explicitly)

## Checks not performed
Missing reference material, areas not covered, tools unavailable.

## What works
What is sound and must be preserved through the remediation.
```

## Phase 4 — Remediation plan

Once the findings are validated, produce the plan in `.audit/<project>-remediation-<YYYY-MM-DD>.md`, in the same language as the report:

1. **Prioritize** by the cost-of-symptom / effort ratio, folding in the pain points voiced in Phase 0. Golden rule: **secure before transforming** — characterization tests for the critical areas come before any refactoring, that is the universal Mikado prerequisite.
2. **Cut into worksites**: each worksite deals with one symptom in one area, with its own small Mikado graph (goal, known prerequisites), an observable definition of done, and a target size of one working session at most.
3. **Order** the worksites so that each one leaves the codebase strictly better and green — never a worksite whose value depends on a future one.

### After the plan

Each worksite is executed through `plan-driven-dev`, the worksite becoming the input to its planning phase. Depending on the findings, also offer:
- `codebase-cartographer` when the lack of reference material is itself a finding — document before or during the remediation;
- `codebase-harness` to turn the remediation decisions into executable invariants, so that the agents who keep contributing do not reintroduce the symptoms just fixed. Two blocks answer symptoms from this list directly: block A (shape thresholds) contains S1 and S2, and block D (mutation testing) keeps S3 from coming back by pinning a threshold at the value measured during the audit.
