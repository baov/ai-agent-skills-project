---
name: clarify-with-qcm
description: Doctrine de validation par QCM — comment un skill interroge l'utilisateur avant d'écrire quoi que ce soit, et comment il dégrade quand l'agent hôte n'a pas de mécanisme de question à choix multiples. Chargé par les skills qui valident des décisions structurantes (codebase-cartographer, codebase-harness, ddd-advisor), rarement invoqué directement. À utiliser aussi quand on écrit ou révise un skill qui doit demander l'avis de l'utilisateur, ou quand on se demande combien de questions poser, sous quelle forme, ou que faire si l'utilisateur répond « à toi de voir ». Ne pas confondre avec code-assimilation-quiz, dont le QCM interroge le développeur pour qu'il apprenne, et non pour trancher une décision.
---

# Valider par QCM

Le QCM est le point de contact entre un skill et la personne qui l'utilise. C'est là que se joue la règle commune à tous les skills de ce dépôt : **rien de structurant ne s'écrit sans validation explicite**.

C'est aussi le seul endroit où les agents diffèrent vraiment. Le reste — lire des fichiers, exécuter des scripts, écrire du markdown — se comporte partout pareil. Poser une question à choix multiples, non.

## Le mécanisme, selon l'hôte

Avant le premier QCM, déterminer ce dont l'agent dispose :

| Situation | Conduite |
|---|---|
| L'hôte expose un outil de question à choix multiples | L'utiliser. Interface cliquable, pas de saisie à l'aveugle, réponses non ambiguës. |
| L'hôte n'en expose aucun | **Mode dégradé** : présenter la question en texte, options numérotées, puis s'arrêter et attendre la réponse. |

Ne jamais coder un nom d'outil en dur dans un skill. Les noms varient d'un agent à l'autre et changent de version en version ; un skill qui nomme son outil est un skill qui casse ailleurs.

**Le mode dégradé n'est pas une excuse pour sauter le QCM.** Une liste numérotée dans un message vaut validation. Ce qui est interdit, c'est d'écrire sans avoir demandé — pas de demander en texte brut.

```
Trois points à trancher avant que j'écrive le glossaire :

1. « Commande » et « Order » désignent-ils la même chose ?
   a) Oui, un seul terme à retenir — je garde « Commande »
   b) Non, ce sont deux concepts distincts
   c) Autre / je précise

2. …

Réponds par exemple « 1a 2c » et je continue.
```

## La structure d'un round

Dans cet ordre, toujours :

1. **Ce que j'ai compris** — un résumé bref en puces de ce que l'agent a inféré du code. C'est ce qui rend la question répondable : sans ça, l'utilisateur arbitre à l'aveugle.
2. **Ce dont je ne suis pas sûr** — 1 à 3 questions.

Puis on écrit. Après écriture, annoncer brièvement ce qui a été produit et enchaîner, **sans redemander confirmation** : l'utilisateur a déjà validé via le QCM.

## Rédiger les questions

| Règle | Raison |
|---|---|
| 3 questions maximum par round | Au-delà, l'utilisateur survole et valide sans lire. |
| 2 à 4 options, mutuellement exclusives | Des options qui se recouvrent produisent une réponse qu'on ne sait pas interpréter. |
| Options courtes — 2 à 6 mots | Elles sont lues sur un écran étroit, parfois sur mobile. |
| Une option « autre / je précise » quand c'est utile | Une porte de sortie évite de forcer un choix faux. |
| Formulation courte et directe | La question porte sur le projet, pas sur la méthode. |

Poser la question à laquelle **seul l'utilisateur** peut répondre. Ce qui se lit dans le code se lit dans le code : demander ce qui est déjà visible use le crédit d'attention sur les vraies incertitudes.

## Cas particuliers

**Aucune incertitude** (rare). Proposer quand même une validation simple : « Voici ce que je vais écrire dans X — je procède ? »

**« À toi de voir » / « conseille-moi ».** Faire un choix par défaut raisonnable, **l'annoncer explicitement**, et passer à la suite. Ne pas re-questionner : l'utilisateur vient de déléguer, lui renvoyer la décision est une réponse à côté.

**Multi-sélection.** Quand les options ne s'excluent pas (activer plusieurs briques, retenir plusieurs invariants), le dire dans l'énoncé et prévoir « toutes » et « aucune ». « Aucune » est une réponse légitime : elle termine le skill proprement, sans négociation.

**Réponse hors options.** L'utilisateur qui répond à côté du QCM répond quand même : prendre sa réponse littérale, pas l'option la plus proche.

## Interdits

- **Écrire un fichier structurant sans QCM préalable.** Même quand la réponse paraît évidente.
- **Coder un nom d'outil en dur.** Voir plus haut.
- **Enchaîner les rounds sans rien produire.** Un QCM sert à débloquer une écriture ; trois rounds d'affilée sans écrire signalent que le skill questionne au lieu d'avancer.
- **Reformuler une question déjà tranchée.** Une décision validée est acquise pour la durée du skill.
