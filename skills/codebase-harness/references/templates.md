# Templates des artefacts du harness

Ce fichier est consulté par Claude au moment de générer chacun des artefacts du harness. Il contient pour chaque artefact : (1) la structure attendue, (2) les questions QCM types à poser en phase de validation.

**Règle de fond** : ces templates fixent la *forme*, jamais le contenu métier. Un invariant, un seuil ou un périmètre est toujours une décision de l'utilisateur, validée par QCM. Claude propose, l'utilisateur tranche.

---

## 1. `docs/technique/invariants.md`

### Structure du fichier

```markdown
# Invariants exécutables

Règles d'architecture et de forme rendues vérifiables mécaniquement. Chaque invariant a un ID immuable, un script qui le vérifie, et une remédiation actionnable.

Lancer tous les checks : `bash tools/harness/run_all.sh`

| ID | Énoncé | Sévérité | Statut |
|----|--------|----------|--------|
| INV-001 | … | error | actif |
| INV-002 | … | warn | actif |
| INV-003 | … | — | déprécié |

---

## INV-001 — [Titre court]

- **Statut** : actif | déprécié
- **Énoncé** : la règle en une phrase, au présent, formulée comme une propriété vraie du codebase
- **Source** : ADR-NNNN | architecture.md § Contraintes structurelles | convention équipe (énoncé utilisateur)
- **Script** : `tools/harness/check_<sujet>.<ext>`
- **Sévérité** : error | warn
- **Remédiation** : ce que doit faire concrètement celui qui viole la règle
- **Exemple de violation** :
  ```
  <extrait minimal>
  ```
- **Correctif** :
  ```
  <le même extrait, corrigé>
  ```
```

### Règles de rédaction

- **La numérotation est immuable.** Un invariant déprécié garde son ID ; on ne renumérote jamais. Un nouvel invariant prend le numéro suivant, même si des trous existent.
- **Un invariant = une règle.** Si l'énoncé contient « et » ou « sauf si », c'est deux invariants ou une règle mal posée.
- **L'énoncé décrit l'état voulu, pas l'interdit.** « La couche domaine ne dépend d'aucun module d'I/O » plutôt que « ne pas importer requests ».
- **La remédiation est une instruction, pas un constat.** Elle doit suffire à un agent qui n'a pas lu l'ADR.
- Les blocs exemple/correctif sont obligatoires : c'est ce qui rend la règle compréhensible sans contexte.

### Questions QCM types

- « J'ai extrait N règles candidates : [liste]. Lesquelles rendre exécutables ? »
- « INV-00X : sévérité `error` (CI bloquante) ou `warn` (signal seulement) ? »
- « Cette règle vient d'ADR-NNNN — j'ajoute le renvoi « Invariants exécutables associés » dans l'ADR ? »
- « L'invariant INV-00X ne trouve plus la couche qu'il surveille. Le passer en `déprécié` ? »

---

## 2. Front-matter des test-cases (brique B)

### Structure

À insérer en tête de chaque `docs/metier/test-cases/[feature]/[nom].md`, avant le titre :

```yaml
---
feature: panier
type: nominal              # nominal | erreur | edge-case
priorite: critique         # critique | importante | nice-to-have
automated_test: tests/test_panier.py::test_ajout_produit   # ou null
status: covered            # covered | pending | manual
---
```

### Sémantique des champs

| Champ | Rôle | Déduction automatique |
|-------|------|------------------------|
| `feature` | Regroupement, doit correspondre au dossier parent | Nom du dossier |
| `type` | Nature du scénario | Déduit du titre et du contenu |
| `priorite` | **Alimente le périmètre de la brique D** — les `critique` sont les candidats naturels au mutation testing | Déduit, à valider |
| `automated_test` | Référence `<chemin>::<nom du test>` | Recherche par nom, heuristique snake_case |
| `status` | État de la couverture | `covered` si un test a été trouvé, `pending` sinon |

`status: manual` signale un scénario qui restera vérifié à la main (parcours visuel, procédure QA) — il est exclu des checks de cohérence, jamais compté comme une lacune.

### Questions QCM types

- « J'ai décoré N test-cases. M sont ambigus : [liste avec options a/b/c]. »
- « Ce test-case n'a pas de test automatisé trouvé — `pending`, ou `manual` parce qu'il ne sera jamais automatisé ? »
- « Ces N tests existent sans test-case associé. En créer, ou les ignorer (tests techniques) ? »

---

## 3. Entrée d'invariant « seuil de mutation » (brique D)

Le seuil de mutation est un invariant comme les autres, avec deux champs supplémentaires : le périmètre et la baseline.

### Structure

```markdown
## INV-0NN — Score de mutation du domaine ≥ 75%

- **Statut** : actif
- **Énoncé** : le score de mutation sur le périmètre critique ne descend pas sous 75%
- **Source** : brique D du harness, périmètre « domaine critique » validé le AAAA-MM-JJ
- **Périmètre** : `<globs ou modules>`
- **Script** : `tools/harness/run_mutation.* --scope critical`
- **Outil** : <outil détecté> — rapport parsable : <format>
- **Sévérité** : warn (→ error prévu après stabilisation)
- **Baseline** : 78.4% mesuré le AAAA-MM-JJ sur <sha>
- **Remédiation** : lire les mutants survivants listés par le script. Pour chacun,
  identifier le comportement non protégé et ajouter un test qui l'exprime. Ne jamais
  ajouter un test dont la seule justification est de tuer un mutant — si un mutant
  survivant ne correspond à aucun comportement qui compte, l'exclure explicitement
  dans la config avec un commentaire justifiant l'exclusion.
```

### Règles de rédaction

- **Le seuil initial est la baseline arrondie vers le bas**, jamais un chiffre rond aspirationnel. Son rôle est d'empêcher la régression, pas de fixer un objectif.
- **La baseline est datée et rattachée à un sha.** Sans ça, impossible de dire si une variation vient du code ou d'un changement de périmètre.
- **Un seuil ne se baisse jamais pour faire repasser la CI.** Si le score chute, c'est un comportement qui a perdu sa protection — la remédiation est un test, pas un ajustement de chiffre.
- Le champ **Outil** est renseigné à la détection et pas figé dans le skill : il documente ce qui a été trouvé, pour que la relecture six mois plus tard sache quoi relancer.

### Questions QCM types

- « Périmètre du mutation testing : domaine critique / incrémental sur le diff / global / combinaison / abandonner la brique ? »
- « Ces N modules portent les test-cases marqués `critique`. Périmètre correct ? »
- « Baseline mesurée à X%. Je fixe le seuil à <X arrondi vers le bas>% en `warn` ? »
- « Le score dépasse la baseline de plus de 5 points depuis N runs. Relever le seuil à Y% ? »

---

## 4. Prompt de la scheduled-task (brique C)

### Structure

```json
{
  "name": "Harness — doc-gardening [nom du projet]",
  "cronExpression": "<choisi via QCM>",
  "prompt": "Relance le skill codebase-harness en mode mise à jour sur le projet [chemin]. Ne modifie aucun fichier automatiquement — produis uniquement un rapport consolidé : violations d'invariants nouvelles, invariants obsolètes, test-cases dérivés (covered_broken ou nouveau test sans test-case), régression du score de mutation par rapport à la baseline et mutants survivants nouveaux, doc qui aurait dérivé. Si tout est au vert, dis-le et n'envoie rien d'autre."
}
```

### Règles de rédaction

- Le prompt doit contenir **« ne modifie aucun fichier automatiquement »** de façon explicite. La tâche s'exécute sans humain au clavier ; c'est la seule protection.
- Le prompt doit contenir **« si tout est au vert, n'envoie rien »**. Une tâche qui produit un rapport vide toutes les semaines apprend à l'équipe à ne plus la lire.
- Le chemin du projet est en dur : la tâche n'a pas de contexte de session.

### Questions QCM types

- « Cadence : quotidienne / hebdomadaire / bi-mensuelle / mensuelle ? »
- « Voici le prompt et la cadence. Je crée la tâche ? »

---

## 5. Section « Harness » de `CLAUDE.md`

La structure complète est dans le SKILL.md, étape 7. Deux règles de rédaction s'appliquent :

- **N'inclure que les sous-sections des briques réellement activées.** Une sous-section qui décrit un check inexistant fait perdre du temps aux agents et sape la confiance dans le reste du fichier.
- **Ne jamais toucher la section « Documentation du projet »** générée par `codebase-cartographer`. Les deux skills coexistent dans le même fichier sans se marcher dessus.

### Questions QCM types

- « J'ajoute la section Harness à CLAUDE.md ? Voici le contenu proposé. »
- « CLAUDE.md a déjà une section Harness qui mentionne la brique X, désactivée depuis. Je la retire ? »

---

## 6. Conventions d'écriture des scripts

Tous les scripts produits dans `tools/harness/` respectent le même contrat, quelle que soit la brique et quel que soit le langage. C'est ce contrat qui permet au mode mise à jour et à la scheduled-task de les agréger sans les connaître individuellement.

### Interface

| Élément | Règle |
|---------|-------|
| `--explain` | Décrit la règle et son périmètre sans rien vérifier. Obligatoire. |
| `--root <chemin>` | Permet de lancer le script hors du répertoire courant. Obligatoire. |
| Sortie standard | Une ligne par violation, format `path:line: [INV-NNN] message — remédiation` |
| Code 0 | Aucune violation |
| Code 1 | Au moins une violation de sévérité `error` |
| Code 2 | Uniquement des violations de sévérité `warn` |

### Règle d'or des messages

Un message d'erreur est écrit **pour un agent qui n'a aucun contexte**. Le test : le message suffit-il à corriger sans ouvrir un autre fichier ?

```
✗  unauthorized import
✗  INV-001 violated
✓  src/domaine/checkout.py:42: [INV-001] import de `requests` dans la couche domaine
   — déplace l'appel HTTP vers `src/application/` et expose un port côté domaine
```

### Interdits

- **Aucun auto-fix.** Même quand le correctif est évident. Le harness produit un signal ; le fix passe par un commit visible.
- **Aucune modification de sa propre config ou de son seuil.** Un ajustement est une décision, il passe par QCM et par `invariants.md`.
- **Aucune dépendance à installer** pour les scripts de vérification documentaire. Ils tournent en CI minimale ; s'ils exigent un `pip install`, ils finiront désactivés.

### Questions QCM types

- « Le script check_X déclenche N faux positifs sur le code existant. Je corrige le script, ou j'assouplis la règle ? »
- « Passer INV-00X de `warn` à `error` ? Les violations existantes sont à zéro depuis N jours. »
