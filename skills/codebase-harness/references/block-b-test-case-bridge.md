# Block B — Test-case bridge to the real tests

Loaded by `codebase-harness` only if this block was retained in the scoping multiple-choice question (step 2). The other blocks live in the neighbouring `block-*.md` files.

---

## 4.1 — Prerequisite

The skill looks for `docs/business/test-cases/**/*.md`. If nothing is there, it tells the user:

> "No test-case found under docs/business/test-cases/. Run `codebase-cartographer` first, or write a few files yourself, then come back here."

And moves on to the next block (or finishes).

Every message the agent addresses to the user is phrased in the target project's language.

## 4.2 — Decorating the test-cases

For each existing test-case, the agent adds a YAML front-matter at the top of the file:

```yaml
---
feature: cart
type: nominal              # nominal | error | edge-case
priority: critical         # critical | important | nice-to-have
automated_test: tests/test_cart.py::test_add_product   # or null
status: covered            # covered | pending | manual
---
```

The keys and their allowed values are a contract shared with the other skills: they stay as they are whatever the project's language. Only the values the agent fills in — the feature name, the test path — belong to the project.

The agent tries to **pre-fill** every field:
- `feature`: inferred from the parent folder's name
- `type` and `priority`: inferred from the test-case's title and content (or flagged "to be confirmed")
- `automated_test`: searched by name across the project's test files (heuristic: the test-case name in snake_case ↔ the test name)
- `status`: `covered` if an automated test was found, `pending` otherwise

For each ambiguous test-case (several possible matches, or none), a multiple-choice question grouped at the end of the analysis:

```
I decorated N test-cases. M of them need your help:

cart/add-product.md:
  Is the test (a) tests/test_cart.py::test_add_item
              (b) tests/integration/test_cart.py::test_add
              (c) neither of those two (pending)
              (d) it exists but I did not find it — I will go looking
```

## 4.3 — Producing the verification script

The agent writes `tools/harness/check_test_coverage.*` — a complete, dependency-free reference implementation is provided in `references/harness-starters/check_test_coverage.py`. It reads nothing but markdown and paths, so it suits most projects as-is whatever their stack; adapt it mainly at the level of the globs used to find the tests. The script:

- Walks `docs/business/test-cases/**/*.md`
- Parses each YAML front-matter
- Sorts them into `covered_ok` / `covered_broken` / `pending` / `manual`
- Lists orphan tests (existing in the code but with no test-case attached)
- Exits 0 if all is well, 1 if there is at least one `covered_broken`, 2 if there are warns only

## 4.4 — Integration

As with block A: the agent proposes the pre-commit/CI snippet and asks permission to add it. Default recommendation: `warn` (exit 2 tolerated) at the start, `error` (exit 1 blocking) once `covered_broken` is down to zero.

---
