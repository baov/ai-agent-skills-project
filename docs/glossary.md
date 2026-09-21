# Translation glossary

Frozen vocabulary for the French-to-English switch of this repository.

This is the only file allowed to contain French. Every term below is binding:
a translation that uses a different English word for a listed French term is a
defect, not a variation. The check that enforces it:

```bash
tools/check-glossary.sh
```

## Doctrine terms

| French | English | Note |
|---|---|---|
| brique (A/B/C/D) | block | Harness building blocks |
| QCM | multiple-choice question | Never abbreviated to MCQ |
| métier (documentation) | business | `docs/business/`, business glossary |
| métier (DDD context) | domain | domain logic, domain model, domain expert |
| périmètre | scope | |
| symptôme | symptom | |
| gauntlet | gauntlet | Unchanged |
| agrégat | aggregate | Standard DDD term |
| anémique | anemic | Standard DDD term |
| mode dégradé | degraded mode | |
| doctrine | doctrine | Unchanged |
| pont test-cases | test-case bridge | |
| verdict | verdict | Unchanged |
| cause racine | root cause | |
| dette | debt | technical debt |
| audit à froid | cold audit | Assumed calque, kept for brevity |
| signalement | announcement | A skill announces itself before applying |
| plan Mikado | Mikado plan | |
| boucle TDD | TDD loop | |
| déclencheur | trigger | |
| capitaliser les leçons | capture lessons learned | |
| skill d'appui | supporting skill | |
| point d'entrée | entry point | |
| micro-itérativité | micro-iteration | |
| relecteur | reviewer | |
| invariant | invariant | Unchanged |
| harness | harness | Unchanged |
| enforcement | enforcement | Unchanged |
| doc-gardening | doc-gardening | Unchanged |
| revue pré-merge | pre-merge review | |
| auto-fix silencieux | silent auto-fix | |
| axe (de revue) | angle | The four review angles, not "axis" |
| criticite | criticality | critique/standard/faible -> critical/standard/low |
| chantier (Mikado) | worksite | |
| derive | drift | |
| frontiere de test | test boundary | |
| cadrage | framing | "scope" is reserved for perimetre |
| bloquant / majeur / mineur | blocking / major / minor | Finding severities |
| priorite: critique (front-matter) | priority: critical | Enum: critical / important / nice-to-have |
| type: erreur (front-matter) | type: error | Enum: nominal / error / edge-case |

## Renamed paths

| Before | After |
|---|---|
| `skills/clarify-with-qcm/` | `skills/clarify-with-choices/` |
| `references/brique-a-invariants.md` | `references/block-a-invariants.md` |
| `references/brique-b-pont-test-cases.md` | `references/block-b-test-case-bridge.md` |
| `references/brique-c-doc-gardening.md` | `references/block-c-doc-gardening.md` |
| `references/brique-d-mutation.md` | `references/block-d-mutation.md` |
| `ddd-advisor/references/strategique.md` | `references/strategic.md` |
| `ddd-advisor/references/tactique.md` | `references/tactical.md` |
| `docs/metier/` (produced) | `docs/business/` |
| `docs/technique/` (produced) | `docs/technical/` |

## Spelling

American spelling throughout: behavior, prioritize, modeling, analyze, honor.
The skill identifier `behavior-driven-testing` settles it for the whole
repository.

## Two languages, two scopes

- **Repository language: English.** Everything versioned *here* — skill bodies,
  descriptions, error messages, script comments and identifiers.
- **Output language: the target project's.** Everything a skill writes
  *elsewhere* — documentation, plans, review reports, audits, and the questions
  it asks. A skill documenting a French codebase produces French documentation.
