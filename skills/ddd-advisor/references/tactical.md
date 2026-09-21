# Tactical DDD — Building blocks, decision heuristics, symptoms

Reference for guidance mode (modeling decisions) and audit mode (Symptoms sections).

## Contents
1. Layered architecture
2. Entities vs value objects (decision tree)
3. Services (and which layer they belong to)
4. Modules
5. Aggregates (boundary rules)
6. Factories vs constructors
7. Repositories
8. Making concepts explicit: constraint, process, specification
9. Tactical audit symptoms

---

## 1. Layered architecture

Four layers, dependencies pointing downwards only:

```
User interface        →  presentation, interpretation of commands
Application           →  thin, coordinates, NO domain logic, no domain state
Domain                →  the core: domain state and rules
Infrastructure        →  persistence, communication, supporting libraries
```

Golden rules:
- The application layer may hold the progress state of a **task**, never the state of a
  **domain object**.
- Domain objects do not display themselves, do not persist themselves, do not orchestrate
  themselves.
- Quick test: can the domain layer be tested without a database and without a web framework?
  If not → a leak.

## 2. Entities vs value objects

**Entity**: what matters is a continuity of identity over time, independent of the attributes
(a bank account, a flight, a customer). **Value object**: only the attributes matter (an
address, an amount, coordinates, a date range).

Decision tree:
```
Do two instances with identical attributes have to be told apart?
├── YES → Entity
│   └── Define the identity: a natural attribute (account number), a generated ID,
│       or a combination of attributes. The model must define what "being the same" means.
└── NO → Value object
    ├── IMMUTABLE is mandatory once it is shared (the golden rule)
    ├── Complete and valid at construction time, otherwise an exception
    └── Group attributes into conceptual wholes (street+city+state → Address)
```

Traps:
- Turning everything into an entity "for consistency": the cost of identity, degraded
  performance, needless complexity.
- A shared mutable value object: silent corruption (a change for one customer propagates to
  the other).

## 3. Services

An important domain behavior that belongs naturally to no entity and no value object (for
instance: a transfer between two accounts). Three criteria, all required:
1. The operation refers to a domain concept that is neither an entity nor a value object
2. It refers to other domain objects
3. It is **stateless**

Placement by layer:
- The operation answers a need **of the domain** → domain service
- It **coordinates** an application task (fetch, invoke, persist) → application service
- It is technical (sending an email, writing a file) → infrastructure

Anti-pattern: one service per operation → an anemic domain model, guaranteed. A service never
replaces an operation that belongs to an object.

## 4. Modules

- Group by conceptual cohesion (communicational or functional), expose interfaces, aim for
  loose coupling.
- Module names are part of the ubiquitous language and must tell the domain's story.
- Refactoring a module is expensive, but less expensive than permanent workarounds.

## 5. Aggregates

A cluster of objects treated as a whole for the purpose of changes. Structural rules:

```
                    ┌──────────────── boundary ────────────────┐
 external objects ─►│ ROOT (entity, global identity)           │
  (root reference   │   ├─► internal entities (local identity) │
   only)            │   └─► value objects                      │
                    └──────────────────────────────────────────┘
```

- Only the root is referenced from the outside and obtained by query (a repository).
- The root enforces the **invariants** at every change of state.
- Transient references to internal objects: allowed for the duration of one operation;
  otherwise, hand out **copies** of value objects.
- An internal object may reference the root of ANOTHER aggregate (never its internals).
- Deleting the root deletes the whole aggregate.

Boundary heuristic: "what has to be consistent within the same transaction?" Before drawing
it, cut the associations down: remove the non-essential ones, constrain multiplicity, make
one-way whatever can be one-way.

## 6. Factories

They encapsulate the creation of complex objects and aggregates. Creation is **atomic**: the
root and every object under an invariant are born together and valid, otherwise an exception.

- **A factory method** on the root: to create an object THAT BELONGS TO the aggregate.
- **A dedicated factory**: to create the whole aggregate; it carries the rules, constraints
  and invariants.

A plain constructor is enough when: construction is simple, nothing cascades, the class is the
type (no hierarchy), and the client picks the implementation.

Reconstitution is a distinct case: recreating an object from the database is not creation (no
new identity, and a broken invariant calls for repair, not an exception).

## 7. Repositories

The illusion of an in-memory collection holding every object of a type. They encapsulate the
storage and querying technology.

- A repository **only per aggregate root** that needs global access.
- The interface speaks pure domain language; the implementation lives in infrastructure.
- Selection by identity, by criteria, or through a **specification** for complex criteria.
- A factory makes something new; a repository finds something that exists. Adding flow:
  client → factory (creation) → repository (storage).

## 8. Making concepts explicit

- **Constraint**: extract the invariant into a named method (`spaceIsAvailable()`), readable
  and open to change.
- **Process**: a service; if there are several algorithms → a strategy. Make it explicit as
  soon as the ubiquitous language names it.
- **Specification**: a domain-layer object testing whether an object meets a set of criteria
  (`eligibleCustomer.isSatisfiedBy(customer)`). They combine. Uses: validation, selection,
  creation condition. It stops complex boolean rules from scattering.

## 9. Tactical audit symptoms

| # | Symptom | Clues in the code | Typical severity | Remediation |
|---|---|---|---|---|
| T1 | Anemic domain model | Entities that are 100 % getters and setters; `*Manager`, `*Helper`, `*Util` classes stuffed with domain logic | Major | Move the behavior back into the entities and value objects; services only for the cross-cutting |
| T2 | Leaking layers | SQL or HTTP in the domain; domain rules in controllers or UI components; a domain that cannot be tested without a database | Blocking | Layered architecture; isolate the domain; inject the infrastructure |
| T3 | Missing aggregate | Everyone references everyone; inconsistent concurrent changes; invariants checked "somewhere else" | Major | Draw the boundaries and the roots; cut the associations down |
| T4 | Bloated aggregate | One root loads half the model; enormous transactions; locking everywhere | Major | Split along the real transactional invariants |
| T5 | Unwarranted identity | IDs on purely descriptive objects; equality by reference on values | Minor | Convert into immutable value objects |
| T6 | Shared mutable value object | Setters on shared objects (Address, Money) | Major | Immutability plus replacement by copy |
| T7 | Unruly data access | Direct queries scattered around; restoring an aggregate's internal objects; domain logic inside queries | Major | Repositories per root; specifications |
| T8 | Scattered construction | Client code assembling complex object graphs; half-built states | Minor | Factories, atomic creation |
| T9 | Diverging language | Technical names (`DataObject`, `ProcessorImpl`) unrelated to the domain glossary; constant translation between expert and code | Major | Refactor the names towards the ubiquitous language; line up code and glossary |
| T10 | Implicit rules | Duplicated boolean conditions; the "why" of the code nowhere to be found | Minor | Named constraints, specifications, explicit processes |
