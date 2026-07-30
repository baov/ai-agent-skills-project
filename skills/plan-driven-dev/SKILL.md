---
name: plan-driven-dev
description: Workflow discipliné pour implémenter une nouvelle fonctionnalité OU corriger un bug dans un projet de code existant. Force une phase de compréhension du contexte avant toute écriture, produit un plan persistant validé étape par étape, applique un TDD orienté comportement, et capitalise les leçons apprises. Utilise cette skill systématiquement dès qu'un prompt utilisateur ressemble à une tâche de code dans un projet existant (mots-clés type "implémente", "ajoute", "corrige", "fix", "bug", "feature", "refactor", "modifie", "il faut que", ou toute demande de modification de code multi-fichier). La skill commence par se signaler et demander validation avant de s'appliquer — ne pas l'invoquer silencieusement. Charge les invariants du harness du projet à l'étape contexte et les vérifie dans la boucle TDD, pour qu'aucune violation ne soit découverte à la revue.
---

# plan-driven-dev

Workflow discipliné qui force Claude à comprendre avant de coder, planifier avant d'agir, et capitaliser après avoir fini. Le **plan** est un fichier persistant sur disque (`.plans/in-progress/<slug>.md`) qui sert de boussole tout au long de la tâche.

---

## Étape 0 — Signalement et validation

Dès que tu identifies une tâche qui ressemble à une feature ou un bug, **arrête-toi avant d'agir** et propose la skill :

> *« Cette tâche ressemble à une feature/un bug à implémenter dans le projet. Je peux appliquer le workflow `plan-driven-dev` (compréhension du contexte → plan validé → TDD → review). Tu veux qu'on le suive ?»*

- Si **non** → code en mode normal, n'applique pas la suite.
- Si **oui** → continue avec l'étape 1.

Ne saute jamais cette étape de validation, même si l'utilisateur semble pressé.

---

## Étape 1 — Comprendre le contexte

Toujours dans cet ordre :

1. **Vue d'ensemble du projet**
   - Lire `README.md` (et `CONTRIBUTING.md` si présent)
   - Inspecter l'arborescence du projet (au moins 2 niveaux)
   - Identifier le langage, le framework, l'outil de test, le linter/typecheck
   - Repérer les conventions visibles (organisation des dossiers, naming, style)

2. **Fichiers directement concernés + dépendances immédiates**
   - Lire les fichiers que la tâche touche évidemment
   - Suivre les imports/exports pour comprendre les couplages

3. **Usages du symbole/fonction à modifier**
   - Faire un `grep` ou recherche d'usages avant toute modification
   - Comprendre l'impact potentiel des changements

4. **Couche d'enforcement, si le projet en a une**
   - Lire la section « Harness » de `CLAUDE.md` et `docs/technique/invariants.md`
   - Inventorier les scripts disponibles dans `tools/harness/` et savoir lequel couvre quoi
   - Retenir les invariants qui s'appliquent aux fichiers que la tâche va toucher — ce sont des contraintes de conception, pas des vérifications de fin de course
   - Reporter ces invariants dans la section 3 (Contexte) du plan, avec leur ID. Un plan qui ignore un invariant applicable produira du code qui échouera au gauntlet.

   Si le projet n'a pas de harness, passer — sans le signaler, ce n'est pas le sujet de la tâche en cours.

**En parallèle de tout ce qui précède** : lire `.plans/FEEDBACK.md` s'il existe. Ce fichier contient les leçons accumulées des tâches précédentes (conventions du projet, pièges déjà rencontrés, principes durables). **Appliquer ces leçons** dans tout ce qui suit.

Si `.plans/` n'existe pas encore, crée le dossier maintenant (avec ses sous-dossiers `in-progress/`, `done/`, `aborted/`).

---

## Étape 2 — Reformulation de l'objectif → VALIDATION

Reformule l'objectif avec tes propres mots, en 2-3 phrases. Présente-la à l'utilisateur et **attends une validation explicite** avant de continuer.

Exemple : *« Si je comprends bien : tu veux X parce que Y, et le résultat attendu est Z. Tu valides ? »*

Si l'utilisateur corrige → reformule à nouveau jusqu'à validation.

---

## Étape 3 — Plan → VALIDATION

Crée le fichier `.plans/in-progress/<slug>.md` (slug = identifiant court en kebab-case dérivé de la tâche, ex: `add-user-export`, `fix-login-timeout`).

**Le fichier doit contenir EXACTEMENT ces 10 sections, dans cet ordre :**

```markdown
# <Titre de la tâche>

## 1. Métadonnées
- **Type**: feature | bug
- **Date**: YYYY-MM-DD
- **Statut**: in-progress

## 2. Objectif
<reformulation validée à l'étape 2>

## 3. Contexte
<résumé des découvertes faites à l'étape 1 : fichiers clés, conventions, contraintes>

## 4. Comportements attendus
<liste à puces des comportements à tester — épine dorsale du TDD>
<format par comportement : étant donné <contexte>, quand <action>, alors <résultat observable> — **frontière de test** : <cas d'usage / port / API de module par lequel le test passe>>
- Nominal : ...
- Edge case 1 : ...
- Edge case 2 : ...

## 5. Étapes
<checklist ordonnée des actions de code>
- [ ] Étape 1 : ...
- [ ] Étape 2 : ...

## 6. Risques & edge cases
<zones sensibles, ce qui pourrait casser, dépendances cachées>

## 7. Hors scope
<ce qu'on ne fait PAS — anti-dérive>

## 8. Déviations
<vide pour l'instant — journal à remplir si on s'écarte du plan>

## 9. Auto-review
<vide pour l'instant — rempli à la clôture>

## 10. Actions de suivi
<vide pour l'instant — rempli à la clôture>
```

Une fois le fichier rédigé, présente-le à l'utilisateur et **attends validation**. S'il demande des modifications, mets à jour le fichier puis redemande validation.

---

## Étape 4 — Risques & edge cases → VALIDATION

Tu as déjà rempli la section 6 dans le plan. À cette étape, **prends un moment dédié** pour la passer en revue avec l'utilisateur :

> *« Voici les risques et edge cases que j'ai identifiés [...]. Tu vois quelque chose à ajouter ou à enlever ? »*

Si l'utilisateur ajoute des éléments → mettre à jour la section 6 ET potentiellement la section 4 (comportements attendus) du plan.

Attends validation explicite avant de passer à l'écriture du code.

---

## Étape 4.5 — Check "plan prêt à dérouler" → décision modèle

Le plan vient d'être validé (étapes 3 et 4). Avant de basculer en mode exécution, **évalue objectivement si le plan est assez explicite pour être déroulé mécaniquement**, sans nouvel arbitrage de fond.

Passe la section 5 (Étapes) et la section 4 (Comportements attendus) au crible de ces critères déterministes :

- [ ] Chaque étape nomme les fichiers ou symboles touchés (pas de « adapter le service concerné » sans dire lequel)
- [ ] Chaque étape a un verbe d'action concret (« créer », « renommer », « ajouter le champ X »), pas un verbe vague (« gérer », « traiter », « voir selon »)
- [ ] Chaque comportement attendu a un critère de validation observable (un test possible, pas « ça doit bien marcher »)
- [ ] Chaque comportement attendu indique sa frontière de test (cas d'usage, port, API de module — pas « à voir » ni une classe interne par défaut)
- [ ] Aucune étape ne contient de TODO, « à définir », « à voir », « selon le cas »
- [ ] Les dépendances entre étapes sont claires (ordre explicite, pas de « en parallèle ou pas, à voir »)

**Si tous les critères sont cochés** → le plan est déroulable mécaniquement. Continue vers l'étape 5 sans rien dire de plus à l'utilisateur.

**Si au moins un critère échoue** → STOP. Présente le constat à l'utilisateur :

> *« Le plan est validé sur le fond, mais en le relisant pour l'exécution, je repère [N] zones qui demanderaient un arbitrage en cours de route : [liste les critères échoués avec l'extrait concerné].*
>
> *Deux options :*
> *(a) **Raffiner le plan ici** jusqu'à ce qu'il soit déroulable mécaniquement (je peux le faire maintenant si tu es sur un modèle fort type Opus).*
> *(b) **Basculer sur un modèle fort pour l'exécution** si tu es actuellement sur un modèle plus léger (Sonnet/Haiku) : ouvre un nouveau chat sur Opus, je reprendrai à l'étape 5 avec le plan existant dans `.plans/in-progress/<slug>.md`.*
>
> *Que préfères-tu ?»*

Note importante : Claude ne peut pas changer de modèle lui-même. C'est à l'utilisateur d'ouvrir un nouveau chat avec le modèle adéquat. Le plan sur disque est précisément là pour que la bascule soit sans couture.

---

## Étape 5 — Implémentation en TDD hybride

Approche **TDD orienté comportement** (les tests testent ce que le code fait, pas comment — ils doivent survivre à un refactoring).

**Avant d'écrire le premier test, lis le skill `behavior-driven-testing` et applique sa doctrine** (frontière de test, nommage, assertions, usage des mocks). Les frontières de test sont déjà fixées par comportement dans la section 4 du plan — écris chaque test à la frontière indiquée, pas classe par classe.

Déroulé :

1. **Les comportements attendus sont déjà listés** dans la section 4 du plan (fait à l'étape 3).

2. **Pour le comportement nominal en premier** :
   - Écrire le test (qui doit échouer — *red*)
   - Vérifier qu'il échoue effectivement (`npm test`, `pytest`, etc.)
   - Implémenter le minimum nécessaire pour le faire passer (*green*)
   - Vérifier que le test passe
   - Refactorer si nécessaire en gardant le test vert

3. **Puis chaque edge case, un par un** :
   - Test (red) → implémentation (green) → refactor
   - Ne passer au suivant que quand le précédent est vert

4. **À chaque passage au vert, lancer les invariants qui couvrent les fichiers touchés** (les scripts repérés à l'étape 1) avant de passer au comportement suivant.

### Un invariant violé est un test rouge

Traiter une violation d'invariant exactement comme un test qui échoue : on ne continue pas, on corrige avant d'avancer. La raison est de coût, pas de discipline — une violation détectée deux comportements plus tôt se corrige en modifiant du code qu'on a encore en tête ; découverte à la revue, elle se corrige sur un diff figé, et impose de refaire toute la relecture.

Le message d'erreur du linter contient la remédiation ; la lire avant de chercher ailleurs. Si la remédiation est inapplicable ou si l'invariant paraît inadapté au cas, **c'est une déviation** au sens de la règle ci-dessous : arrêt, documentation en section 8, validation. Ne jamais contourner un invariant en silence, ni ajouter une exclusion sans validation.

**Le mutation testing ne va pas dans cette boucle.** Son coût d'exécution est incompatible avec un cycle rouge-vert-refactor ; il a sa place au gauntlet et en CI, pas ici.

À chaque étape terminée du plan (section 5), **cocher la case `[x]`** dans le fichier et donner un **résumé court** (1-2 phrases) à l'utilisateur, puis enchaîner sans demander de validation.

### ⚠️ Règle de déviation — ARRÊT OBLIGATOIRE

**Dès que tu t'écartes du plan**, tu t'arrêtes immédiatement et tu demandes validation à l'utilisateur. Cas concrets :

- Un comportement attendu non prévu émerge (ex: « ah, il faut aussi gérer le cas non-connecté »)
- Une étape du plan se révèle infaisable telle qu'écrite
- Tu dois toucher un fichier non identifié dans la phase de contexte
- Tu modifies l'approche technique prévue
- Tout autre écart visible par rapport au plan

À chaque déviation :
1. Documente-la dans la section 8 (Déviations) du plan : *« [date/étape] — Déviation : ... Raison : ... Décision prise : ... »*
2. Présente la déviation à l'utilisateur et demande validation
3. Mets à jour le plan si nécessaire (sections 5, 6, ou autres)
4. Ne reprends qu'après validation

---

## Étape 6 — Clôture

Une fois toutes les étapes de la section 5 cochées :

1. **Vérifier la complétude du plan**
   - Toutes les cases `[x]` ? Si une étape n'a pas été suivie correctement → l'expliquer dans la section 8 (Déviations).

2. **Lancer la suite complète, puis le gauntlet**
   - Tests du projet entier (`npm test`, `pytest`, `cargo test`, etc.)
   - Linter (`eslint`, `ruff`, etc.)
   - Typecheck (`tsc --noEmit`, `mypy`, etc.)
   - Si le projet a un harness : **tous** les invariants (`bash tools/harness/run_all.sh`), pas seulement ceux touchés par la tâche — une modification peut faire échouer une règle sur un fichier qu'on croyait hors périmètre — puis le pont test-cases (`check_test_coverage.*`)
   - Tout doit passer. Si échec → revenir en arrière et corriger.

   C'est exactement ce que `premerge-review` rejouera en phase 3. Le passer ici signifie qu'aucune revue ne sera arrêtée par un check que la tâche pouvait résoudre elle-même.

3. **Auto-review du diff**
   - Faire un `git diff` (ou équivalent) et le lire activement
   - Passer les tests ajoutés au crible des « signaux de mauvaise direction » du skill `behavior-driven-testing` (tests reflétant l'implémentation, mocks omniprésents, test sans comportement clair à protéger…) — reformuler ou supprimer les tests concernés avant de poursuivre
   - Remplir la section 9 du plan avec :
     - Zones risquées du diff (logique complexe, état partagé, sécurité…)
     - Dette ajoutée (TODO, hacks, raccourcis assumés)
     - Points qui méritent une seconde paire d'yeux
   - Présenter cette auto-review à l'utilisateur

4. **Proposer des actions de suivi**
   - Remplir la section 10 du plan :
     - Refactos différés à prévoir
     - Tickets à créer
     - Docs à mettre à jour
     - Tests additionnels qu'on a choisi de ne pas écrire mais qui seraient pertinents
   - Présenter ces propositions à l'utilisateur

5. **Demander systématiquement** : *« Des leçons à capitaliser dans `.plans/FEEDBACK.md` pour s'améliorer en continu sur ce projet ? »*
   - Cette question est posée **à chaque fois**, même si tout s'est bien passé.
   - Les leçons doivent être **fil rouge** (principes durables réutilisables), pas spécifiques à la tâche.
     - ✅ Bon : *« Dans ce projet, les tests vont à côté des sources et non dans `__tests__/`. »*
     - ✅ Bon : *« Toujours lancer `pnpm typecheck` avant de proposer un commit. »*
     - ❌ Mauvais : *« On a corrigé un bug de timeout sur la page de login. »* (trop spécifique)
   - Si l'utilisateur propose des leçons → mettre à jour `.plans/FEEDBACK.md` (créer le fichier s'il n'existe pas, sinon append en respectant la structure existante).
   - Si l'utilisateur répond non → noter simplement *« Aucune leçon ajoutée »* en section 9 du plan.

6. **Validation finale et déplacement du plan**
   - Mettre à jour le statut en section 1 : `done` ou `aborted`
   - Sur validation finale de l'utilisateur :
     - Si tâche menée à terme → déplacer le fichier vers `.plans/done/<slug>.md`
     - Si abandonnée → déplacer vers `.plans/aborted/<slug>.md`
   - Confirmer à l'utilisateur : *« Plan archivé dans `.plans/done/<slug>.md`. »*

---

## Récapitulatif des points de validation

| # | Moment | Type |
|---|--------|------|
| 0 | Application de la skill | Validation **explicite** avant de continuer |
| 2 | Reformulation de l'objectif | Validation **explicite** |
| 3 | Plan complet | Validation **explicite** |
| 4 | Risques & edge cases | Validation **explicite** |
| 4.5 | Check "plan prêt à dérouler" | **Silencieux si OK, arrêt + décision si KO** |
| 5 | Étapes intermédiaires | **Pas de validation**, résumé court suffit |
| 5 | Invariant du harness violé | **Corriger avant d'avancer** ; si la remédiation est inapplicable → déviation |
| 5 | Déviation détectée | **Arrêt immédiat + validation** |
| 6 | Clôture (review, suivi, leçons, archivage) | Validation **explicite** finale |

---

## Notes pour bien utiliser cette skill

- **Le plan est sacré** : il sert d'ancre pour éviter la dérive. Si tu t'éloignes du plan, soit tu le mets à jour avec validation, soit tu ne le fais pas.
- **Le plan est le pont entre modèles** : il est conçu pour qu'une session Opus de planification puisse être reprise par une session Sonnet d'exécution. L'étape 4.5 est le garde-fou qui empêche cette bascule quand le plan n'est pas assez explicite.
- **Le harness contraint la conception, pas seulement le résultat** : les invariants sont chargés à l'étape 1 et vérifiés dans la boucle TDD, pas découverts à la clôture. Un plan écrit en ignorant un invariant applicable est un plan à refaire.
- **Dépendance assumée** : cette skill s'appuie sur `behavior-driven-testing` pour la doctrine de test (étapes 5 et 6). Les frontières de test inscrites dans la section 4 du plan permettent toutefois à une session d'exécution de tester au bon endroit même si ce skill n'est pas chargé.
- **Les tests sont des spécifications** : les tests de comportement encodent les attentes. Ils doivent être lisibles comme une documentation.
- **L'auto-review est honnête** : si tu as pris un raccourci ou laissé de la dette, dis-le. La section 9 du plan est faite pour ça.
- **Le FEEDBACK.md est cumulatif** : il grossit avec le temps. Si une leçon devient obsolète, propose de la retirer plutôt que d'empiler.
- **Pas d'allègement automatique** : si la tâche est trop petite pour ce workflow, l'utilisateur le dira au moment du signalement (étape 0). Ne décide jamais de skip des étapes de toi-même.
