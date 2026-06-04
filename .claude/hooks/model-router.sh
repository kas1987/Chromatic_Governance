#!/bin/bash
# model-router.sh — v3 Multi-Provider LLM Route Selector (standalone CLI helper)
#
# NOTE: This is NOT a Claude Code hook and is intentionally NOT wired into
# .claude/settings.json. A PreToolUse hook receives JSON on stdin and can only
# allow/deny/annotate a tool call — it CANNOT change which model an Agent
# subagent runs. To control a Claude subagent's model, set `model:` explicitly
# on the Agent call (see ~/.claude memory: "always set model:haiku on C1/C2").
#
# What this IS: a positional-arg CLI that prints a `provider:model` string for
# external dispatchers (n8n / LangGraph / shell scripts) choosing among the
# Ollama / Featherless / Gemini backends below.
#   usage: model-router.sh <complexity:low|medium|high> <latency_ms> <offline:true|false>
#
# Routes work across:
# - T0: Ollama local (llama3.2:3b) — cost-free, offline, latency ~500ms
# - T1: Ollama Cloud (https://ollama.com/api) — subscription-backed cloud GPU, same API, latency ~1s
# - T2: Featherless API (https://api.featherless.ai/v1) — serverless open models, low cost, ~1.6s
# - T3: Gemini cloud (gemini-2.5-flash) — high quality, ~3.4s
#
# Tier order: T0 → T1 → T2 → T3 (cost/latency ascending)

set -euo pipefail

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------
readonly OLLAMA_LOCAL_BASE="http://127.0.0.1:11434"
readonly OLLAMA_LOCAL_MODEL="llama3.2:3b"           # must be pulled locally

readonly OLLAMA_CLOUD_BASE="https://ollama.com/api"
readonly OLLAMA_CLOUD_MODEL="llama3.3:70b"          # cloud-enabled model

readonly FEATHERLESS_BASE="https://api.featherless.ai/v1"
readonly FEATHERLESS_MODEL="NousResearch/Hermes-3-Llama-3.1-8B"

readonly GEMINI_MODEL="gemini-2.5-flash"

# Metadata: concurrency, cost, latency expectations
declare -A PROVIDER_TIERS=(
    [T0_OLLAMA_LOCAL]="cost=free latency_ms=500 concurrency=4 offline=true"
    [T1_OLLAMA_CLOUD]="cost=subscription latency_ms=1000 concurrency=3 offline=false"
    [T2_FEATHERLESS]="cost=low latency_ms=1600 concurrency=unlimited offline=false"
    [T3_GEMINI]="cost=medium latency_ms=3400 concurrency=unlimited offline=false"
)

# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------
check_provider_health() {
    local provider="$1"
    case "$provider" in
        ollama_local)
            curl -sf "${OLLAMA_LOCAL_BASE}/api/tags" > /dev/null 2>&1
            ;;
        ollama_cloud)
            [[ -n "${OLLAMA_API_KEY:-}" ]]
            ;;
        featherless)
            [[ -n "${FEATHERLESS_API_KEY:-}" ]]
            ;;
        gemini)
            [[ -n "${GEMINI_API_KEY:-}" ]]
            ;;
        *)
            return 1
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Route decision tree
# ---------------------------------------------------------------------------
route_model() {
    local task_complexity="${1:-medium}"
    local latency_budget_ms="${2:-5000}"
    local offline_required="${3:-false}"

    # Rule 1: Must be offline → local Ollama only
    if [[ "$offline_required" == "true" ]]; then
        echo "ollama_local:${OLLAMA_LOCAL_MODEL}"
        return 0
    fi

    # Rule 2: Tight latency budget (<1.2s) → local Ollama
    if [[ $latency_budget_ms -lt 1200 ]]; then
        echo "ollama_local:${OLLAMA_LOCAL_MODEL}"
        return 0
    fi

    # Rule 3: High quality required → T3 Gemini
    if [[ "$task_complexity" == "high" ]]; then
        echo "gemini:${GEMINI_MODEL}"
        return 0
    fi

    # Default: balanced — prefer Ollama Cloud (subscription-backed, fast, private)
    # then fall through to Featherless if no cloud key
    if check_provider_health "ollama_cloud"; then
        echo "ollama_cloud:${OLLAMA_CLOUD_MODEL}"
        return 0
    fi
    echo "featherless:${FEATHERLESS_MODEL}"
}

# ---------------------------------------------------------------------------
# Fallback cascade
# ---------------------------------------------------------------------------
apply_fallback() {
    local provider="$1"
    case "$provider" in
        ollama_cloud)
            if check_provider_health "featherless"; then
                echo "featherless:${FEATHERLESS_MODEL}"
            elif check_provider_health "gemini"; then
                echo "gemini:${GEMINI_MODEL}"
            elif check_provider_health "ollama_local"; then
                echo "ollama_local:${OLLAMA_LOCAL_MODEL}"
            else
                echo "none:unavailable"
            fi
            ;;
        featherless)
            if check_provider_health "ollama_cloud"; then
                echo "ollama_cloud:${OLLAMA_CLOUD_MODEL}"
            elif check_provider_health "gemini"; then
                echo "gemini:${GEMINI_MODEL}"
            elif check_provider_health "ollama_local"; then
                echo "ollama_local:${OLLAMA_LOCAL_MODEL}"
            else
                echo "none:unavailable"
            fi
            ;;
        gemini)
            if check_provider_health "featherless"; then
                echo "featherless:${FEATHERLESS_MODEL}"
            elif check_provider_health "ollama_cloud"; then
                echo "ollama_cloud:${OLLAMA_CLOUD_MODEL}"
            elif check_provider_health "ollama_local"; then
                echo "ollama_local:${OLLAMA_LOCAL_MODEL}"
            else
                echo "none:unavailable"
            fi
            ;;
        ollama_local)
            if check_provider_health "ollama_cloud"; then
                echo "ollama_cloud:${OLLAMA_CLOUD_MODEL}"
            elif check_provider_health "featherless"; then
                echo "featherless:${FEATHERLESS_MODEL}"
            elif check_provider_health "gemini"; then
                echo "gemini:${GEMINI_MODEL}"
            else
                echo "none:unavailable"
            fi
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Hook mode (PreToolUse:Agent advisory)
# ---------------------------------------------------------------------------
# Invoked by .claude/settings.json as a PreToolUse hook on Agent calls. Reads
# the tool-call JSON on stdin, infers task complexity from the prompt, and emits
# non-blocking `additionalContext` recommending an external-LLM backend + the
# Claude subagent tier. It NEVER blocks (always exit 0) and CANNOT change the
# subagent's model — that requires an explicit `model:` on the Agent call.
hook_mode() {
    local input complexity route
    input="$(cat)"   # raw PreToolUse JSON; parsed leniently below

    complexity="medium"
    if grep -qiE 'architect|refactor|design|security|migrat|root cause|debug|complex|audit' <<<"$input"; then
        complexity="high"
    elif grep -qiE 'format|extract|rename|list files|lint|typo|boilerplate|stub' <<<"$input"; then
        complexity="low"
    fi

    route=$(route_model "$complexity" 5000 false)
    local provider
    provider=$(echo "$route" | cut -d: -f1)
    if ! check_provider_health "$provider"; then
        route=$(apply_fallback "$provider")
    fi

    # All emitted values are from fixed enums / `provider:model` (no quotes,
    # backslashes, or newlines), so this is JSON-safe without an escaper.
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Route advisor: task complexity=%s -> suggested external backend %s. For Claude subagents set model explicitly (C1/C2->haiku, C3->sonnet, C4->opus)."}}\n' \
        "$complexity" "$route"
    exit 0
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    if [[ "${1:-}" == "--hook" ]]; then
        hook_mode
    fi

    local route
    route=$(route_model "$@")
    local provider
    provider=$(echo "$route" | cut -d: -f1)

    # Validate primary provider; cascade to fallback if unhealthy
    if ! check_provider_health "$provider"; then
        route=$(apply_fallback "$provider")
        provider=$(echo "$route" | cut -d: -f1)
    fi

    echo "$route"

}

# Execute if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
