# VS Code Extension Stack (Repo Baseline)

**Version:** 2026-06-04  
**Scope:** `C:\.00_Governance` workspace profile baseline

## Purpose

This document records the approved minimal VS Code extension stack for this repository so future sessions can keep tooling lean, predictable, and governance-aligned.

## Current Baseline

Installed extension count at capture time: **4**

1. `github.copilot-chat`
2. `eamodio.gitlens`
3. `dbcode.dbcode`
4. `ms-vscode.powershell`

## Why These Extensions

1. `github.copilot-chat`: Primary in-editor AI assistant for implementation, review, and governed execution.
2. `eamodio.gitlens`: Git history, blame, and review context for PR-oriented workflows.
3. `dbcode.dbcode`: Database inspection and query tooling when governance or review-intake artifacts involve DB-backed flows.
4. `ms-vscode.powershell`: First-class terminal/scripting support for Windows-native operational tasks.

## Operating Policy

1. Keep the baseline at 4 by default.
2. Add extensions only for a clearly scoped task.
3. Remove temporary extensions after the task is complete.
4. Prefer one primary AI assistant surface to avoid overlap and context noise.

## Audit Commands

Use these commands to audit and maintain the stack.

```powershell
$code = "C:\Users\kas41\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"

# List installed extensions (sorted)
& $code --list-extensions | Sort-Object

# Count installed extensions
((& $code --list-extensions) | Measure-Object).Count
```

## Change Log

### 2026-06-04

1. Consolidated extension inventory to the minimal baseline above.
2. Removed overlapping AI assistant surfaces and non-essential cloud/SQL duplicates.
3. Set this file as the source of truth for future extension audits in this repo.
