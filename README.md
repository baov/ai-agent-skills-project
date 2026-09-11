# claude-skills

Skills Claude pour le développement logiciel — workflow discipliné, enforcement mécanique, revue orientée défauts.

Neuf skills qui se chaînent : la documentation alimente les invariants, les invariants contraignent l'implémentation, l'implémentation passe le gauntlet avant la revue.

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

## Comment les enchaîner

Le cas nominal — une feature sur un projet déjà outillé :

```
codebase-cartographer → codebase-harness      (une fois, pour outiller le projet)
plan-driven-dev → premerge-review             (à chaque feature ou bug)
```

Les autres cas (bug en production, codebase vibe-codé, tests creux…), la circulation des artefacts entre skills et les erreurs de chaînage courantes sont dans **[workflows.md](workflows.md)**.

## Installation

**Claude Code** — copier les dossiers dans `~/.claude/skills/` (personnel) ou `.claude/skills/` (projet) :

```bash
cp -r skills/* ~/.claude/skills/
```

Ou créer des liens symboliques pour que les mises à jour du dépôt soient prises en compte sans recopier :

```bash
for d in skills/*/; do ln -sfn "$PWD/${d%/}" ~/.claude/skills/; done
```

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

## Contrainte de plateforme

Le champ `description` d'un `SKILL.md` est limité à **1024 caractères**. À vérifier avant tout ajout de déclencheur (gère les descriptions YAML multilignes, compte en caractères et non en octets) :

```bash
for f in skills/*/SKILL.md; do
  n=$(awk '
    /^---$/ { c++; next }
    c == 1 && /^description:/ { d = 1; sub(/^description:[ ]*[>|]?[ ]*/, ""); s = $0; next }
    c == 1 && d && /^[ ]+/ { sub(/^[ ]+/, ""); s = (s == "" ? $0 : s " " $0); next }
    c == 1 && d { d = 0 }
    END { printf "%s", s }
  ' "$f" | LC_ALL=en_US.UTF-8 wc -m | tr -d ' ')
  printf '%-28s %5s %s\n' "$(basename "$(dirname "$f")")" "$n" "$([ "$n" -gt 1024 ] && echo '← trop long')"
done
```
