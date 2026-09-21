---
name: plan-driven-dev
description: Disciplined workflow for implementing a new feature OR fixing a bug in an existing code project. Forces a context-gathering phase before anything is written, produces a persistent plan validated step by step, applies behavior-driven TDD, and captures lessons learned. Use this skill whenever a user prompt looks like a code task in an existing project (keywords such as "implement", "add", "fix", "bug", "feature", "refactor", "change", "it should", or any multi-file code change request). The skill starts with an announcement and asks for validation before it applies — never invoke it silently. It loads the project's harness invariants at the context step and checks them inside the TDD loop, so that no violation is discovered at review time.
---

# plan-driven-dev

A disciplined workflow that forces the agent to understand before coding, to plan before acting, and to capture lessons once it is done. The **plan** is a file persisted on disk (`.plans/in-progress/<slug>.md`) that acts as a compass for the whole task.

---

## Step 0 — Announcement and validation

As soon as you identify a task that looks like a feature or a bug, **stop before acting** and offer the skill:

> *"This task looks like a feature/bug to implement in the project. I can apply the `plan-driven-dev` workflow (context gathering → validated plan → TDD → review). Do you want to follow it?"*

- If **no** → code in normal mode, do not apply what follows.
- If **yes** → move on to step 1.

Never skip this validation step, even if the user seems in a hurry.

All the questions the skill asks, and everything it writes to disk, are in the language of the target project — not necessarily the language of this file.

---

## Step 1 — Understand the context

Always in this order:

1. **Project overview**
   - Read `README.md` (and `CONTRIBUTING.md` if present)
   - Inspect the project tree (at least 2 levels deep)
   - Identify the language, the framework, the test runner, the linter/typechecker
   - Spot the visible conventions (folder layout, naming, style)

2. **Files directly involved + immediate dependencies**
   - Read the files the task obviously touches
   - Follow imports/exports to understand the coupling

3. **Usages of the symbol/function to modify**
   - Run a `grep` or a usage search before changing anything
   - Understand the potential impact of the changes

4. **Enforcement layer, if the project has one**
   - Read the "Harness" section of `AGENTS.md` and `docs/technical/invariants.md`
   - Inventory the scripts available in `tools/harness/` and know which one covers what
   - Note the invariants that apply to the files the task is going to touch — these are design constraints, not end-of-the-line checks
   - Carry those invariants into section 3 (Context) of the plan, with their ID. A plan that ignores an applicable invariant will produce code that fails the gauntlet.

   If the project has no harness, skip this — without mentioning it, it is not the subject of the task at hand.

**In parallel with all of the above**: read `.plans/FEEDBACK.md` if it exists. That file holds the lessons accumulated from previous tasks (project conventions, traps already hit, durable principles). **Apply those lessons** in everything that follows.

If `.plans/` does not exist yet, create the folder now (along with its `in-progress/`, `done/` and `aborted/` subfolders).

---

## Step 2 — Restate the goal → VALIDATION

Restate the goal in your own words, in 2-3 sentences. Present it to the user and **wait for explicit validation** before continuing.

Example: *"If I understand correctly: you want X because Y, and the expected outcome is Z. Does that work?"*

If the user corrects you → restate again until validated.

---

## Step 3 — Plan → VALIDATION

Create the file `.plans/in-progress/<slug>.md` (slug = short kebab-case identifier derived from the task, e.g. `add-user-export`, `fix-login-timeout`).

**The file must contain EXACTLY these 10 sections, in this order:**

```markdown
# <Task title>

## 1. Metadata
- **Type**: feature | bug
- **Date**: YYYY-MM-DD
- **Status**: in-progress

## 2. Goal
<the restatement validated at step 2>

## 3. Context
<summary of what step 1 uncovered: key files, conventions, constraints>

## 4. Expected behaviors
<bullet list of the behaviors to test — the backbone of the TDD loop>
<format per behavior: given <context>, when <action>, then <observable outcome> — **test boundary**: <use case / port / module API the test goes through>>
- Nominal: ...
- Edge case 1: ...
- Edge case 2: ...

## 5. Steps
<ordered checklist of the coding actions>
- [ ] Step 1: ...
- [ ] Step 2: ...

## 6. Risks & edge cases
<sensitive areas, what could break, hidden dependencies>

## 7. Out of scope
<what we are NOT doing — the anti-drift section>

## 8. Deviations
<empty for now — a log to fill in if we depart from the plan>

## 9. Self-review
<empty for now — filled in at closing>

## 10. Follow-up actions
<empty for now — filled in at closing>
```

The section titles above are the skeleton; the plan's prose is written in the language of the target project.

Once the file is written, present it to the user and **wait for validation**. If they ask for changes, update the file and ask for validation again.

---

## Step 4 — Risks & edge cases → VALIDATION

You have already filled in section 6 of the plan. At this step, **take a dedicated moment** to go through it with the user:

> *"Here are the risks and edge cases I identified [...]. Anything you would add or drop?"*

If the user adds items → update section 6 AND possibly section 4 (expected behaviors) of the plan.

Wait for explicit validation before moving on to writing code.

---

## Step 4.5 — "Plan ready to run" check → model decision

The plan has just been validated (steps 3 and 4). Before switching to execution mode, **assess objectively whether the plan is explicit enough to be run mechanically**, with no further judgment calls on substance.

Run section 5 (Steps) and section 4 (Expected behaviors) through these deterministic criteria:

- [ ] Every step names the files or symbols it touches (no "adapt the relevant service" without saying which one)
- [ ] Every step has a concrete action verb ("create", "rename", "add field X"), not a vague one ("handle", "process", "depending")
- [ ] Every expected behavior has an observable acceptance criterion (a test you could write, not "it should work fine")
- [ ] Every expected behavior states its test boundary (use case, port, module API — not "to be decided", and not an internal class by default)
- [ ] No step contains a TODO, "to be defined", "to be decided", "case by case"
- [ ] Dependencies between steps are clear (explicit ordering, no "in parallel or not, we will see")

**If every criterion is checked** → the plan can be run mechanically. Move on to step 5 without saying anything more to the user.

**If at least one criterion fails** → STOP. Lay out the finding for the user:

> *"The plan is validated on substance, but rereading it for execution I spot [N] areas that would need a judgment call along the way: [list the failed criteria with the relevant excerpt].*
>
> *Two options:*
> *(a) **Refine the plan here** until it can be run mechanically (I can do it now if you are on a strong model such as Opus).*
> *(b) **Switch to a strong model for execution** if you are currently on a lighter one (Sonnet/Haiku): open a new chat on Opus, and I will pick up at step 5 with the existing plan in `.plans/in-progress/<slug>.md`.*
>
> *Which do you prefer?"*

Important note: an agent cannot switch models by itself. It is up to the user to open a new session with the right model. The plan on disk exists precisely to make that switch seamless.

---

## Step 5 — Implementation with hybrid TDD

A **behavior-driven TDD** approach (tests exercise what the code does, not how — they must survive a refactoring).

**Before writing the first test, read the `behavior-driven-testing` skill and apply its doctrine** (test boundary, naming, assertions, use of mocks). The test boundaries are already fixed per behavior in section 4 of the plan — write each test at the stated boundary, not class by class.

How it goes:

1. **The expected behaviors are already listed** in section 4 of the plan (done at step 3).

2. **Nominal behavior first**:
   - Write the test (it must fail — *red*)
   - Check that it does fail (`npm test`, `pytest`, etc.)
   - Implement the minimum needed to make it pass (*green*)
   - Check that the test passes
   - Refactor if needed, keeping the test green

3. **Then each edge case, one at a time**:
   - Test (red) → implementation (green) → refactor
   - Only move to the next one once the previous one is green

4. **On every move to green, run the invariants that cover the files you touched** (the scripts spotted at step 1) before moving to the next behavior.

### A violated invariant is a failing test

Treat an invariant violation exactly like a failing test: you do not carry on, you fix it before moving forward. The reason is cost, not discipline — a violation caught two behaviors earlier is fixed in code you still have in mind; discovered at review time, it is fixed on a frozen diff, and forces the whole read-through to start over.

The linter's error message contains the remediation; read it before looking elsewhere. If the remediation does not apply, or if the invariant looks ill-suited to the case, **that is a deviation** in the sense of the rule below: stop, document in section 8, ask for validation. Never bypass an invariant silently, and never add an exclusion without validation.

**Mutation testing does not belong in this loop.** Its runtime cost is incompatible with a red-green-refactor cycle; its place is the gauntlet and CI, not here.

At every completed step of the plan (section 5), **tick the `[x]` box** in the file and give the user a **short summary** (1-2 sentences), then carry on without asking for validation.

### ⚠️ Deviation rule — MANDATORY STOP

**The moment you depart from the plan**, you stop immediately and ask the user for validation. Concrete cases:

- An unforeseen expected behavior emerges (e.g. "ah, we also need to handle the logged-out case")
- A step of the plan turns out to be unworkable as written
- You have to touch a file that was not identified during the context phase
- You change the planned technical approach
- Any other visible departure from the plan

For each deviation:
1. Document it in section 8 (Deviations) of the plan: *"[date/step] — Deviation: ... Reason: ... Decision taken: ..."*
2. Present the deviation to the user and ask for validation
3. Update the plan if needed (sections 5, 6, or others)
4. Do not resume until validated

---

## Step 6 — Closing

Once every step of section 5 is ticked:

1. **Check that the plan is complete**
   - All boxes `[x]`? If a step was not followed properly → explain it in section 8 (Deviations).

2. **Run the full suite, then the gauntlet**
   - The whole project's tests (`npm test`, `pytest`, `cargo test`, etc.)
   - Linter (`eslint`, `ruff`, etc.)
   - Typecheck (`tsc --noEmit`, `mypy`, etc.)
   - If the project has a harness: **all** the invariants (`bash tools/harness/run_all.sh`), not just the ones the task touched — a change can break a rule on a file everyone thought was out of scope — then the test-case bridge (`check_test_coverage.*`)
   - Everything must pass. On failure → go back and fix.

   This is exactly what `premerge-review` will replay in phase 3. Passing it here means no review will be stopped by a check the task could have resolved itself.

3. **Self-review of the diff**
   - Run a `git diff` (or equivalent) and read it actively
   - Run the tests you added through the "wrong direction signals" of the `behavior-driven-testing` skill (tests mirroring the implementation, mocks everywhere, a test with no clear behavior to protect...) — rewrite or delete the tests concerned before going further
   - Fill in section 9 of the plan with:
     - Risky areas of the diff (complex logic, shared state, security...)
     - Debt added (TODOs, hacks, shortcuts taken knowingly)
     - Points that deserve a second pair of eyes
   - Present this self-review to the user

4. **Propose follow-up actions**
   - Fill in section 10 of the plan:
     - Deferred refactorings to schedule
     - Tickets to open
     - Docs to update
     - Additional tests we chose not to write but that would be relevant
   - Present these proposals to the user

5. **Always ask**: *"Any lessons to capture in `.plans/FEEDBACK.md` so we keep improving on this project?"*
   - This question is asked **every single time**, even when everything went well.
   - Lessons must be **long-running** (durable, reusable principles), not specific to the task.
     - ✅ Good: *"In this project, tests sit next to the sources, not in `__tests__/`."*
     - ✅ Good: *"Always run `pnpm typecheck` before proposing a commit."*
     - ❌ Bad: *"We fixed a timeout bug on the login page."* (too specific)
   - If the user offers lessons → update `.plans/FEEDBACK.md` (create the file if it does not exist, otherwise append, following the existing structure). Write them in the language of the target project.
   - If the user says no → simply note *"No lesson added"* in section 9 of the plan.

6. **Final validation and moving the plan**
   - Update the status in section 1: `done` or `aborted`
   - Once the user gives final validation:
     - If the task was carried through → move the file to `.plans/done/<slug>.md`
     - If it was abandoned → move it to `.plans/aborted/<slug>.md`
   - Confirm to the user: *"Plan archived in `.plans/done/<slug>.md`."*

---

## Validation checkpoints at a glance

| # | Moment | Type |
|---|--------|------|
| 0 | Applying the skill | **Explicit** validation before continuing |
| 2 | Restating the goal | **Explicit** validation |
| 3 | Complete plan | **Explicit** validation |
| 4 | Risks & edge cases | **Explicit** validation |
| 4.5 | "Plan ready to run" check | **Silent if OK, stop + decision if KO** |
| 5 | Intermediate steps | **No validation**, a short summary is enough |
| 5 | Harness invariant violated | **Fix before moving forward**; if the remediation does not apply → deviation |
| 5 | Deviation detected | **Immediate stop + validation** |
| 6 | Closing (review, follow-up, lessons, archiving) | Final **explicit** validation |

---

## Notes on using this skill well

- **The plan is sacred**: it is the anchor that prevents drift. If you move away from the plan, either you update it with validation, or you do not do it.
- **The plan is the bridge between models**: it is designed so that an Opus planning session can be picked up by a Sonnet execution session. Step 4.5 is the guardrail that blocks that handover when the plan is not explicit enough.
- **The harness constrains the design, not just the result**: invariants are loaded at step 1 and checked inside the TDD loop, not discovered at closing. A plan written while ignoring an applicable invariant is a plan to redo.
- **An acknowledged dependency**: this skill relies on `behavior-driven-testing` for its test doctrine (steps 5 and 6). The test boundaries recorded in section 4 of the plan do, however, let an execution session test in the right place even when that skill is not loaded.
- **Tests are specifications**: behavior tests encode the expectations. They must read like documentation.
- **The self-review is honest**: if you took a shortcut or left debt behind, say so. Section 9 of the plan is there for that.
- **FEEDBACK.md is cumulative**: it grows over time. If a lesson becomes obsolete, offer to remove it rather than piling on.
- **No automatic trimming**: if the task is too small for this workflow, the user will say so at the announcement (step 0). Never decide to skip steps on your own.
