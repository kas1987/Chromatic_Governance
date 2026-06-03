# Review Skill — Extended Reference

Supplementary content for the `review` skill. Use for review criteria, checklist templates, and language-specific patterns.

---

## Review Checklist Template

Copy into review output to document coverage:

```markdown
## Review: <file or PR>

### Correctness
- [ ] Logic matches specification/intent
- [ ] Error paths handled (all return codes, exceptions)
- [ ] Edge cases: empty input, null/nil, overflow, concurrent access
- [ ] State mutations visible to callers are correct

### Security
- [ ] No hardcoded credentials or secrets
- [ ] User input validated and sanitized before use
- [ ] No SQL/command injection vectors
- [ ] Auth checks not skipped on new endpoints

### Performance
- [ ] No N+1 query pattern
- [ ] No unbounded allocations in hot paths
- [ ] Caching used where appropriate

### Maintainability
- [ ] Names are clear without a comment
- [ ] Functions are small and single-purpose
- [ ] No duplicated logic (DRY violation)
- [ ] Tests cover new behavior

### Tests
- [ ] Happy path covered
- [ ] Error paths covered
- [ ] Edge cases tested
- [ ] Tests assert specific values (not just "not nil")
```

---

## Language-Specific Review Focus

### Go
- Check all `error` return values are handled (not ignored with `_`)
- `defer` inside loops creates unbounded closures — flag it
- Goroutine leaks: every spawned goroutine needs a shutdown path
- `context.Context` should be first arg in all public functions

### Python
- Check for mutable default arguments: `def f(x=[])` — classic bug
- `except Exception` without re-raise swallows unexpected errors
- Implicit `None` returns in functions that should always return a value

### TypeScript/JavaScript
- `any` type usage — flag; suggest specific types
- Missing `await` on async functions returns Promise, not value
- `==` vs `===` — always use `===` for comparisons

---

## Severity Levels for Review Findings

| Severity | Label | Examples |
|----------|-------|---------|
| Blocker | 🔴 BLOCK | Security vulnerability, data loss risk, incorrect logic |
| Required | 🟡 REQ | Missing error handling, test coverage gap |
| Suggestion | 🟢 SUG | Style, naming, optional optimization |
| Nit | 💬 NIT | Minor formatting, preference-level feedback |

Only BLOCK and REQ should prevent merge. SUG and NIT are advisory.

---

## Deep Review Mode (--deep)

When `--deep` flag is set:
1. Standard review pass runs first (as normal)
2. Council is spawned with the review output as context
3. Council judges: security analyst, senior engineer, fresh eyes
4. Debate round: judges challenge each other's findings
5. Final council report merged into review document under `## Council Findings`

Use `--deep` for:
- Security-sensitive modules (auth, payments, crypto)
- Public API changes
- Complex concurrency code
- Code from external contributors
