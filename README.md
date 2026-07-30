# claude-skills

Skills Claude pour le développement logiciel — workflow discipliné, enforcement mécanique, revue orientée défauts.

Neuf skills qui se chaînent : la documentation alimente les invariants, les invariants contraignent l'implémentation, l'implémentation passe le gauntlet avant la revue.

## Contenu

| Skill | Rôle |
|---|---|
| [`codebase-cartographer`](skills/codebase-cartographer) | Cartographie un projet en doc métier + technique (glossaire, features, test-cases, ADR) |
| [`codebase-harness`](skills/codebase-harness) | Couche d'enforcement : invariants exécutables, pont test-cases, mutation testing, doc-gardening |
| [`plan-driven-dev`](skills/plan-driven-dev) | Workflow d'implémentation : plan validé, TDD orienté comportement, invariants dans la boucle |
| [`premerge-review`](skills/premerge-review) | Revue pré-merge : gauntlet mécanique puis quatre axes, verdict GO/NO-GO |
| [`systematic-debugging`](skills/systematic-debugging) | Diagnostic jusqu'à la cause racine prouvée — sans correctif |
| [`ai-code-remediation`](skills/ai-code-remediation) | Audit à froid d'un codebase généré par IA, huit symptômes, plan Mikado |
| [`ddd-advisor`](skills/ddd-advisor) | Audit et conseil Domain-Driven Design |
| [`behavior-driven-testing`](skills/behavior-driven-testing) | Doctrine de test par comportements plutôt que par classes |
| [`code-assimilation-quiz`](skills/code-assimilation-quiz) | Quiz d'assimilation sur le diff — apprentissage, pas revue |

## Comment les enchaîner

Voir **[workflows.md](workflows.md)** : cinq scénarios types, la circulation des artefacts entre skills, et les erreurs de chaînage courantes.

## Installation

**Claude Code** — copier les dossiers dans `~/.claude/skills/` (personnel) ou `.claude/skills/` (projet) :

```bash
cp -r skills/* ~/.claude/skills/
```

**Claude (web / desktop)** — zipper chaque skill individuellement et le téléverser dans Customize > Skills :

```bash
cd skills && for d in */; do zip -r "../${d%/}.zip" "$d"; done
```

## Conventions

Tous les skills suivent les mêmes règles :

- **Signalement** — le skill s'annonce avant de s'appliquer, jamais silencieusement
- **Validation par QCM** — les décisions structurantes passent par l'utilisateur, rien n'est appliqué d'office
- **Persistance sur fichiers** — plans, rapports et invariants vivent dans le dépôt, pas dans le contexte
- **Mode dégradé explicite** — un skill fonctionne sans ses référentiels, mais le dit
- **Pas d'auto-fix silencieux** — le harness signale, l'humain ou l'agent corrige dans un commit visible
- **Langue française**

## Contrainte de plateforme

Le champ `description` d'un `SKILL.md` est limité à **1024 caractères**. À vérifier avant tout ajout de déclencheur :

```bash
for f in skills/*/SKILL.md; do
  printf '%-28s %s\n' "$(basename $(dirname $f))" \
    "$(sed -n 's/^description: //p' "$f" | head -1 | wc -c)"
done
```
