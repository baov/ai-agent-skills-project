---
name: systematic-debugging
description: Méthodologie rigoureuse de diagnostic de bug — trouver et prouver la cause racine avant tout correctif. À utiliser SYSTÉMATIQUEMENT dès qu'un comportement inattendu doit être expliqué : "pourquoi ça ne marche pas", "bug bizarre", "ça plante", "régression", "comportement intermittent", "ça marchait avant", "erreur incompréhensible", "investigue", "diagnostique", ou toute demande de fix dont la cause n'est pas encore identifiée et prouvée. Couvre la phase de DIAGNOSTIC uniquement : reproduction minimale, hypothèses falsifiables, bissection, instrumentation ciblée, preuve de la cause racine. Une fois la cause prouvée, le correctif est délégué à plan-driven-dev (ou au pipeline en cours). Ne pas utiliser si la cause est déjà connue et prouvée — dans ce cas aller directement au correctif.
---

# Systematic Debugging

Diagnostic de bug discipliné. Objectif : identifier la **cause racine** et la **prouver**, jamais "faire disparaître le symptôme". Le correctif lui-même est hors périmètre : il est remis à `plan-driven-dev` (ou au workflow en cours) une fois la cause établie.

## Signalement initial

Avant d'appliquer ce skill, se signaler à l'utilisateur :

> Je propose d'appliquer le skill `systematic-debugging` : reproduction minimale, hypothèses explicites, investigation tracée dans `.debug/`, et preuve de la cause racine avant tout correctif. OK ?

Ne pas l'invoquer silencieusement. Si l'utilisateur refuse, suivre ses instructions.

## Principes non négociables

1. **Pas de repro fiable = pas de debug.** On ne passe pas à la phase d'hypothèses sans reproduction déterministe (ou statistiquement caractérisée pour les bugs intermittents).
2. **Aucune modification de code sans hypothèse écrite.** Chaque investigation découle d'une hypothèse formulée AVANT, avec une prédiction falsifiable.
3. **Interdiction du fix au hasard.** Un changement qui "fait passer le test" sans qu'on puisse expliquer *pourquoi le bug se produisait* n'est pas un diagnostic — c'est une dette. Revenir aux hypothèses.
4. **Corrélation ≠ causalité.** "Ça a commencé après le déploiement X" est un indice, pas une conclusion. La cause racine doit être démontrée par un mécanisme complet : *parce que A, alors B, donc le symptôme C*.
5. **Une hypothèse à la fois.** Ne jamais tester deux hypothèses dans la même expérience — résultat ininterprétable.
6. **Instrumentation ciblée, pas de printf partout.** Chaque point d'instrumentation répond à une question précise issue d'une hypothèse. Nettoyer l'instrumentation en fin d'investigation.
7. **Tout est tracé.** L'investigation vit dans `.debug/INVESTIGATION-<slug>.md`, pas dans la tête de l'agent. Un humain (ou un autre agent) doit pouvoir reprendre l'investigation à froid.

## Workflow

### Phase 0 — Cadrage

Établir avec l'utilisateur, et consigner dans le fichier d'investigation :
- **Symptôme observé** (factuel : message d'erreur exact, valeur obtenue) vs **comportement attendu**
- **Contexte** : environnement, version, fréquence (systématique / intermittent), périmètre (un utilisateur / tous)
- **Chronologie** : depuis quand ? qu'est-ce qui a changé récemment ? (`git log`, déploiements, config, dépendances)
- **Criticité** : prod en feu ou confort de dev ? (ajuste la profondeur d'investigation acceptable)

Créer `.debug/INVESTIGATION-<slug>.md` dès cette phase (modèle ci-dessous).

### Phase 1 — Reproduction minimale (GATE)

Construire la reproduction la plus petite et la plus rapide possible :
- Idéalement : **un test automatisé qui échoue**, formulé en termes de comportement. Si le skill `behavior-driven-testing` est disponible, l'appliquer pour formuler ce test (cas d'usage, pas détail d'implémentation). Sinon, règle minimale : le test décrit le comportement attendu du point de vue de l'appelant, et son nom énonce ce comportement.
- À défaut : une commande/script reproductible documenté dans le fichier d'investigation.
- Pour les bugs intermittents : caractériser le taux (ex. "échoue ~3 fois sur 20 runs") et chercher à le rendre déterministe (seed fixe, contrôle de la concurrence, horloge simulée) avant de continuer.

**Gate** : tant qu'il n'y a pas de repro, la seule activité autorisée est la recherche de repro. Si la repro est impossible après effort raisonnable, le dire explicitement à l'utilisateur et proposer une stratégie d'observabilité (logs/métriques à ajouter pour capturer la prochaine occurrence) plutôt que de spéculer.

### Phase 2 — Collecte de faits

Rassembler sans interpréter : stack traces complètes, logs pertinents, état des données, diff des changements récents (`git log -p` sur la zone suspecte), versions des dépendances. Distinguer dans le fichier d'investigation les **faits** (observés) des **interprétations** (supposées).

### Phase 3 — Hypothèses explicites

Lister les hypothèses plausibles dans le fichier d'investigation. Chaque hypothèse DOIT avoir :
- **Énoncé** : le mécanisme supposé ("le cache renvoie une entrée périmée car la clé n'inclut pas le tenant")
- **Prédiction falsifiable** : "si c'est vrai, alors en loggant la clé de cache on verra la même clé pour deux tenants différents"
- **Coût du test** : rapide/moyen/cher — pour prioriser
- **Statut** : à tester / confirmée / réfutée

Prioriser par probabilité × rapidité de vérification. Tester les hypothèses bon marché d'abord, même si moins probables.

### Phase 4 — Investigation

Pour chaque hypothèse, dans l'ordre de priorité :
1. Concevoir l'expérience qui teste la prédiction (instrumentation ciblée, breakpoint, requête, test unitaire exploratoire)
2. Exécuter, noter le résultat brut dans le fichier d'investigation
3. Verdict : confirmée ou réfutée. **Une hypothèse réfutée est un progrès** — la consigner, ne pas la supprimer.

Quand l'espace de recherche est grand, bissecter :
- **Dans l'historique** : `git bisect` avec la repro comme oracle (l'automatiser si possible : `git bisect run`)
- **Dans le code** : désactiver/court-circuiter la moitié du pipeline suspect, resserrer
- **Dans les données** : réduire le jeu d'entrée par dichotomie jusqu'à l'entrée minimale déclenchante

Si toutes les hypothèses sont réfutées : retourner en phase 2 (il manque des faits), élargir le périmètre, ou remettre en cause une certitude ("qu'est-ce que je crois vrai sans l'avoir vérifié ?").

### Phase 5 — Preuve de la cause racine

La cause est établie quand les trois conditions sont réunies :
1. **Mécanisme complet** expliqué : chaîne causale de la cause au symptôme, sans maillon "magique"
2. **Démonstration positive** : on peut déclencher le bug à volonté en activant la cause, et le faire disparaître en la neutralisant (toggle minimal, pas un vrai fix)
3. **Le mécanisme explique TOUS les faits observés** — y compris la fréquence (pourquoi intermittent ?), la chronologie (pourquoi maintenant ?) et le périmètre (pourquoi seulement ces cas ?). Un fait inexpliqué = investigation incomplète ou bug multiple.

Consigner la conclusion dans le fichier d'investigation.

### Phase 6 — Handoff

Produire un résumé de handoff (section dédiée du fichier d'investigation) :
- Cause racine et mécanisme (3-5 lignes)
- La repro / le test qui échoue (référence au fichier de test)
- Pistes de correctif envisageables avec leurs trade-offs (sans en choisir un)
- Risques de régression connexes identifiés pendant l'investigation

Puis proposer à l'utilisateur : « Cause racine prouvée. Je passe au correctif via `plan-driven-dev` ? » (ou remettre au pipeline en cours, ex. checkpoint humain post-analyse). Nettoyer toute instrumentation temporaire avant le handoff.

## Modèle de fichier d'investigation

```markdown
# Investigation — <titre court>
Date : <date> | Statut : en cours | cause prouvée | abandonnée

## Cadrage
- Symptôme observé :
- Comportement attendu :
- Contexte / fréquence / périmètre :
- Chronologie & changements récents :

## Reproduction
- Repro : <test ou commande> | Déterministe : oui/non (taux si non)

## Faits
- [F1] ...
- [F2] ...

## Hypothèses
| # | Énoncé | Prédiction falsifiable | Coût | Statut |
|---|--------|------------------------|------|--------|
| H1 | ... | ... | rapide | réfutée |
| H2 | ... | ... | moyen | confirmée |

## Journal d'investigation
- <date/heure> H1 : <expérience> → <résultat brut> → verdict

## Cause racine
- Mécanisme :
- Démonstration :
- Faits expliqués : F1 ✔ F2 ✔

## Handoff
- Pistes de correctif & trade-offs :
- Risques connexes :
```

## Anti-patterns à refuser explicitement

- **Shotgun debugging** : modifier plusieurs choses "pour voir"
- **Fix par superstition** : redémarrer / vider le cache / réordonner sans expliquer pourquoi ça change quoi que ce soit
- **Conclure sur corrélation** : "c'est sûrement le déploiement d'hier" sans démonstration
- **Patcher le symptôme** : attraper l'exception, ajouter un `if null`, élargir un timeout — sans comprendre l'origine
- **Continuer sans repro** : empiler des hypothèses invérifiables

Si l'utilisateur demande un de ces raccourcis, le faire remarquer une fois, expliquer le risque, puis suivre sa décision (c'est lui qui arbitre criticité vs rigueur).
