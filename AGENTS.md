# AGENTS.md

Conventions de contribution à ce dépôt. Elles s'appliquent à tout agent qui y écrit.

Ce dépôt **produit** des skills ; il n'en consomme pas pour lui-même. Pour savoir lequel utiliser dans un projet, voir [workflows.md](workflows.md).

## Format

Chaque skill est un dossier de `skills/` conforme à la [spécification Agent Skills](https://agentskills.io/specification) : un `SKILL.md` avec `name` et `description` en frontmatter, le détail dans `references/`.

Avant tout commit :

```bash
python3 tools/validate-skills.py --root .
```

Le hook pre-commit le lance déjà (`pre-commit install`). Ce que le script vérifie, et pourquoi chaque règle existe : `python3 tools/validate-skills.py --explain`.

## Règles d'écriture

- **Langue française.** Corps, descriptions, messages d'erreur, commentaires de script.
- **Aucun nom d'outil en dur.** Ni `mcp__*`, ni un outil de question à choix multiples, ni un chemin propre à un agent. Un skill qui nomme son outil casse chez les autres. Pour les QCM, déléguer à `clarify-with-choices`.
- **`AGENTS.md`, jamais `CLAUDE.md`.** Quand un skill écrit dans le fichier d'instructions du projet cible, la cible est `AGENTS.md`. La compatibilité Claude Code passe par un `CLAUDE.md` d'une ligne qui importe `AGENTS.md`.
- **« l'agent », jamais le nom d'un produit.** Le narrateur d'un skill est l'agent qui l'exécute, quel qu'il soit.
- **Le corps d'un `SKILL.md` reste sous 500 lignes.** Il est chargé en entier dès que le skill s'active. Au-delà, déporter dans `references/` — un fichier par branche du workflow, pour que l'agent ne lise que ce qui le concerne.
- **Une `description` est un déclencheur, pas un résumé.** C'est le seul texte chargé en permanence : il dit ce que fait le skill *et* quand l'utiliser, avec les mots que l'utilisateur emploiera. Plafond de 1024 caractères.

## Doctrine commune aux skills

Ces règles sont dans les skills eux-mêmes ; les rappeler ici évite qu'une contribution les contredise.

- **Signalement** — le skill s'annonce avant de s'appliquer, jamais silencieusement.
- **Validation par QCM** — les décisions structurantes passent par l'utilisateur.
- **Persistance sur fichiers** — plans, rapports et invariants vivent dans le dépôt, pas dans le contexte.
- **Mode dégradé explicite** — un skill fonctionne sans ses référentiels, mais le dit.
- **Pas d'auto-fix silencieux** — le harness signale ; la correction passe par un commit visible.
