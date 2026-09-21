# POV — Proof Over Vibes

> Agent skills for software development: documented, enforced, reviewed — not guessed.

Skills de développement logiciel pour agents IA — workflow discipliné, enforcement mécanique, revue orientée défauts.

Dix skills qui se chaînent : la documentation alimente les invariants, les invariants contraignent l'implémentation, l'implémentation passe le gauntlet avant la revue.

Conformes à la [spécification Agent Skills](https://agentskills.io/specification), donc chargés nativement — avec leur déclenchement par description — par Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, Amp, OpenCode et les autres clients conformes.

## Contenu

**Points d'entrée** — déclenchés par une demande de l'utilisateur.

| Skill | Rôle | Produit |
|---|---|---|
| [`codebase-cartographer`](skills/codebase-cartographer) | Cartographie un projet en doc métier + technique (glossaire, features, test-cases, ADR) | `docs/`, section dans `CLAUDE.md` |
| [`codebase-harness`](skills/codebase-harness) | Couche d'enforcement : invariants exécutables, pont test-cases, mutation testing, doc-gardening | `tools/harness/`, `docs/technique/invariants.md` |
| [`plan-driven-dev`](skills/plan-driven-dev) | Workflow d'implémentation : plan validé, TDD orienté comportement, invariants dans la boucle | `.plans/` |
| [`premerge-review`](skills/premerge-review) | Revue pré-merge : gauntlet mécanique puis quatre axes, verdict GO/NO-GO | `.reviews/` |
| [`systematic-debugging`](skills/systematic-debugging) | Diagnostic jusqu'à la cause racine prouvée — sans correctif | — |
| [`ai-code-remediation`](skills/ai-code-remediation) | Audit à froid d'un codebase généré par IA, huit symptômes, plan Mikado | `.audit/` |
| [`code-assimilation-quiz`](skills/code-assimilation-quiz) | Quiz d'assimilation sur le diff — apprentissage, pas revue. **Jamais automatique** | — |

**Skills d'appui** — chargés par un autre skill, rarement demandés directement.

| Skill | Rôle | Chargé par |
|---|---|---|
| [`behavior-driven-testing`](skills/behavior-driven-testing) | Doctrine de test par comportements plutôt que par classes | `plan-driven-dev`, `ai-code-remediation` |
| [`ddd-advisor`](skills/ddd-advisor) | Audit et conseil Domain-Driven Design | `ai-code-remediation` |
| [`clarify-with-qcm`](skills/clarify-with-qcm) | Doctrine de validation par QCM, et son mode dégradé selon l'agent hôte | `codebase-cartographer`, `codebase-harness`, `ddd-advisor` |

## Comment les enchaîner

Le cas nominal — une feature sur un projet déjà outillé :

```
codebase-cartographer → codebase-harness      (une fois, pour outiller le projet)
plan-driven-dev → premerge-review             (à chaque feature ou bug)
```

Les autres cas (bug en production, codebase vibe-codé, tests creux…), la circulation des artefacts entre skills et les erreurs de chaînage courantes sont dans **[workflows.md](workflows.md)**.

## Installation

```bash
./install.sh                    # pour toi, sur cette machine
./install.sh --scope project --into ~/projets/mon-app
```

Le script pose des liens symboliques — les mises à jour du dépôt sont prises en compte sans réinstaller. `--copy` produit des copies indépendantes, `--help` détaille les options.

À la main, si tu préfères : les skills sont des dossiers, il suffit de les mettre là où le client les cherche.

| Client | Portée utilisateur | Portée projet |
|---|---|---|
| Codex, Cursor, Gemini CLI, Copilot, Amp, OpenCode… | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |

`.agents/skills/` est le répertoire interopérable : la plupart des clients conformes l'y cherchent, souvent en priorité sur leur répertoire propre.

**Claude (web / desktop)** — zipper chaque skill individuellement et le téléverser dans Customize > Skills :

```bash
cd skills && for d in */; do zip -r "../${d%/}.zip" "$d"; done
```

**Publier sa propre copie** — `setup-repo.sh` crée un dépôt GitHub privé et y pousse le contenu, avec l'authentification `gh` existante :

```bash
./setup-repo.sh [nom-du-depot]
```

## Conventions

Tous les skills suivent les mêmes règles :

- **Signalement** — le skill s'annonce avant de s'appliquer, jamais silencieusement
- **Validation par QCM** — les décisions structurantes passent par l'utilisateur, rien n'est appliqué d'office
- **Persistance sur fichiers** — plans, rapports et invariants vivent dans le dépôt, pas dans le contexte
- **Mode dégradé explicite** — un skill fonctionne sans ses référentiels, mais le dit
- **Pas d'auto-fix silencieux** — le harness signale, l'humain ou l'agent corrige dans un commit visible
- **Langue française**

## Contribuer

Les conventions d'écriture — format, langue, interdits — sont dans [AGENTS.md](AGENTS.md).

Elles sont vérifiées mécaniquement, parce qu'un check non exécuté n'est pas un check :

```bash
python3 tools/validate-skills.py --root .
```

Aucune dépendance à installer. Le script couvre les règles de la spécification (nom, plafond de 1024 caractères sur les `description`, correspondance nom/dossier) et signale les `SKILL.md` qui dépassent 500 lignes. Il tourne en pre-commit (`pre-commit install`) et en CI. `--explain` décrit chaque règle sans rien vérifier.
