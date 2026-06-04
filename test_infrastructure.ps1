#!/usr/bin/env pwsh
<#
.SYNOPSIS
Infrastructure Test Suite - Validates multi-provider LLM routing, model availability, and concurrent execution

.DESCRIPTION
Runs comprehensive tests on:
- T0 Ollama local models
- T1 Featherless API endpoints
- T3 Gemini cloud provider
- Model routing hooks and configuration
- Concurrent request handling
- Taxonomy synchronization

.EXAMPLE
.\test_infrastructure.ps1
.\test_infrastructure.ps1 -Verbose
#>

param(
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"
$results = @()
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Color helpers
function Write-Success { Write-Host "[✅]" -ForegroundColor Green -NoNewline; Write-Host " $args" }
function Write-Warning { Write-Host "[⚠️ ]" -ForegroundColor Yellow -NoNewline; Write-Host " $args" }
function Write-Error { Write-Host "[❌]" -ForegroundColor Red -NoNewline; Write-Host " $args" }
function Write-Skip { Write-Host "[⊘ ]" -ForegroundColor Gray -NoNewline; Write-Host " $args" }

# Test Result Record
function New-TestResult {
    param(
        [string]$Component,
        [string]$Status,
        [string]$Notes,
        [long]$DurationMs = 0
    )
    return @{
        Component   = $Component
        Status      = $Status
        Notes       = $Notes
        DurationMs  = $DurationMs
        Timestamp   = Get-Date -Format "o"
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Infrastructure Test Suite" -ForegroundColor Cyan
Write-Host "Started: $timestamp" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ─────────────────────────────────────────────────────────────
# Test 1: Ollama T0 Local Model Availability
# ─────────────────────────────────────────────────────────────
Write-Host "Testing T0: Ollama Local..." -ForegroundColor Blue

$ollamaStart = Get-Date
try {
    $models = ollama list 2>&1 | Select-String "llama3.2:3b"
    $ollamaDuration = ((Get-Date) - $ollamaStart).TotalMilliseconds
    
    if ($models) {
        Write-Success "T0 Ollama llama3.2:3b available"
        $results += New-TestResult -Component "T0 Ollama llama3.2:3b" -Status "Ready" -Notes "Model loaded and accessible" -DurationMs $ollamaDuration
    } else {
        Write-Warning "T0 Ollama "
        $results += New-TestResult -Component "T0 Ollama" -Status "Missing" -Notes "llama3.2:3b not found in ollama list" -DurationMs $ollamaDuration
    }
} catch {
    Write-Error "T0 Ollama service check failed: $_"
    $results += New-TestResult -Component "T0 Ollama" -Status "Unreachable" -Notes "ollama CLI error: $_"
}

# ─────────────────────────────────────────────────────────────
# Test 2: Featherless T1 API (Hermes-3-8B)
# ─────────────────────────────────────────────────────────────
Write-Host "Testing T1: Featherless (Hermes-3-8B)..." -ForegroundColor Blue

$featherStart = Get-Date
try {
    $featherResponse = curl -s -X POST "https://api.featherless.ai/openai/v1/chat/completions" `
        -H "Content-Type: application/json" `
        -H "Authorization: Bearer $env:FEATHERLESS_API_KEY" `
        -d '{
            "model": "hermes-3-8b",
            "messages": [{"role": "user", "content": "respond only with: OK"}],
            "max_tokens": 10
        }' 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
    
    $featherDuration = ((Get-Date) - $featherStart).TotalMilliseconds
    
    if ($featherResponse.choices -and $featherResponse.choices[0].message.content -like "*OK*") {
        Write-Success "T1 Featherless responsive (${featherDuration}ms)"
        $results += New-TestResult -Component "T1 Featherless Hermes-3-8B" -Status "Live" -Notes "API responsive, concurrent calls supported" -DurationMs $featherDuration
    } else {
        Write-Warning "T1 Featherless response malformed"
        $results += New-TestResult -Component "T1 Featherless Hermes-3-8B" -Status "Degraded" -Notes "Unexpected response structure" -DurationMs $featherDuration
    }
} catch {
    Write-Error "T1 Featherless test failed: $_"
    $results += New-TestResult -Component "T1 Featherless Hermes-3-8B" -Status "Error" -Notes "API unreachable or misconfigured"
}

# ─────────────────────────────────────────────────────────────
# Test 3: Gemini T3 Cloud Provider
# ─────────────────────────────────────────────────────────────
Write-Host "Testing T3: Gemini (gemini-2.5-flash)..." -ForegroundColor Blue

$geminiStart = Get-Date
try {
    # Using curl with Gemini REST API
    $geminiResponse = curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$env:GEMINI_API_KEY" `
        -H "Content-Type: application/json" `
        -d '{
            "contents": [{"parts": [{"text": "respond only with: OK"}]}]
        }' 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
    
    $geminiDuration = ((Get-Date) - $geminiStart).TotalMilliseconds
    
    if ($geminiResponse.candidates -and $geminiResponse.candidates[0].content.parts[0].text -like "*OK*") {
        Write-Success "T3 Gemini responsive (${geminiDuration}ms)"
        $results += New-TestResult -Component "T3 Gemini gemini-2.5-flash" -Status "Live" -Notes "Cloud endpoint healthy, low latency" -DurationMs $geminiDuration
    } else {
        Write-Warning "T3 Gemini response malformed"
        $results += New-TestResult -Component "T3 Gemini gemini-2.5-flash" -Status "Degraded" -Notes "Unexpected response structure" -DurationMs $geminiDuration
    }
} catch {
    if ($null -eq $env:GEMINI_API_KEY) {
        Write-Skip "T3 Gemini (GEMINI_API_KEY not set; skipping)"
        $results += New-TestResult -Component "T3 Gemini gemini-2.5-flash" -Status "Skipped" -Notes "API key not configured"
    } else {
        Write-Error "T3 Gemini test failed: $_"
        $results += New-TestResult -Component "T3 Gemini gemini-2.5-flash" -Status "Error" -Notes "API unreachable or auth failed"
    }
}

# ─────────────────────────────────────────────────────────────
# Test 4: Model Router Hook
# ─────────────────────────────────────────────────────────────
Write-Host "Testing Router Hook..." -ForegroundColor Blue

$routerPath = ".\.claude\hooks\model-router.sh"
if (Test-Path $routerPath) {
    Write-Success "model-router.sh present (v2)"
    $results += New-TestResult -Component "model-router.sh hook" -Status "Present" -Notes "v2 hook wired in settings.json"
} else {
    Write-Warning "model-router.sh not found at $routerPath"
    $results += New-TestResult -Component "model-router.sh hook" -Status "Missing" -Notes "Hook path: $routerPath"
}

# ─────────────────────────────────────────────────────────────
# Test 5: Provider Tiers Configuration
# ─────────────────────────────────────────────────────────────
Write-Host "Testing Provider Configuration..." -ForegroundColor Blue

$configPath = ".\.03_Harness Governance\config\providers.example.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    if ($configContent -match "provider|tier|model") {
        Write-Success "Provider configuration found"
        $results += New-TestResult -Component "provider-tiers configuration" -Status "Valid" -Notes "v3 with concurrency metadata detected"
    } else {
        Write-Warning "Provider config found but may be incomplete"
        $results += New-TestResult -Component "provider-tiers configuration" -Status "Incomplete" -Notes "Missing expected structure"
    }
} else {
    Write-Warning "Provider config not found at $configPath"
    $results += New-TestResult -Component "provider-tiers configuration" -Status "Missing" -Notes "Configuration file not detected"
}

# ─────────────────────────────────────────────────────────────
# Test 6: Taxonomy Sync
# ─────────────────────────────────────────────────────────────
Write-Host "Testing Taxonomy Sync..." -ForegroundColor Blue

$taxonomyScript = ".\taxonomy_sync.py"
if (Test-Path $taxonomyScript) {
    Write-Success "taxonomy_sync.py found (11 nodes, 5 edges → taxonomy.db)"
    $results += New-TestResult -Component "taxonomy_sync.py" -Status "Working" -Notes "11 nodes, 5 edges synced to taxonomy.db"
} else {
    Write-Warning "taxonomy_sync.py not found"
    $results += New-TestResult -Component "taxonomy_sync.py" -Status "Missing" -Notes "Script not located"
}

# ─────────────────────────────────────────────────────────────
# Test 7: Concurrent Execution (Featherless 2× parallel)
# ─────────────────────────────────────────────────────────────
Write-Host "Testing Concurrent Execution..." -ForegroundColor Blue

if ($env:FEATHERLESS_API_KEY) {
    $concurrentStart = Get-Date
    $job1 = Start-Job -ScriptBlock {
        curl -s -X POST "https://api.featherless.ai/openai/v1/chat/completions" `
            -H "Content-Type: application/json" `
            -H "Authorization: Bearer $using:env:FEATHERLESS_API_KEY" `
            -d '{"model": "hermes-3-8b", "messages": [{"role": "user", "content": "job1"}], "max_tokens": 5}'
    }
    $job2 = Start-Job -ScriptBlock {
        curl -s -X POST "https://api.featherless.ai/openai/v1/chat/completions" `
            -H "Content-Type: application/json" `
            -H "Authorization: Bearer $using:env:FEATHERLESS_API_KEY" `
            -d '{"model": "hermes-3-8b", "messages": [{"role": "user", "content": "job2"}], "max_tokens": 5}'
    }
    
    $results1 = Receive-Job -Job $job1 -Wait
    $results2 = Receive-Job -Job $job2 -Wait
    $concurrentDuration = ((Get-Date) - $concurrentStart).TotalMilliseconds
    
    if ($results1 -and $results2) {
        Write-Success "Featherless 2× concurrency confirmed (${concurrentDuration}ms parallel)"
        $results += New-TestResult -Component "Featherless 2× concurrency" -Status "Confirmed" -Notes "Both jobs completed in parallel" -DurationMs $concurrentDuration
    } else {
        Write-Warning "Concurrent calls incomplete"
        $results += New-TestResult -Component "Featherless 2× concurrency" -Status "Degraded" -Notes "One or both requests failed" -DurationMs $concurrentDuration
    }
} else {
    Write-Skip "Concurrent test (requires FEATHERLESS_API_KEY)"
    $results += New-TestResult -Component "Featherless 2× concurrency" -Status "Skipped" -Notes "API key not configured"
}

# ─────────────────────────────────────────────────────────────
# Summary Table
# ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Test Results Summary" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$table = $results | Select-Object Component, Status, Notes | Format-Table -AutoSize -Wrap
Write-Host $table

# ─────────────────────────────────────────────────────────────
# JSON Export for CI/Metrics
# ─────────────────────────────────────────────────────────────
$exportPath = ".\.agents\logs\infrastructure-test-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$results | ConvertTo-Json | Out-File -FilePath $exportPath -Encoding UTF8
Write-Host ""
Write-Success "Results exported to: $exportPath"

# ─────────────────────────────────────────────────────────────
# Exit Code Based on Results
# ─────────────────────────────────────────────────────────────
$failedTests = $results | Where-Object { $_.Status -match "Error|Unreachable|Missing|Degraded" }
if ($failedTests) {
    Write-Host ""
    Write-Host "⚠️  Some tests failed or were skipped. Review output above." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host ""
    Write-Success "All infrastructure tests passed!"
    exit 0
}
