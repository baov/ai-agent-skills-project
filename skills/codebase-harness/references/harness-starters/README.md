# Starters de scripts harness

Ce dossier contient des implémentations de référence des scripts que le skill génère. **Ce sont des exemples, pas une bibliothèque.** Le skill génère toujours le script adapté à la stack détectée ; ces fichiers servent à montrer le contrat en action et à éviter de le réinventer.

**En cas de divergence, le contrat prime sur le starter.** Un starter qui s'écarterait des conventions de `templates.md` § 6 est à corriger, pas à imiter.

## Contenu

| Fichier | Brique | Portée |
|---------|--------|--------|
| `check_test_coverage.py` | B | Générique — ne lit que du markdown et des chemins, fonctionne quelle que soit la stack du projet |

## Ce que ce dossier ne contient volontairement pas

**Des linters par stack (brique A).** Un check d'isolation de couche s'écrit en ArchUnit sur JVM, en dependency-cruiser sur JS/TS, en AST sur Python — trois implémentations sans code commun. Les figer ici produirait un dossier qui vieillit plus vite que les stacks. Le skill les génère à partir des conventions de `templates.md` § 6.

**Des configs de mutation (brique D).** Voir SKILL.md § 5.3.a : le cahier des charges en cinq points est la source de vérité, l'outillage est détecté au run.

Si tu figes ici un starter éprouvé en interne, ajoute-le au tableau ci-dessus et note la stack visée. Un starter non documenté est un starter que personne ne réutilisera.

## Le contrat, en résumé

Tout script de `tools/harness/`, quelle que soit la brique :

- accepte `--explain` (décrit sans vérifier) et `--root <chemin>`
- écrit une ligne par violation : `path:line: [INV-NNN] message — remédiation`
- sort `0` (OK), `1` (violation `error`), `2` (violations `warn` uniquement)
- ne corrige rien, ne modifie ni sa config ni son seuil
- n'exige aucune installation de dépendance pour les vérifications documentaires
