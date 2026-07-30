---
name: codebase-harness
description: Couche d'enforcement déterministe pour qu'un codebase reste cohérent quand des agents IA y contribuent. Quatre briques optionnelles proposées via QCM : (A) invariants exécutables — ADR, règles d'architecture et seuils de forme (taille, complexité) transformés en linters custom pre-commit/CI ; (B) pont test-cases ↔ tests réels — front-matter YAML + script de couverture ; (D) mutation testing — vérifie que les tests non relus attraperaient réellement un bug ; outil détecté selon la stack, périmètre calibré par criticité ; (C) doc-gardening — scheduled-task qui signale les dérives. Artefacts dans `tools/harness/` et `docs/technique/invariants.md`. À utiliser quand l'utilisateur veut un "harness pour agents", "rendre les ADR exécutables", des "linters custom", de l'"architecture enforcement" (ArchUnit, dependency-cruiser), du "mutation testing", ou dit que "ses tests ne testent rien". Marche mieux après `codebase-cartographer`, tourne aussi en mode dégradé.
---

# Codebase Harness

Met en place une couche d'enforcement déterministe pour qu'un codebase reste cohérent quand des agents IA (ou des humains pressés) y contribuent. La documentation seule ne suffit pas : il faut des checks mécaniques qui empêchent les dérives avant qu'elles n'arrivent en main.

## Doctrine

**Le harness n'existe pas pour compenser la vitesse des agents. Il existe pour l'encadrer.** Quand une machine écrit le code, la boucle de contrôle devient plus stricte, pas moins — c'est précisément parce que le débit augmente que les garde-fous doivent être mécaniques plutôt que déclaratifs. Un harness traité comme un simple outil de lint rate son objet.

Trois conséquences qui gouvernent tout ce qui suit :

1. **Un check non exécuté n'est pas un check.** Une règle écrite dans un ADR ou un CLAUDE.md est une intention ; un script qui sort en code 1 est une contrainte. Le rôle de ce skill est de convertir les premières en secondes.
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
| **C — Doc-gardening automatisé** | Scheduled-task (cadence configurable) qui produit un rapport sans rien modifier | Doc existante + checks A, B et D |

**Les briques B et D répondent à deux questions différentes.** B vérifie qu'un test *existe* pour un comportement documenté. D vérifie qu'un test *attraperait un bug* s'il y en avait un. Un test-case peut être `covered` au sens de B et protégé par un test qui n'assert rien — seule D voit ce cas. Les activer ensemble est le cas nominal ; activer B seule laisse un angle mort connu.

---

## Vue d'ensemble du workflow

```
[Première exécution]
1. Détection du contexte (cartographer a-t-il tourné ? quels artefacts trouve-t-on ?)
2. QCM de scoping : quelles briques activer parmi A, B, D, C ?
3. Pour chaque brique activée :
   a. Analyse + QCM ciblé
   b. Production des artefacts (md, scripts, config, scheduled-task)
   c. Proposition d'intégration (pre-commit, CI) — JAMAIS appliquée sans validation
4. Mise à jour de la section "Harness" dans CLAUDE.md (avec QCM)

[Ré-exécution : mode mise à jour]
1. Inventaire des briques déjà installées (présence de tools/harness/, invariants.md, config mutation, scheduled-task)
2. Pour chaque brique : exécution des checks existants + analyse du delta
3. Rapport consolidé (violations nouvelles, invariants obsolètes, test-cases dérivés, régression du score de mutation)
4. QCM groupé pour proposer les ajustements (jamais rien d'auto)
```

**Principe central** : ce skill ne modifie jamais le code applicatif. Il produit uniquement des fichiers de doc, des scripts dans `tools/harness/`, et des configs d'intégration (proposées, pas écrites). Les violations détectées sont remontées à l'humain, jamais corrigées en silence.

---

## Étape 1 — Détection du contexte

Avant tout, Claude inspecte le projet pour comprendre ce qu'il a à sa disposition. En parallèle :

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

Si la doc cartographer n'a pas tourné (pas d'ADR, pas de test-cases), Claude le signale et explique :

> « Je peux quand même mettre en place une couche harness, mais j'aurai besoin de te poser les questions sur les règles d'architecture directement. Si tu préfères, lance d'abord `codebase-cartographer` pour structurer la doc, puis reviens ici. Que choisis-tu ? »

QCM avec deux options : « continuer en mode dégradé » / « stop, je vais d'abord lancer cartographer ».

---

## Étape 2 — QCM de scoping

Claude présente les trois briques avec un résumé d'une phrase chacune et demande lesquelles activer. Format type :

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
    Crée une scheduled-task hebdo (ou autre cadence) qui re-vérifie la doc
    et les checks au fil du temps, et te remonte un rapport. Aucun fichier
    modifié sans validation. Recommandé si le projet évolue régulièrement.
```

QCM multi-sélection via `ask_user_input_v0` : « Lesquelles activer ? A / B / D / C / toutes / aucune ». Si « aucune » → fin du skill avec message « Compris, rien à faire. ».

L'ordre d'exécution est imposé : **A → B → D → C**. B s'appuie potentiellement sur la stack détectée à A ; D s'appuie sur B pour cibler les périmètres critiques (les test-cases marqués `priorite: critique` sont le meilleur candidat de départ) ; C s'appuie sur A, B et D pour savoir quoi monitorer.

Si l'utilisateur active D sans B, le signaler une fois : le périmètre de mutation devra être défini à la main faute de test-cases priorisés. Ce n'est pas bloquant.

---

## Étape 3 — Brique A : Invariants exécutables

### 3.1 — Extraction des règles candidates

Claude relit (s'ils existent) :
- `docs/technique/architecture.md` section « Contraintes structurelles »
- Tous les ADR `docs/technique/adr/*.md` — en particulier la section « Décision »
- `README.md` racine pour des indices de conventions (« no direct DB calls in handlers », etc.)

Si la doc cartographer n'a pas tourné, Claude demande directement à l'utilisateur :

> « Quelles règles de code/architecture aimerais-tu rendre testables ? Exemples : couches isolées, interdiction d'imports d'I/O dans une couche, conventions de nommage de fichiers, types de retour obligatoires sur les fonctions publiques, etc. »

### 3.1 bis — Les seuils de forme sont des invariants comme les autres

Aux règles issues des ADR, ajouter systématiquement une famille de candidats souvent oubliée parce qu'elle passe pour cosmétique : **taille de fonction, taille de fichier, complexité cyclomatique, profondeur d'imbrication, nombre de paramètres**.

La justification n'est pas esthétique, et il faut la formuler comme telle à l'utilisateur : **le code emmêlé dégrade la productivité des agents**. Un agent qui retravaille une fonction de 300 lignes à complexité élevée y fait des passes répétées, produit des diffs larges, casse des choses adjacentes, et échoue parfois à démêler ses propres nœuds — l'humain doit alors reprendre la main, ce qui annule le gain de la délégation. Contraindre la forme en amont coûte moins cher que de démêler en aval.

C'est un argument mesurable, pas un principe : si l'utilisateur doute, proposer de démarrer en `warn` et d'observer sur deux semaines la corrélation entre violations et tours d'agent nécessaires.

Seuils de départ raisonnables, à ajuster au projet plutôt qu'à imposer :

| Métrique | Seuil `warn` | Outil typique |
|----------|--------------|---------------|
| Lignes par fonction | 40 | Checkstyle/Detekt (JVM), ESLint `max-lines-per-function` (JS/TS) |
| Complexité cyclomatique | 10 | PMD/Detekt, ESLint `complexity` |
| Profondeur d'imbrication | 4 | Detekt, ESLint `max-depth` |
| Paramètres par fonction | 5 | Detekt, ESLint `max-params` |

Ne pas réinventer ces checks : quand le linter standard de la stack sait déjà le faire, l'invariant consiste à **activer et configurer la règle existante**, et `invariants.md` documente le seuil et sa raison d'être. N'écrire un script custom dans `tools/harness/` que si aucun outil de la stack ne couvre la règle.

### 3.1 ter — Consolidation

Claude consolide une liste de **règles candidates** (5-15 max), avec pour chacune :
- Énoncé en une phrase
- Source (ADR-XXXX, section d'architecture.md, ou « énoncé par l'utilisateur »)
- Mécanisme de check proposé (AST Python, ESLint custom, ArchUnit, dependency-cruiser, test custom)
- Estimation de complexité (faible / moyenne / forte)

### 3.2 — QCM de sélection

```
J'ai extrait N règles candidates :

INV-CANDIDATE-1 : "La couche `src/domaine/` n'importe aucun module d'I/O"
    Source : ADR-0003 (architecture hexagonale)
    Check proposé : AST Python custom (faible complexité)

INV-CANDIDATE-2 : "Tout endpoint REST a un schéma de réponse Pydantic"
    Source : architecture.md section "Contraintes structurelles"
    Check proposé : AST Python custom (moyenne)

INV-CANDIDATE-3 : "Pas de TODO dans le code main"
    Source : convention équipe (énoncé utilisateur)
    Check proposé : grep + regex (faible)

...
```

QCM : « Lesquelles veux-tu rendre exécutables ? ». Options : tout / sélection / aucune.

Pour chaque règle validée, second QCM : « Sévérité ? `error` (CI bloquante) ou `warn` (signal seulement) ? ». Recommandation par défaut : démarrer en `warn` pendant 1-2 semaines, puis passer en `error` quand les violations existantes sont à zéro.

### 3.3 — Production des artefacts

Pour chaque invariant validé, Claude produit :

**a) Une entrée dans `docs/technique/invariants.md`** suivant le template (voir `references/templates.md` section 1) :
- ID `INV-NNN` (numérotation immuable, jamais re-numérotée)
- Statut `actif`
- Énoncé, source, lien vers le script, sévérité, remédiation actionnable, exemple de violation et de correctif

**b) Un script de check dans `tools/harness/check_<sujet>.{py,js,kt,go}`** suivant les conventions :
- Sortie format `path:line: [INV-NNN] message — remédiation`
- Mode `--explain` qui décrit la règle sans rien vérifier
- Mode `--root <chemin>` pour pouvoir tester localement
- Code de sortie : 0 OK, 1 violation `error`, 2 violations `warn`
- Voir `references/harness-starters/README.md` pour le contrat que tout script doit respecter, et `references/templates.md` § 6 pour les conventions de message

**c) Une remontée vers les ADR concernés** : si la règle vient d'un ADR, Claude propose d'ajouter dans l'ADR le champ « Invariants exécutables associés : INV-NNN ». Toujours via QCM avant modification.

### 3.4 — Proposition d'intégration

Claude présente à l'utilisateur le snippet à ajouter à pre-commit / CI, et demande explicitement la permission de l'écrire :

```yaml
# Exemple pre-commit
- id: harness-invariants
  name: Harness — vérification des invariants
  entry: python tools/harness/check_layer_isolation.py
  language: system
  pass_filenames: false
```

```yaml
# Exemple GitHub Actions
- name: Harness checks
  run: |
    python tools/harness/check_layer_isolation.py
    python tools/harness/check_api_typing.py
```

Le skill ne modifie pas ces fichiers sans validation. Si l'utilisateur dit non, les scripts existent quand même dans `tools/harness/` — il peut les lancer à la main.

---

## Étape 4 — Brique B : Pont test-cases ↔ tests réels

### 4.1 — Pré-requis

Le skill cherche `docs/metier/test-cases/**/*.md`. Si rien n'existe, il signale à l'utilisateur :

> « Aucun test-case trouvé sous docs/metier/test-cases/. Lance d'abord `codebase-cartographer` ou crée toi-même quelques fichiers, puis reviens ici. »

Et passe à la brique suivante (ou termine).

### 4.2 — Décoration des test-cases

Pour chaque test-case existant, Claude ajoute un front-matter YAML en tête de fichier :

```yaml
---
feature: panier
type: nominal              # nominal | erreur | edge-case
priorite: critique         # critique | importante | nice-to-have
automated_test: tests/test_panier.py::test_ajout_produit   # ou null
status: covered            # covered | pending | manual
---
```

Claude tente de **pré-remplir** chaque champ :
- `feature` : déduit du nom du dossier parent
- `type` et `priorite` : déduits du titre et du contenu du test-case (ou marqués « à valider »)
- `automated_test` : recherche par nom dans les fichiers de test du projet (heuristique : nom du test-case en snake_case ↔ nom du test)
- `status` : `covered` si un test automatisé a été trouvé, `pending` sinon

Pour chaque test-case ambigu (plusieurs matches possibles, ou aucun), QCM groupé en fin d'analyse :

```
J'ai décoré N test-cases. M ont besoin de ton aide :

panier/ajout-produit.md :
  Le test est-il (a) tests/test_panier.py::test_add_item
                 (b) tests/integration/test_cart.py::test_add
                 (c) aucun de ces deux (pending)
                 (d) il existe mais je ne l'ai pas trouvé — je vais le chercher
```

### 4.3 — Production du script de vérification

Claude écrit `tools/harness/check_test_coverage.*` — une implémentation de référence complète et sans dépendance est fournie dans `references/harness-starters/check_test_coverage.py`. Elle ne lit que du markdown et des chemins, donc elle convient telle quelle à la plupart des projets quelle que soit leur stack ; l'adapter surtout au niveau des globs de recherche des tests. Le script :

- Parcourt `docs/metier/test-cases/**/*.md`
- Parse chaque front-matter YAML
- Classe en `covered_ok` / `covered_broken` / `pending` / `manual`
- Liste les tests orphelins (existant dans le code mais sans test-case associé)
- Sort 0 si tout va bien, 1 si au moins un `covered_broken`, 2 si uniquement des warns

### 4.4 — Intégration

Comme pour la brique A : Claude propose le snippet pre-commit/CI et demande la permission de l'ajouter. Par défaut, recommandation : `warn` (exit 2 toléré) au début, `error` (exit 1 bloquant) quand `covered_broken` est à zéro.

---

## Étape 5 — Brique D : Mutation testing

### 5.0 — Ce que cette brique résout

Les briques A et B contrôlent le code et l'existence des tests. Aucune ne contrôle **la valeur des tests eux-mêmes**. C'est l'angle mort qui compte le plus quand des agents écrivent la suite de tests : un test peut s'exécuter, être vert, couvrir 100 % des lignes et n'asserter rien d'utile.

Le mutation testing répond exactement à ça : l'outil introduit des altérations mécaniques du code (inverser une condition, remplacer un `+` par un `-`, supprimer un appel, retourner `null`), relance les tests, et vérifie qu'au moins un test échoue. Un mutant **tué** signifie que les tests protègent ce comportement. Un mutant **survivant** signifie qu'on peut casser cette ligne sans qu'aucun test ne s'en aperçoive.

À dire explicitement à l'utilisateur, parce que c'est la confusion la plus fréquente : **le score de mutation n'est pas un coverage amélioré**. Le coverage mesure quelles lignes s'exécutent ; le score de mutation mesure si les assertions valent quelque chose. C'est la métrique que le coverage prétend être sans jamais l'être — et la seule qui justifie de ne pas relire un test à la main.

> Cohérence avec `behavior-driven-testing` : ce skill ne fixe pas d'objectif chiffré comme but en soi. Le score de mutation est un **outil de diagnostic** — un mutant survivant est une question (« quel comportement n'est pas protégé ici ? »), pas une case à cocher. Un seuil en CI sert à empêcher une régression, pas à faire monter un chiffre.

### 5.1 — Pré-requis et arbitrage du coût

Avant toute proposition, Claude vérifie trois choses :

1. **Une suite de tests existe et passe.** Le mutation testing sur une suite rouge n'a aucun sens. Si des tests échouent, le signaler et s'arrêter là.
2. **La durée d'une exécution complète de la suite.** C'est le facteur multiplicatif : un run de mutation exécute la suite (partiellement) une fois par mutant. Mesurer si possible, sinon demander.
3. **Le périmètre candidat.** Le run global est presque toujours le mauvais choix.

Claude présente ensuite l'arbitrage honnêtement, sans vendre la brique :

```
Ta suite tourne en ~4 min. Un run de mutation sur l'ensemble du code
prendrait vraisemblablement plusieurs heures — inexploitable en CI de MR.

Trois périmètres possibles :

1. Domaine critique uniquement (recommandé)
   Les packages/modules qui portent les règles métier. Typiquement
   10-20% du code, l'essentiel du risque. Run estimé : 10-20 min.
   → CI nocturne ou pre-merge sur les MR qui touchent ce périmètre.

2. Incrémental sur le diff
   Ne mute que les fichiers modifiés par la branche. Run court et
   proportionné, mais ne protège pas contre l'érosion du reste.
   → CI de MR.

3. Global
   Couverture complète, run long. Réservé à une exécution
   hebdomadaire ou mensuelle.
   → scheduled-task, jamais en CI bloquante.
```

QCM : périmètre 1 / 2 / 3 / combinaison (typiquement 2 en MR + 1 en nocturne) / abandonner la brique D.

**« Abandonner » est une réponse légitime et doit être présentée comme telle.** Si la suite est lente, instable, ou si la CI est déjà saturée, le mutation testing est un mauvais investissement et Claude le dit franchement plutôt que d'installer un check qui sera désactivé au premier build rouge.

### 5.2 — Choix du périmètre critique

Si l'utilisateur retient le périmètre 1, Claude propose une liste de modules en s'appuyant, dans l'ordre :

- Les test-cases marqués `priorite: critique` en brique B → remonter aux modules qu'ils exercent.
- La couche domaine identifiée par les ADR ou par `ddd-advisor` s'il a tourné.
- À défaut : les modules avec la plus forte densité de logique conditionnelle, ou ceux que l'utilisateur désigne.

Présenter la liste en QCM multi-sélection. Ne jamais deviner en silence : le périmètre est la décision structurante de cette brique.

### 5.3 — Production des artefacts

#### a) Configuration de l'outil de mutation

Comme pour les briques A et B, **Claude détecte l'écosystème et génère la config adaptée**. Ce qui suit est le cahier des charges, valable quel que soit l'outil — c'est lui qui fait foi, pas une liste d'outils qui vieillira.

Cinq points à cadrer dans toute config générée, dans cet ordre de priorité :

1. **Périmètre explicite.** Restreindre les cibles au périmètre retenu en 5.2, par globs ou packages nommés. Ne jamais laisser le défaut « tout le code » — c'est la première cause de run inexploitable.
2. **Jeu de mutateurs par défaut au premier passage.** Les jeux étendus multiplient le temps de run et produisent des mutants équivalents (des altérations sémantiquement neutres, impossibles à tuer). N'élargir que si le score plafonne artificiellement haut.
3. **Aucun seuil bloquant au premier run.** On mesure avant de contraindre. Le seuil arrive en 5.3.c, après la baseline.
4. **Un rapport lisible par un humain et un rapport parsable par une machine.** Le second alimente le script du harness ; sans lui, la brique ne peut pas remonter dans le rapport consolidé.
5. **Timeout et parallélisme calibrés sur la CI réelle**, pas sur les valeurs par défaut de l'outil — et mode incrémental activé s'il existe, c'est ce qui rend le périmètre « diff » viable.

La config est écrite dans le projet à l'emplacement standard de l'outil, **pas** dans `tools/harness/`. Le harness fournit le pilotage et la normalisation, jamais la config de l'outil : un développeur doit pouvoir lancer l'outil directement sans passer par le harness.

Repères par écosystème, à vérifier au moment du run plutôt qu'à prendre pour argent comptant — l'outillage bouge :

| Écosystème | Outil usuel | Format parsable |
|------------|-------------|-----------------|
| JVM | PIT (`pitest`), via Maven ou Gradle | XML |
| JS/TS | Stryker | JSON |
| .NET | Stryker.NET | JSON |
| Python | mutmut, cosmic-ray | JSON / SQLite selon l'outil |
| Go | go-mutesting, ou `gremlins` | JSON |
| Rust | `cargo-mutants` | JSON |
| PHP | Infection | JSON |

Si aucun outil mature n'existe pour la stack détectée, **le dire et proposer d'abandonner la brique D** plutôt que d'installer un outil abandonné ou expérimental. Un harness qui repose sur un outil non maintenu est une dette, pas une protection.

#### b) `tools/harness/run_mutation.{sh,ps1}`

Le wrapper est la pièce qui rend la brique agnostique : il absorbe la différence d'outillage et expose un contrat stable, identique à celui des scripts des briques A et B. C'est ce contrat qui doit être respecté, pas une implémentation particulière.

**Interface** — alignée sur les autres scripts du harness :
- `--scope critical|diff|full` (défaut `critical`)
- `--explain` : décrit le périmètre, l'outil utilisé et le seuil, sans rien exécuter
- `--root <chemin>` : pour pouvoir tester localement

**Comportement en mode `diff`** : calculer la base avec `git merge-base HEAD origin/<branche cible>` et restreindre le périmètre aux fichiers modifiés, en respectant le format de sélection de l'outil détecté.

**Sortie normalisée** — indépendante de l'outil sous-jacent :
```
MUTATION — périmètre: critical (4 modules) · outil: <détecté>
score: 78.4% (312 tués / 398 générés)  seuil: 75%  → OK

Mutants survivants les plus significatifs :
  <fichier>:44  [NEGATE_CONDITIONS]  aucun test ne distingue > de >=
  <fichier>:71  [MATH]               le calcul du prorata n'est pas asserté
```

**Codes de sortie** identiques aux autres scripts : `0` OK, `1` sous le seuil `error`, `2` sous le seuil `warn`.

**Deux interdits** :
- Le script n'écrit jamais de test. Il signale ; le correctif passe par `plan-driven-dev` avec `behavior-driven-testing` en appui.
- Le script ne modifie jamais la config de l'outil ni le seuil. Un ajustement de seuil est une décision, elle passe par un QCM et une entrée dans `invariants.md`.

Si le projet est multi-modules avec plusieurs stacks (typique d'un monorepo back + front), générer **un wrapper par stack** avec le même contrat, et un `run_mutation.sh` racine qui les appelle et agrège les scores. Le contrat de sortie reste le même ; seule la ligne `outil:` change.

#### c) Entrées dans `invariants.md`

Le seuil de mutation est un invariant à part entière et suit la même numérotation `INV-NNN`, avec un champ supplémentaire :

```markdown
## INV-012 — Score de mutation du domaine ≥ 75%

- **Statut** : actif
- **Source** : brique D du harness, périmètre « domaine critique »
- **Périmètre** : `src/domaine/**`
- **Script** : `tools/harness/run_mutation.sh --scope critical`
- **Sévérité** : warn (→ error prévu après stabilisation)
- **Baseline** : 78.4% mesuré le AAAA-MM-JJ
- **Remédiation** : lire les mutants survivants listés par le script. Pour chacun,
  identifier le comportement non protégé et ajouter un test qui l'exprime. Ne jamais
  ajouter un test dont la seule justification est de tuer un mutant — si un mutant
  survivant ne correspond à aucun comportement qui compte, l'exclure explicitement
  dans la config avec un commentaire justifiant l'exclusion.
```

**La règle du seuil** : le seuil initial est fixé **à la baseline mesurée, arrondie vers le bas**, jamais à un chiffre rond aspirationnel. Son rôle est d'empêcher la régression. On le relève ensuite par paliers explicites, chacun validé par QCM.

### 5.4 — Intégration

Comme pour les autres briques, Claude présente le snippet et demande la permission avant d'écrire.

Deux règles spécifiques à cette brique :

- **Jamais en pre-commit.** Le temps d'exécution est incompatible avec un hook local. Si l'utilisateur le demande quand même, expliquer pourquoi c'est une mauvaise idée avant de suivre sa décision.
- **`warn` obligatoire au premier passage.** Passer un seuil de mutation en CI bloquante dès l'installation garantit une CI rouge et un check désactivé dans la semaine.

```yaml
# GitHub Actions — mutation incrémentale sur les MR
- name: Harness — mutation (diff)
  run: bash tools/harness/run_mutation.sh --scope diff
  continue-on-error: true   # retirer quand le seuil est stabilisé
```

```yaml
# GitHub Actions — mutation nocturne sur le domaine critique
on:
  schedule:
    - cron: '0 2 * * *'
jobs:
  mutation:
    steps:
      - name: Harness — mutation (domaine critique)
        run: bash tools/harness/run_mutation.sh --scope critical
```

Sur GitLab CI, transposer avec un job `rules: - if: $CI_PIPELINE_SOURCE == "merge_request_event"` pour l'incrémental et un `schedule` pour le nocturne.

---

## Étape 6 — Brique C : Doc-gardening automatisé

### 6.1 — Cadence

Claude propose les cadences via QCM :

| Cadence | Cron | Cas d'usage |
|---------|------|-------------|
| Quotidienne | `0 9 * * *` | Projet actif, beaucoup de contributions |
| Hebdomadaire (défaut) | `0 9 * * 1` | Projet en développement normal |
| Bi-mensuelle | `0 9 1,15 * *` | Projet en maintenance |
| Mensuelle | `0 9 1 * *` | Projet stable |

### 6.2 — Création de la scheduled-task

Via `mcp__scheduled-tasks__create_scheduled_task` :

```json
{
  "name": "Harness — doc-gardening [nom du projet]",
  "cronExpression": "<choisi>",
  "prompt": "Relance le skill codebase-harness en mode mise à jour sur le projet [chemin]. Ne modifie aucun fichier automatiquement — produis uniquement un rapport consolidé : violations d'invariants nouvelles, invariants obsolètes, test-cases dérivés (covered_broken ou nouveau test sans test-case), régression du score de mutation par rapport à la baseline et mutants survivants nouveaux, doc qui aurait dérivé. Si tout est au vert, dis-le et n'envoie rien d'autre."
}
```

Claude présente le prompt et la cadence à l'utilisateur, **demande explicitement la permission**, et crée la tâche seulement après confirmation.

### 6.3 — Garde-fous

La tâche ne doit JAMAIS appliquer de changements sans QCM, même quand elle s'exécute sans humain au clavier. Son rôle est de produire un signal, pas un fix. Si le rapport est vide (tout au vert), elle ne produit aucun message — silence = OK.

---

## Étape 7 — Mise à jour de CLAUDE.md

Claude ajoute (ou met à jour) une section dans `CLAUDE.md`. **Toujours avec QCM avant d'écrire**.

### Contenu de la section

```markdown
## Harness

Ce projet a une couche d'enforcement déterministe générée par le skill `codebase-harness`. Les agents (Claude ou autres) doivent respecter ces règles.

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

Une scheduled-task tourne périodiquement et signale les dérives. Quand le rapport remonte des violations, traiter ça comme un signal d'amélioration du repo (ajouter une doc, préciser un invariant, etc.), pas comme du bruit.
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
- Vérifier si une scheduled-task existe pour ce projet (`mcp__scheduled-tasks__list_scheduled_tasks`)

### Exécution des checks

Claude exécute (via bash) tous les scripts de `tools/harness/` et collecte la sortie. Pour chaque invariant :

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
  - Scheduled-task active (hebdo lundi 9h) — dernier run il y a 3 jours, OK
```

QCM consolidé pour valider l'ensemble des actions proposées.

### Si rien n'a changé

Si tous les checks passent et qu'il n'y a aucun delta, Claude dit simplement « Harness OK, rien à faire » et termine. Pas de tool call superflu.

---

## Conseils transverses

**Démarrer petit**. Ne pas essayer de rendre exécutables 20 règles d'un coup. Commencer par 2-3 invariants qui font vraiment mal quand ils sont violés (ex : couche isolée, secret en clair, console.log en prod). Étendre ensuite.

**Sévérité `warn` au démarrage**. Un linter qui passe en `error` sur du code existant non-conforme va bloquer toute l'équipe. Recommander `warn` pendant 1-2 semaines, le temps de nettoyer les violations existantes, puis passer à `error`.

**Messages d'erreur actionnables**. C'est la règle d'or. Un message qui dit « unauthorized import » est inutile pour un agent. Un message qui dit « déplace ce import vers `src/application/` et expose un port côté domaine — voir INV-001 » est utilisable. Tous les starters fournis suivent cette règle.

**Pas d'auto-fix silencieux**. Même si Claude est sûr qu'il sait corriger une violation, il ne le fait jamais sans QCM. Le harness produit un signal ; l'humain ou l'agent applique le fix dans un commit visible.

**Boucle de feedback**. Quand un agent (Claude ou autre) bute sur un invariant, traiter ça comme un signal : la remédiation est-elle assez claire ? l'invariant est-il trop strict ? la doc manque-t-elle d'un exemple ? Mettre à jour `invariants.md` et le message d'erreur du linter en conséquence. C'est ce qui fait évoluer le harness avec le projet.

**Garde la confiance**. Un harness qui produit trop de faux positifs sera ignoré. Si une règle déclenche systématiquement des faux positifs, c'est un bug du linter, pas du code. Corriger le linter en priorité.

**Le coût d'exécution est une contrainte de conception, pas un détail**. Un check juste mais trop lent finit désactivé, ce qui est pire qu'un check absent — il laisse croire à une protection qui n'existe plus. Pour la brique D en particulier : mieux vaut un mutation testing exigeant sur 15 % du code, qui tourne vraiment, qu'un run global que l'équipe met en `continue-on-error` et cesse de lire.

**Ne jamais empiler par réflexe**. Toutes les briques ne se justifient pas sur tous les projets. Un utilitaire interne sans enjeu de fiabilité n'a pas besoin de mutation testing ; un moteur de calcul de facturation en a besoin plus que de doc-gardening. Quand l'utilisateur active tout par défaut, poser la question de la criticité réelle avant d'installer.

**Ce qui n'est plus relu doit être davantage vérifié**. Quand un projet bascule vers un mode où les agents écrivent le code et les tests unitaires sans relecture ligne à ligne, ce n'est pas le moment d'alléger le harness — c'est le moment où il devient la seule protection restante. Le signal à surveiller : si les invariants sont en `warn` depuis des mois et que personne ne lit les rapports, la protection est nominale.

---

## Référence

- `references/templates.md` — six sections : (1) `invariants.md` et ses règles de rédaction, (2) front-matter des test-cases, (3) entrée type d'un seuil de mutation avec baseline, (4) prompt de la scheduled-task, (5) section Harness de `CLAUDE.md`, (6) conventions d'écriture des scripts et règle d'or des messages
- `references/harness-starters/` — implémentations de référence. Contient `README.md` (le contrat commun à tous les scripts) et `check_test_coverage.py` (brique B, complet et générique). Volontairement dépourvu de linters par stack : le skill les génère à partir des conventions, ce qui vieillit moins vite qu'un dossier figé
- `references/harness-starters/mutation/` — optionnel. La brique D **génère** son wrapper et sa config à partir de la stack détectée (voir 5.3.a et 5.3.b) ; ce dossier ne sert qu'à figer des exemples déjà éprouvés en interne, jamais de source de vérité. Le contrat de sortie normalisée décrit en 5.3.b prime sur tout starter qui s'en écarterait.
