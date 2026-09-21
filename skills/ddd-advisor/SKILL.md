---
name: ddd-advisor
description: >
  DDD audit of an existing codebase AND Domain-Driven Design guidance while development is
  under way. Use as soon as the user mentions DDD, an "anemic domain model", "aggregates",
  "entities vs value objects", "bounded context", "ubiquitous language", "context map",
  "anti-corruption layer", or asks a domain modeling question ("where does this domain logic
  belong?", "is this an entity?", "how do I split this monolith into contexts?"). Use it ALSO
  when an audit or a remediation surfaces scattered domain logic, leaking layers, or tight
  coupling between subsystems — even when the word "DDD" is never said. The
  ai-code-remediation, codebase-cartographer and codebase-harness skills may invoke this skill
  to qualify design symptoms or to produce architecture invariants.
---

# DDD Advisor

Domain-Driven Design audit and guidance, built on Eric Evans's patterns (tactical **and**
strategic). Two modes, picked from the context of the request.

## Initial announcement

Like `plan-driven-dev`, this skill **announces itself before applying**: state the mode it
expects to use (audit or guidance) in a line or two and ask the user to confirm. Never run a
full audit without explicit agreement.

## Picking the mode

| Signal in the request | Mode |
|---|---|
| "audit this", "analyze this code", "why is this code hard to maintain", a codebase handed over | **Audit** |
| A one-off design question, a feature under way, a modeling choice | **Guidance** |
| Ambiguous | Ask with a multiple-choice question (2 options) |

---

## Audit mode

Cold analysis of a codebase to assess how well it lines up with DDD. Always in this order:

### 1. Prior context
- If `docs/business/` and `docs/technical/` exist (output of `codebase-cartographer`), read
  them first: the glossary is a candidate ubiquitous language, the ADRs are boundary decisions
  already taken.
- Otherwise, explore the codebase: folder structure, dependencies between layers, class names
  against the domain vocabulary.

### 2. Spotting the symptoms
Read `references/tactical.md` (Symptoms section) and `references/strategic.md` (Symptoms
section). For every symptom found, record: where it lives, how severe it is (blocking /
major / minor), which DDD pattern it violates.

The 8 families of symptoms to sweep through every time:
1. **Anemic domain model** — entities are bags of getters and setters, logic sits in "managers"
2. **Leaking layers** — domain logic in the UI, SQL in the domain
3. **Missing or bloated aggregates** — no clear root, or a root that swallows everything
4. **Entities and value objects confused** — identity created without need, or shared mutable values
5. **Diverging language** — the code does not match the domain experts' or the glossary's vocabulary
6. **Unruly data access** — direct queries bypassing every repository
7. **Tangled contexts** — a single contradictory "big model", overlapping terms
8. **Core domain drowned** — the differentiating logic indistinguishable from generic code

### 3. Reporting back
- A short prose summary, then a table of findings (symptom, location, severity, pattern).
- **Diagrams**: Mermaid for structural views (the current context map, dependencies between
  layers, proposed aggregate boundaries); ASCII for one-off inline illustrations. Always show
  the CURRENT state and the TARGET state when proposing a change.

The report is written in the target project's language, like everything else this skill
produces outside this repository.

### 4. Interactive recommendations
Offer the possible remediations as a **prioritization multiple-choice question** (5 options
max, decreasing severity). The user picks what to dig into; only then detail the remediation
plan for the chosen option, with a target diagram.

### 5. Persistence (closing multiple-choice question, mandatory)
Always finish with a multiple-choice question (shape and degraded mode: see
`clarify-with-choices`):
- **Nothing** — the audit stays conversational
- **`docs/technical/ddd-audit.md`** — a full dated report (create `docs/technical/` if it is
  missing; if the folder came from the cartographer, follow its format and reference the
  report in `AGENTS.md`)
- **ADR** — one ADR per structural decision retained, under `docs/technical/adr/`

---

## Guidance mode

One-off support for a design decision. Load the relevant reference **before** answering:

| Kind of question | Reference |
|---|---|
| Entity or value object? Where does this logic go? Aggregate boundary? Factory or constructor? | `references/tactical.md` |
| Split into contexts? Integrate two systems? Relationship between teams? What to distill? | `references/strategic.md` |

Rules for guidance mode:
- Answer with a **clear-cut recommendation** plus the pattern that justifies it, never a
  neutral catalog of options.
- Draw a diagram as soon as the answer involves 3 or more related elements (ASCII when simple,
  Mermaid when structural).
- When the decision hinges on a fact only the user knows (for instance: "do both teams report
  to the same management?" for customer/supplier vs conformist), ask THE discriminating
  question as a multiple-choice question rather than laying out every branch.
- Stay concrete: restate the user's question in their own domain, not in generic banking or
  aviation examples. Questions are asked in the target project's language.

---

## Fitting into the ecosystem

- **codebase-cartographer**: consume `docs/business/glossary.md` as a proxy for the ubiquitous
  language; a gap between code and glossary is an audit finding in its own right.
- **plan-driven-dev**: any remediation retained that touches code across several files must be
  handed over as a `plan-driven-dev` task (never implement straight from the audit).
- **codebase-harness**: for every boundary confirmed (layers, contexts, aggregates), offer to
  turn it into an executable invariant (for instance: "the domain layer imports neither the UI
  nor the infrastructure", "only aggregate roots have a repository").
- **behavior-driven-testing**: aggregate invariants are behaviors to test first.

## Guardrails

- Do not apply DDD to everything: when the subdomain is generic or trivial (plain CRUD), say
  so out loud — that is the doctrine itself (distillation, "do not try to apply DDD to
  everything").
- Vocabulary: use the canonical DDD pattern names (repository, factory, value object, bounded
  context...). The ubiquitous language, on the other hand, belongs to the target project's
  domain: if that domain speaks French, its terms stay French — translating them would break
  the very principle. Pattern names and domain words are two different things.
- An audit NEVER modifies code. Neither does guidance mode — it recommends.
