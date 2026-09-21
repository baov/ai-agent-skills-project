# Workflows — enchaînement des skills

Neuf skills, deux familles, et une règle : les artefacts circulent, les skills ne s'appellent pas dans le vide.

## Deux familles

**Points d'entrée** — invoqués par une demande de l'utilisateur.

| Skill | Déclencheur | Produit |
|---|---|---|
| `codebase-cartographer` | « documente le projet » | `docs/business/`, `docs/technical/`, section dans `AGENTS.md` |
| `codebase-harness` | « mets en place les garde-fous » | `tools/harness/`, `docs/technical/invariants.md` |
| `ai-code-remediation` | « audite ce codebase » | `.audit/<projet>-<date>.md` + plan de remédiation |
| `systematic-debugging` | « pourquoi ça plante » | Cause racine prouvée (pas de fichier) |
| `plan-driven-dev` | « implémente », « corrige » | `.plans/done/<slug>.md`, `.plans/FEEDBACK.md` |
| `premerge-review` | « relis ma branche » | `.reviews/<branche>-<date>.md` + verdict |
| `code-assimilation-quiz` | « fais-moi un quiz » — **jamais automatique** | Rien (apprentissage) |

**Skills d'appui** — chargés par un autre skill, rarement demandés directement.

| Skill | Chargé par | Rôle |
|---|---|---|
| `behavior-driven-testing` | `plan-driven-dev` (étapes 5-6), `ai-code-remediation` (S3) | Doctrine de test |
| `ddd-advisor` | `ai-code-remediation` (quand S8 domine) | Qualification de conception |
| `clarify-with-choices` | `codebase-cartographer`, `codebase-harness`, `ddd-advisor` | Forme des QCM de validation, et mode dégradé si l'agent hôte n'a pas d'outil de question |

---

## Scénario 1 — Nouvelle feature sur un projet outillé

Le cas nominal, celui pour lequel la chaîne a été pensée.

```
plan-driven-dev
  étape 1   lit invariants.md + tools/harness/ + .plans/FEEDBACK.md
  étape 3   plan validé, invariants applicables notés en section 3
  étape 5   TDD ; les invariants tournent à chaque passage au vert
            └─ charge behavior-driven-testing pour les frontières de test
  étape 6   suite complète + run_all.sh + check_test_coverage
       ↓
premerge-review
  phase 2   criticité déterminée
  phase 3   gauntlet — vert par construction si l'étape 6 a été faite
  phase 4   test-cases d'abord (si critique), puis les quatre axes
  phase 6   verdict GO/NO-GO
       ↓
code-assimilation-quiz   (optionnel, sur demande explicite)
```

**Le point qui compte** : l'étape 6 de `plan-driven-dev` rejoue exactement le gauntlet de la phase 3 de `premerge-review`. Une revue arrêtée par un check mécanique signale que l'étape 6 a été bâclée.

---

## Scénario 2 — Bug en production

```
systematic-debugging      diagnostic uniquement, jusqu'à la cause prouvée
       ↓                  ne jamais corriger ici
plan-driven-dev           la cause racine devient l'entrée de l'étape 2
       ↓
premerge-review           criticité relevée d'office si le bug touche la sécurité
```

**L'erreur classique** : corriger pendant le diagnostic. La séparation existe parce qu'un correctif appliqué avant la preuve masque souvent le vrai problème.

---

## Scénario 3 — Codebase vibe-codé qu'on récupère

```
ai-code-remediation
  phase 1   signaux mesurés, dont le score de mutation sur échantillon
  phase 2   les huit symptômes
            └─ si S8 domine → ddd-advisor
            └─ si S3 suspecté → le score de mutation le prouve ou l'infirme
  phase 4   plan découpé en chantiers
       ↓
codebase-cartographer     si l'absence de doc est elle-même un finding
       ↓
plan-driven-dev           un passage par chantier
       ↓
codebase-harness          en dernier — les décisions de remédiation
                          deviennent des invariants exécutables
```

**Pourquoi le harness arrive à la fin** : il fige des règles. Les figer avant de savoir lesquelles comptent produit un harness qu'on désactive au premier build rouge. L'audit fournit aussi la baseline de mutation.

---

## Scénario 4 — Outiller un projet sain

```
codebase-cartographer     ADR, architecture, test-cases
       ↓
codebase-harness
  brique A   les ADR deviennent des linters — commencer en `warn`
  brique B   front-matter sur les test-cases
  brique D   mutation testing — périmètre calibré sur les `priorite: critique`
  brique C   doc-gardening
```

L'ordre A → B → D → C est imposé : D cible son périmètre à partir des test-cases priorisés par B.

**Deux semaines en `warn` avant de passer en `error`.** Un linter bloquant sur du code existant non conforme arrête toute l'équipe.

---

## Scénario 5 — « Mes tests ne servent à rien »

```
behavior-driven-testing   diagnostic de doctrine : que testent-ils vraiment ?
       ↓
codebase-harness          brique D seule — mesurer avant de conclure
```

Un score de mutation transforme une impression en chiffre. Si les tests sont effectivement creux, la réécriture passe par `plan-driven-dev`, un comportement à la fois.

---

## Circulation des artefacts

C'est ce tableau qui fait la cohérence de l'ensemble : chaque fichier produit par un skill est lu par un autre.

| Artefact | Écrit par | Lu par |
|---|---|---|
| `docs/business/glossary.md` | cartographer | premerge-review (axe 3), ddd-advisor |
| `docs/business/test-cases/**` | cartographer | harness (B décore), premerge-review (phase 4) |
| `docs/technical/adr/**` | cartographer | harness (A extrait), premerge-review (axe 3) |
| `docs/technical/invariants.md` | harness | plan-driven-dev (étape 1), premerge-review (phase 1) |
| `tools/harness/*` | harness | plan-driven-dev (étape 5), premerge-review (phase 3) |
| `.plans/FEEDBACK.md` | plan-driven-dev | plan-driven-dev (étape 1, tâches suivantes) |
| `.reviews/<branche>.md` | premerge-review | plan-driven-dev (entrée du correctif) |
| `.audit/<projet>.md` | ai-code-remediation | plan-driven-dev (un chantier par passage) |

**Mode dégradé** : chaque skill fonctionne sans ces fichiers, mais le dit. Dans `premerge-review`, l'absence de référentiel **augmente** la profondeur de revue au lieu de la réduire.

---

## Erreurs de chaînage

| Ce qu'on fait | Pourquoi c'est raté |
|---|---|
| `premerge-review` pour apprendre le code | C'est `code-assimilation-quiz`. La revue cherche des défauts, pas à enseigner. |
| `premerge-review` sur un codebase entier | C'est `ai-code-remediation`. La revue travaille sur un diff. |
| `ai-code-remediation` sur une branche | Inverse du précédent. |
| `codebase-harness` avant `codebase-cartographer` | Marche, mais l'agent devra poser à la main toutes les questions d'architecture. |
| Corriger pendant `systematic-debugging` | Le skill s'arrête à la cause prouvée, par construction. |
| `code-assimilation-quiz` déclenché tout seul | Interdit : uniquement sur demande explicite. |
| Mutation testing dans la boucle TDD | Trop lent. Sa place est au gauntlet et en CI. |

---

## Un principe transversal

Trois skills modulent leur profondeur sur la **criticité** : `systematic-debugging`, `premerge-review`, `codebase-harness` (brique D).

La criticité module ce qu'on regarde et à quelle profondeur — jamais le périmètre, jamais le seuil de blocage. Un diff est lu en entier quelle que soit sa criticité, et un gauntlet rouge reste un NO-GO.
