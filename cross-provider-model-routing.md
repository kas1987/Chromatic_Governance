# Cross-Provider Model Routing Reference

**Version:** 2026-06-04  
**Scope:** Cross-provider routing guidance for GPT, Gemini, Claude, and local Ollama-class models  
**Companion files:** `model-effort-routing.md`, `cross-provider-model-routing.csv`

---

## Purpose

This document defines a provider-agnostic routing layer for choosing between GPT, Gemini, Claude, and local Ollama models.

The goal is not to chase exact benchmark rankings. The goal is to route work by task shape, risk, latency, cost, ecosystem fit, and execution constraints.

Use this reference when deciding:
- which provider family should receive a task
- which model tier inside that provider should receive it
- when to prefer local models over cloud models
- when ecosystem fit matters more than raw reasoning quality

---

## Core Routing Dimensions

### Task class

| Task class | Description | Primary pressure |
|---|---|---|
| C1 | Mechanical transforms, extraction, routing, formatting | Cost and latency |
| C2 | Known-pattern implementation and standard analysis | Speed and reliability |
| C3 | Multi-step reasoning, debugging, review, synthesis | Reasoning quality |
| C4 | Ambiguous framing, architecture, policy, high-trust judgment | Judgment quality |

### Tooling tier

| Tier | Description |
|---|---|
| T1 | Pure text completion with minimal judgment |
| T2 | Cheap structured output and batch transforms |
| T3 | Strong coding, review, and reasoning workflows |
| T4 | High-trust judgment, architecture, creative synthesis |

### Additional routing flags

Use these flags before choosing a provider:

- `google-native`: the work lives in Docs, Gmail, Drive, NotebookLM, or Google media tools
- `local-only`: data must remain on-device or offline
- `multimodal-heavy`: image, video, or visual ideation is central
- `web-research`: broad web discovery is required
- `agentic-coding`: tool use, repo work, or code execution quality matters
- `huge-context`: the main problem is ingesting or compressing a large corpus
- `high-stakes`: the output will drive security, governance, architecture, or irreversible decisions

---

## Provider Strengths

| Provider | Best at | Weakest when |
|---|---|---|
| GPT | General reasoning, architecture, critique, coding, final synthesis | You mainly need Google-native context or local-only execution |
| Gemini | Google ecosystem workflows, NotebookLM, large-source ingestion, broad research, media ideation | The task depends on final judgment, architecture, or policy coherence |
| Claude | Long-form reasoning, careful writing, structured analysis, code review, governance framing | The task is tightly tied to Google-native workflows or local-only execution |
| Ollama | Local/private execution, cheap repeated inference, offline workflows, controlled automation | The task needs frontier-level judgment, top-tier tool use, or provider-native ecosystem features |

---

## Current Harness Inventory Snapshot

This reference is grounded in the current inventory documented in `C:\Users\kas41\chromatic-harness-v2\GOVERNANCE_AND_ROUTING_ARCHITECTURE.md`.

Source-of-truth rule:
- The harness repo remains the operational source of truth for live provider inventory and credentials.
- This document is a governance mirror and decision aid, not a live config file.
- If the harness config and this document disagree, treat the harness config as authoritative until this document is refreshed.
- Refresh this snapshot whenever provider inventory, enabled state, or fallback order changes materially.

### Confirmed available providers

| Provider surface | Current status | Representative models or endpoints | Notes |
|---|---|---|---|
| Ollama local | Available | `llama3.2:3b`, `qwen3-vl:4b`, `qwen2.5-coder:14b` | Laptop-local, CPU-first |
| Ollama Cloud | Available — `https://ollama.com/api` | `llama3.3:70b`, cloud-enabled model catalog | Subscription-backed cloud GPU; same API shape as local Ollama; requires `OLLAMA_API_KEY` |
| Ollama remote (LAN) | Planned / probe-first | `desktop.local:11434` | Prefer when desktop is awake and LAN latency is low |
| Featherless | Available — `https://api.featherless.ai/v1` | `NousResearch/Hermes-3-Llama-3.1-8B`, `Qwen/Qwen2.5-7B-Instruct` | OpenAI-compatible, serverless open-model inference; models use HuggingFace `Org/ModelName` paths; requires `FEATHERLESS_API_KEY` |
| LM Studio local | Installed, model-dependent | Loaded model varies | Treat as local T0 when active |
| Native Claude session | Available | `claude-sonnet-4-6` | Subscription-backed session path |
| OpenAI API | Key present in harness | `gpt-4o-mini`, `gpt-4o`, `o3-mini` | General cloud coding and reasoning |
| Gemini API | Key present in harness | `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-ultra` | Google-native, large-context, research workflows |
| Claude API | Key present in harness | `claude-haiku`, `claude-sonnet`, `claude-opus` | High-trust reasoning and governance |
| RunPod | Documented overflow path, not currently configured in `providers.yaml` | Self-hosted larger models | Use when local hardware is insufficient once configured |

### Confirmed routing posture from the harness

- Laptop context prefers T0 local first for C1-C2, then cloud escalation.
- Ollama Cloud (`https://ollama.com/api`) is the T1 cloud tier — subscription-backed, same API as local, higher-capability models.
- Featherless (`https://api.featherless.ai/v1`) is the T2 serverless tier — any open model via HuggingFace path, low per-call cost.
- Desktop or remote Ollama (LAN) shifts more C2-C3 work back to local GPU inference when awake.
- Gemini Pro is the current preferred long-context C3 route.
- Native Claude and Claude API remain the premium C3-C4 reasoning and governance routes.
- RunPod is a documented overflow option for larger-model needs, but it is not yet part of the live provider config.

---

## Default Model Family Mapping

This section maps task shape to a default provider family. Replace exact model names with the current catalog in your environment.

| Task shape | Default route | Why |
|---|---|---|
| Mechanical extraction, format conversion, lightweight classification | GPT mini, Gemini Flash-class, Claude Haiku-class, or small Ollama | Cheapest acceptable path |
| Standard coding, known-pattern implementation, routine review | GPT flagship or mini-high, Claude Sonnet-class, Gemini Pro-class | Strong T3 capability without overpaying |
| Multi-file reasoning, deep debugging, architecture review | GPT flagship, Claude Sonnet high, Claude Opus low/medium | Reasoning quality matters more than ecosystem fit |
| Ambiguous architecture, policy, high-trust decision support | GPT flagship high-effort, Claude Opus-class | Final judgment quality dominates |
| Google Docs, Gmail, Drive, NotebookLM workflows | Gemini Pro/Flash-class | Ecosystem fit dominates |
| Huge source-pack ingestion before analysis | Gemini Pro-class or NotebookLM first, then GPT or Claude | Ingestion first, reasoning second |
| Local-only or privacy-constrained automation | Ollama medium/large local model | Local control dominates |
| Visual ideation and short video experimentation | Gemini media stack | Provider-native capability dominates |

### Current-model defaults for this harness

| Task shape | Current preferred route | Fallback |
|---|---|---|
| C1 mechanical transforms | `llama3.2:3b` via local Ollama | Featherless `NousResearch/Hermes-3-Llama-3.1-8B` |
| C2 structured coding | Ollama Cloud `llama3.3:70b` or Featherless `Qwen/Qwen2.5-7B-Instruct` | `gemini-2.5-flash` |
| C3 reasoning and multi-file debug | `gemini-2.5-pro` | Native Claude or Claude Sonnet |
| C4 novel, strategic, or creative reasoning | Native Claude / Claude Opus / Gemini Ultra | RunPod if a larger hosted model is specifically needed |
| Google-native workflow | `gemini-2.5-flash` or `gemini-2.5-pro` | ChatGPT or Claude only after extraction |

---

## Routing Matrix

| Provider + tier | C-Level fit | T-Level fit | Best for | Avoid when |
|---|---|---|---|---|
| GPT mini | C1-C2 | T2-T3 | Fast transforms, lightweight coding, structured extraction | You need high-trust judgment or very deep synthesis |
| GPT flagship | C3-C4 | T3-T4 | Architecture, coding, critique, final synthesis | The task is mainly Google-native workflow execution |
| Gemini Flash-class | C1-C2 | T2-T3 | Cheap summarization, fast research passes, Google-connected productivity | You need final architecture or policy-quality reasoning |
| Gemini Pro-class | C2-C3 | T3 | Large-context ingestion, NotebookLM-adjacent workflows, broad research | You need the final decision layer for complex architecture or governance |
| Gemini Ultra-class | C4 | T4 | High-context, high-capability research synthesis and premium Gemini workflows | You mainly need agentic coding or governance-grade final judgment |
| Claude Haiku-class | C1-C2 | T1-T2 | Routing, formatting, classification, batch transforms | Multi-file reasoning or judgment-heavy work |
| Claude Sonnet-class | C2-C3 | T3 | Standard coding, review, synthesis, debugging | Creative or high-stakes work where final judgment dominates |
| Claude Opus-class | C4 | T4 | High-trust writing, governance, architecture, nuanced synthesis | Cheap or routine tasks |
| Native Claude session | C3-C4 | T4 | Subscription-backed deep reasoning and session-native agentic work | The task is cheap, repetitive, or better handled locally |
| Ollama small | C1 | T1-T2 | Local extraction, lightweight labeling, private transforms | Anything requiring strong judgment |
| Ollama medium | C1-C2 | T2-T3 | Local coding help, internal summaries, cheap private automation | Mission-critical reasoning |
| Ollama large | C2-C3 | T3 | Better local reasoning when privacy matters more than frontier quality | Top-end architecture, security, or high-stakes decisions |
| Ollama Cloud | C2-C3 | T3 | Subscription-backed cloud GPU; higher-capability models than typical local; same API as local Ollama | When privacy requires fully local execution |
| Featherless | C1-C2 | T2-T3 | Serverless open-model inference; any HuggingFace model on-demand; low cost per call | When you need top-tier frontier model quality or Google-native features |
| RunPod hosted large | C3-C4 | T4 | Larger hosted open models when local VRAM is insufficient | Routine work that fits local or standard cloud APIs |

---

## Routing Decision Tree

```text
Is the task local-only, offline, or privacy-constrained?
  -> Ollama first
  -> Use the largest local model the hardware can support for C2-C3 work

Does the task live primarily inside Google Docs, Gmail, Drive, NotebookLM, or Google media tools?
  -> Gemini first
  -> Hand off to GPT or Claude if final synthesis quality matters

Is the task mechanical, repetitive, or batch-oriented?
  -> Cheapest acceptable model: GPT mini, Gemini Flash-class, Claude Haiku-class, or small Ollama

Does the task require strong coding, review, or architecture reasoning?
  -> GPT flagship or Claude Sonnet/Opus depending on stakes

Is the task high-stakes, ambiguous, or policy-heavy?
  -> GPT flagship high-effort or Claude Opus-class

Is the task mainly broad research or huge-source ingestion?
  -> Gemini first for collection and compression
  -> GPT or Claude second for recommendation-quality synthesis
```

---

## Provider-Specific Rules

Machine-readable boundary:
- `cross-provider-model-routing.csv` is a compact inventory and tier summary.
- The markdown document is the full policy source for routing rules, anti-patterns, and implementation guidance.
- Do not treat the CSV alone as a complete routing policy.

### R1 — Prefer ecosystem fit when the task is operational, not judgment-heavy

If the work is mainly happening inside a provider's own ecosystem, route there first. The clearest example is Gemini for Google-native workflows.

### R2 — Prefer reasoning quality when the output must survive critique

For architecture, policy, audits, and agent handoffs, use GPT flagship or Claude Opus/Sonnet over ecosystem-oriented models unless a hard integration constraint says otherwise.

### R3 — Split ingestion from judgment

For huge corpora, use the best ingestion layer first, then hand the structured output to the best reasoning layer.

Typical pattern:
- Gemini or NotebookLM for ingestion and compression
- GPT or Claude for architecture, judgment, and final synthesis

### R4 — Prefer local models only when local execution is the real requirement

Do not use Ollama because it is available. Use it because privacy, offline execution, predictable cost, or automation control actually matter.

### R5 — Do not spend frontier-model budget on C1 work

Cheap tasks should go to cheap models unless the workflow overhead of switching models is worse than the cost savings.

### R6 — Native Claude is a premium path, not a default path

If a native Claude session is already active, it is a strong C3-C4 route because marginal per-call billing may effectively be zero in-session. That does not make it the default for C1-C2 work. Keep cheap work cheap.

### R7 — Remote Ollama should outrank cloud for eligible C2-C3 work

If the desktop endpoint is reachable, awake, and hosting the right model with acceptable LAN latency, prefer remote Ollama over paid cloud APIs for C2-C3 tasks.

---

## Anti-Patterns

| Pattern | Why it is wrong | Correct route |
|---|---|---|
| Using Gemini as the final architecture or policy judge | Ecosystem strength is not the same as judgment strength | Use Gemini for prep, then GPT or Claude for final reasoning |
| Using GPT flagship for mass extraction or formatting | Frontier quality is wasted on mechanical work | Use GPT mini, Gemini Flash-class, Claude Haiku-class, or Ollama small |
| Using Ollama small for high-stakes reasoning | Local availability does not create judgment quality | Escalate to GPT flagship or Claude Opus-class |
| Using Claude Opus-class for routine transforms | Premium judgment model on C1 work is wasteful | Down-route to Haiku, GPT mini, or Gemini Flash-class |
| Treating huge-context ingestion and final synthesis as the same problem | The best intake model is often not the best decision model | Split the workflow into ingestion then judgment |
| Ignoring ecosystem fit | Workflow friction can erase model-quality gains | Route Google-native work to Gemini first |
| Ignoring remote Ollama availability on the desktop | Pays cloud cost for work that fits local GPU inference | Probe remote Ollama before escalating C2-C3 tasks |

---

## Practical Defaults

| Scenario | Default |
|---|---|
| Fast structured extraction | Local Ollama `llama3.2:3b` or Gemini Flash-class |
| Default cloud coding assistant | GPT flagship, Claude Sonnet-class, or `gemini-2.5-flash` depending on context size |
| High-trust architecture memo | GPT flagship high-effort, Native Claude, or Claude Opus-class |
| Google Docs or Gmail operating workflow | Gemini |
| Research pack compression | NotebookLM or `gemini-2.5-pro` |
| Private local batch automation | Ollama medium |
| Local reasoning with stronger quality | Remote or desktop Ollama `qwen2.5-coder:14b` |
| Final audit or governance call | GPT flagship, Native Claude, or Claude Opus-class |
| Larger open-model overflow | RunPod |

---

## Governance Operations

Operationalize this reference with these minimum controls:

1. Log each routing decision with task class, privacy class, chosen provider, fallback path, and reason code.
2. Record cost estimates or zero-cost attribution for each provider path, including local and subscription-backed routes.
3. Review routing outcomes on a fixed cadence and update the provider inventory snapshot when the harness changes.
4. Escalate any disagreement between ingestion output and final judgment output to a human review step for high-stakes tasks.
5. Keep raw credentials and tokens in the harness or secret store, never in governance documentation.

---

## Implementation Guidance

If you operationalize this in code or policy:

1. Route first by hard constraints: `local-only`, `google-native`, `multimodal-heavy`, `high-stakes`.
2. Route second by task class: C1 through C4.
3. Route third by budget and latency.
4. Allow provider handoffs instead of forcing one model to do intake, reasoning, and output alone.
5. Keep provider-specific model names in config, not in the policy logic.
6. Source credentials and provider availability from the harness repo configuration, but never duplicate raw secrets into governance docs.

---

## External Reference: 9Router

`C:\Repos\9router` is useful as a routing-pattern reference, not as an implementation dependency for this governance stack.

9Router appears to be a local AI API proxy and dashboard that exposes an OpenAI-compatible endpoint, routes across many providers, applies fallback tiers, tracks quota, and translates request formats between provider families. Those patterns are relevant to provider normalization, but the project is optimized for consumer routing, quota use, and coding-tool continuity rather than governance, brokered access, RBAC, or policy enforcement.

Use 9Router selectively for these ideas:

| 9Router concept | Governance or harness mapping | Reuse posture |
|---|---|---|
| Provider executors | Harness provider adapters and adapter registry | Mine the abstraction shape, not the code |
| Subscription to cheap to free fallback tiers | Routing-table fallback policy and budget gates | Re-express as C-level, privacy, and budget rules |
| OpenAI-compatible proxy surface | Broker-facing API compatibility option | Consider only behind policy and audit gates |
| Format translation across Claude, OpenAI, Gemini-style APIs | Provider request and response normalization | Reuse as a design reference for adapter contracts |
| Quota and usage tracking | Audit telemetry, cost attribution, and routing-decision logs | Adopt the accounting pattern where it fits existing logs |

Mined patterns retained before local clone deletion:

- Executor contract: keep provider-specific URL construction, auth header shaping, request translation, credential refresh, retry, and fallback handling as separate override points.
- Registry contract: keep specialized provider handlers discoverable by provider key, with a default adapter only for explicitly allowed compatible providers.
- Compatibility shims: normalize OpenAI-compatible and Anthropic-compatible endpoints at the adapter boundary, not in policy logic.
- Provider metadata: allow provider-specific data such as base URL, account ID, organization ID, and local host selection to live in config or credential metadata, never in governance prose.
- Token economy: copy the idea of compressing bulky tool outputs before provider format translation, but gate it with tests so compression never hides audit-relevant evidence.
- Fallback accounting: reuse subscription, cheap, and free tier tracking as an accounting model, while keeping actual fallback order in audited routing policy.
- Local endpoint resolution: keep local Ollama and similar endpoint discovery in provider adapters or runtime config, not hardcoded into routing docs.

### Adapter-pattern comparison

9Router's `BaseExecutor` pattern is useful because it separates a few concerns that also exist in the harness:

| Concern | 9Router pattern | Harness posture |
|---|---|---|
| Provider lookup | `getExecutor(provider)` returns a specialized executor or default executor | Keep `adapters.yaml` as the registry source for exact and prefix-based provider adapter lookup |
| URL construction | `buildUrl()` handles provider-specific endpoint shape and fallback base URLs | Keep endpoint construction inside adapters, but source provider identity and availability from `providers.yaml` |
| Auth headers | `buildHeaders()` normalizes API key, bearer token, and provider-specific headers | Keep secret material out of governance docs; normalize auth inside adapters or token issuer code |
| Request translation | `transformRequest()` lets each executor reshape payloads | Preserve a normalized `RouteRequest` and translate only at adapter boundaries |
| Retry and fallback | Base executor retries statuses and walks alternate base URLs | Keep routing fallback policy in the router/config layer, not hidden inside provider adapters |
| Response contract | Executor returns raw upstream response context | Harness adapters should return normalized `RouteResponse` with audit-friendly usage and reason fields |

The practical takeaway is to copy the separation of concerns, not the control flow. 9Router can let executor logic choose alternate URLs because it is a convenience proxy. The governance harness should keep provider selection, privacy constraints, budget decisions, and fallback order explicit in policy/config so those decisions can be audited.

Do not use 9Router to replace the current broker or governance model. It does not provide the permission matrix, policy-engine decisions, GitHub App access mediation, secret-handling rules, or PR-only write controls required by the governance kit. Any useful idea from 9Router should be rewritten into the current harness schemas and covered by local tests before being treated as operational policy.

---

## Bottom Line

Use GPT or Claude when judgment quality is the main requirement.
Use Gemini when ecosystem fit, ingestion, or media workflows dominate.
Use Ollama when locality, privacy, or predictable low marginal cost dominate.

The best routing systems do not ask one provider to do everything. They split collection, compression, reasoning, and final synthesis across the models that are actually best suited to each stage.