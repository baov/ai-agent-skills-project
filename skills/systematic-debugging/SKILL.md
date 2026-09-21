---
name: systematic-debugging
description: Rigorous bug diagnosis methodology — find and prove the root cause before any fix. Use SYSTEMATICALLY whenever unexpected behavior has to be explained: "why isn't this working", "weird bug", "it crashes", "regression", "flaky behavior", "it worked before", "error I don't understand", "investigate", "diagnose", or any fix request whose cause is not yet identified and proven. Covers the DIAGNOSIS phase only: minimal reproduction, falsifiable hypotheses, bisection, targeted instrumentation, proof of the root cause. Once the cause is proven, the fix is delegated to plan-driven-dev (or to the pipeline in progress). Do not use if the cause is already known and proven — go straight to the fix in that case.
---

# Systematic Debugging

Disciplined bug diagnosis. Goal: identify the **root cause** and **prove** it, never "make the symptom go away". The fix itself is out of scope: it is handed over to `plan-driven-dev` (or to the workflow in progress) once the cause is established.

## Initial announcement

Before applying this skill, announce it to the user:

> I suggest applying the `systematic-debugging` skill: minimal reproduction, explicit hypotheses, investigation tracked in `.debug/`, and proof of the root cause before any fix. OK?

Phrase that message in the target project's language, as with every question this skill puts to the user.

Do not invoke it silently. If the user declines, follow their instructions.

## Non-negotiable principles

1. **No reliable repro, no debugging.** Never move on to the hypothesis phase without a deterministic reproduction (or a statistically characterized one for flaky bugs).
2. **No code change without a written hypothesis.** Every investigation follows from a hypothesis stated BEFOREHAND, with a falsifiable prediction.
3. **No fixing at random.** A change that "makes the test pass" without explaining *why the bug was happening* is not a diagnosis — it is debt. Go back to the hypotheses.
4. **Correlation ≠ causation.** "It started after deployment X" is a clue, not a conclusion. The root cause has to be demonstrated by a complete mechanism: *because A, then B, hence symptom C*.
5. **One hypothesis at a time.** Never test two hypotheses in the same experiment — the result is uninterpretable.
6. **Targeted instrumentation, no printf everywhere.** Every instrumentation point answers one precise question coming from a hypothesis. Clean up the instrumentation at the end of the investigation.
7. **Everything is tracked.** The investigation lives in `.debug/INVESTIGATION-<slug>.md`, not in the agent's head. A human (or another agent) has to be able to pick the investigation up cold.

## Workflow

### Phase 0 — Framing

Establish with the user, and record in the investigation file:
- **Observed symptom** (factual: exact error message, value obtained) vs **expected behavior**
- **Context**: environment, version, frequency (systematic / flaky), scope (one user / everyone)
- **Timeline**: since when? what changed recently? (`git log`, deployments, config, dependencies)
- **Criticality**: production on fire, or developer comfort? (sets how deep an investigation is acceptable)

Create `.debug/INVESTIGATION-<slug>.md` as early as this phase (template below). Write it in the target project's language.

### Phase 1 — Minimal reproduction (GATE)

Build the smallest and fastest reproduction possible:
- Ideally: **a failing automated test**, expressed in terms of behavior. If the `behavior-driven-testing` skill is available, apply it to word that test (use case, not implementation detail). Otherwise, minimum rule: the test describes the expected behavior from the caller's point of view, and its name states that behavior.
- Failing that: a reproducible command/script documented in the investigation file.
- For flaky bugs: characterize the rate (e.g. "fails ~3 times out of 20 runs") and try to make it deterministic (fixed seed, concurrency control, simulated clock) before going further.

**Gate**: as long as there is no repro, the only allowed activity is finding one. If reproducing turns out to be impossible after reasonable effort, say so explicitly to the user and propose an observability strategy (logs/metrics to add in order to capture the next occurrence) rather than speculating.

### Phase 2 — Fact gathering

Gather without interpreting: full stack traces, relevant logs, data state, diff of recent changes (`git log -p` over the suspect area), dependency versions. In the investigation file, keep the **facts** (observed) separate from the **interpretations** (assumed).

### Phase 3 — Explicit hypotheses

List the plausible hypotheses in the investigation file. Every hypothesis MUST have:
- **Statement**: the assumed mechanism ("the cache returns a stale entry because the key does not include the tenant")
- **Falsifiable prediction**: "if that is true, then logging the cache key will show the same key for two different tenants"
- **Test cost**: fast/medium/expensive — to prioritize
- **Status**: to test / confirmed / refuted

Prioritize by probability × speed of verification. Test the cheap hypotheses first, even the less likely ones.

### Phase 4 — Investigation

For each hypothesis, in priority order:
1. Design the experiment that tests the prediction (targeted instrumentation, breakpoint, query, exploratory unit test)
2. Run it, record the raw result in the investigation file
3. Verdict: confirmed or refuted. **A refuted hypothesis is progress** — record it, do not delete it.

When the search space is large, bisect:
- **In history**: `git bisect` with the repro as the oracle (automate it when possible: `git bisect run`)
- **In the code**: disable/short-circuit half of the suspect pipeline, then narrow down
- **In the data**: halve the input set until the minimal triggering input

If every hypothesis is refuted: go back to phase 2 (facts are missing), widen the scope, or challenge a certainty ("what am I holding as true without having checked it?").

### Phase 5 — Proof of the root cause

The cause is established once all three conditions hold:
1. **Complete mechanism** explained: causal chain from the cause to the symptom, with no "magic" link
2. **Positive demonstration**: the bug can be triggered at will by activating the cause, and made to disappear by neutralizing it (minimal toggle, not a real fix)
3. **The mechanism explains EVERY observed fact** — including the frequency (why flaky?), the timeline (why now?) and the scope (why only those cases?). One unexplained fact = incomplete investigation, or several bugs.

Record the conclusion in the investigation file.

### Phase 6 — Handoff

Produce a handoff summary (dedicated section of the investigation file), written in the target project's language:
- Root cause and mechanism (3-5 lines)
- The repro / the failing test (reference to the test file)
- Possible fix approaches with their trade-offs (without picking one)
- Related regression risks spotted during the investigation

Then ask the user: "Root cause proven. Shall I move on to the fix via `plan-driven-dev`?" (or hand back to the pipeline in progress, e.g. a post-analysis human checkpoint). Clean up any temporary instrumentation before the handoff.

## Investigation file template

Structure stays as below; headings and content go in the target project's language.

```markdown
# Investigation — <short title>
Date: <date> | Status: in progress | cause proven | abandoned

## Framing
- Observed symptom:
- Expected behavior:
- Context / frequency / scope:
- Timeline & recent changes:

## Reproduction
- Repro: <test or command> | Deterministic: yes/no (rate if no)

## Facts
- [F1] ...
- [F2] ...

## Hypotheses
| # | Statement | Falsifiable prediction | Cost | Status |
|---|-----------|------------------------|------|--------|
| H1 | ... | ... | fast | refuted |
| H2 | ... | ... | medium | confirmed |

## Investigation log
- <date/time> H1: <experiment> → <raw result> → verdict

## Root cause
- Mechanism:
- Demonstration:
- Facts explained: F1 ✔ F2 ✔

## Handoff
- Fix approaches & trade-offs:
- Related risks:
```

## Anti-patterns to refuse explicitly

- **Shotgun debugging**: changing several things "to see what happens"
- **Superstition fix**: restart / clear the cache / reorder, without explaining why that changes anything
- **Concluding from correlation**: "it must be yesterday's deployment", with no demonstration
- **Patching the symptom**: catching the exception, adding an `if null`, widening a timeout — without understanding the origin
- **Carrying on without a repro**: piling up unverifiable hypotheses

If the user asks for one of these shortcuts, point it out once, explain the risk, then follow their decision (they are the one arbitrating criticality vs rigor).
