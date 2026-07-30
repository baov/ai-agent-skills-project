---
name: code-assimilation-quiz
description: Quiz d'assimilation post-implémentation — une code review pédagogique sous forme de QCM, une question à la fois, pour que le développeur s'approprie le code écrit par l'IA. À utiliser UNIQUEMENT sur demande explicite de l'utilisateur, jamais automatiquement. Déclencheurs typiques — "lance la live code review", "fais-moi un quiz sur ce qui a été implémenté", "vérifie que j'ai compris le code", "QCM sur le diff", "aide-moi à assimiler ce que tu as codé", "code review pédagogique". Ne pas confondre avec une revue de code classique (recherche de défauts) — ici l'objectif est l'apprentissage du développeur, pas la critique du code.
---

# Live Code Review — Quiz d'assimilation

## Pourquoi ce skill existe

Quand une IA implémente du code, le développeur risque de devenir un simple
valideur passif : le code marche, il merge, mais il ne saurait ni le maintenir
ni le défendre en revue. Ce skill inverse la dynamique : après une
implémentation, le développeur passe un QCM construit sur le diff réel. Le but
n'est pas de le piéger ni de le noter, mais de transformer une lecture passive
en rappel actif (active recall) — la façon la plus efficace de mémoriser et de
détecter ses propres zones floues.

Garde ce but en tête à chaque étape : tout ce qui humilie, piège ou noie le
développeur est contre-productif. Tout ce qui l'amène à se reposer une vraie
question sur le code est productif.

## Pourquoi ce skill compte davantage à mesure que les agents écrivent plus

Une objection se pose naturellement : si la tendance est de déléguer
l'implémentation aux agents et de relire de moins en moins de code, à quoi bon
un quiz sur du code qu'on ne lira plus ? C'est l'inverse qui est vrai, et il
vaut la peine de savoir pourquoi.

Déléguer sans relire ne fonctionne que si des contraintes mécaniques encadrent
l'agent : invariants d'architecture, seuils de forme, tests d'acceptation,
mutation testing. Or **calibrer ces contraintes demande un jugement qui ne
s'acquiert qu'en ayant lu beaucoup de code**. Savoir qu'une fonction est trop
grosse, qu'un couplage va coûter cher, qu'un cas limite manque — cela ne
s'apprend pas en lisant des seuils, cela s'apprend en ayant vu les dégâts.

Le raccourci qui consiste à adopter « je ne relis plus » sans avoir d'abord
construit ce jugement produit un pari très différent, et beaucoup plus risqué,
de celui que fait un développeur expérimenté avec la même phrase. La formule
est la même ; ce qu'elle recouvre ne l'est pas.

Ce skill est l'un des endroits où ce jugement se fabrique. Il ne sert pas à
vérifier le code — `premerge-review` s'en charge — mais à faire que le
développeur qui pilotera des agents demain sache ce qu'il pilote. C'est aussi
pourquoi il reste utile quand tout est vert : un diff sans défaut est un
excellent support d'apprentissage.

Conséquence pratique : quand le développeur signale qu'il connaît déjà bien la
zone touchée, le prendre au mot et réduire le quiz. Quand il découvre une
technique, un pattern ou une partie du codebase, c'est le moment où le quiz
rend le plus.

## Étape 1 — Délimiter le périmètre

Le quiz se base sur le **diff git**, pas sur ta mémoire de la conversation
(elle peut diverger de ce qui est réellement sur le disque).

1. Regarde d'abord les changements non commités : `git status`, puis
   `git diff` et `git diff --staged`.
2. S'il n'y a rien de non commité, regarde les derniers commits :
   `git log --oneline -10`, puis le diff des commits concernés.
3. Si le périmètre est ambigu (plusieurs commits récents, mélange de sujets),
   demande au développeur lequel couvrir avant de continuer. Une seule
   question, avec les options identifiées.

Lis le diff en entier, et ouvre les fichiers modifiés si le diff seul ne
suffit pas à comprendre le contexte (signatures appelées, classes voisines).
Tu ne peux pas écrire de bonnes questions sur du code que tu n'as pas
réellement lu.

## Étape 2 — Calibrer le quiz

Nombre de questions, proportionnel à l'ampleur du changement :

| Ampleur du diff | Questions |
|---|---|
| Petit (< ~50 lignes, 1-2 fichiers) | 3 |
| Moyen (~50-300 lignes) | 5 |
| Gros (> 300 lignes ou nombreux fichiers) | 7 |

Annonce le format au développeur avant de commencer : nombre de questions,
et le fait qu'il y a une question à la fois.

## Étape 3 — Construire les questions

Avant de poser la première question, construis mentalement (ou dans un bloc de
réflexion) la liste complète des questions. Cela garantit la couverture des
trois axes et évite la redondance.

Les questions couvrent **trois axes**, à équilibrer sur l'ensemble du quiz :

1. **Le QUOI** — structure du changement : quels fichiers/modules sont
   touchés, où vit telle responsabilité, quel est le flux d'appel.
2. **Le POURQUOI** — choix de conception : pourquoi cette structure plutôt
   qu'une alternative, quel problème ce choix évite, quel compromis il fait.
3. **Les risques / cas limites** — qu'est-ce qui casse si on passe telle
   entrée, quel cas n'est pas couvert, où est le point fragile.

Règles de qualité des questions :

- **Ancrées dans le diff réel.** Chaque question doit citer son ancrage
  (fichier, fonction, voire ligne). Pas de question de culture générale qu'on
  pourrait répondre sans avoir vu le code.
- **4 options (A-D), une seule correcte.** Les distracteurs doivent être
  *plausibles* — typiquement les alternatives de conception réellement
  envisageables, ou des confusions probables. Un distracteur absurde est une
  option offerte gratuitement.
- **Pas de pièges de formulation.** La difficulté doit venir de la
  compréhension du code, jamais d'une subtilité de phrasé ou d'un détail
  mémoriel insignifiant (ordre exact des paramètres, nom précis d'une
  variable locale).
- **Le POURQUOI prime quand il faut choisir.** Si le quota de questions force
  un arbitrage, privilégie les questions de conception et de risque : ce sont
  elles qui rendent le développeur capable de maintenir le code.

## Étape 4 — Dérouler le quiz, une question à la fois

C'est la règle cardinale du skill : **une seule question par message, puis
attendre la réponse**. Ne jamais lister plusieurs questions d'avance, ne
jamais enchaîner sans réponse. Le rappel actif ne fonctionne que si le
développeur s'engage sur une réponse avant de voir la correction.

Format de présentation : l'énoncé, puis les options en **liste à puces**
(une par ligne, plus lisible qu'un paragraphe) :

```
Question 2/5 — [axe : pourquoi]
Dans `OrderService.cancel()`, le remboursement est délégué à un événement
asynchrone plutôt qu'appelé directement. Pourquoi ?

- **A.** ...
- **B.** ...
- **C.** ...
- **D.** ...
```

Le développeur répond par la lettre. N'utilise un mécanisme de choix
interactif (boutons, widget de sélection) **que s'il peut afficher
l'énoncé complet ET ses quatre options au même endroit**. Un widget qui ne
montre que des boutons A/B/C/D séparés de l'énoncé fait répondre le
développeur à l'aveugle — dans ce cas, le texte simple est meilleur.

**Après une bonne réponse** : confirme brièvement, et ajoute en une ou deux
phrases le *pourquoi* de la bonne réponse (la confirmation seule n'apprend
rien). Puis question suivante.

**Après une mauvaise réponse** :

1. Donne la bonne réponse avec une explication pédagogique, en pointant
   l'endroit exact du code (`fichier:fonction`) pour que le développeur
   puisse aller voir.
2. **Note la notion ratée.** Plus tard dans le quiz (pas immédiatement —
   laisse au moins une question d'écart), repose une question **reformulée**
   sur la même notion : autre angle, autre formulation, autres options. Une
   re-question est un nouveau test de la notion, pas la même question
   recyclée — sinon tu testes la mémoire à court terme, pas la compréhension.
3. Les re-questions s'ajoutent au quota initial (un quiz à 5 questions avec 2
   erreurs peut monter à 7). Annonce-le naturellement ("on y reviendra").

Ton à tenir : bienveillant et factuel. Une erreur du développeur est une
information utile (zone floue détectée), jamais un échec. Pas de
condescendance, pas de félicitations excessives non plus.

## Étape 5 — Restitution finale

À la fin du quiz, en conversation (pas de fichier à produire) :

1. **Score** : x/n au premier essai, et le résultat des re-questions.
2. **Synthèse par zones** :
   - *Maîtrisé* — les notions répondues correctement du premier coup.
   - *À revoir* — les notions ratées, même rattrapées en re-question, chacune
     avec le pointeur code (`fichier:fonction`) pour une relecture ciblée.
3. **Suggestion de suite** si pertinente : par exemple "relis le bloc
   try/except de `retry.py` en te demandant ce qui se passe si X" — une
   consigne de lecture active vaut mieux qu'un "relis le fichier".

Ne transforme pas la synthèse en rapport bureaucratique : quelques phrases
par zone suffisent.

## Ce que ce skill ne fait pas

- Il ne critique pas le code et ne propose pas de refactoring — ce n'est pas
  une revue de qualité. Si tu repères un vrai problème dans le diff en
  préparant les questions, signale-le *après* le quiz, séparément.
- Il ne se déclenche jamais de lui-même. Même en fin d'implémentation, tu
  peux au plus *mentionner* que le skill existe si le contexte s'y prête,
  jamais lancer le quiz sans demande.
