# Refactor Skill — Extended Reference

Supplementary content for the `refactor` skill. Use for deep refactoring patterns, decision trees, and language-specific techniques.

---

## Refactoring Decision Tree

```
Is the code working correctly?
├── NO  → Do NOT refactor. Fix the bug first (/bug-hunt). Refactoring broken code spreads bugs.
└── YES
    ├── Do tests cover the function?
    │   ├── NO  → Add tests FIRST (/test). Refactoring without tests is risky.
    │   └── YES → Proceed with refactoring
    │       ├── Is it a naming issue? → Rename in-place (IDE rename, not find-replace)
    │       ├── Is it too long (>30 lines)? → Extract sub-functions
    │       ├── Is it duplicated? → Extract shared helper, update all call sites
    │       └── Is it too complex (cyclomatic >10)? → Decompose conditionals, use early returns
```

---

## Pattern Catalogue

### Extract Function

Before:
```go
func processOrder(order Order) error {
    // 80 lines of mixed validation + DB + notification logic
}
```
After:
```go
func processOrder(order Order) error {
    if err := validateOrder(order); err != nil { return err }
    if err := saveOrder(order); err != nil { return err }
    return notifyFulfillment(order)
}
```

### Replace Nested Conditionals with Guard Clauses

Before:
```go
func getUser(id string) (*User, error) {
    if id != "" {
        user, err := db.Find(id)
        if err == nil {
            if user.Active {
                return user, nil
            }
        }
    }
    return nil, ErrNotFound
}
```
After:
```go
func getUser(id string) (*User, error) {
    if id == ""          { return nil, ErrNotFound }
    user, err := db.Find(id)
    if err != nil        { return nil, ErrNotFound }
    if !user.Active      { return nil, ErrNotFound }
    return user, nil
}
```

### Eliminate Magic Numbers

Before:
```python
if attempts > 3:
    sleep(0.5 * attempts)
```
After:
```python
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 0.5
if attempts > MAX_RETRIES:
    sleep(BACKOFF_BASE_SECONDS * attempts)
```

---

## Refactoring Scope Guidelines

| Scope | Risk | Commit Strategy |
|-------|------|-----------------|
| Single function rename | Low | Single commit |
| Extract function (1-2 files) | Low | Single commit |
| Extract package (3-10 files) | Medium | Separate PR |
| Restructure directory layout | High | Separate PR per layer |
| Change public API | Very High | Versioned, with deprecation period |

---

## When to Stop Refactoring

1. **Tests start flaking** — Stabilize first. Flaky tests indicate shared mutable state that the refactor is surfacing.
2. **Diff exceeds ~300 LOC** — Split into smaller PRs. One PR per conceptual change.
3. **Complexity doesn't drop** — You moved complexity, not removed it. Rethink the decomposition.
4. **You're renaming for preference** — Preference != clarity. Stop if the new name isn't objectively clearer to an outsider.
