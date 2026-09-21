---
name: codebase-harness
description: Couche d'enforcement déterministe pour qu'un codebase reste cohérent quand des agents IA y contribuent. Quatre briques optionnelles proposées via QCM : (A) invariants exécutables — ADR, règles d'architecture et seuils de forme (taille, complexité) transformés en linters custom pre-commit/CI ; (B) pont test-cases ↔ tests réels — front-matter YAML + script de couverture ; (D) mutation testing — vérifie que les tests non relus attraperaient réellement un bug ; outil détecté selon la stack, périmètre calibré par criticité ; (C) doc-gardening — tâche planifiée (CI ou ordonnanceur de l'hôte) qui signale les dérives. Artefacts dans `tools/harness/` et `docs/technique/invariants.md`. À utiliser quand l'utilisateur veut un "harness pour agents", "rendre les ADR exécutables", des "linters custom", de l'"architecture enforcement" (ArchUnit, dependency-cruiser), du "mutation testing", ou dit que "ses tests ne testent rien". Marche mieux après `codebase-cartographer`, tourne aussi en mode dégradé.
compatibility: Nécessite git et un shell. La brique C suppose en plus un ordonnanceur — CI planifiée (GitHub Actions, pipeline GitLab), tâche planifiée de l'agent hôte, ou cron.
---

# Codebase Harness

Met en place une couche d'enforcement déterministe pour qu'un codebase reste cohérent quand des agents IA (ou des humains pressés) y contribuent. La documentation seule ne suffit pas : il faut des checks mécaniques qui empêchent les dérives avant qu'elles n'arrivent en main.

## Doctrine

**Le harness n'existe pas pour compenser la vitesse des agents. Il existe pour l'encadrer.** Quand une machine écrit le code, la boucle de contrôle devient plus stricte, pas moins — c'est précisément parce que le débit augmente que les garde-fous doivent être mécaniques plutôt que déclaratifs. Un harness traité comme un simple outil de lint rate son objet.

Trois conséquences qui gouvernent tout ce qui suit :

1. **Un check non exécuté n'est pas un check.** Une règle écrite dans un ADR ou un AGENTS.md est une intention ; un script qui sort en code 1 est une contrainte. Le rôle de ce skill est de convertir les premières en secondes.
2. **Ce qui n'est pas relu doit être vérifié autrement.** Plus la relecture humaine se raréfie sur un artefact, plus la vérification mécanique de cet artefact doit être forte. C'est la raison d'être de la brique D : des tests que personne ne relit ont besoin d'un contrôle qui ne soit pas la relecture.
3. **La profondeur se calibre sur la criticité, pas sur la disponibilité de l'outil.** Empiler tous les checks sur toutes les tâches est facile à automatiser et rarement justifié. Chaque brique doit pouvoir être restreinte à un périmètre.

> **Skill compagnon** : ce skill marche mieux après [`codebase-cartographer`](#) qui produit les ADR, l'architecture documentée et les test-cases. Mais il peut aussi tourner en mode dégradé sur un projet sans cette doc — il s'adapte à ce qu'il trouve et pose les questions manquantes directement.

## Les quatre briques

Le skill propose quatre briques indépendantes. L'utilisateur peut en activer une, plusieurs, toutes ou aucune. Chacune est proposée via QCM au début du run.

| Brique | Produit | Source d'inspiration |
|--------|---------|----------------------|
| **A — Invariants exécutables** | `docs/technique/invariants.md` + linters dans `tools/harness/` + intégration pre-commit/CI | ADR, contraintes d'architecture, seuils de forme, conventions de l'équipe |
| **B — Pont test-cases ↔ tests réels** | Front-matter YAML dans chaque test-case.md + `tools/harness/check_test_coverage.*` | Test-cases existants + suite de tests automatisés |
| **D — Mutation testing** | Config de l'outil détecté + `tools/harness/run_mutation.*` + seuils par périmètre dans `invariants.md` | Suite de tests existante, périmètres critiques du domaine |
| **C — Doc-gardening automatisé** | Tâche planifiée (cadence configurable) qui produit un rapport sans rien modifier | Doc existante + checks A, B et D |

**Les briques B et D répondent à deux questions différentes.** B vérifie qu'un test *existe* pour un comportement documenté. D vérifie qu'un test *attraperait un bug* s'il y en avait un. Un test-case peut être `covered` au sens de B et protégé par un test qui n'assert rien — seule D voit ce cas. Les activer ensemble est le cas nominal ; activer B seule laisse un angle mort connu.

---

## Vue d'ensemble du workflow

```
[Première exécution]
1. Détection du contexte (cartographer a-t-il tourné ? quels artefacts trouve-t-on ?)
2. QCM de scoping : quelles briques activer parmi A, B, D, C ?
3. Pour chaque brique activée :
   a. Analyse + QCM ciblé
   b. Production des artefacts (md, scripts, config, tâche planifiée)
   c. Proposition d'intégration (pre-commit, CI) — JAMAIS appliquée sans validation
4. Mise à jour de la section "Harness" dans AGENTS.md (avec QCM)

[Ré-exécution : mode mise à jour]
1. Inventaire des briques déjà installées (présence de tools/harness/, invariants.md, config mutation, tâche planifiée)
2. Pour chaque brique : exécution des checks existants + analyse du delta
3. Rapport consolidé (violations nouvelles, invariants obsolètes, test-cases dérivés, régression du score de mutation)
4. QCM groupé pour proposer les ajustements (jamais rien d'auto)
```

**Principe central** : ce skill ne modifie jamais le code applicatif. Il produit uniquement des fichiers de doc, des scripts dans `tools/harness/`, et des configs d'intégration (proposées, pas écrites). Les violations détectées sont remontées à l'humain, jamais corrigées en silence.

---

## Étape 1 — Détection du contexte

Avant tout, l'agent inspecte le projet pour comprendre ce qu'il a à sa disposition. En parallèle :

- `docs/technique/architecture.md` existe-t-il ? Contient-il une section « Contraintes structurelles » ?
- `docs/technique/adr.md` et `docs/technique/adr/*.md` existent-ils ? Si oui, lire tous les ADR pour extraire les décisions structurantes.
- `docs/metier/test-cases/**/*.md` existe-t-il ? Compter, et noter si un front-matter YAML est déjà présent.
- `tools/harness/` existe-t-il déjà ? (signature : ce skill a déjà tourné)
- `docs/technique/invariants.md` existe-t-il ? (idem)
- Inspecter la stack pour choisir le bon type de linter : Python (AST), JS/TS (ESLint custom ou dependency-cruiser), JVM (ArchUnit), Go (analyzer custom), Rust (clippy + custom lints), etc.
- Repérer l'outillage de mutation déjà présent, en cherchant dans les manifestes et les configs de la stack détectée (ex. `pitest` dans `pom.xml`/`build.gradle(.kts)`, `@stryker-mutator/*` dans `package.json`, `stryker.conf.*`, `infection.json`, `setup.cfg`/`pyproject.toml` pour mutmut) ainsi que les dossiers de rapports déjà versionnés. Noter aussi le runner de tests et, si possible, la durée d'une exécution complète de la suite — c'est la donnée qui conditionne la brique D.
- Inspecter la CI : `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, etc. pour savoir où proposer l'intégration.
- Inspecter pre-commit : `.pre-commit-config.yaml`, `lefthook.yml`, `.husky/`, `package.json` (husky), etc.

Si le skill détecte que `tools/harness/` ou `invariants.md` existent déjà, il bascule en **mode mise à jour** (voir section dédiée). C'est idempotent.

Si la doc cartographer n'a pas tourné (pas d'ADR, pas de test-cases), l'agent le signale et explique :

> « Je peux quand même mettre en place une couche harness, mais j'aurai besoin de te poser les questions sur les règles d'architecture directement. Si tu préfères, lance d'abord `codebase-cartographer` pour structurer la doc, puis reviens ici. Que choisis-tu ? »

QCM avec deux options : « continuer en mode dégradé » / « stop, je vais d'abord lancer cartographer ».

---

## Étape 2 — QCM de scoping

L'agent présente les trois briques avec un résumé d'une phrase chacune et demande lesquelles activer. Format type :

```
Trois briques disponibles :

A — Invariants exécutables
    Transforme tes règles d'architecture et tes ADR en linters custom qui
    tournent en pre-commit/CI. Coût d'installation : moyen (1 script par règle).
    Coût de maintenance : faible. Recommandé si > 2 développeurs ou si des
    agents IA contribuent.

B — Pont test-cases ↔ tests réels
    Ajoute un front-matter YAML à tes test-cases métier et produit un script
    qui vérifie qu'ils pointent vers des tests qui existent vraiment. Coût
    d'installation : faible. Coût de maintenance : nul. Recommandé si tu
    as déjà des test-cases sous docs/metier/test-cases/.

D — Mutation testing
    Injecte des bugs artificiels dans le code et vérifie que tes tests les
    attrapent. C'est le seul check qui mesure la *qualité des assertions*
    plutôt que l'exécution de lignes. Coût d'installation : faible (config).
    Coût d'exécution : ÉLEVÉ — un run complet se compte en dizaines de
    minutes. Coût de maintenance : faible. Recommandé si des agents écrivent
    des tests que personne ne relit ligne à ligne.

C — Doc-gardening automatisé
    Crée une tâche planifiée hebdo (ou autre cadence) qui re-vérifie la doc
    et les checks au fil du temps, et te remonte un rapport. Aucun fichier
    modifié sans validation. Recommandé si le projet évolue régulièrement.
```

QCM multi-sélection (doctrine dans `clarify-with-qcm`) : « Lesquelles activer ? A / B / D / C / toutes / aucune ». Si « aucune » → fin du skill avec message « Compris, rien à faire. ».

L'ordre d'exécution est imposé : **A → B → D → C**. B s'appuie potentiellement sur la stack détectée à A ; D s'appuie sur B pour cibler les périmètres critiques (les test-cases marqués `priorite: critique` sont le meilleur candidat de départ) ; C s'appuie sur A, B et D pour savoir quoi monitorer.

Si l'utilisateur active D sans B, le signaler une fois : le périmètre de mutation devra être défini à la main faute de test-cases priorisés. Ce n'est pas bloquant.

---

## Étapes 3 à 6 — Les briques

Chaque brique retenue au QCM de scoping se déroule dans son propre fichier.
**Ne lire que celles qui ont été activées** : l'ordre d'exécution imposé reste
A → B → D → C.

| Brique | Procédure détaillée |
|---|---|
| A — Invariants exécutables | [`references/brique-a-invariants.md`](references/brique-a-invariants.md) |
| B — Pont test-cases ↔ tests réels | [`references/brique-b-pont-test-cases.md`](references/brique-b-pont-test-cases.md) |
| D — Mutation testing | [`references/brique-d-mutation.md`](references/brique-d-mutation.md) |
| C — Doc-gardening automatisé | [`references/brique-c-doc-gardening.md`](references/brique-c-doc-gardening.md) |

Chaque fichier suit la même structure : pré-requis et arbitrage du coût,
production des artefacts, proposition d'intégration pre-commit/CI. Aucun n'écrit
quoi que ce soit sans validation explicite.

## Étape 7 — Mise à jour d'AGENTS.md

L'agent ajoute (ou met à jour) une section dans `AGENTS.md`. **Toujours avec QCM avant d'écrire**.

**Compatibilité Claude Code.** `AGENTS.md` est lu nativement par la plupart des agents, mais pas par Claude Code, qui cherche `CLAUDE.md`. Si le projet n'a pas de `CLAUDE.md`, ou en a un qui n'importe pas `AGENTS.md`, proposer par QCM d'y ajouter la ligne d'import :

```markdown
@AGENTS.md
```

Une seule source de vérité, lisible par tous. Ne jamais dupliquer le contenu dans les deux fichiers : deux copies divergent.


### Contenu de la section

```markdown
## Harness

Ce projet a une couche d'enforcement déterministe générée par le skill `codebase-harness`. Les agents doivent respecter ces règles.

### Invariants exécutables

Les règles d'architecture sont rendues exécutables par des scripts dans `tools/harness/`. Liste complète et statuts dans [docs/technique/invariants.md](docs/technique/invariants.md).

- Avant tout commit, lancer : `bash tools/harness/run_all.sh` (ou les scripts individuels)
- Les messages d'erreur de chaque linter incluent la remédiation à appliquer — lis-les avant de chercher ailleurs
- Pour comprendre un invariant sans le vérifier : `python tools/harness/check_<sujet>.py --explain`

### Pont test-cases ↔ tests réels

Chaque scénario sous `docs/metier/test-cases/` porte un front-matter YAML qui pointe vers son test automatisé. Le script `tools/harness/check_test_coverage.*` vérifie la cohérence.

- Ajout d'un test-case → remplir le front-matter (champ `automated_test` ou `status: pending`)
- Ajout d'un test → vérifier qu'il a un test-case correspondant, sinon en créer un

### Mutation testing

Les tests écrits sans relecture humaine ligne à ligne sont contrôlés par mutation testing. Un test vert n'est pas une preuve : seul un mutant tué l'est.

- Périmètre et seuils : voir l'invariant correspondant dans [docs/technique/invariants.md](docs/technique/invariants.md)
- Lancer localement : `bash tools/harness/run_mutation.sh --scope diff`
- Un mutant survivant se traite en ajoutant un test qui exprime le **comportement** non protégé — jamais un test écrit pour tuer le mutant. Si le mutant ne correspond à aucun comportement qui compte, l'exclure explicitement en config avec un commentaire de justification
- Ne jamais baisser un seuil pour faire passer la CI : c'est le signal qu'un comportement a perdu sa protection

### Doc-gardening

Une tâche planifiée tourne périodiquement et signale les dérives. Quand le rapport remonte des violations, traiter ça comme un signal d'amélioration du repo (ajouter une doc, préciser un invariant, etc.), pas comme du bruit.
```

> Les sous-sections présentes dépendent des briques activées. Si seule la brique B est active, n'inclure que la sous-section « Pont test-cases ↔ tests réels ».

**Coexistence avec `codebase-cartographer`** : la section « Documentation du projet » (générée par cartographer) n'est jamais touchée par ce skill. Si seule la section « Harness » manque, l'ajouter après la section Documentation.

---

## Mode mise à jour (ré-exécution du skill)

Quand le skill détecte qu'il a déjà tourné (présence de `tools/harness/` ou de `docs/technique/invariants.md`), il bascule automatiquement en mode mise à jour.

### Inventaire

- Lister les invariants définis (parser `invariants.md`) et leur statut (`actif`, `déprécié`)
- Lister les scripts dans `tools/harness/` et identifier ceux liés à un invariant
- Lister les test-cases avec front-matter et noter leur `status`
- Relever la baseline de mutation et le seuil actuel dans `invariants.md`, et vérifier que la config de l'outil et le wrapper `run_mutation.*` sont toujours en place et cohérents avec la stack
- Vérifier si une tâche planifiée existe pour ce projet : job planifié en CI (`.github/workflows/`, *Schedules* GitLab), tâche de l'ordonnanceur de l'hôte, ou entrée cron

### Exécution des checks

L'agent exécute (via bash) tous les scripts de `tools/harness/` et collecte la sortie. Pour chaque invariant :

| Résultat | Action |
|----------|--------|
| Pass | RAS |
| Fail nouveau (code passait avant, ne passe plus) | Signaler, proposer remédiation |
| Fail déjà connu | Rappeler (sans bruit) |
| Invariant obsolète (la couche/le pattern n'existe plus) | Proposer passage à `déprécié` |
| Invariant manquant (nouvel ADR sans invariant) | Proposer création |

Pour les test-cases :

| Résultat | Action |
|----------|--------|
| `pending` dont le test existe maintenant | Proposer `covered` |
| `covered_broken` (test disparu ou échoue) | Proposer enquête |
| Test orphelin (nouveau test sans test-case) | Proposer création du test-case |

Pour le mutation testing (si la brique D est installée) :

| Résultat | Action |
|----------|--------|
| Score stable ou en hausse | RAS — proposer un relèvement du seuil si l'écart à la baseline dépasse 5 points |
| Score en baisse sous le seuil | Signaler, lister les mutants survivants nouveaux, proposer enquête |
| Nouveau module dans le périmètre critique, non couvert par la config | Proposer extension du périmètre |
| Run qui dépasse largement sa durée habituelle | Signaler — souvent le signe d'un test lent ajouté, ou d'un périmètre qui a grossi sans qu'on le décide |

**Ne jamais proposer d'aligner le seuil sur un score en baisse.** Un seuil qu'on abaisse pour repasser au vert transforme un signal en décoration.

### Rapport consolidé

```
## Harness — rapport

INVARIANTS (5 actifs)
  - INV-001 (isolation domaine) : 2 violations nouvelles
      src/domaine/checkout.py:42 import requests → remédiation: déplacer en application/
      src/domaine/checkout.py:67 import boto3 → idem
  - INV-002 à INV-005 : OK

  Candidat à dépréciation :
  - INV-003 (statut REST JSON) : plus de routes REST dans le code (ADR-0007 a remplacé)

COUVERTURE TEST-CASES (12 fichiers)
  - 10 covered_ok, 1 pending → 1 covered_ok (un test pending a été implémenté)
  - 1 covered_broken : panier/suppression-bulk.md → test absent depuis le commit abc1234

MUTATION (périmètre: domaine critique)
  - score 74.1% (baseline 78.4%, seuil 75%) → SOUS LE SEUIL
  - 3 mutants survivants nouveaux, tous dans src/domaine/panier/Remise.kt
      → introduits par la branche feat/remises-cumulables

DOC-GARDENING
  - Tâche planifiée active (hebdo lundi 9h) — dernier run il y a 3 jours, OK
```

QCM consolidé pour valider l'ensemble des actions proposées.

### Si rien n'a changé

Si tous les checks passent et qu'il n'y a aucun delta, l'agent dit simplement « Harness OK, rien à faire » et termine. Pas de tool call superflu.

---

## Conseils transverses

**Démarrer petit**. Ne pas essayer de rendre exécutables 20 règles d'un coup. Commencer par 2-3 invariants qui font vraiment mal quand ils sont violés (ex : couche isolée, secret en clair, console.log en prod). Étendre ensuite.

**Sévérité `warn` au démarrage**. Un linter qui passe en `error` sur du code existant non-conforme va bloquer toute l'équipe. Recommander `warn` pendant 1-2 semaines, le temps de nettoyer les violations existantes, puis passer à `error`.

**Messages d'erreur actionnables**. C'est la règle d'or. Un message qui dit « unauthorized import » est inutile pour un agent. Un message qui dit « déplace ce import vers `src/application/` et expose un port côté domaine — voir INV-001 » est utilisable. Tous les starters fournis suivent cette règle.

**Pas d'auto-fix silencieux**. Même si l'agent est sûr qu'il sait corriger une violation, il ne le fait jamais sans QCM. Le harness produit un signal ; l'humain ou l'agent applique le fix dans un commit visible.

**Boucle de feedback**. Quand un agent bute sur un invariant, traiter ça comme un signal : la remédiation est-elle assez claire ? l'invariant est-il trop strict ? la doc manque-t-elle d'un exemple ? Mettre à jour `invariants.md` et le message d'erreur du linter en conséquence. C'est ce qui fait évoluer le harness avec le projet.

**Garde la confiance**. Un harness qui produit trop de faux positifs sera ignoré. Si une règle déclenche systématiquement des faux positifs, c'est un bug du linter, pas du code. Corriger le linter en priorité.

**Le coût d'exécution est une contrainte de conception, pas un détail**. Un check juste mais trop lent finit désactivé, ce qui est pire qu'un check absent — il laisse croire à une protection qui n'existe plus. Pour la brique D en particulier : mieux vaut un mutation testing exigeant sur 15 % du code, qui tourne vraiment, qu'un run global que l'équipe met en `continue-on-error` et cesse de lire.

**Ne jamais empiler par réflexe**. Toutes les briques ne se justifient pas sur tous les projets. Un utilitaire interne sans enjeu de fiabilité n'a pas besoin de mutation testing ; un moteur de calcul de facturation en a besoin plus que de doc-gardening. Quand l'utilisateur active tout par défaut, poser la question de la criticité réelle avant d'installer.

**Ce qui n'est plus relu doit être davantage vérifié**. Quand un projet bascule vers un mode où les agents écrivent le code et les tests unitaires sans relecture ligne à ligne, ce n'est pas le moment d'alléger le harness — c'est le moment où il devient la seule protection restante. Le signal à surveiller : si les invariants sont en `warn` depuis des mois et que personne ne lit les rapports, la protection est nominale.

---

## Référence

- `references/brique-a-invariants.md`, `-b-pont-test-cases`, `-c-doc-gardening`, `-d-mutation` — la procédure détaillée de chaque brique. Ne lire que celles retenues au QCM de scoping : c'est tout l'intérêt du découpage
- `references/templates.md` — six sections : (1) `invariants.md` et ses règles de rédaction, (2) front-matter des test-cases, (3) entrée type d'un seuil de mutation avec baseline, (4) prompt de la tâche planifiée, (5) section Harness d'`AGENTS.md`, (6) conventions d'écriture des scripts et règle d'or des messages
- `references/harness-starters/` — implémentations de référence. Contient `README.md` (le contrat commun à tous les scripts) et `check_test_coverage.py` (brique B, complet et générique). Volontairement dépourvu de linters par stack : le skill les génère à partir des conventions, ce qui vieillit moins vite qu'un dossier figé
- `references/harness-starters/mutation/` — optionnel. La brique D **génère** son wrapper et sa config à partir de la stack détectée (voir `references/brique-d-mutation.md`, sections 5.3.a et 5.3.b) ; ce dossier ne sert qu'à figer des exemples déjà éprouvés en interne, jamais de source de vérité. Le contrat de sortie normalisée décrit en 5.3.b de ce fichier prime sur tout starter qui s'en écarterait.
