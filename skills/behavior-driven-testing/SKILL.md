---
name: behavior-driven-testing
description: Stratégie de test orientée comportements plutôt que « un test par classe ». À utiliser dès qu'on écrit, conçoit ou revoit des tests, qu'on parle de stratégie de test, de coverage, de mutation testing ou de score de mutation, de TDD, qu'on demande « comment tester ça », ou qu'on se plaint de tests fragiles. À utiliser aussi quand quelqu'un propose un mapping « 1 test ↔ 1 classe », fixe un objectif chiffré de coverage comme but, ou se demande si ses tests valent quelque chose — c'est le réflexe que ce skill corrige.
---

# Tester par comportements, pas par classes

## L'idée centrale

Un test vérifie qu'un **comportement observable** est correct : une entrée produit la sortie attendue, un cas d'usage se déroule comme prévu, une règle métier est respectée. Il n'existe pas pour « couvrir une classe ».

La fausse croyance à corriger : « pour bien tester, il faut une suite de tests dédiée à chaque classe ». C'est faux, et ça produit des suites volumineuses, fragiles, qui testent la mécanique interne plutôt que ce qui compte.

Pourquoi, mécaniquement : le coverage mesure **quelles lignes s'exécutent**, pas combien de classes ont leur fichier de test. Or un seul test de comportement traverse souvent N classes, qui sont donc couvertes sans test direct. Le mapping « 1 test ↔ 1 classe » n'est imposé par aucun outil ; c'est une discipline qu'on s'inflige soi-même.

## Le piège du coverage

Ce skill **ne vise pas** « 100% de coverage ». Le coverage mesure l'exécution, pas la qualité des assertions : on peut exécuter 100% des lignes sans jamais vérifier le bon résultat. Un coverage élevé est une *conséquence* de bons tests, jamais l'objectif.

Concrètement : ne jamais ajouter un test dont la seule justification est de faire monter le pourcentage. Une zone non couverte est un signal de diagnostic (« ai-je oublié un cas d'usage ? »), pas une case à cocher. Si l'utilisateur fixe un objectif chiffré, expliquer brièvement la distinction puis recentrer sur les comportements à couvrir.

## La métrique qui mesure ce que le coverage ne mesure pas

Le reproche fait au coverage — il mesure l'exécution, pas la valeur des assertions — appelle une question légitime : existe-t-il une métrique qui mesure vraiment cette valeur ? Oui, le **mutation testing**.

Le principe : l'outil altère mécaniquement le code (inverser une condition, remplacer un opérateur, supprimer un appel, retourner une valeur nulle), relance les tests, et regarde s'ils échouent. Un mutant *tué* signifie que les tests protègent réellement ce comportement. Un mutant *survivant* signifie qu'on peut casser cette ligne sans qu'aucun test ne s'en aperçoive — un test peut être vert, couvrir 100% des lignes, et n'asserter rien d'utile.

C'est le complément naturel de la démarche par comportements : un mutant survivant se lit comme une question — « quel comportement n'est pas protégé ici ? » — et la réponse est un test à écrire, formulé selon les règles de la section précédente.

Trois mises en garde, dans le prolongement direct du piège du coverage :

- **Le score de mutation n'est pas un objectif chiffré déguisé.** Il diagnostique, il ne se vise pas. Un seuil en CI sert à empêcher une régression, jamais à faire monter un chiffre.
- **Ne jamais écrire un test dont la seule justification est de tuer un mutant.** C'est le même travers que le test écrit pour faire monter le coverage, avec un habillage plus flatteur. Si un mutant survivant ne correspond à aucun comportement qui compte, il s'exclut en configuration, avec un commentaire qui justifie l'exclusion.
- **Les mutants équivalents existent.** Certaines altérations sont sémantiquement neutres et donc intuables. Un score de 100% n'est ni atteignable ni souhaitable.

Le coût d'exécution est réel — un run se compte en dizaines de minutes. En pratique, on le restreint au périmètre qui porte les règles métier. La mise en place opérationnelle (périmètre, seuils, intégration CI) relève de `codebase-harness`, brique D.

## Démarche

1. **Identifier l'unité de comportement, pas l'unité de code.** Avant d'écrire un test, demander : « quel cas d'usage ou quelle règle est-ce que je valide ? ». Le sujet est un comportement (« un panier vide refuse le paiement »), pas une classe (« `CartValidator` »).

2. **Tester à la bonne frontière.** Préférer tester à travers une interface stable — point d'entrée d'un cas d'usage, API d'un module, port applicatif — plutôt que classe par classe. Les classes internes traversées sont couvertes de facto.

   *Exception :* tester une classe en isolation seulement quand elle porte une logique complexe difficile à exercer depuis la frontière, ou pour piloter un algorithme délicat.

3. **Nommer les tests par comportement.** Le nom décrit l'intention et le résultat (« refuse une commande au-delà du stock »), pas la méthode appelée (« test_checkStock »).

4. **Assertions sur le résultat observable**, pas sur les détails d'implémentation. Sur-vérifier les appels internes (tout mocker) rend les tests fragiles. Un bon test de comportement survit au refactoring tant que le comportement ne change pas.

## Adapter à la stack du projet

Avant d'écrire des tests, déduire le contexte (langage, framework, architecture) en inspectant le dépôt : manifestes (`pom.xml`, `build.gradle`, `package.json`, `pyproject.toml`, `*.csproj`, `go.mod`…), dossiers de tests existants, conventions de nommage. Respecter le framework et le style déjà en place.

Si le projet suit une architecture en couches / hexagonale / DDD, la frontière de test naturelle est le cas d'usage applicatif ou le port — c'est là qu'on teste, en couvrant le domaine derrière. S'il existe déjà une doc de stratégie de test (ex. sous `docs/`), s'y conformer et la compléter.

## Signaux de mauvaise direction

- Un fichier de test créé « parce que la classe existe », sans comportement clair à valider.
- Des mocks pour chaque dépendance, au point que le test reflète l'implémentation ligne à ligne.
- Un test qui casse à chaque renommage ou extraction de méthode sans changement de comportement.
- Un objectif exprimé en pourcentage de coverage plutôt qu'en cas d'usage couverts.

Dans ces cas, recentrer : « quel comportement ce test protège-t-il ? ». Sans réponse claire, le test est à supprimer ou reformuler.

## Exemple de recadrage

**Demande :** « Il me faut un test pour `OrderValidator`, `PriceCalculator` et `StockChecker` pour couvrir le module commande. »

**Réponse orientée comportement :** écrire des tests sur le cas d'usage « passer une commande » — cas nominal, stock insuffisant, prix promotionnel — qui traversent naturellement les trois classes. Les trois sont couvertes, les tests décrivent de vraies règles métier, et ils résistent à un refactoring interne.
