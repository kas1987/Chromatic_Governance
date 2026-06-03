# Test Skill — Extended Reference

Supplementary content for the `test` skill. Loaded on-demand for extended patterns, edge cases, and anti-pattern catalogues.

---

## Extended Troubleshooting

### Coverage Tooling Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `go test -coverprofile` reports 0% | Running in wrong directory | Ensure `./...` scope includes the package under test |
| pytest-cov not installed | Missing dev dependency | `pip install pytest-cov` or add to `[project.optional-dependencies]` |
| Vitest coverage requires `@vitest/coverage-v8` | Plugin missing | `npm i -D @vitest/coverage-v8` and set `coverage.provider = 'v8'` |
| `cargo tarpaulin` timeout on large codebase | Default 1-minute timeout | Pass `--timeout 600` flag |
| Coverage report shows 100% but tests are weak | Only happy path tested | Run `/complexity` to find high-risk untested branches |

### TDD Loop Edge Cases

- **Red step passes immediately**: The behavior already exists. Narrow the test to a sub-behavior that hasn't been implemented yet. Never skip the red step.
- **Green step adds too much code**: Failing red → green should be the *minimum* change. Complexity goes in the refactor step.
- **Refactor step breaks tests**: The refactor touched external interface, not just internals. Roll back refactor; redesign so internal structure is decoupled from the API.

### Language-Specific Patterns

#### Go: Table-Driven Test with Subtests

```go
// Correct pattern: t.Run for each row, not a single assertion
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel() // safe if no shared state
        got, err := TargetFunc(tt.input)
        if (err != nil) != tt.wantErr {
            t.Fatalf("TargetFunc(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
        }
        if !tt.wantErr && !reflect.DeepEqual(got, tt.want) {
            t.Errorf("TargetFunc(%q) = %v, want %v", tt.input, got, tt.want)
        }
    })
}
```

#### Python: Fixture Scope

```python
# Module-scoped fixture avoids repeated DB connection
@pytest.fixture(scope="module")
def db_conn():
    conn = create_test_db()
    yield conn
    conn.close()
```

#### JS/TS: Async Test with proper teardown

```typescript
describe("ApiClient", () => {
  let server: MockServer;
  beforeAll(() => { server = startMockServer(); });
  afterAll(() => server.close());

  it("retries on 429", async () => {
    server.enqueue({ status: 429 });
    server.enqueue({ status: 200, body: { ok: true } });
    const result = await client.get("/test");
    expect(result.ok).toBe(true);
  });
});
```

---

## Bad Test Catalogue

Tests that inflate coverage metrics without providing value. Flag but do not delete without user confirmation.

| Anti-Pattern | Example | Why It's Bad |
|--------------|---------|--------------|
| Zero-assertion smoke | `func TestFoo(t *testing.T) { Foo() }` | Proves it doesn't panic, nothing else |
| Not-nil assertion | `assert result != nil` | Doesn't verify correctness |
| Tautological | `assert foo(x) == foo(x)` | Tests nothing |
| Implementation-coupled | Asserts internal struct field layout | Breaks on refactor, not behavior change |
| Time-dependent | `time.Sleep(100ms)` in test | Flaky on slow CI |

---

## Coverage Target Guidance

| Project Type | Recommended Minimum | Notes |
|---|---|---|
| CLI tool | 70% | Integration tests cover remaining paths |
| Library | 85% | Consumers depend on contract correctness |
| Core infrastructure | 90% | High blast radius for bugs |
| Glue code / config | 60% | Low complexity, tested implicitly |
| Generated code | Skip | Don't write tests for generated output |

---

## Output Artifacts Reference

All artifacts in `.agents/test/`:

- `coverage-raw.txt` — raw `go test`/`pytest`/`jest` output
- `coverage-func.txt` — per-function coverage (Go only, via `go tool cover -func`)
- `coverage.json` — machine-readable (Python/JS)
- `gaps.md` — ranked gap list sorted by risk (high complexity + low coverage first)
- `summary.md` — before/after delta; include this in PRs
- `tdd-log.md` — TDD cycle narrative (tdd mode)
- `strategy.md` — test architecture recommendations (strategy mode)
