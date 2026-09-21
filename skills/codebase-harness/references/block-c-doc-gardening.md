# Brique C — Doc-gardening automatisé

Chargé par `codebase-harness` uniquement si cette brique a été retenue au QCM de scoping (étape 2). Les autres briques sont dans les fichiers `brique-*.md` voisins.

---

## 6.0 — Ce que cette brique automatise, et ce qu'elle ne peut pas

Le doc-gardening fait deux choses de nature différente :

| | Nature | Besoin |
|---|---|---|
| **Exécuter les checks** et collecter les violations | Déterministe | Un ordonnanceur. C'est tout. |
| **Interpréter la dérive** — invariant devenu obsolète, test-case orphelin, doc qui ne décrit plus le code | Jugement | Un agent. |

La première partie tourne partout. La seconde suppose que l'hôte sache planifier l'exécution d'un agent — ce que tous ne savent pas faire.

**Par défaut, ne livrer que la première.** Un rapport mécanique hebdomadaire vaut mieux qu'une interprétation qui ne s'exécute jamais. La seconde s'ajoute si, et seulement si, l'hôte la permet.

## 6.1 — Cadence

L'agent propose les cadences via QCM (voir `clarify-with-choices`) :

| Cadence | Cron | Cas d'usage |
|---------|------|-------------|
| Quotidienne | `0 9 * * *` | Projet actif, beaucoup de contributions |
| Hebdomadaire (défaut) | `0 9 * * 1` | Projet en développement normal |
| Bi-mensuelle | `0 9 1,15 * *` | Projet en maintenance |
| Mensuelle | `0 9 1 * *` | Projet stable |

## 6.2 — Ordonnanceur : choisir le support

L'agent détecte ce dont le projet dispose et propose **un seul** support, dans cet ordre de préférence :

| Support | Condition | Pourquoi ce rang |
|---|---|---|
| **GitHub Actions planifié** | `.github/` présent | Versionné avec le code, visible par l'équipe, aucun secret requis |
| **Pipeline planifié GitLab** | `.gitlab-ci.yml` présent | Idem ; la planification se configure dans *CI/CD → Schedules* |
| **Ordonnanceur de l'agent hôte** | L'hôte expose un mécanisme de tâche planifiée | Seul support capable d'ajouter l'interprétation (voir 6.4) |
| **cron local** | Aucun des précédents | Repli. Ne tourne que sur la machine où il est posé — le dire à l'utilisateur. |

Ne jamais en installer deux : deux rapports pour la même dérive, c'est du bruit qui finit ignoré.

## 6.3 — Rapport mécanique (portable, par défaut)

Le job exécute tous les scripts de `tools/harness/` et agrège leur sortie. Ils respectent le contrat commun (`--explain`, `--root`, codes 0/1/2), donc l'agrégation ne connaît aucun script individuellement.

```yaml
# .github/workflows/doc-gardening.yml
name: doc-gardening

on:
  schedule:
    - cron: '0 9 * * 1'   # cadence retenue au QCM
  workflow_dispatch:       # déclenchement manuel, pour tester sans attendre

permissions:
  contents: read
  issues: write

jobs:
  rapport:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Exécution des checks du harness
        id: checks
        run: |
          : > rapport.md
          for script in tools/harness/*; do
            [ -x "$script" ] || continue
            sortie=$("$script" --root . 2>&1) || true
            [ -n "$sortie" ] && printf '## %s\n\n```\n%s\n```\n\n' "$(basename "$script")" "$sortie" >> rapport.md
          done
          if [ -s rapport.md ]; then echo "derive=oui" >> "$GITHUB_OUTPUT"; fi

      # Silence = OK. Aucune issue ouverte quand tout est au vert.
      - name: Remontée
        if: steps.checks.outputs.derive == 'oui'
        run: gh issue create --title "Doc-gardening — dérives détectées" --body-file rapport.md
        env:
          GH_TOKEN: ${{ github.token }}
```

Pour GitLab, le même corps de script dans un job dont la règle est `if: $CI_PIPELINE_SOURCE == "schedule"`, la planification étant définie dans *CI/CD → Schedules*.

**Présenter le fichier à l'utilisateur et demander la permission avant de l'écrire**, comme pour les autres briques.

## 6.4 — Interprétation (optionnelle, dépend de l'hôte)

Si l'hôte expose un ordonnanceur capable de lancer un agent, proposer en plus une tâche planifiée portant ce prompt :

```
Relance le skill codebase-harness en mode mise à jour sur le projet [chemin].
Ne modifie aucun fichier automatiquement — produis uniquement un rapport
consolidé : violations d'invariants nouvelles, invariants obsolètes,
test-cases dérivés (covered_broken ou nouveau test sans test-case),
régression du score de mutation par rapport à la baseline et mutants
survivants nouveaux, doc qui aurait dérivé. Si tout est au vert, dis-le et
n'envoie rien d'autre.
```

Le nom de l'outil de planification varie selon l'agent : ne pas le coder en dur, utiliser celui que l'hôte expose. Si l'hôte n'en expose aucun, **ne pas simuler** — le dire, et s'en tenir au rapport mécanique du 6.3.

Présenter le prompt et la cadence, **demander explicitement la permission**, et créer la tâche seulement après confirmation.

## 6.5 — Garde-fous

La tâche ne doit JAMAIS appliquer de changements sans QCM, même quand elle s'exécute sans humain au clavier. Son rôle est de produire un signal, pas un fix.

Si le rapport est vide (tout au vert), elle ne produit aucun message — **silence = OK**. Un rapport « rien à signaler » envoyé chaque semaine apprend à l'équipe à ne plus l'ouvrir.

---
