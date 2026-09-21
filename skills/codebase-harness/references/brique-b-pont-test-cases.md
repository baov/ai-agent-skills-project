# Brique B — Pont test-cases ↔ tests réels

Chargé par `codebase-harness` uniquement si cette brique a été retenue au QCM de scoping (étape 2). Les autres briques sont dans les fichiers `brique-*.md` voisins.

---

## 4.1 — Pré-requis

Le skill cherche `docs/metier/test-cases/**/*.md`. Si rien n'existe, il signale à l'utilisateur :

> « Aucun test-case trouvé sous docs/metier/test-cases/. Lance d'abord `codebase-cartographer` ou crée toi-même quelques fichiers, puis reviens ici. »

Et passe à la brique suivante (ou termine).

## 4.2 — Décoration des test-cases

Pour chaque test-case existant, l'agent ajoute un front-matter YAML en tête de fichier :

```yaml
---
feature: panier
type: nominal              # nominal | erreur | edge-case
priorite: critique         # critique | importante | nice-to-have
automated_test: tests/test_panier.py::test_ajout_produit   # ou null
status: covered            # covered | pending | manual
---
```

L'agent tente de **pré-remplir** chaque champ :
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

## 4.3 — Production du script de vérification

L'agent écrit `tools/harness/check_test_coverage.*` — une implémentation de référence complète et sans dépendance est fournie dans `references/harness-starters/check_test_coverage.py`. Elle ne lit que du markdown et des chemins, donc elle convient telle quelle à la plupart des projets quelle que soit leur stack ; l'adapter surtout au niveau des globs de recherche des tests. Le script :

- Parcourt `docs/metier/test-cases/**/*.md`
- Parse chaque front-matter YAML
- Classe en `covered_ok` / `covered_broken` / `pending` / `manual`
- Liste les tests orphelins (existant dans le code mais sans test-case associé)
- Sort 0 si tout va bien, 1 si au moins un `covered_broken`, 2 si uniquement des warns

## 4.4 — Intégration

Comme pour la brique A : l'agent propose le snippet pre-commit/CI et demande la permission de l'ajouter. Par défaut, recommandation : `warn` (exit 2 toléré) au début, `error` (exit 1 bloquant) quand `covered_broken` est à zéro.

---
