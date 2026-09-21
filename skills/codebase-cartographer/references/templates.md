# Templates des fichiers de documentation

Ce fichier est consulté par l'agent au moment de générer chacun des 7 fichiers. Il contient pour chaque fichier : (1) la structure attendue, (2) des questions QCM types à poser à l'utilisateur en phase de validation.

---

## 1. `docs/business/glossary.md`

### Structure

```markdown
# Glossaire métier

Vocabulaire du domaine. Chaque terme est défini une seule fois ici et référencé depuis les autres docs.

## [Terme A]
Définition courte (1-3 phrases). Si pertinent, exemple concret entre parenthèses.

## [Terme B]
...
```

Ordre : alphabétique. Pas plus de 3 phrases par entrée. Si une définition demande plus, c'est probablement une feature, pas un terme.

### Questions QCM types

- "J'ai identifié ces termes métier candidats : [liste]. Lesquels garder ?"
- "Le terme X : je vois deux usages possibles dans le code — [A] ou [B] ?"
- "Manque-t-il des termes importants que je n'ai pas vus dans le code ?"

---

## 2. `docs/business/core-features.md`

### Structure

```markdown
# Features core

Fonctionnalités principales du produit, du point de vue utilisateur.

## [Feature 1 : nom court]

**Description** : Une à trois phrases sur ce que la feature permet de faire.

**Utilisateurs concernés** : [rôles / personae]

**Parcours principal** :
1. ...
2. ...

**Règles métier clés** :
- ...

## [Feature 2 : nom court]
...
```

Une feature = une capacité utilisateur, pas un endpoint technique. Si l'agent hésite, c'est probablement de l'architecture, pas une feature.

### Questions QCM types

- "J'ai identifié ces features : [liste]. Laquelle est la feature principale ?"
- "La feature X concerne quels utilisateurs : [A] / [B] / les deux ?"
- "Y a-t-il des features en cours de dev ou prévues à documenter, ou seulement l'existant ?"

---

## 3. `docs/business/test-cases/[feature]/[nom].md` (un fichier par test case)

### Sources à parcourir

Pour identifier les test cases candidats, l'agent inspecte dans cet ordre :

1. **Tests existants dans le code** : fichiers `*_test.*`, `*.spec.*`, dossier `tests/`, `__tests__/`, `spec/`, etc. Chaque test unitaire ou d'intégration métier devient un candidat.
2. **Controllers / endpoints / handlers** : routes HTTP, handlers d'événements, commandes CLI. Chaque endpoint suggère au moins un cas nominal + cas d'erreur.
3. **Features métier déjà documentées** dans `core-features.md` : pour chaque feature, déduire les scénarios principaux non couverts par les deux sources précédentes.

L'agent consolide la liste, dédoublonne, et présente un récapitulatif à l'utilisateur en QCM AVANT d'écrire les fichiers.

### Organisation

Un fichier `.md` par test case, groupé par feature dans un sous-dossier :

```
docs/business/test-cases/
├── authentification/
│   ├── connexion-reussie.md
│   ├── connexion-mot-de-passe-invalide.md
│   └── connexion-compte-bloque.md
├── panier/
│   ├── ajout-produit.md
│   └── ...
└── ...
```

Convention de nommage : kebab-case, descriptif, sans préfixe numérique (l'ordre n'a pas de sens métier).

### Structure d'un fichier test case

```markdown
# [Titre clair en une phrase]

**Feature** : [nom de la feature, lien vers core-features.md#feature]
**Type** : nominal / cas d'erreur / edge case
**Priorité** : critique / importante / nice-to-have

## Contexte
État du système et préconditions avant le test. Acteurs concernés. Données initiales.

## Action
Ce que l'utilisateur (ou le système amont) déclenche. Une action principale, claire.

## Résultat attendu
Ce qui doit se produire. État final du système, retour côté utilisateur, effets de bord observables.

## Notes (optionnel)
- Test automatisé existant : `chemin/vers/test.py::test_xxx` (si applicable)
- Endpoint concerné : `POST /api/...` (si applicable)
- Cas liés : [lien vers autres TC]
```

### Questions QCM types

- "J'ai trouvé [N] tests dans le code et [M] endpoints. Je propose ces [X] test cases (liste). Lesquels garder ?"
- "Pour la feature [X], j'ai trouvé seulement des cas nominaux dans le code. Veux-tu que je propose aussi des cas d'erreur ?"
- "Niveau de granularité : un TC par scénario distinct (verbeux) / regrouper les variantes proches dans un seul TC (compact) ?"
- "Inclure le mapping vers les tests automatisés existants dans le champ Notes ?"

---

## 4. `docs/technical/architecture.md`

### Structure

```markdown
# Architecture

## Vue d'ensemble

Schéma (ASCII ou mermaid) + 2-3 paragraphes d'explication.

## Composants

### [Composant 1]
- **Rôle** : ...
- **Technologies clés** : [voir tech-stack.md]
- **Interfaces** : (avec qui il parle, comment)

### [Composant 2]
...

## Flux principaux

Pour les 2-3 flux les plus structurants, expliquer le cheminement entre composants.

## Données

Si pertinent : modèle de données simplifié, sources externes, persistance.
```

Pas de copier-coller de tech-stack.md ici. Mentionner les techs UNIQUEMENT quand elles sont structurantes pour l'architecture.

### Questions QCM types

- "L'architecture est plutôt : monolithe / microservices / serverless / hybride ?"
- "Le format de diagramme préféré : ASCII art / mermaid / lien vers un fichier externe ?"
- "Quels sont les 2-3 flux les plus critiques à documenter ?"

---

## 5. `docs/technical/tech-stack.md`

### Structure

```markdown
# Stack technique

## Langages & runtimes
- ...

## Frameworks & libs principales
- **[Nom]** (version) — rôle dans le projet

## Base de données / persistance
- ...

## Infrastructure & déploiement
- ...

## Outils de dev
- Tests : ...
- Lint / format : ...
- CI/CD : ...

## Services externes
- ...
```

Versions importantes uniquement (langage, framework majeur, DB). Pas la peine de lister toutes les sous-deps.

### Questions QCM types

- "Pour les versions, je liste : tout / juste les majeures / juste si critique pour la compat ?"
- "Inclure les outils de dev personnels (IDE config, etc.) ou seulement la stack partagée ?"

---

## 6. `docs/technical/test-strategy.md`

### Structure

```markdown
# Stratégie de test

## Pyramide / philosophie
Décrire le type de pyramide utilisée (classique, trophée, ice-cream, etc.) et pourquoi.

## Types de tests
- **Unitaires** : framework, conventions de nommage, où ils vivent, couverture cible
- **Intégration** : ...
- **End-to-end** : ...
- **Autres** (perf, sécurité, accessibilité) : ...

## Conventions
- Structure d'un test (AAA, Given/When/Then en code, etc.)
- Fixtures & mocks : approche
- Nommage des fichiers et fonctions de test

## Exécution
- Commandes locales
- Exécution en CI
- Critères de merge (couverture min, tests qui doivent passer)
```

### Questions QCM types

- "Quel type de pyramide : classique (beaucoup d'unitaires) / trophée (beaucoup d'intégration) / autre ?"
- "Couverture cible globale : [valeur] / pas de cible chiffrée / définie par type de test ?"
- "Les tests E2E sont : existants / à mettre en place / pas prévus ?"

---

## 7. `docs/technical/adr.md` + `docs/technical/adr/`

### Sources à parcourir AVANT le QCM

Pour proposer des ADR candidats, l'agent analyse :

1. **Le code** : choix techniques structurants détectables (framework choisi, pattern d'architecture, choix de DB, approche d'authentification, gestion d'état, stratégie de cache, etc.)
2. **L'historique git** (si disponible) :
   - `git log --oneline` pour repérer les commits qui parlent de migration, refactor, choix, décision, switch, replace, introduce, remove
   - `git log --all --grep="ADR\|decision\|migrat\|refactor\|switch\|replace"` pour les commits explicites
   - Tags et branches qui signalent des changements majeurs
   - Fichiers supprimés ou renommés en masse (signal de refactor structurant)
3. **Les fichiers de configuration** : `package.json` (deps majeures retirées/ajoutées), `Dockerfile` (base image switchée), config CI/CD (changements de pipeline)

L'agent consolide une liste de **décisions candidates** (5-15 entrées max), avec pour chacune :
- Le nom court de la décision
- L'indice qui l'a fait remonter (commit, code, etc.)
- Le niveau d'évidence (claire / probable / hypothétique)

Cette liste est présentée à l'utilisateur en QCM pour qu'il sélectionne les vraies décisions à formaliser.

### Structure de `adr.md` (index)

```markdown
# Architecture Decision Records

Décisions structurantes du projet. Chaque ADR est un fichier numéroté dans `adr/`.

## Format

Utiliser le template `adr/0000-template.md` pour créer un nouvel ADR.

## Index

- [ADR-0001 : Titre](adr/0001-titre.md) — statut : accepté
- [ADR-0002 : Titre](adr/0002-titre.md) — statut : proposé
```

### Structure d'un ADR individuel (`adr/NNNN-titre.md`)

```markdown
# ADR-NNNN : [Titre]

**Statut** : proposé / accepté / déprécié / remplacé par ADR-XXXX
**Date** : YYYY-MM-DD
**Source** : (optionnel) commit abc1234, ou "reconstitué a posteriori"

## Contexte
Quel problème, quelles contraintes ?

## Décision
Ce qui a été décidé, en une à trois phrases claires.

## Conséquences
- Positives : ...
- Négatives / coûts : ...
- Risques : ...

## Alternatives considérées
- [Option A] — rejetée parce que ...
- [Option B] — rejetée parce que ...
```

### Questions QCM types

- "J'ai détecté ces décisions candidates dans le code et l'historique git : [liste avec niveau d'évidence]. Lesquelles formaliser en ADR ?"
- "Pour la décision X (évidence : probable), je manque de contexte sur le pourquoi. Tu peux préciser : [option A] / [option B] / je détaille en texte libre ?"
- "Y a-t-il des décisions importantes que je n'ai pas détectées et que tu veux ajouter ?"
- "Pour les ADR reconstitués, indiquer clairement 'reconstitué a posteriori' dans le champ Source ?"

**Important** :
- Ne JAMAIS écrire un ADR sans validation utilisateur, même si l'évidence semble forte
- Si l'utilisateur n'a aucune décision à formaliser, créer uniquement `adr.md` (index vide) + `adr/0000-template.md` pour les futurs ADR
- Pour les décisions reconstituées (sans contexte git clair), marquer la Source comme "reconstitué a posteriori" pour la transparence

---

## Notes générales sur la phase QCM

La doctrine de validation par QCM — mécanisme selon l'agent hôte, structure d'un round, rédaction des questions, cas particuliers — vit dans le skill `clarify-with-choices`. Les templates ci-dessus fixent *ce qu'on demande* ; `clarify-with-choices` fixe *comment on le demande*.
