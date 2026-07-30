---
name: ai-code-remediation
description: Audit à froid d'un codebase majoritairement généré par IA, suivi d'un plan de remédiation priorisé selon une doctrine stricte (TDD, méthode Mikado, micro-itérativité). À utiliser SYSTÉMATIQUEMENT quand l'utilisateur demande d'"auditer ce codebase", "évaluer la dette de ce projet généré par IA", "remettre d'aplomb un projet vibe-codé", "diagnostiquer ce que les agents ont produit", "plan de remédiation", "assainir ce code", ou exprime un doute sur la qualité d'un projet écrit en grande partie par des agents — même sans employer le mot "audit". Couvre 8 catégories de symptômes typiques du code généré par IA. Ne pas confondre avec premerge-review (revue d'un diff avant merge, pas d'un codebase entier) ni avec codebase-cartographer (documentation, pas diagnostic). Peut invoquer ddd-advisor quand les symptômes relèvent de la conception du domaine.
---

# AI Code Remediation

Audit à froid d'un codebase produit en grande partie par des agents IA, puis plan de remédiation discipliné. L'objectif n'est pas de juger le code mais de le rendre maintenable : identifier les symptômes, prouver leur réalité, et organiser leur résorption sans big-bang.

**Principe cardinal : l'audit est en lecture seule.** Ne jamais corriger pendant l'audit, même un défaut trivial — corriger au fil de l'eau détruit la vision d'ensemble et mélange diagnostic et traitement. La remédiation vient après, plan en main, et son exécution est déléguée à `plan-driven-dev`.

## La doctrine de remédiation

Toute la remédiation obéit à trois disciplines, non négociables :

1. **TDD orienté comportement** — aucun refactoring sans filet. Si le code à remédier n'est pas testé (cas fréquent du code généré), commencer par des tests de caractérisation qui capturent le comportement actuel, même imparfait. S'appuyer sur le skill `behavior-driven-testing` pour la stratégie : tester des comportements, pas des classes.
2. **Méthode Mikado** — chaque objectif de remédiation est décomposé en graphe de prérequis. On tente le changement ; s'il casse, on note ce qui manque, on revert, et on s'attaque d'abord aux feuilles du graphe. Jamais de chantier ouvert qui ne compile pas.
3. **Micro-itérativité** — des pas si petits qu'ils paraissent ridicules : chaque étape laisse le codebase au vert, committable, livrable. Un refactoring qu'on ne peut pas interrompre à tout moment est un refactoring mal découpé.

## Phase 0 — Cadrage

1. Établir le périmètre : tout le repo, ou un sous-ensemble (module, service) ? Sur un gros codebase (>~50k lignes), proposer de découper l'audit par zone plutôt que de tout survoler.
2. Recueillir le contexte minimal auprès de l'utilisateur : quelle proportion du code est générée, depuis quand, quels sont les irritants déjà ressentis (bugs récurrents, peur de toucher certaines zones, builds lents) ? Les irritants vécus orientent la priorisation finale.
3. Inventorier les référentiels disponibles : `CLAUDE.md`, `docs/technique/` (ADR, architecture), `docs/metier/` (glossaire, test-cases), `docs/technique/invariants.md` et `tools/harness/`. **Mode dégradé** : leur absence n'empêche pas l'audit, mais elle est elle-même un finding — un codebase généré sans référentiel dérive plus vite.

## Phase 1 — Collecte des signaux

Avant l'analyse fine, mesurer ce qui se mesure. Objectiver d'abord, interpréter ensuite.

- **Structure** : taille par module, profondeur des arborescences, fichiers anormalement longs.
- **Duplication** : détecteur de clones si disponible (jscpd, PMD/CPD, simian), sinon échantillonnage manuel ciblé.
- **Tests** : ratio tests/code, mais surtout lecture qualitative d'un échantillon — que vérifient les assertions ?
- **Score de mutation sur échantillon**, si et seulement si trois conditions sont réunies : la suite est verte, un outil de mutation existe pour la stack, et un module porteur de règles métier peut être isolé. Un run sur ce seul module suffit — l'objectif est un ordre de grandeur, pas une mesure exhaustive. Noter le score, le périmètre et la durée. Si l'une des conditions manque, ne pas insister : c'est un signal en plus, jamais un prérequis de l'audit.
- **Historique git** : rythme et taille des commits, messages génériques en rafale ("fix", "update"), fichiers réécrits plusieurs fois en boucle — signatures typiques de sessions agentiques non supervisées.
- **Dépendances** : manifestes (package.json, pom.xml…), dépendances inutilisées ou redondantes (trois libs HTTP, deux frameworks de mock).

## Phase 2 — Analyse par symptômes

Parcourir le codebase avec huit lectures ciblées. Comme pour une revue, une passe unique qui "regarde tout" rate l'essentiel ; chaque catégorie a sa question.

### S1 — Duplication systémique
*Le même savoir est-il écrit plusieurs fois ?* Le code généré duplique au lieu de factoriser, car chaque session de génération repart de zéro. Chercher les clones exacts, mais aussi les clones sémantiques : trois validateurs d'email, deux clients HTTP maison.

### S2 — Sur-abstraction et over-engineering
*Y a-t-il des couches que rien ne justifie ?* Interfaces à implémentation unique, patterns plaqués (factory de factory, stratégie à un seul cas), généricité spéculative. L'IA reproduit des patterns "best practice" hors de tout besoin réel.

### S3 — Tests cosmétiques
*Les tests détecteraient-ils une régression réelle ?* Coverage élevé mais assertions creuses, tests qui vérifient des mocks, mapping mécanique 1 test ↔ 1 classe, happy path uniquement. Confronter au skill `behavior-driven-testing`. Test décisif : muter une règle métier — un test rougit-il ?

**C'est le seul des huit symptômes qui dispose d'une preuve mécanique.** Quand le score de mutation de la Phase 1 est disponible, l'utiliser plutôt que le jugement : « 43% des mutants survivent sur le module de facturation » est opposable à une équipe qui conteste l'audit, là où « ces tests m'ont l'air creux » ouvre un débat d'opinion. Citer le score, le périmètre et la date.

À défaut de run réel, la mutation mentale reste valable — mais le finding se formule alors comme une hypothèse à vérifier, pas comme un constat. La doctrine de la phase est de **prouver** les symptômes ; un symptôme prouvé et un symptôme soupçonné ne se priorisent pas pareil.

### S4 — Incohérence de conventions
*Combien de styles cohabitent ?* Nommage hétérogène, trois façons de gérer les erreurs, mélange de paradigmes — trace de sessions de génération successives sans mémoire l'une de l'autre. L'incohérence coûte : chaque zone se relit avec une grille différente.

### S5 — Code mort et chemins fantômes
*Qu'est-ce qui ne sert à rien ?* Fonctions jamais appelées, features à moitié branchées, flags de config orphelins, fichiers générés puis abandonnés. Le code mort généré est dangereux : il a l'air intentionnel.

### S6 — Gestion d'erreurs de façade
*Que se passe-t-il quand ça échoue ?* try/catch qui avalent, messages génériques, erreurs loggées puis ignorées, absence de stratégie (retry ? propagation ? compensation ?). Le code généré gère la forme de l'erreur, rarement son fond.

### S7 — Documentation et commentaires mensongers
*Ce qui est écrit est-il vrai ?* Commentaires qui paraphrasent le code, docstrings génériques, README qui décrit un projet qui n'existe plus, exemples qui ne compilent pas. Une doc fausse est pire qu'une absence de doc.

### S8 — Frontières architecturales poreuses
*La logique métier est-elle là où elle doit être ?* Logique métier éparpillée dans les contrôleurs et l'infra, couches qui fuient, couplage fort entre modules censés être indépendants, modèle anémique. **Quand cette catégorie domine, invoquer le skill `ddd-advisor`** pour qualifier les symptômes de conception et proposer le découpage cible.

Pour chaque symptôme constaté : citer des occurrences précises (`fichier:ligne`), estimer l'étendue (cas isolé, zone, systémique), et noter la conséquence concrète (pourquoi c'est un coût, pas juste une laideur).

## Phase 3 — Rapport d'audit

Classer chaque finding :

- **Critique** — empêche de travailler en confiance : zone non testable, comportement imprévisible, faille, corruption possible.
- **Structurel** — dette qui ralentit chaque évolution : duplication systémique, frontières poreuses, tests cosmétiques étendus.
- **Cosmétique** — coût réel mais localisé : nommage, code mort isolé, doc obsolète.

Écrire le rapport dans `.audit/<projet>-<AAAA-MM-JJ>.md`, puis présenter la synthèse en conversation et **faire valider les findings par l'utilisateur avant de passer au plan** — il connaît des contraintes que le code ne montre pas. TOUJOURS suivre cette structure :

```markdown
# Audit à froid — <projet>
**Date** : … · **Périmètre** : … · **Référentiels disponibles** : …

## Synthèse
État général en 3-5 phrases, et les 2-3 chantiers qui changeraient le plus la donne.

## Signaux mesurés
Chiffres bruts de la Phase 1.

## Findings par symptôme
### S1 — Duplication systémique : <néant | localisé | systémique>
- **[C1|St1|c1] <titre>** — `fichier:ligne` · étendue · conséquence concrète
(… S2 à S8, même format ; mentionner explicitement les catégories saines)

## Vérifications non réalisées
Référentiels absents, zones non couvertes, outils indisponibles.

## Points positifs
Ce qui est sain et doit être préservé pendant la remédiation.
```

## Phase 4 — Plan de remédiation

Une fois les findings validés, produire le plan dans `.audit/<projet>-remediation-<AAAA-MM-JJ>.md` :

1. **Prioriser** par le ratio coût-du-symptôme / effort, en intégrant les irritants exprimés en Phase 0. Règle d'or : **sécuriser avant de transformer** — les tests de caractérisation des zones critiques passent avant tout refactoring, c'est le prérequis Mikado universel.
2. **Découper en chantiers** : chaque chantier traite un symptôme dans une zone, avec son mini-graphe Mikado (objectif, prérequis connus), son critère de fin observable, et une taille cible d'une session de travail maximum.
3. **Ordonner** les chantiers pour que chacun laisse le codebase strictement meilleur et au vert — jamais de chantier dont la valeur dépend d'un chantier futur.

### Après le plan

L'exécution de chaque chantier passe par `plan-driven-dev`, le chantier devenant l'entrée de la phase de plan. Proposer aussi, selon les findings :
- `codebase-cartographer` si l'absence de référentiel est elle-même un finding — documenter avant ou pendant la remédiation ;
- `codebase-harness` pour transformer les décisions de remédiation en invariants exécutables, afin que les agents qui continueront à contribuer ne réintroduisent pas les symptômes corrigés. Deux briques répondent directement à des symptômes de cette liste : la brique A (seuils de forme) contient S1 et S2, la brique D (mutation testing) empêche S3 de revenir en fixant un seuil à la valeur mesurée pendant l'audit.
