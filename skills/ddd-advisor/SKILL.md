---
name: ddd-advisor
description: >
  Audit DDD d'un codebase existant ET guide de conception Domain-Driven Design en cours de
  développement. À utiliser dès que l'utilisateur mentionne DDD, un "modèle anémique", des
  "agrégats", "entités vs objets-valeurs", "bounded context" / "contexte borné", "langage
  omniprésent" / "ubiquitous language", "carte de contexte", "couche anticorruption", ou pose
  une question de modélisation du domaine ("où mettre cette logique métier ?", "est-ce une
  entité ?", "comment découper ce monolithe en contextes ?"). À utiliser AUSSI quand un audit
  ou une remédiation révèle de la logique métier éparpillée, des couches qui fuient, ou un
  couplage fort entre sous-systèmes — même si le mot "DDD" n'est pas prononcé. Les skills
  ai-code-remediation, codebase-cartographer et codebase-harness peuvent invoquer ce skill
  pour qualifier des symptômes de conception ou produire des invariants d'architecture.
---

# DDD Advisor

Audit et accompagnement Domain-Driven Design, basé sur les patterns d'Eric Evans
(tactiques **et** stratégiques). Deux modes, sélectionnés selon le contexte de la demande.

## Signalement initial

Comme `plan-driven-dev`, ce skill **se signale avant de s'appliquer** : annoncer brièvement
le mode pressenti (audit ou guide) et demander validation à l'utilisateur. Ne jamais dérouler
un audit complet sans accord explicite.

## Choix du mode

| Indice dans la demande | Mode |
|---|---|
| "audite", "analyse ce code", "pourquoi ce code est dur à maintenir", codebase fourni | **Audit** |
| Question de conception ponctuelle, feature en cours, choix de modélisation | **Guide** |
| Ambigu | Demander via QCM (2 options) |

---

## Mode Audit

Analyse à froid d'un codebase pour évaluer son alignement DDD. Toujours dans cet ordre :

### 1. Contexte préalable
- Si `docs/metier/` et `docs/technique/` existent (sortie de `codebase-cartographer`), les lire
  d'abord : glossaire = candidat Langage omniprésent, ADR = décisions de frontières déjà prises.
- Sinon, explorer le codebase : structure des dossiers, dépendances entre couches,
  noms des classes vs vocabulaire métier.

### 2. Détection des symptômes
Lire `references/tactique.md` (section Symptômes) et `references/strategique.md`
(section Symptômes). Pour chaque symptôme détecté, noter : localisation, gravité
(bloquant / majeur / mineur), pattern DDD violé.

Les 8 familles de symptômes à balayer systématiquement :
1. **Modèle anémique** — entités = sacs de getters/setters, logique dans des "managers"
2. **Couches qui fuient** — logique métier dans l'IHM, SQL dans le domaine
3. **Agrégats absents ou obèses** — pas de racine claire, ou racine qui englobe tout
4. **Entités/Objets-Valeurs confondus** — identité créée sans besoin, ou valeurs mutables partagées
5. **Langage divergent** — code ≠ vocabulaire des experts métier / du glossaire
6. **Accès aux données anarchique** — requêtes directes contournant tout Entrepôt
7. **Contextes enchevêtrés** — un "gros modèle" unique contradictoire, termes qui se chevauchent
8. **Cœur de domaine noyé** — la logique différenciante indiscernable du code générique

### 3. Restitution
- Synthèse courte en prose, puis tableau des constats (symptôme, localisation, gravité, pattern).
- **Schémas** : Mermaid pour les vues structurelles (carte de contexte actuelle, dépendances
  entre couches, frontières d'agrégats proposées) ; ASCII pour les illustrations ponctuelles
  inline. Toujours montrer l'état ACTUEL et l'état CIBLE quand on propose un changement.

### 4. Recommandations interactives
Présenter les remédiations possibles via **QCM de priorisation** (max 5 options, gravité
décroissante). L'utilisateur choisit ce qu'il veut approfondir ; détailler alors le plan de
remédiation de l'option choisie, avec schéma cible.

### 5. Persistance (QCM final obligatoire)
Toujours terminer par un QCM (forme et mode dégradé : voir `clarify-with-qcm`) :
- **Rien** — l'audit reste conversationnel
- **`docs/technique/ddd-audit.md`** — rapport complet daté (créer `docs/technique/` si absent ;
  si le dossier vient du cartographer, respecter son format et référencer le rapport dans `AGENTS.md`)
- **ADR** — un ADR par décision structurante retenue, dans `docs/technique/adr/`

---

## Mode Guide

Accompagnement ponctuel d'une décision de conception. Charger la référence pertinente
**avant** de répondre :

| Question type | Référence |
|---|---|
| Entité ou Objet-Valeur ? Où placer cette logique ? Frontière d'agrégat ? Fabrique ou constructeur ? | `references/tactique.md` |
| Découper en contextes ? Intégrer deux systèmes ? Relation entre équipes ? Que distiller ? | `references/strategique.md` |

Règles du mode guide :
- Répondre par une **recommandation tranchée** + sa justification par le pattern, jamais un
  catalogue neutre d'options.
- Illustrer par un schéma dès que la réponse implique ≥ 3 éléments en relation
  (ASCII si simple, Mermaid si structurel).
- Quand la décision dépend d'un fait que seul l'utilisateur connaît (ex. : "les deux équipes
  ont-elles le même management ?" pour Client-Fournisseur vs Conformiste), poser LA question
  discriminante via QCM plutôt que de présenter toutes les branches.
- Ancrer dans le concret : reformuler la question de l'utilisateur dans son domaine métier
  à lui, pas dans des exemples génériques de banque ou d'aviation.

---

## Articulation avec l'écosystème

- **codebase-cartographer** : consommer `docs/metier/glossaire.md` comme proxy du Langage
  omniprésent ; un écart code ↔ glossaire est un constat d'audit en soi.
- **plan-driven-dev** : toute remédiation retenue qui implique du code multi-fichier doit être
  proposée comme tâche `plan-driven-dev` (ne pas implémenter directement depuis l'audit).
- **codebase-harness** : pour chaque frontière validée (couches, contextes, agrégats), proposer
  de la transformer en invariant exécutable (ex. : "la couche domaine n'importe ni l'IHM ni
  l'infrastructure", "seules les racines d'agrégats ont un Entrepôt").
- **behavior-driven-testing** : les invariants d'agrégats sont des comportements à tester en
  priorité.

## Garde-fous

- Ne pas appliquer DDD à tout : si le sous-domaine est générique ou trivial (CRUD pur),
  le dire explicitement — c'est conforme à la doctrine (distillation, "n'essayez pas
  d'appliquer DDD à tout").
- Vocabulaire : utiliser les termes français du lexique d'Evans (Entrepôt, Fabrique,
  Objet-Valeur, Contexte borné...) avec le terme anglais entre parenthèses à la première
  occurrence.
- Un audit ne modifie JAMAIS le code. Le mode guide non plus — il recommande.
