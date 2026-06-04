# ART-HERMES Model Evaluation Report
Date: 2026-06-04

## Setup

Tested **Qwen/Qwen2.5-Coder-32B-Instruct** (Featherless, T1 coding alt) vs
**gemini-2.5-flash** (Gemini, T3) on 3 C1/C2 Hermes mission tasks.

## Tasks

| ID | Type | Description |
|----|------|-------------|
| T1 | Mission comprehension | Extract fields from mission-001 packet as JSON |
| T2 | YAML edit | Add hermes3:8b to model-capabilities.yaml registry |
| T3 | Scope compliance | Add Hermes to C1/C2 routing only — must not appear in C4 |

## Results

| Task | Qwen Score | Qwen Latency | Gemini Score | Gemini Latency |
|------|-----------|--------------|-------------|----------------|
| T1 — comprehension | 100/100 | 31.3s | 100/100 | 3.4s |
| T2 — YAML edit | 100/100 | 14.4s | 100/100 | 5.3s |
| T3 — scope compliance | 100/100 | 16.8s | 100/100 | 3.1s |
| **AVERAGE** | **100/100** | **20.8s** | **100/100** | **3.9s** |

**Speed factor: Gemini is ~5.3x faster.**

## Quality Notes

- Both models passed all acceptance criteria on all 3 tasks.
- **Output hygiene**: Qwen echoed the prompt section header ("CURRENT ROUTING TABLE:") before the YAML output on T3. Gemini returned clean YAML immediately. Minor issue — acceptable for C1/C2 ops with post-processing trim.
- Both models respected scope compliance (hermes in C1/C2, C4 clean — 0 violations).
- Both produced valid JSON and valid YAML without markdown fences.

## Concurrency Context

### Featherless Premium ($25/mo)
| Model | Concurrency units | Simultaneous at 4-unit plan |
|-------|------------------|-----------------------------|
| Hermes-3-Llama-3.1-8B | 1 | **4 concurrent** (max swarm) |
| Qwen2.5-Coder-32B | 2 | **2 concurrent** |
| Llama-3.3-70B / Hermes-3-70B | 4 | **1 concurrent** |

### Ollama Cloud Pro ($20/mo)
- 3 concurrent cloud models
- Session limits reset every 5h; weekly every 7d
- Upgrade to Max ($100/mo) → 10 concurrent, 5x more usage

## Recommendations

### Default C1/C2 Hermes worker
→ **`NousResearch/Hermes-3-Llama-3.1-8B`** on Featherless (current T1)
- 1 concurrency unit → swarm 4 simultaneous agents at flat $25/mo
- Adequate for queue management, handoffs, summaries, bounded edits

### Coding-specialized C2 work
→ **`Qwen/Qwen2.5-Coder-32B-Instruct`** on Featherless (T1 coding_alt)
- Best dedicated coding model available on plan
- 2 concurrency units → 2 simultaneous; use for complex code edits, YAML surgery, test generation
- Registered as `coding_alt` in `~/.claude/config/provider-tiers.json`

### Latency-critical / pipeline tasks
→ **`gemini-2.5-flash`** (T3) if sub-5s response needed
- 5x faster than Featherless 32B
- Per-token cost vs flat-rate — watch usage on long context

### Swarm strategy
- For burst C1 work: fire 4× Hermes-3-8B jobs simultaneously on Featherless
- For coding burst: fire 2× Qwen2.5-Coder-32B (uses full 4 concurrency units)
- HTTP 429 returned when concurrency exceeded — implement retry with 2s backoff

## Promotion Threshold Status

Per HERMES_EVAL_PLAN.md, model may become default C1/C2 ops worker when:

| Criterion | Required | Result |
|-----------|----------|--------|
| Mission comprehension | ≥95% | ✅ 100% |
| Scope compliance | 100% | ✅ 100% |
| Schema-valid outputs | ≥95% | ✅ 100% |
| CI pass rate bounded tasks | ≥85% | *not yet measured — needs real CI run* |
| No critical stop violations in 50 missions | 0 | *not yet — 3 missions run* |

Both models clear the quality thresholds on comprehension/scope. CI validation requires harness integration.
