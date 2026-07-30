# DDD Tactique — Blocs de construction, heuristiques de décision, symptômes

Référence pour le mode Guide (décisions de modélisation) et le mode Audit (sections Symptômes).

## Sommaire
1. Architecture en couches
2. Entités vs Objets-Valeurs (arbre de décision)
3. Services (et dans quelle couche)
4. Modules
5. Agrégats (règles de frontière)
6. Fabriques vs constructeurs
7. Entrepôts
8. Concepts explicites : Contrainte, Processus, Spécification
9. Symptômes d'audit tactiques

---

## 1. Architecture en couches

Quatre couches, dépendances uniquement vers le bas :

```
Interface utilisateur  →  présentation, interprétation des commandes
Application            →  fine, coordonne, AUCUNE logique métier, pas d'état métier
Domaine                →  cœur : état et règles métier
Infrastructure         →  persistance, communication, bibliothèques de soutien
```

Règles d'or :
- La couche application peut détenir l'état d'avancement d'une **tâche**, jamais l'état d'un
  **objet métier**.
- Les objets du domaine ne s'affichent pas, ne se persistent pas, ne s'orchestrent pas
  eux-mêmes.
- Test rapide : peut-on tester la couche domaine sans base de données ni framework web ?
  Si non → fuite.

## 2. Entités vs Objets-Valeurs

**Entité** : ce qui compte est une continuité d'identité au fil du temps, indépendante des
attributs (compte bancaire, vol, client). **Objet-Valeur** : seuls les attributs comptent
(adresse, montant, coordonnées, plage de dates).

Arbre de décision :
```
Doit-on distinguer deux instances aux attributs identiques ?
├── OUI → Entité
│   └── Définir l'identité : attribut naturel (n° de compte), ID généré,
│       ou combinaison d'attributs. Le modèle doit définir "être le même".
└── NON → Objet-Valeur
    ├── IMMUABLE obligatoire s'il est partagé (règle d'or)
    ├── Création complète et valide au constructeur, sinon exception
    └── Regrouper les attributs en touts conceptuels (rue+ville+état → Adresse)
```

Pièges :
- Tout transformer en entité « par uniformité » : coût d'identité, dégradation des
  performances, complexité inutile.
- Objet-Valeur mutable partagé : corruption silencieuse (le changement d'un client se
  propage à l'autre).

## 3. Services

Un comportement important du domaine qui n'appartient naturellement à aucune Entité ni
Objet-Valeur (ex. : virement entre deux comptes). Trois critères cumulatifs :
1. L'opération réfère à un concept du domaine hors Entité/Objet-Valeur
2. Elle réfère à d'autres objets du domaine
3. Elle est **sans état**

Placement par couche :
- L'opération répond à un besoin **du domaine** → Service de domaine
- Elle **coordonne** une tâche applicative (récupérer, invoquer, persister) → Service applicatif
- Elle est technique (envoi d'email, fichier) → Infrastructure

Anti-pattern : créer un Service par opération → modèle anémique garanti. Un Service
ne remplace jamais une opération qui appartient à un objet.

## 4. Modules

- Regrouper par cohésion conceptuelle (communicationnelle ou fonctionnelle), exposer des
  interfaces, viser couplage faible.
- Les noms de modules font partie du Langage omniprésent et doivent raconter le domaine.
- Refactorer un module coûte cher mais coûte moins cher que des palliatifs permanents.

## 5. Agrégats

Groupe d'objets traité comme un tout vis-à-vis des modifications. Règles structurelles :

```
                    ┌──────────────── frontière ───────────────┐
 objets externes ──►│ RACINE (Entité, identité globale)        │
   (réf. racine     │   ├─► entités internes (identité locale) │
    uniquement)     │   └─► objets-valeurs                     │
                    └──────────────────────────────────────────┘
```

- Seule la racine est référencée de l'extérieur et obtenue par requête (Entrepôt).
- La racine fait respecter les **invariants** à chaque changement d'état.
- Références éphémères d'objets internes : autorisées le temps d'une opération ; sinon,
  passer des **copies** d'Objets-Valeurs.
- Un objet interne peut référencer la racine d'un AUTRE agrégat (jamais ses internes).
- Suppression de la racine = suppression de tout l'agrégat.

Heuristique de frontière : « qu'est-ce qui doit être cohérent dans la même transaction ? »
Avant de tracer, réduire les associations : supprimer les non essentielles, contraindre la
multiplicité, rendre unidirectionnel ce qui peut l'être.

## 6. Fabriques

Encapsulent la création d'objets/agrégats complexes. Création **atomique** : la racine et
tous les objets sous invariants naissent ensemble, valides, sinon exception.

- **Méthode de fabrication** sur la racine : pour créer un objet QUI APPARTIENT à l'agrégat.
- **Fabrique dédiée** : pour créer l'agrégat entier ; elle porte règles, contraintes, invariants.

Un simple constructeur suffit quand : construction simple, pas de création en cascade, la
classe est le type (pas de hiérarchie), le client choisit l'implémentation.

Distinction reconstitution : recréer un objet depuis la base ≠ création (pas de nouvelle
identité, violation d'invariant → réparation, pas exception).

## 7. Entrepôts

Illusion d'une collection en mémoire de tous les objets d'un type. Encapsulent la
technologie de stockage et de requêtage.

- Un Entrepôt **seulement par racine d'agrégat** nécessitant un accès global.
- Interface en pur langage du domaine ; implémentation côté infrastructure.
- Sélection par identité, par critères, ou par **Spécification** pour les critères complexes.
- Fabrique crée du neuf ; Entrepôt retrouve l'existant. Flux d'ajout :
  client → Fabrique (création) → Entrepôt (stockage).

## 8. Rendre les concepts explicites

- **Contrainte** : extraire l'invariant dans une méthode nommée (`espaceEstDisponible()`),
  lisible et évolutive.
- **Processus** : Service ; si plusieurs algorithmes → Stratégie. À rendre explicite quand
  le Langage omniprésent le nomme.
- **Spécification** : objet de la couche domaine qui teste qu'un objet satisfait des critères
  (`clientEligible.estSatisfaitePar(client)`). Combinables. Usages : validation, sélection,
  condition de création. Évite l'éparpillement des règles booléennes complexes.

## 9. Symptômes d'audit tactiques

| # | Symptôme | Indices dans le code | Gravité typique | Remédiation |
|---|---|---|---|---|
| T1 | Modèle anémique | Entités 100 % getters/setters ; classes `*Manager`, `*Helper`, `*Util` pleines de logique métier | Majeur | Rapatrier le comportement dans les Entités/OV ; Services seulement pour le transverse |
| T2 | Fuite de couches | SQL/HTTP dans le domaine ; règles métier dans contrôleurs ou composants UI ; domaine intestable sans BDD | Bloquant | Architecture en couches ; isoler le domaine ; injection de l'infra |
| T3 | Agrégat absent | Tout le monde référence tout le monde ; modifications concurrentes incohérentes ; invariants vérifiés « ailleurs » | Majeur | Tracer frontières + racines ; réduire les associations |
| T4 | Agrégat obèse | Une racine charge la moitié du modèle ; transactions énormes ; verrouillage généralisé | Majeur | Scinder par invariants transactionnels réels |
| T5 | Identité injustifiée | IDs sur des objets purement descriptifs ; comparaison d'égalité par référence sur des valeurs | Mineur | Convertir en Objets-Valeurs immuables |
| T6 | OV mutable partagé | setters sur objets partagés (Adresse, Money) | Majeur | Immuabilité + remplacement par copie |
| T7 | Accès données anarchique | Requêtes directes éparpillées ; restauration d'objets internes d'agrégats ; logique métier dans les requêtes | Majeur | Entrepôts par racine ; Spécifications |
| T8 | Construction éparpillée | Le code client assemble des graphes d'objets complexes ; états semi-construits | Mineur | Fabriques, création atomique |
| T9 | Langage divergent | Noms techniques (`DataObject`, `ProcessorImpl`) sans rapport avec le glossaire métier ; traduction permanente expert ↔ code | Majeur | Refactorer les noms vers le Langage omniprésent ; aligner code et glossaire |
| T10 | Règles implicites | Conditions booléennes dupliquées ; « pourquoi » du code introuvable | Mineur | Contraintes nommées, Spécifications, Processus explicites |
