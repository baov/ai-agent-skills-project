# Brique A — Invariants exécutables

Chargé par `codebase-harness` uniquement si cette brique a été retenue au QCM de scoping (étape 2). Les autres briques sont dans les fichiers `brique-*.md` voisins.

---

## 3.1 — Extraction des règles candidates

L'agent relit (s'ils existent) :
- `docs/technical/architecture.md` section « Contraintes structurelles »
- Tous les ADR `docs/technical/adr/*.md` — en particulier la section « Décision »
- `README.md` racine pour des indices de conventions (« no direct DB calls in handlers », etc.)

Si la doc cartographer n'a pas tourné, l'agent demande directement à l'utilisateur :

> « Quelles règles de code/architecture aimerais-tu rendre testables ? Exemples : couches isolées, interdiction d'imports d'I/O dans une couche, conventions de nommage de fichiers, types de retour obligatoires sur les fonctions publiques, etc. »

## 3.1 bis — Les seuils de forme sont des invariants comme les autres

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

## 3.1 ter — Consolidation

L'agent consolide une liste de **règles candidates** (5-15 max), avec pour chacune :
- Énoncé en une phrase
- Source (ADR-XXXX, section d'architecture.md, ou « énoncé par l'utilisateur »)
- Mécanisme de check proposé (AST Python, ESLint custom, ArchUnit, dependency-cruiser, test custom)
- Estimation de complexité (faible / moyenne / forte)

## 3.2 — QCM de sélection

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

## 3.3 — Production des artefacts

Pour chaque invariant validé, l'agent produit :

**a) Une entrée dans `docs/technical/invariants.md`** suivant le template (voir `references/templates.md` section 1) :
- ID `INV-NNN` (numérotation immuable, jamais re-numérotée)
- Statut `actif`
- Énoncé, source, lien vers le script, sévérité, remédiation actionnable, exemple de violation et de correctif

**b) Un script de check dans `tools/harness/check_<sujet>.{py,js,kt,go}`** suivant les conventions :
- Sortie format `path:line: [INV-NNN] message — remédiation`
- Mode `--explain` qui décrit la règle sans rien vérifier
- Mode `--root <chemin>` pour pouvoir tester localement
- Code de sortie : 0 OK, 1 violation `error`, 2 violations `warn`
- Voir `references/harness-starters/README.md` pour le contrat que tout script doit respecter, et `references/templates.md` § 6 pour les conventions de message

**c) Une remontée vers les ADR concernés** : si la règle vient d'un ADR, l'agent propose d'ajouter dans l'ADR le champ « Invariants exécutables associés : INV-NNN ». Toujours via QCM avant modification.

## 3.4 — Proposition d'intégration

L'agent présente à l'utilisateur le snippet à ajouter à pre-commit / CI, et demande explicitement la permission de l'écrire :

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
