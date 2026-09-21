---
name: codebase-cartographer
description: Cartographie un projet de code existant ou nouveau pour produire une documentation structurée métier + technique. Crée un dossier `docs/` organisé en `docs/business/` (glossaire, features core, test cases — un .md par cas, groupés par feature) et `docs/technical/` (architecture, stack, stratégie de test, ADR avec analyse de l'historique git), valide chaque section avec l'utilisateur via QCM, refactorise pour éliminer les redondances, et référence le tout dans `AGENTS.md`. À utiliser DÈS QUE l'utilisateur demande de "documenter le projet", "cartographier le code", "générer la doc", "créer un glossaire métier", "documenter l'architecture", "écrire des ADR", "produire une stratégie de test", ou mentionne vouloir structurer la connaissance d'un projet — même si le mot "skill" n'est pas employé. À utiliser aussi quand l'utilisateur invoque explicitement ce skill par son nom.
---

# Codebase Cartographer

Génère une documentation projet complète et structurée, validée pas à pas avec l'utilisateur.

## Vue d'ensemble du workflow

```
[Première exécution]
1. Analyse initiale du projet
2. Pour chaque doc à générer (7 fichiers) :
   a. QCM de validation (ce que l'agent a compris + ses incertitudes)
   b. Écriture du fichier .md
3. Refactor global anti-redondance
4. Demande de validation avant de modifier AGENTS.md
5. Mise à jour d'AGENTS.md (création ou patch)

[Ré-exécution : bascule automatique en mode mise à jour]
1. Inventaire des docs existantes
2. Analyse du delta entre code et docs (nouveau/obsolète/modifié/inchangé)
3. QCM consolidé par type de doc pour valider les changements
4. Application des changements (archivage des suppressions, préservation des éditions manuelles)
5. Refactor global sur l'ensemble
6. Mise à jour d'AGENTS.md si nécessaire
```

**Principe central** : l'agent n'écrit JAMAIS un fichier de doc sans avoir d'abord présenté à l'utilisateur ce qu'il a compris et fait valider les points incertains. Le QCM est obligatoire avant chaque écriture.

**Idempotence** : ré-exécuter le skill ne dégrade pas la doc. Le mode mise à jour est conçu pour être lancé régulièrement à mesure que le code évolue.

---

## Étape 1 — Analyse initiale

Avant toute question à l'utilisateur, l'agent inspecte le projet pour se faire une idée. Tâches à faire en parallèle quand c'est possible :

- Lister la racine et les dossiers de premier niveau
- Lire le `README.md` s'il existe
- Repérer les fichiers de manifeste (`package.json`, `pyproject.toml`, `pom.xml`, `Cargo.toml`, `go.mod`, `Gemfile`, etc.) pour déduire la stack
- Repérer les fichiers de config CI/CD, Docker, infra (`docker-compose.yml`, `Dockerfile`, `.github/workflows/`, `terraform/`, etc.)
- Repérer le dossier de tests et identifier le framework de test
- Repérer les dossiers source principaux et leur organisation
- Vérifier si `docs/` ou `AGENTS.md` existe déjà (pour éviter d'écraser bêtement)
- Si le projet est sous git, inspecter `git log --oneline -200` et les tags pour repérer les décisions structurantes passées (utile pour la phase ADR)

Si un `docs/` généré par ce skill existe déjà (présence des fichiers attendus : `docs/business/glossary.md`, `docs/technical/architecture.md`, etc.), l'agent bascule en **mode mise à jour** — voir section dédiée plus bas. Le skill est idempotent : ré-exécuté, il met à jour intelligemment au lieu de tout regénérer.

Si un `docs/` existe mais ne ressemble pas à une sortie de ce skill (structure différente, fichiers inconnus), l'agent signale l'ambiguïté et demande à l'utilisateur : compléter / repartir de zéro avec backup / annuler.

Si un `AGENTS.md` existe déjà, on le note pour l'étape finale — surtout pas le toucher tout de suite.

**Stocker mentalement** (ou dans un fichier scratch si la session est longue) : ce qui est clair, ce qui est ambigu, ce qui est manquant. Cette cartographie alimente les QCM.

---

## Étape 2 — Génération doc par doc avec validation QCM

Pour chacun des 7 fichiers, l'agent suit le même cycle : **analyser → QCM → écrire**.

L'ordre recommandé est métier d'abord (donne le vocabulaire) puis technique :

| # | Fichier(s) | Emplacement |
|---|------------|-------------|
| 1 | `glossary.md` | `docs/business/` |
| 2 | `core-features.md` | `docs/business/` |
| 3 | un `.md` par test case, groupé par feature | `docs/business/test-cases/[feature]/` |
| 4 | `architecture.md` | `docs/technical/` |
| 5 | `tech-stack.md` | `docs/technical/` |
| 6 | `test-strategy.md` | `docs/technical/` |
| 7 | `adr.md` (index) + un `.md` par ADR | `docs/technical/` + `docs/technical/adr/` |

### Format du QCM

Pour chaque section, présenter à l'utilisateur, dans cet ordre :

1. **Ce que j'ai compris** : un résumé bref en bullet points de ce que l'agent a inféré
2. **Ce dont je ne suis pas sûr** : 1 à 3 questions sous forme de QCM

La doctrine complète — rédaction des questions, nombre d'options, mode dégradé quand l'agent hôte n'expose pas d'outil de question à choix multiples — est dans le skill `clarify-with-choices`. Le charger avant le premier QCM.

Si l'agent n'a aucune incertitude sur une section (rare), il propose quand même une validation simple : "Voici ce que je vais écrire dans X — je procède ?"

### Détail par fichier

Chaque fichier suit un template spécifique. Voir `references/templates.md` pour les structures détaillées et les questions QCM types par section.

### Écriture du fichier

Une fois le QCM répondu, l'agent écrit le fichier `.md` directement dans `docs/business/` ou `docs/technical/`. Le contenu doit :
- Suivre le template adapté (voir `references/templates.md`)
- Rester factuel et concis (pas de remplissage)
- Utiliser le vocabulaire du glossaire (cohérence)
- Inclure des liens relatifs vers les autres docs quand pertinent

Après écriture, l'agent **annonce brièvement** ce qu'il vient de produire et passe au fichier suivant, sans attendre confirmation (l'utilisateur a déjà validé via le QCM).

---

## Étape 3 — Refactor anti-redondance

Une fois les 7 fichiers générés, l'agent relit l'ensemble en une passe et cherche :

1. **Définitions dupliquées** : un terme défini dans le glossaire ET ré-expliqué dans une autre doc → garder dans le glossaire, remplacer par un lien dans l'autre doc
2. **Listes de features redondantes** : `core-features.md` et `architecture.md` qui décrivent les mêmes flows → la feature reste métier, l'architecture renvoie au feature avec un lien
3. **Stack répétée** : `tech-stack.md` et `architecture.md` qui listent les mêmes outils → la liste exhaustive reste dans `tech-stack.md`, l'architecture ne mentionne que ce qui est structurant
4. **Stratégie de test vs test cases** : `test-strategy.md` décrit le COMMENT (pyramide, outils, couverture cible), `test-cases.md` décrit le QUOI (scénarios métier) — pas de mélange
5. **Décisions techniques** : si une décision est dans `architecture.md` ET mériterait un ADR, créer/déplacer vers l'ADR et linker

Pour chaque redondance détectée, l'agent présente brièvement le diff proposé à l'utilisateur en une seule passe (liste à puces), puis applique les corrections après validation globale.

Si rien à refactorer (cas idéal), l'agent le mentionne et passe à l'étape suivante.

---

## Étape 4 — Mise à jour d'AGENTS.md (avec validation)

**Règle stricte** : avant toute modification d'`AGENTS.md`, l'agent demande explicitement la permission à l'utilisateur, en montrant :
- Si `AGENTS.md` n'existe pas : le contenu complet qu'il propose de créer
- Si `AGENTS.md` existe : le diff exact qu'il propose d'appliquer (section ajoutée à la fin par défaut)

### Contenu de la section à ajouter / créer

```markdown
## Documentation du projet

Ce projet dispose d'une documentation structurée dans `docs/`. Consulter ces fichiers avant toute modification importante.

### Métier
- [Glossaire](docs/business/glossary.md) — vocabulaire du domaine
- [Features core](docs/business/core-features.md) — fonctionnalités principales
- [Test cases](docs/business/test-cases/) — scénarios de test métier (un fichier par cas, groupés par feature)

### Technique
- [Architecture](docs/technical/architecture.md) — vue d'ensemble et composants
- [Stack technique](docs/technical/tech-stack.md) — technologies et outils
- [Stratégie de test](docs/technical/test-strategy.md) — approche de testing
- [ADR](docs/technical/adr.md) — décisions d'architecture
```

Si `AGENTS.md` existait déjà avec d'autres sections, ajouter cette section sans toucher au reste. Si une section "Documentation" existait déjà, proposer un merge plutôt qu'un écrasement.

**Compatibilité Claude Code.** `AGENTS.md` est lu nativement par la plupart des agents, mais pas par Claude Code, qui cherche `CLAUDE.md`. Si le projet n'a pas de `CLAUDE.md`, ou en a un qui n'importe pas `AGENTS.md`, proposer par QCM d'y ajouter la ligne d'import :

```markdown
@AGENTS.md
```

Une seule source de vérité, lisible par tous. Ne jamais dupliquer le contenu dans les deux fichiers : deux copies divergent.


---

## Mode mise à jour (ré-exécution du skill)

Quand le skill détecte un `docs/` déjà généré par lui (signature : présence de `docs/business/glossary.md`, `docs/business/core-features.md`, `docs/technical/architecture.md` au minimum), il bascule automatiquement en mode mise à jour. **C'est le comportement par défaut, pas une option** — le skill est conçu pour être ré-exécuté à chaque évolution significative du projet.

### Principe

Le skill produit un **diff de doc**, pas une nouvelle doc. Il compare l'état actuel du code à ce qui est consigné dans `docs/`, et propose à l'utilisateur les ajustements pertinents — sans jamais perdre du contenu humain ajouté à la main.

### Procédure détaillée

**1. Inventaire de l'existant**

Avant tout, l'agent lit la totalité des fichiers de `docs/` et en construit une représentation interne. Il note en particulier :
- Liste des termes du glossaire
- Liste des features
- Liste des test cases existants (par feature) avec leur titre et identifiant de fichier
- Liste des ADR existants avec leur numéro et statut
- Tout commentaire ou section qui semble avoir été édité manuellement (présence de `> TODO`, formulations très spécifiques, contenu absent du code)

**2. Analyse du delta**

L'agent refait l'analyse complète du projet (étape 1 du workflow normal) et compare au snapshot de l'étape précédente. Pour chaque type de doc, il classe les éléments en 4 catégories :

| Catégorie | Action par défaut |
|-----------|-------------------|
| **Inchangé** (présent ici et là, contenu cohérent) | Ne rien faire |
| **Nouveau** (présent dans le code, absent de la doc) | Proposer ajout via QCM |
| **Obsolète** (présent dans la doc, plus dans le code) | Proposer suppression via QCM, avec contexte |
| **Modifié** (présent des deux côtés mais divergent) | Proposer mise à jour via QCM, en montrant le diff |

**3. QCM consolidé**

Au lieu d'un QCM par fichier comme en première exécution, l'agent présente en une seule passe (par type de doc) un récapitulatif structuré :

```
## Glossaire — 3 changements proposés

NOUVEAU (1) :
- "Idempotence" — détecté dans src/api/handlers.py (nouveau concept central)

OBSOLÈTE (1) :
- "LegacyAuth" — plus aucune référence dans le code (supprimé au commit abc1234)

MODIFIÉ (1) :
- "Panier" — définition actuelle parle de "session", mais le code utilise maintenant
  une persistance DB. Mettre à jour ?
```

Puis un QCM pour valider l'ensemble : accepter tout / refuser tout / sélection fine (voir `clarify-with-choices`).

**4. Application des changements**

Une fois validés :
- Les **ajouts** sont insérés en respectant l'ordre existant (alphabétique pour le glossaire, par feature pour les test cases, numérotation continue pour les ADR)
- Les **suppressions** déplacent le fichier vers `docs/.archive/[date]/` plutôt que de le supprimer définitivement (récupération possible)
- Les **modifications** préservent les éventuelles sections marquées manuellement (commentaires, notes à la main) — l'agent met à jour uniquement la partie auto-générée et signale ce qu'il a préservé

### Règles spécifiques par doc

**Test cases** : la numérotation séquentielle est évitée justement pour éviter les conflits en ré-exécution (noms en kebab-case descriptifs). Si un test case existant a été renommé manuellement, ne pas le recréer sous l'ancien nom — utiliser le nom actuel comme référence.

**ADR** : la numérotation est continue et **immuable**. Un ADR existant n'est jamais renuméroté. Les nouveaux ADR prennent le prochain numéro libre. Un ADR obsolète n'est pas supprimé — son statut passe à `déprécié` ou `remplacé par ADR-XXXX` (à valider via QCM).

**AGENTS.md** : si la section "Documentation du projet" existe déjà et pointe vers la bonne structure, ne pas la toucher. Sinon proposer un patch ciblé.

### Refactor en mode mise à jour

Le refactor anti-redondance (étape 3 du workflow normal) tourne aussi en mode mise à jour, mais sur l'**ensemble** des fichiers (existants + modifiés + ajoutés), pas seulement sur les changements. Cela permet d'attraper des redondances qui auraient survécu à l'exécution précédente.

### Si rien n'a changé

Si l'analyse révèle aucun delta significatif, l'agent le dit clairement à l'utilisateur (« La doc est à jour, rien à modifier ») et termine sans tool call superflu. C'est un cas heureux, pas une erreur.

---

## Conseils transverses

**Langue** : suivre la langue du projet existant. Si le projet est en français (README, commentaires, noms de variables métier), générer la doc en français. Sinon en anglais. En cas de mix, demander à l'utilisateur.

**Niveau de détail** : viser des fichiers utilisables, pas exhaustifs. Un glossaire de 200 lignes ne sera pas lu. Mieux vaut 30 entrées précises que 100 vagues.

**Honnêteté sur les incertitudes** : si l'agent ne trouve pas l'info dans le code et que l'utilisateur ne sait pas répondre, marquer la section avec un `> TODO: à compléter — [question précise]` plutôt que d'inventer.

**ADR** : ne pas en inventer rétroactivement à partir du code. Demander à l'utilisateur quelles décisions structurantes mériteraient un ADR. Si aucune, créer un `adr.md` minimal qui explique le format à utiliser pour les futurs ADR (template inclus).

**Pas d'over-engineering** : si le projet est petit (script unique, ~500 lignes), proposer une version condensée (un seul `docs/README.md` plutôt que 7 fichiers). Demander à l'utilisateur s'il préfère la version complète ou condensée.

---

## Référence

- `references/templates.md` — templates détaillés des 7 fichiers + questions QCM types par section
