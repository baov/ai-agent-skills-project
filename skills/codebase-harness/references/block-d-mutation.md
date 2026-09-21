# Brique D — Mutation testing

Chargé par `codebase-harness` uniquement si cette brique a été retenue au QCM de scoping (étape 2). Les autres briques sont dans les fichiers `brique-*.md` voisins.

---

## 5.0 — Ce que cette brique résout

Les briques A et B contrôlent le code et l'existence des tests. Aucune ne contrôle **la valeur des tests eux-mêmes**. C'est l'angle mort qui compte le plus quand des agents écrivent la suite de tests : un test peut s'exécuter, être vert, couvrir 100 % des lignes et n'asserter rien d'utile.

Le mutation testing répond exactement à ça : l'outil introduit des altérations mécaniques du code (inverser une condition, remplacer un `+` par un `-`, supprimer un appel, retourner `null`), relance les tests, et vérifie qu'au moins un test échoue. Un mutant **tué** signifie que les tests protègent ce comportement. Un mutant **survivant** signifie qu'on peut casser cette ligne sans qu'aucun test ne s'en aperçoive.

À dire explicitement à l'utilisateur, parce que c'est la confusion la plus fréquente : **le score de mutation n'est pas un coverage amélioré**. Le coverage mesure quelles lignes s'exécutent ; le score de mutation mesure si les assertions valent quelque chose. C'est la métrique que le coverage prétend être sans jamais l'être — et la seule qui justifie de ne pas relire un test à la main.

> Cohérence avec `behavior-driven-testing` : ce skill ne fixe pas d'objectif chiffré comme but en soi. Le score de mutation est un **outil de diagnostic** — un mutant survivant est une question (« quel comportement n'est pas protégé ici ? »), pas une case à cocher. Un seuil en CI sert à empêcher une régression, pas à faire monter un chiffre.

## 5.1 — Pré-requis et arbitrage du coût

Avant toute proposition, l'agent vérifie trois choses :

1. **Une suite de tests existe et passe.** Le mutation testing sur une suite rouge n'a aucun sens. Si des tests échouent, le signaler et s'arrêter là.
2. **La durée d'une exécution complète de la suite.** C'est le facteur multiplicatif : un run de mutation exécute la suite (partiellement) une fois par mutant. Mesurer si possible, sinon demander.
3. **Le périmètre candidat.** Le run global est presque toujours le mauvais choix.

L'agent présente ensuite l'arbitrage honnêtement, sans vendre la brique :

```
Ta suite tourne en ~4 min. Un run de mutation sur l'ensemble du code
prendrait vraisemblablement plusieurs heures — inexploitable en CI de MR.

Trois périmètres possibles :

1. Domaine critique uniquement (recommandé)
   Les packages/modules qui portent les règles métier. Typiquement
   10-20% du code, l'essentiel du risque. Run estimé : 10-20 min.
   → CI nocturne ou pre-merge sur les MR qui touchent ce périmètre.

2. Incrémental sur le diff
   Ne mute que les fichiers modifiés par la branche. Run court et
   proportionné, mais ne protège pas contre l'érosion du reste.
   → CI de MR.

3. Global
   Couverture complète, run long. Réservé à une exécution
   hebdomadaire ou mensuelle.
   → tâche planifiée, jamais en CI bloquante.
```

QCM : périmètre 1 / 2 / 3 / combinaison (typiquement 2 en MR + 1 en nocturne) / abandonner la brique D.

**« Abandonner » est une réponse légitime et doit être présentée comme telle.** Si la suite est lente, instable, ou si la CI est déjà saturée, le mutation testing est un mauvais investissement et l'agent le dit franchement plutôt que d'installer un check qui sera désactivé au premier build rouge.

## 5.2 — Choix du périmètre critique

Si l'utilisateur retient le périmètre 1, l'agent propose une liste de modules en s'appuyant, dans l'ordre :

- Les test-cases marqués `priorite: critique` en brique B → remonter aux modules qu'ils exercent.
- La couche domaine identifiée par les ADR ou par `ddd-advisor` s'il a tourné.
- À défaut : les modules avec la plus forte densité de logique conditionnelle, ou ceux que l'utilisateur désigne.

Présenter la liste en QCM multi-sélection. Ne jamais deviner en silence : le périmètre est la décision structurante de cette brique.

## 5.3 — Production des artefacts

#### a) Configuration de l'outil de mutation

Comme pour les briques A et B, **L'agent détecte l'écosystème et génère la config adaptée**. Ce qui suit est le cahier des charges, valable quel que soit l'outil — c'est lui qui fait foi, pas une liste d'outils qui vieillira.

Cinq points à cadrer dans toute config générée, dans cet ordre de priorité :

1. **Périmètre explicite.** Restreindre les cibles au périmètre retenu en 5.2, par globs ou packages nommés. Ne jamais laisser le défaut « tout le code » — c'est la première cause de run inexploitable.
2. **Jeu de mutateurs par défaut au premier passage.** Les jeux étendus multiplient le temps de run et produisent des mutants équivalents (des altérations sémantiquement neutres, impossibles à tuer). N'élargir que si le score plafonne artificiellement haut.
3. **Aucun seuil bloquant au premier run.** On mesure avant de contraindre. Le seuil arrive en 5.3.c, après la baseline.
4. **Un rapport lisible par un humain et un rapport parsable par une machine.** Le second alimente le script du harness ; sans lui, la brique ne peut pas remonter dans le rapport consolidé.
5. **Timeout et parallélisme calibrés sur la CI réelle**, pas sur les valeurs par défaut de l'outil — et mode incrémental activé s'il existe, c'est ce qui rend le périmètre « diff » viable.

La config est écrite dans le projet à l'emplacement standard de l'outil, **pas** dans `tools/harness/`. Le harness fournit le pilotage et la normalisation, jamais la config de l'outil : un développeur doit pouvoir lancer l'outil directement sans passer par le harness.

Repères par écosystème, à vérifier au moment du run plutôt qu'à prendre pour argent comptant — l'outillage bouge :

| Écosystème | Outil usuel | Format parsable |
|------------|-------------|-----------------|
| JVM | PIT (`pitest`), via Maven ou Gradle | XML |
| JS/TS | Stryker | JSON |
| .NET | Stryker.NET | JSON |
| Python | mutmut, cosmic-ray | JSON / SQLite selon l'outil |
| Go | go-mutesting, ou `gremlins` | JSON |
| Rust | `cargo-mutants` | JSON |
| PHP | Infection | JSON |

Si aucun outil mature n'existe pour la stack détectée, **le dire et proposer d'abandonner la brique D** plutôt que d'installer un outil abandonné ou expérimental. Un harness qui repose sur un outil non maintenu est une dette, pas une protection.

#### b) `tools/harness/run_mutation.{sh,ps1}`

Le wrapper est la pièce qui rend la brique agnostique : il absorbe la différence d'outillage et expose un contrat stable, identique à celui des scripts des briques A et B. C'est ce contrat qui doit être respecté, pas une implémentation particulière.

**Interface** — alignée sur les autres scripts du harness :
- `--scope critical|diff|full` (défaut `critical`)
- `--explain` : décrit le périmètre, l'outil utilisé et le seuil, sans rien exécuter
- `--root <chemin>` : pour pouvoir tester localement

**Comportement en mode `diff`** : calculer la base avec `git merge-base HEAD origin/<branche cible>` et restreindre le périmètre aux fichiers modifiés, en respectant le format de sélection de l'outil détecté.

**Sortie normalisée** — indépendante de l'outil sous-jacent :
```
MUTATION — périmètre: critical (4 modules) · outil: <détecté>
score: 78.4% (312 tués / 398 générés)  seuil: 75%  → OK

Mutants survivants les plus significatifs :
  <fichier>:44  [NEGATE_CONDITIONS]  aucun test ne distingue > de >=
  <fichier>:71  [MATH]               le calcul du prorata n'est pas asserté
```

**Codes de sortie** identiques aux autres scripts : `0` OK, `1` sous le seuil `error`, `2` sous le seuil `warn`.

**Deux interdits** :
- Le script n'écrit jamais de test. Il signale ; le correctif passe par `plan-driven-dev` avec `behavior-driven-testing` en appui.
- Le script ne modifie jamais la config de l'outil ni le seuil. Un ajustement de seuil est une décision, elle passe par un QCM et une entrée dans `invariants.md`.

Si le projet est multi-modules avec plusieurs stacks (typique d'un monorepo back + front), générer **un wrapper par stack** avec le même contrat, et un `run_mutation.sh` racine qui les appelle et agrège les scores. Le contrat de sortie reste le même ; seule la ligne `outil:` change.

#### c) Entrées dans `invariants.md`

Le seuil de mutation est un invariant à part entière et suit la même numérotation `INV-NNN`, avec un champ supplémentaire :

```markdown
## INV-012 — Score de mutation du domaine ≥ 75%

- **Statut** : actif
- **Source** : brique D du harness, périmètre « domaine critique »
- **Périmètre** : `src/domaine/**`
- **Script** : `tools/harness/run_mutation.sh --scope critical`
- **Sévérité** : warn (→ error prévu après stabilisation)
- **Baseline** : 78.4% mesuré le AAAA-MM-JJ
- **Remédiation** : lire les mutants survivants listés par le script. Pour chacun,
  identifier le comportement non protégé et ajouter un test qui l'exprime. Ne jamais
  ajouter un test dont la seule justification est de tuer un mutant — si un mutant
  survivant ne correspond à aucun comportement qui compte, l'exclure explicitement
  dans la config avec un commentaire justifiant l'exclusion.
```

**La règle du seuil** : le seuil initial est fixé **à la baseline mesurée, arrondie vers le bas**, jamais à un chiffre rond aspirationnel. Son rôle est d'empêcher la régression. On le relève ensuite par paliers explicites, chacun validé par QCM.

## 5.4 — Intégration

Comme pour les autres briques, l'agent présente le snippet et demande la permission avant d'écrire.

Deux règles spécifiques à cette brique :

- **Jamais en pre-commit.** Le temps d'exécution est incompatible avec un hook local. Si l'utilisateur le demande quand même, expliquer pourquoi c'est une mauvaise idée avant de suivre sa décision.
- **`warn` obligatoire au premier passage.** Passer un seuil de mutation en CI bloquante dès l'installation garantit une CI rouge et un check désactivé dans la semaine.

```yaml
# GitHub Actions — mutation incrémentale sur les MR
- name: Harness — mutation (diff)
  run: bash tools/harness/run_mutation.sh --scope diff
  continue-on-error: true   # retirer quand le seuil est stabilisé
```

```yaml
# GitHub Actions — mutation nocturne sur le domaine critique
on:
  schedule:
    - cron: '0 2 * * *'
jobs:
  mutation:
    steps:
      - name: Harness — mutation (domaine critique)
        run: bash tools/harness/run_mutation.sh --scope critical
```

Sur GitLab CI, transposer avec un job `rules: - if: $CI_PIPELINE_SOURCE == "merge_request_event"` pour l'incrémental et un `schedule` pour le nocturne.

---
