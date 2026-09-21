# Vocabulary

One concept, one word. Ten skills only read as one system if they name the same
thing the same way — a reader who meets "block B" here and "module B" there has
to stop and ask whether they are the same thing.

The **Use** column is binding. The **Not** column lists the words that would
otherwise creep in: plausible synonyms, not mistakes. Reaching for one of them
is a defect, not a variation.

A term is listed here because it is load-bearing across several skills. A word
used once, in one file, does not need an entry.

## Doctrine terms

| Use | Not | Why |
|---|---|---|
| block (A/B/C/D) | module, brick, component | The four harness building blocks |
| multiple-choice question | MCQ, poll, survey | Never abbreviated; "quiz" belongs to `code-assimilation-quiz` alone |
| business | functional | The documentation side: `docs/business/`, business glossary |
| domain | business | The DDD side: domain logic, domain model, domain expert |
| scope | perimeter, extent, coverage | What a piece of work covers |
| framing | scoping | The phase-0 activity, so that "scope" stays free for the noun |
| symptom | issue, smell, problem | The eight audit symptoms |
| gauntlet | pipeline, CI run, pre-checks | The mechanical barrier a branch clears before review |
| degraded mode | fallback, reduced mode, safe mode | A skill works without its reference material, and says so |
| doctrine | principles, guidelines, conventions | The rules every skill shares |
| invariant | rule, constraint, policy | An executable check, never a written wish |
| harness | framework, tooling, scaffolding | `tools/harness/` and what it enforces |
| enforcement | validation, gating, policing | Making a rule mechanical |
| doc-gardening | doc maintenance, upkeep, grooming | Block C |
| test-case bridge | test mapping, traceability matrix | Block B |
| verdict | decision, outcome, result | GO / NO-GO, nothing else |
| root cause | underlying issue, real problem | It is proven, never guessed |
| debt | cruft, legacy, mess | Technical debt |
| cold audit | baseline audit, fresh audit | Auditing a codebase you did not write |
| announcement | notice, heads-up, disclosure | A skill announces itself before applying |
| Mikado plan | dependency plan, unblocking plan | |
| worksite | workstream, chunk, batch | One unit of a Mikado plan |
| TDD loop | red-green cycle | |
| test boundary | test scope, seam | What a test is allowed to touch |
| trigger | keyword, hook | What makes a `description` fire |
| capture lessons learned | retrospective, post-mortem | `.plans/FEEDBACK.md` |
| supporting skill | helper, sub-skill, utility skill | Loaded by another skill |
| entry point | main skill, top-level skill | Invoked by the user |
| micro-iteration | small steps, baby steps | |
| reviewer | referee, checker, approver | |
| pre-merge review | code review | "code review" stays in the triggers, since that is what users type |
| angle | axis, dimension | The four review angles |
| criticality | severity, importance | critical / standard / low — what a change is worth, not what a finding is worth |
| blocking / major / minor | critical / high / low | Finding severities — deliberately different words from criticality, so the two never blur |
| drift | divergence, rot, staleness | Documentation or tests falling out of step |
| silent auto-fix | autofix | Always named to be forbidden |

## Front-matter contract

These keys are written by `codebase-cartographer` and read by `codebase-harness`
and `premerge-review`. They are a contract between skills, so they are spelled
one way only — and changing one is a breaking change for every project already
decorated.

```yaml
feature: cart
type: nominal              # nominal | error | edge-case
priority: critical         # critical | important | nice-to-have
automated_test: tests/test_cart.py::test_add_product   # or null
status: covered_ok         # covered_ok | covered_broken
```

## Spelling

American spelling throughout: behavior, prioritize, modeling, analyze, honor.
The skill identifier `behavior-driven-testing` settles it for the whole
repository.

## Language

Which language goes where — the repository versus what a skill writes into
someone else's project — is defined in [AGENTS.md](../AGENTS.md), not here.
