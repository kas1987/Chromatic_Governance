#!/bin/bash
# model-router.sh — v2 Multi-Provider LLM Router Hook
# Wired into Claude Code settings.json to select appropriate provider/model based on task context
# 
# Routes work across:
# - T0: Ollama local (llama3.2:3b) — cost-free, offline, latency ~500ms
# - T1: Featherless API (Hermes-3-8B) — responsive, low cost, ~1.6s
# - T3: Gemini cloud (2.5-flash) — high quality, ~3.4s response
#
# Uses context window, latency budget, and cost constraints to route

set -euo pipefail

# Configuration
readonly OLLAMA_BASE="http://127.0.0.1:11434"
readonly FEATHERLESS_MODEL="hermes-3-8b"
readonly GEMINI_MODEL="gemini-2.5-flash"

# Metadata: concurrency, cost, latency expectations
declare -A PROVIDER_TIERS=(
    [T0_OLLAMA]="cost=free latency_ms=500 concurrency=4 offline=true"
    [T1_FEATHERLESS]="cost=low latency_ms=1600 concurrency=unlimited offline=false"
    [T3_GEMINI]="cost=medium latency_ms=3400 concurrency=unlimited offline=false"
)

# Route decision tree
route_model() {
    local task_complexity="${1:-medium}"
    local latency_budget_ms="${2:-5000}"
    local offline_required="${3:-false}"
    
    # Rule 1: Must be offline → T0 only
    if [[ "$offline_required" == "true" ]]; then
        echo "ollama:$FEATHERLESS_MODEL"
        return 0
    fi
    
    # Rule 2: Tight latency budget (<2s) → T1 Featherless
    if [[ $latency_budget_ms -lt 2000 ]]; then
        echo "featherless:$FEATHERLESS_MODEL"
        return 0
    fi
    
    # Rule 3: High quality required → T3 Gemini
    if [[ "$task_complexity" == "high" ]]; then
        echo "gemini:$GEMINI_MODEL"
        return 0
    fi
    
    # Default: Balanced choice → T1 Featherless (good quality/speed tradeoff)
    echo "featherless:$FEATHERLESS_MODEL"
}

# Health check + fallback
check_provider_health() {
    local provider="$1"
    
    case "$provider" in
        ollama)
            if curl -s "$OLLAMA_BASE/api/tags" > /dev/null 2>&1; then
                return 0
            else
                return 1
            fi
            ;;
        featherless)
            if [[ -n "${FEATHERLESS_API_KEY:-}" ]]; then
                return 0
            else
                return 1
            fi
            ;;
        gemini)
            if [[ -n "${GEMINI_API_KEY:-}" ]]; then
                return 0
            else
                return 1
            fi
            ;;
        *)
            return 1
            ;;
    esac
}

# Main routing logic
main() {
    local route
    route=$(route_model "$@")
    local provider=$(echo "$route" | cut -d: -f1)
    
    # Validate provider is healthy; fallback if not
    if ! check_provider_health "$provider"; then
        # Fallback cascade: if primary route fails, try alternatives
        case "$provider" in
            featherless)
                if check_provider_health "gemini"; then
                    route="gemini:$GEMINI_MODEL"
                elif check_provider_health "ollama"; then
                    route="ollama:$FEATHERLESS_MODEL"
                fi
                ;;
            gemini)
                if check_provider_health "featherless"; then
                    route="featherless:$FEATHERLESS_MODEL"
                elif check_provider_health "ollama"; then
                    route="ollama:$FEATHERLESS_MODEL"
                fi
                ;;
            ollama)
                if check_provider_health "featherless"; then
                    route="featherless:$FEATHERLESS_MODEL"
                elif check_provider_health "gemini"; then
                    route="gemini:$GEMINI_MODEL"
                fi
                ;;
        esac
    fi
    
    echo "$route"
}

# Execute if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
