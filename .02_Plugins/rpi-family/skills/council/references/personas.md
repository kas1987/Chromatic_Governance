# Perspectives

## Default: Independent Judges (No Perspectives)

When no `--preset` or `--perspectives` flag is provided, all judges get the **same prompt** with no perspective label. Diversity comes from independent sampling, not personality labels.

| Judge | Prompt | Assigned To |
|-------|--------|-------------|
| **Judge 1** | Independent judge — same prompt as all others | Agent 1 |
| **Judge 2** | Independent judge — same prompt as all others | Agent 2 |
| **Judge 3** | Independent judge — same prompt as all others | Agent 3 (--deep/--mixed) |

The default judge prompt (no perspective labels):

```
You are Council Judge {N}. You are one of {TOTAL} independent judges evaluating the same target.

{JSON_PACKET}

Instructions:
1. Analyze the target thoroughly
2. Write your analysis to: .agents/council/{OUTPUT_FILENAME}
   - Start with a JSON code block matching the output_schema
   - Follow with Markdown explanation
3. Send verdict to team lead

Your job is to find problems. A PASS with caveats is less valuable than a specific FAIL.
```

When `--preset` or `--perspectives` is used, judges receive the perspective-labeled prompt instead (see Agent Prompts section).

## Custom Perspectives

Simple name-based:
```bash
/council --perspectives="security,performance,ux" validate the API
```

## Built-in Presets

Use `--preset=<name>` for common persona configurations:

| Preset | Perspectives | Best For |
|--------|-------------|----------|
| `default` | (none — independent judges) | General validation |
| `security-audit` | attacker, defender, compliance, web-security | Security review |
| `architecture` | scalability, maintainability, simplicity | System design |
| `research` | breadth, depth, contrarian | Deep investigation |
| `ops` | reliability, observability, incident-response | Operations review |
| `code-review` | error-paths, api-surface, spec-compliance | Code validation (used by /vibe) |
| `plan-review` | missing-requirements, feasibility, scope, spec-completeness | Plan validation (used by /pre-mortem) |
| `doc-review` | clarity-editor, accuracy-verifier, completeness-auditor, audience-advocate | Documentation quality review |
| `retrospective` | plan-compliance, tech-debt, learnings | Post-implementation review (used by /post-mortem) |
| `product` | user-value, adoption-barriers, competitive-position, strategic-fit | Product-market fit review (used by /pre-mortem when PRODUCT.md exists) |
| `developer-experience` | api-clarity, error-experience, discoverability | Developer UX review (used by /vibe when PRODUCT.md exists) |
| `performance` | latency, throughput, memory, profiling | Performance bottleneck review |
| `data-integrity` | schema, migration, consistency, audit-trail | Data safety and migration review |
| `dependency-audit` | supply-chain, transitive, licensing, version-drift | Dependency health and CVE review |
| `test-quality` | coverage, assertions, pyramid, mutation | Test suite robustness review |
| `cost-analysis` | token-budget, api-spend, wave-sizing, efficiency | Agent cost and ROI review |
| `empirical` | historical, evidence, benchmark, skeptic | Evidence-first / data-backed review (uses git history + WebFetch) |

```bash
/council --preset=security-audit validate the auth system
/council --preset=research --explorers=3 research upgrade automation
/council --preset=architecture research microservices boundaries
```

**Preset definitions** are built-in perspective configurations.

**Persona name mappings:**

| Preset | Name | Perspective |
|--------|------|-------------|
| security-audit | **Red** | attacker |
| security-audit | **Blue** | defender |
| security-audit | **Auditor** | compliance |
| security-audit | **WebSec** | web-security |
| architecture | **Scale** | scalability |
| architecture | **Craft** | maintainability |
| architecture | **Razor** | simplicity |
| code-review | **Pathfinder** | error-paths |
| code-review | **Surface** | api-surface |
| code-review | **Spec** | spec-compliance |
| plan-review | **Gaps** | missing-requirements |
| plan-review | **Reality** | feasibility |
| plan-review | **Scope** | scope |
| plan-review | **Completeness** | spec-completeness |
| retrospective | **Compass** | plan-compliance |
| retrospective | **Debt** | tech-debt |
| retrospective | **Harvest** | learnings |
| product | **Value** | user-value |
| product | **Barriers** | adoption-barriers |
| product | **Edge** | competitive-position |
| product | **North** | strategic-fit |
| developer-experience | **Signal** | api-clarity |
| developer-experience | **SOS** | error-experience |
| developer-experience | **Beacon** | discoverability |
| doc-review | **Clarity** | clarity-editor |
| doc-review | **Accuracy** | accuracy-verifier |
| doc-review | **Coverage** | completeness-auditor |
| doc-review | **Audience** | audience-advocate |
| research | **Wide** | breadth |
| research | **Deep** | depth |
| research | **Contrarian** | contrarian |
| ops | **Uptime** | reliability |
| ops | **Lens** | observability |
| ops | **Oncall** | incident-response |
| performance | **Timer** | latency |
| performance | **Flood** | throughput |
| performance | **Heap** | memory |
| performance | **Probe** | profiling |
| data-integrity | **Schema** | schema |
| data-integrity | **Migra** | migration |
| data-integrity | **Anchor** | consistency |
| data-integrity | **Ledger** | audit-trail |
| dependency-audit | **Chain** | supply-chain |
| dependency-audit | **Depth** | transitive |
| dependency-audit | **Counsel** | licensing |
| dependency-audit | **Drift** | version-drift |
| test-quality | **Blanket** | coverage |
| test-quality | **Assert** | assertions |
| test-quality | **Pyramid** | pyramid |
| test-quality | **Mutant** | mutation |
| cost-analysis | **Meter** | token-budget |
| cost-analysis | **Ledge** | api-spend |
| cost-analysis | **Batch** | wave-sizing |
| cost-analysis | **Trim** | efficiency |
| empirical | **Historian** | historical |
| empirical | **Evidence** | evidence |
| empirical | **Benchmark** | benchmark |
| empirical | **Skeptic** | skeptic |

**Preset perspective details:**

```
security-audit:
  attacker:   {name: Red}       "How would I exploit this? What's the weakest link?"
  defender:   {name: Blue}      "How do we detect and prevent attacks? What's our blast radius?"
  compliance:   {name: Auditor}   "Does this meet regulatory requirements? What's our audit trail?"
  web-security: {name: WebSec}    "What OWASP Top 10 risks are present? Check for injection, XSS, path traversal, CORS misconfig, auth bypass, CSRF, response splitting, SSRF (outbound URL validation), missing security headers (HSTS, X-Frame-Options, CSP), rate limiting on auth/API/upload endpoints, and credential/token exposure in logs."

architecture:
  scalability:     {name: Scale}  "Will this handle 10x load? Where are the bottlenecks?"
  maintainability: {name: Craft}  "Can a new engineer understand this in a week? Where's the complexity?"
  simplicity:      {name: Razor}  "What can we remove? Is this the simplest solution?"

research:
  breadth:     {name: Wide}       "What's the full landscape? What options exist? What's adjacent?"
  depth:       {name: Deep}       "What are the deep technical details? What's under the surface?"
  contrarian:  {name: Contrarian} "What's the conventional wisdom wrong about? What's overlooked?"

ops:
  reliability:       {name: Uptime}  "What fails first? What's our recovery time? Where are SPOFs?"
  observability:     {name: Lens}    "Can we see what's happening? What metrics/logs/traces do we need?"
  incident-response: {name: Oncall}  "When this breaks at 3am, what do we need? What's our runbook?"

code-review:
  error-paths:      {name: Pathfinder}  "Trace every error handling path. What's uncaught? What fails silently? For classifiers: generate 5 realistic false-positive inputs per pattern. For enums parsed from wire: check allowlist validation. For struct fields: verify every code path (including synthesized/summary instances) populates all fields."
  api-surface:      {name: Surface}     "Review every public interface. Is the contract clear? Breaking changes? For structs with new fields: grep all literal constructors, verify completeness. For sorted data with index fields: verify index refers to original position, not post-sort. For default/fallback cases: verify semantic distinction (execution_error vs unknown)."
  spec-compliance:  {name: Spec}        "Compare implementation against the spec/bead. What's missing? What diverges? Check test quality: assertions must use exact expected values (== Y), never negations (!= X). Negation assertions silently pass when results drift to a third wrong value."
  # Note: spec-compliance gracefully degrades to general correctness review when no spec
  # is present in context.spec. The judge reviews code on its own merits.

plan-review:
  missing-requirements: {name: Gaps}         "What's not in the spec that should be? What questions haven't been asked?"
  feasibility:          {name: Reality}       "What's technically hard or impossible here? What will take 3x longer than estimated? For classification/pattern-matching work: does the plan specify false-positive testing strategy and taxonomy completeness criteria? For struct changes: does the plan account for all construction sites and synthesized instances?"
  scope:                {name: Scope}         "What's unnecessary? What's missing? Where will scope creep?"
  spec-completeness:    {name: Completeness}  "Are boundaries defined (Always/Ask First/Never)? Do conformance checks cover all acceptance criteria? Can every acceptance criterion be mechanically verified? Are schema enum values and field names domain-neutral (meaningful in ANY codebase, not just this repo)? Also enforce lifecycle contract completeness: canonical mutation+ack sequence, crash-safe consume protocol with atomic boundary + restart recovery, field-level precedence truth table with anomaly codes, and boundary failpoint conformance tests. Missing/contradictory checklist items are WARN minimum; critical non-mechanically-verifiable invariants are FAIL."

retrospective:
  plan-compliance: {name: Compass}  "What was planned vs what was delivered? What's missing? What was added?"
  tech-debt:       {name: Debt}     "What shortcuts were taken? What will bite us later? What needs cleanup?"
  learnings:       {name: Harvest}  "What patterns emerged? What should be extracted as reusable knowledge?"

product:
  user-value:            {name: Value}     "Evaluate whether the target delivers meaningful value to defined personas. Check if it addresses stated user needs, solves real problems, and creates measurable benefit."
  adoption-barriers:     {name: Barriers}  "Identify obstacles that could prevent users from adopting or benefiting from this. Consider onboarding friction, learning curve, prerequisite knowledge, and migration costs."
  competitive-position:  {name: Edge}      "Assess how this strengthens or weakens competitive position. Check differentiation, parity gaps, and whether this creates defensible advantages."
  strategic-fit:         {name: North}     "Evaluate alignment with stated product mission, goals, and roadmap. Flag scope creep or misalignment with strategic direction."

doc-review:
  clarity-editor:       {name: Clarity}   "Is every sentence unambiguous? Can a reader understand without re-reading? Where's the jargon?"
  accuracy-verifier:    {name: Accuracy}  "Do code examples match the actual API? Are version numbers current? Do links resolve?"
  completeness-auditor: {name: Coverage}  "What's documented but not explained? What's missing entirely? Are edge cases covered?"
  audience-advocate:    {name: Audience}  "Who is the reader? Is the assumed knowledge level consistent? Would a newcomer get lost?"

developer-experience:
  api-clarity:     {name: Signal}  "Is every public interface self-documenting? Can a user predict behavior from names alone?"
  error-experience: {name: SOS}    "When something goes wrong, does the user know what happened, why, and what to do next?"
  discoverability: {name: Beacon}  "Can a new user find this feature without reading docs? Is the happy path obvious?"

performance:
  # Role: JUDGE — subagent_type=Explore. Tools: Read, Glob, Grep, Bash(perf cmds read-only)
  latency:    {name: Timer}  "Where is time spent? What's P99 vs P50? Identify blocking calls, synchronous I/O, and lock contention. Check for missing async/await, N+1 query patterns, and sequential work that could parallelize."
  throughput: {name: Flood}  "What's the maximum sustainable request rate? Where does degradation begin under load? Check for connection pool limits, thread starvation, and backpressure-absent queues."
  memory:     {name: Heap}   "What leaks? What allocates unnecessarily? Check for unbounded caches, goroutine/thread proliferation, large object graphs held in closures, and missing defer-close on resources."
  profiling:  {name: Probe}  "Which code paths are hot? Where do cache misses occur? Identify hot loops, repeated string allocations, and code that runs in the critical request path but doesn't need to."

data-integrity:
  # Role: JUDGE — subagent_type=Explore. Tools: Read, Glob, Grep
  schema:      {name: Schema}  "Are all field constraints enforced at the DB/schema layer? What's the null/default behavior for every field? Check for missing NOT NULL, missing FK constraints, and fields that can hold semantically invalid values."
  migration:   {name: Migra}   "Is the migration reversible? What's the down migration? Is it safe under concurrent writes during deploy? Check for table locks on large tables, column renames vs add-then-drop, and enum value additions."
  consistency: {name: Anchor}  "Where can data reach an inconsistent state? What invariants must always hold? Check for multi-step writes without transactions, optimistic-lock races, and denormalized data that can diverge."
  audit-trail: {name: Ledger}  "What operations lack audit logs? What mutations are unattributable? Check for missing created_by/updated_by, soft-delete vs hard-delete policy, and operations that bypass the audit layer."

dependency-audit:
  # Role: EVIDENCE_JUDGE — subagent_type=Explore. Tools: Read, Glob, Grep, WebFetch (CVE lookups)
  supply-chain:  {name: Chain}    "Which direct dependencies have known CVEs? Use WebFetch to check NVD/OSV/GitHub Advisories. What's the last-commit date for each dep? Flag unmaintained packages (no commits >12 months)."
  transitive:    {name: Depth}    "What are the transitive dependency trees? Which transitive deps pull in abandonware or conflicting versions? Check for diamond-dependency version conflicts."
  licensing:     {name: Counsel}  "Are all dependency licenses compatible with the project license? Flag copyleft (GPL/AGPL) contamination in non-GPL projects. Check for SSPL, BUSL, and 'non-commercial' clauses."
  version-drift: {name: Drift}    "How far behind are direct deps compared to latest releases? What breaking changes are pending in major version upgrades? Check CHANGELOG/migration guides via WebFetch."

test-quality:
  # Role: JUDGE — subagent_type=Explore. Tools: Read, Glob, Grep
  coverage:   {name: Blanket}  "What code paths are untested? Grep for untested error returns, uncovered branches, and functions with zero test references. Flag files with no corresponding test file."
  assertions: {name: Assert}   "Are assertions specific? Do they use exact expected values (== Y) rather than negations (!= X)? Check for tautological assertions, missing error message checks, and tests that pass vacuously when the subject returns early."
  pyramid:    {name: Pyramid}  "Is the test distribution L0–L3 healthy? Too many slow integration tests, too few fast unit tests? Check for tests that cross multiple boundaries unnecessarily. See test-pyramid.md for level definitions."
  mutation:   {name: Mutant}   "Would tests catch a logical mutation (flip a condition, swap a value, remove a branch)? Identify tests with no assertions, tests that only assert side effects, and tests where the pass condition is too broad."

cost-analysis:
  # Role: JUDGE — subagent_type=Explore. Tools: Read, Glob, Grep
  token-budget: {name: Meter}  "What's the estimated token cost per wave? Which workers receive oversized prompts? Check for knowledge injections >40% of context window, full-file reads that could be targeted Grep calls, and result files that explode back into orchestrator context."
  api-spend:    {name: Ledge}  "What's the estimated API spend for this plan (workers × waves × model tier × avg tokens)? Flag waves where opus is used for mechanical work that haiku could handle."
  wave-sizing:  {name: Batch}  "Are waves correctly sized for the available concurrency? Too many workers (collision risk) or too few (serial bottleneck)? Check that dependency ordering matches the wave structure."
  efficiency:   {name: Trim}   "What can be cached across sessions (cache prefix discipline)? Where are redundant file reads across workers? What's the ROI per worker — are any tasks so small they're not worth the spawn overhead?"

empirical:
  # Role: EVIDENCE_JUDGE + HISTORIAN — subagent_type=Explore. Tools: Read, Glob, Grep, WebFetch, WebSearch, Bash(git read-only)
  historical:  {name: Historian}  "What does git history reveal? Run git log --follow, git blame, git log --grep to find how this code evolved. What recurring patterns appear in commit messages? What's been attempted and reverted? Cite specific commits."
  evidence:    {name: Evidence}   "Find empirical support or contradiction for every claim in the target. Use WebFetch to gather external evidence: relevant issues, RFCs, benchmark results, prior art. Every assertion should cite a source."
  benchmark:   {name: Benchmark} "Are performance or scale claims backed by measurements? Grep for benchmark files. Use WebFetch to find published benchmarks for comparable systems. Flag unsupported quantitative claims (e.g., '10x faster', '99.9% uptime') with severity=significant."
  skeptic:     {name: Skeptic}    "Challenge every assumption with data. For each stated benefit, find evidence it actually holds. For each risk dismissed as 'unlikely', find historical examples of it occurring. Weight data over intuition."
```

## Tool Usage by Judge Role

| Role | subagent_type | Read/Glob/Grep | Bash | WebFetch | WebSearch | Writes |
|------|--------------|----------------|------|----------|-----------|--------|
| Standard JUDGE | `Explore` | ✓ | — | — | — | — |
| EVIDENCE_JUDGE | `Explore` | ✓ | — | ✓ | ✓ | — |
| HISTORIAN | `Explore` | ✓ | git log/blame/show only | — | — | — |

**Preset → role mapping:**
- Standard presets (security-audit, architecture, code-review, plan-review, retrospective, product, developer-experience, ops, research, doc-review, performance, data-integrity, test-quality, cost-analysis) → **JUDGE** role
- `dependency-audit` → **EVIDENCE_JUDGE** (needs WebFetch for CVE lookups and changelogs)
- `empirical` → **HISTORIAN** (historical/benchmark judges) + **EVIDENCE_JUDGE** (evidence/skeptic judges)

Governance rules for each role are in `skills/shared/references/subagent-governance.md`.
