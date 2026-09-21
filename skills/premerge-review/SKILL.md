---
name: premerge-review
description: Revue de code pré-merge orientée défauts — fait d'abord passer la branche par un gauntlet de checks mécaniques (tests, lint, invariants du harness, pont test-cases, mutation sur le diff), puis analyse le diff par rapport à main avec une profondeur calibrée sur la criticité, et produit un rapport structuré avec verdict GO/NO-GO. Un gauntlet rouge arrête la revue : inutile de relire à la main un diff appelé à changer. À utiliser SYSTÉMATIQUEMENT quand l'utilisateur demande une "code review", "revue de code", "relis ma branche", "vérifie mon diff avant merge", "est-ce que ma MR est prête", "passe en revue ce que j'ai fait", ou avant tout merge dans le cadre d'un pipeline agentique (checkpoint pré-merge). Couvre quatre axes — bugs/régressions, sécurité, conformité ADR/architecture, dette/lisibilité. Ne pas confondre avec code-assimilation-quiz (apprentissage du développeur, pas recherche de défauts) ni avec ai-code-remediation (audit à froid d'un codebase entier, pas d'un diff).
---

# Premerge Review

Revue de code orientée défauts sur le diff d'une branche, avant merge. L'objectif est de jouer le rôle du relecteur exigeant mais juste : trouver ce qui doit être corrigé avant que le code n'atteigne `main`, sans noyer le signal sous du bruit stylistique.

**Premier principe cardinal : la revue est en lecture seule.** Ne jamais modifier le code pendant une revue. Si l'utilisateur veut corriger les findings ensuite, c'est le rôle de `plan-driven-dev` (ou du pipeline en cours) — le rapport de revue devient alors l'entrée du plan de correction.

**Second principe cardinal : l'attention se dépense après la machine, pas avant.** Tout ce qu'un check mécanique sait trancher doit être tranché avant que la revue ne commence. Relire à la main un diff que le harness rejette déjà est du temps perdu deux fois : le correctif changera le diff, et il faudra tout relire. D'où l'ordre imposé — gauntlet, puis revue. La revue existe pour ce qu'aucune machine ne sait voir : une intention qui ne correspond pas au besoin, un contrat implicite rompu, une complexité qui coûtera cher dans six mois.

## Phase 0 — Établir le diff

Avant toute analyse, fixer précisément ce qui est revu :

1. Identifier la branche cible (par défaut `main`, sinon `master`, sinon demander).
2. Calculer la base de comparaison avec `git merge-base` pour ne revoir que les changements de la branche, pas les commits arrivés sur main entre-temps :
   ```bash
   git fetch origin
   BASE=$(git merge-base HEAD origin/main)
   git diff --stat $BASE..HEAD
   git log --oneline $BASE..HEAD
   ```
3. Annoncer le périmètre à l'utilisateur : nombre de fichiers, volume du diff, liste des commits. Si le diff est très gros (>~2000 lignes), proposer de découper la revue par sous-ensemble cohérent plutôt que de tout survoler superficiellement — une revue diluée rate les vrais défauts.

Ne pas se limiter au diff brut : pour chaque fichier modifié, lire suffisamment de contexte autour des changements (la fonction entière, la classe, les appelants si pertinent). Beaucoup de bugs ne sont visibles que depuis le code non modifié qui dépend du code modifié.

## Phase 1 — Charger le contexte projet

La qualité de la revue dépend de ce qu'on sait du projet. Chercher, dans cet ordre :

- `AGENTS.md` — conventions du projet.
- `docs/technical/` — architecture, ADR, stratégie de test. Les ADR sont la référence pour l'axe conformité : un changement qui contredit une décision actée est au minimum un finding majeur.
- `docs/technical/invariants.md` et `tools/harness/` — inventorier ce qui existe (invariants documentés, scripts disponibles, seuil de mutation et sa baseline). Les invariants servent de grille de lecture pour l'axe conformité ; leur **exécution** a lieu en phase 3, pas ici.
- `docs/business/` — glossaire et test-cases, pour juger si le diff respecte le langage du domaine et si les comportements modifiés sont couverts.

**Mode dégradé** : si tout ou partie de cette documentation est absente, poursuivre la revue sur les trois axes restants pleinement, et traiter l'axe conformité à partir des conventions observables dans le code existant (cohérence avec les patterns en place). Signaler explicitement dans le rapport ce qui n'a pas pu être vérifié faute de référentiel — l'absence de vérification n'est pas une absence de problème.

## Phase 2 — Calibrer la profondeur sur la criticité

Toutes les branches ne méritent pas la même rigueur, et prétendre le contraire produit soit des revues diluées partout, soit un coût insoutenable. La criticité est la variable qui gouverne la profondeur — elle se détermine avant de lire, à partir de ce que le diff touche.

Signaux de criticité, par ordre de poids :

- Le diff touche du code exercé par des test-cases marqués `priorite: critique` (front-matter de la brique B du harness).
- Il touche la couche domaine, ou un module désigné comme critique par un ADR.
- Il touche l'authentification, l'autorisation, un flux de paiement, une migration de données, ou une frontière exposée publiquement (API, webhook, format persisté).
- Il modifie un contrat consommé ailleurs : signature publique, schéma, événement.

| Niveau | Quand | Profondeur de revue |
|--------|-------|---------------------|
| **Critique** | Au moins un signal fort ci-dessus | Quatre axes en profondeur, lecture du contexte élargie aux appelants, mutation testing sur le diff en phase 3 |
| **Standard** | Le cas courant | Quatre axes, lecture du contexte autour des changements |
| **Faible** | Doc, commentaires, tests seuls, renommage mécanique, montée de version sans changement de comportement | Axes 1 et 2 en survol ciblé, axes 3 et 4 seulement si un signal apparaît |

Annoncer le niveau retenu et le signal qui l'a déclenché, en une ligne. L'utilisateur peut le corriger ; sans réponse, poursuivre au niveau annoncé — le checkpoint doit rester prévisible pour un pipeline.

**Deux garde-fous.** La criticité module la profondeur, jamais le périmètre : même en niveau faible, un diff est lu en entier. Et elle ne descend jamais en dessous de « standard » quand le diff touche la sécurité, quelle que soit sa taille — une correction d'une ligne dans un contrôle d'accès n'est pas un petit diff.

## Phase 3 — Le gauntlet

Avant toute lecture, faire passer la branche par ce que la machine sait vérifier seule. L'ordre n'est pas une préférence : c'est ce qui rend la revue rentable.

### Ce qui compose le gauntlet

Exécuter, dans cet ordre, ce qui existe dans le projet :

1. **La suite de tests** sur la branche. Une suite rouge rend tout le reste sans objet.
2. **Le linter et le formateur** du projet, dans leur configuration versionnée.
3. **Les invariants du harness** — `bash tools/harness/run_all.sh`, ou les scripts individuels de `tools/harness/`.
4. **Le pont test-cases ↔ tests** — `check_test_coverage.*`, qui signale les comportements documentés dont le test a disparu.
5. **Le mutation testing sur le diff** — `run_mutation.* --scope diff` — uniquement en criticité **critique**, et seulement si la brique D est installée. C'est le seul check du gauntlet dont le coût justifie d'être conditionnel.

Reporter pour chacun : exécuté / non disponible / échoué, avec la sortie utile.

### La règle d'arrêt

**Si un check du gauntlet échoue en sévérité `error`, la revue s'arrête là.** Verdict NO-GO immédiat, rapport limité à la section Gauntlet, pas de revue sur quatre axes.

La justification tient en deux points, et mérite d'être dite à l'utilisateur qui trouverait ça brutal : le correctif va modifier le diff, donc toute lecture faite maintenant sera à refaire ; et l'attention dépensée sur du code que la machine rejette déjà est prise sur celle qui manquera plus tard, sur ce que la machine ne voit pas.

Deux nuances :

- Les échecs en sévérité `warn` n'arrêtent rien. Ils sont repris comme findings majeurs ou mineurs en phase 5, selon leur nature.
- Si l'utilisateur demande explicitement la revue complète malgré un gauntlet rouge, la faire — en signalant en tête de rapport que le diff est appelé à changer.

### Mode dégradé — et pourquoi il alourdit la revue

Si le projet n'a ni harness, ni suite de tests exploitable, le dire clairement et poursuivre. Mais **l'absence de gauntlet augmente la profondeur de revue au lieu de la réduire** : ce que la machine ne vérifie pas, personne ne le vérifie. Concrètement, un projet sans harness passe au niveau de profondeur immédiatement supérieur à celui déterminé en phase 2, et la section « Vérifications non réalisées » du rapport devient la partie la plus importante du document.

C'est aussi le bon moment pour signaler que `codebase-harness` existe — une fois, sans insister, et jamais à la place de la revue demandée.

## Phase 4 — Revue sur quatre axes

Parcourir le diff avec quatre lectures distinctes. Une seule passe qui "regarde tout" rate des choses ; quatre passes ciblées avec une question précise en tête sont plus fiables.

### Ordre de lecture : le quoi avant le comment

En criticité **critique**, lire d'abord les test-cases de `docs/business/test-cases/` que le diff touche — via le champ `automated_test` du front-matter, qui pointe vers les tests modifiés. Le code ensuite.

La raison : ces fichiers décrivent le comportement attendu (contexte, action, résultat attendu), et c'est la seule couche que la revue peut valider contre le besoin réel. Le code, lui, ne peut être validé que contre ces fichiers. Les lire après avoir lu le code, c'est les lire en cherchant à confirmer ce qu'on vient de comprendre.

En criticité standard, les survoler. En criticité faible, les ignorer sauf si le diff les modifie.

### Axe 1 — Bugs et régressions
La question : *qu'est-ce qui va casser ?*
- Cas limites non gérés (null/vide/zéro, bornes, concurrence, encodage, fuseaux).
- Changements de contrat : signature, format de retour, comportement d'erreur — vérifier les appelants existants.
- Logique inversée, conditions incomplètes, off-by-one, état partagé muté.
- Tests : les comportements ajoutés ou modifiés sont-ils couverts par des tests qui testent le comportement (et non la structure) ? Un comportement modifié sans test modifié est suspect.

### Axe 2 — Sécurité
La question : *qu'est-ce qu'un attaquant ou une donnée hostile en ferait ?*
- Entrées non validées, injections (SQL, commande, chemin, template), désérialisation.
- Secrets en dur, logs verbeux sur données sensibles, permissions élargies.
- AuthN/AuthZ : tout nouveau point d'entrée vérifie-t-il qui appelle et avec quel droit ?
- Dépendances ajoutées : provenance et surface.

### Axe 3 — Conformité ADR / architecture
La question : *ce changement respecte-t-il les décisions actées ?*
- Confronter chaque changement structurel aux ADR et invariants chargés en Phase 1.
- Frontières : dépendances entre couches/modules qui violent le sens autorisé, logique métier qui fuit dans l'infrastructure ou l'UI.
- En mode dégradé : cohérence avec les patterns dominants du codebase (un troisième style de gestion d'erreur n'est pas une amélioration).
- **Le comportement décrit est-il le bon ?** Un test-case modifié par le diff, ou ajouté, décrit-il ce que le métier attend vraiment ? Un test-case qui décrit le mauvais comportement est un finding **bloquant** même si le code l'implémente parfaitement et que tous les tests passent — c'est la seule erreur qu'aucun check mécanique ne peut attraper. Confronter au glossaire de `docs/business/` et signaler tout écart de vocabulaire : un test-case qui invente un terme absent du glossaire signale souvent un malentendu sur le besoin.

### Axe 4 — Dette et lisibilité
La question : *le prochain développeur comprendra-t-il, et à quel prix ?*
- Duplication introduite, complexité accidentelle, nommage qui trahit l'intention ou le glossaire métier.
- Code mort, TODO sans ticket, commentaires qui mentent.
- Ne signaler ici que ce qui a un coût réel de maintenance — les préférences purement stylistiques déjà gérées par un linter ne méritent pas un finding.

## Phase 5 — Classer les findings

Chaque finding reçoit une sévérité. Les définitions comptent : c'est elles qui rendent le verdict objectif.

- **Bloquant** — défaut qui causera un incident, une faille exploitable, une corruption de données, ou une violation frontale d'un ADR. Mergé tel quel, il faudra revenir en urgence.
- **Majeur** — défaut réel qui dégrade la fiabilité, la sécurité ou l'architecture, mais sans danger immédiat : cas limite plausible non géré, comportement modifié sans test, dette structurelle notable.
- **Mineur** — amélioration souhaitable sans risque : lisibilité, nommage, petite duplication.

En cas d'hésitation entre deux niveaux, retenir le niveau inférieur mais le dire dans le finding — la crédibilité de la revue repose sur des bloquants qui bloquent vraiment. Une revue qui crie au loup finit ignorée.

## Phase 6 — Rapport et verdict

### Règle de verdict

- **NO-GO** si un check du gauntlet échoue en sévérité `error` (phase 3), OU si au moins un finding **bloquant**, OU si au moins trois findings **majeurs**.
- **GO** sinon. Les findings majeurs (≤2) et mineurs restants sont listés comme dette à traiter, sans bloquer le merge.

Un gauntlet rouge est un NO-GO **quelle que soit la criticité**. La criticité module ce qu'on lit, jamais ce qu'on laisse passer.

Appliquer la règle mécaniquement — le jugement s'exerce dans la classification (phase 5), pas dans le verdict. C'est ce qui rend le checkpoint prévisible pour un pipeline.

### Structure du rapport

Écrire le rapport dans `.reviews/<branche>-<AAAA-MM-JJ>.md` (créer le dossier si besoin), puis en présenter la synthèse en conversation. TOUJOURS suivre cette structure :

```markdown
# Revue pré-merge — <branche>
**Verdict : GO | NO-GO**
**Date** : … · **Base** : <sha base>..<sha head> · **Périmètre** : N fichiers, ±N lignes
**Criticité** : critique | standard | faible — <signal qui l'a déclenchée>

## Synthèse
2-4 phrases : nature du changement, état général, raison du verdict.

## Gauntlet
| Check | Résultat |
|-------|----------|
| Suite de tests | OK / ÉCHEC / non disponible |
| Lint / format | … |
| Invariants harness | … (INV-NNN en échec, le cas échéant) |
| Pont test-cases | … |
| Mutation (diff) | … (score, seuil) — ou « non applicable : criticité <niveau> » |
| Test-cases touchés | N relus / N survolés / non applicable — lister les fichiers |

En cas d'arrêt sur gauntlet rouge, s'arrêter après cette section et l'indiquer explicitement : « Revue sur quatre axes non effectuée — le diff est appelé à changer. »

## Findings
### Bloquants
- **[B1] <titre>** — `fichier:ligne` · axe : <bugs|sécurité|conformité|dette>
  Constat, conséquence concrète, recommandation.
### Majeurs
- **[M1] …** (même format)
### Mineurs
- **[m1] …** (même format, recommandation en une ligne)

## Vérifications non réalisées
Référentiels absents (ADR, invariants, test-cases métier) et impact sur la revue.

## Points positifs
1-3 points notables — une revue honnête signale aussi ce qui est bien fait.
```

Chaque finding cite l'endroit exact (`fichier:ligne`) et propose une recommandation actionnable. Un finding sans localisation ni recommandation n'aide personne.

### Après le verdict

- **NO-GO sur gauntlet** : proposer d'enchaîner sur la correction via `plan-driven-dev`, puis **relancer la revue depuis la phase 3** — le diff ayant changé, la revue précédente ne vaut plus.
- **NO-GO sur findings** : proposer d'enchaîner sur la correction des bloquants/majeurs via `plan-driven-dev`, avec le rapport comme entrée.
- **GO** : rappeler les majeurs restants éventuels pour qu'ils soient tracés (ticket, `.plans/FEEDBACK.md`, ou backlog selon les usages du projet).
