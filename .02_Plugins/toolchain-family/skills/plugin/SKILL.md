---
name: plugin
description: 'Activate, deactivate, or list Claude Code plugins via junction management. Hot-swappable — changes take effect on the next message. Triggers: "activate plugin", "deactivate plugin", "list plugins", "plugin list", "load plugin", "unload plugin".'
skill_api_version: 1
model: haiku
permissions:
  allowed: [Bash]
  forbidden: [Read, Glob, Grep, Edit, Write, Agent, Skill, WebFetch, WebSearch, NotebookEdit, TaskCreate, TaskUpdate]
  bash_scope: "PowerShell junction management in ~/.claude/plugins/local/ and C:\\.00_Governance\\.02_Plugins\\"
  model_tier: micro
context:
  window: inherit
  intent:
    mode: none
  intel_scope: none
metadata:
  tier: session
  dependencies: []
---

# /plugin — Plugin Manager

> **Purpose:** Activate or deactivate plugin families by managing directory junctions between `~/.claude/plugins/local/` and `C:\.00_Governance\.02_Plugins\`. Changes are hot — they take effect on the next message without restarting Claude Code.

**YOU MUST EXECUTE THIS WORKFLOW. Do not just describe it.**

---

## Commands

```
/plugin list                    # Show all available plugins and which are active
/plugin activate <name>         # Junction a plugin into plugins/local/
/plugin deactivate <name>       # Remove junction (source in .02_Plugins is untouched)
/plugin activate <n1> <n2>      # Activate multiple at once
/plugin deactivate <n1> <n2>    # Deactivate multiple at once
```

---

## Paths

| Role | Path |
|------|------|
| Source of truth | `C:\.00_Governance\.02_Plugins\` |
| Claude loads from | `C:\Users\kas41\.claude\plugins\local\` |
| Active = | junction in `plugins/local/` pointing at `.02_Plugins\<name>` |

---

## Execution Steps

### /plugin list

Run this PowerShell via Bash:

```powershell
$governance = "C:\.00_Governance\.02_Plugins"
$active_dir = "C:\Users\kas41\.claude\plugins\local"

$available = Get-ChildItem $governance -Directory |
  Where-Object { Test-Path "$($_.FullName)\.claude-plugin\plugin.json" } |
  ForEach-Object {
    $name = $_.Name
    $manifest = Get-Content "$($_.FullName)\.claude-plugin\plugin.json" | ConvertFrom-Json
    $junction = Get-Item "$active_dir\$name" -ErrorAction SilentlyContinue
    $isActive = $junction -and $junction.LinkType -eq 'Junction'
    $skillCount = (Get-ChildItem "$($_.FullName)\skills" -Directory -ErrorAction SilentlyContinue).Count
    [PSCustomObject]@{
      Name = $name
      Active = if ($isActive) { "[ACTIVE]" } else { "       " }
      Skills = $skillCount
      Description = $manifest.description
    }
  }

Write-Host ""
Write-Host "Plugin Families"
Write-Host ("=" * 60)
$available | ForEach-Object {
  Write-Host "$($_.Active)  $($_.Name) ($($_.Skills) skills)"
  Write-Host "           $($_.Description)"
  Write-Host ""
}
Write-Host "Active plugins load on next message. Edit skills in C:\.00_Governance\.02_Plugins\"
```

Render the output as a clean table to the user. Do not add commentary beyond what the data shows.

---

### /plugin activate \<name\> [name2 ...]

For each name provided, run:

```powershell
$name = "<plugin-name>"
$source = "C:\.00_Governance\.02_Plugins\$name"
$target = "C:\Users\kas41\.claude\plugins\local\$name"

# Validate source exists and is a plugin
if (-not (Test-Path "$source\.claude-plugin\plugin.json")) {
  Write-Host "ERROR: '$name' not found in .02_Plugins or missing plugin.json"
  exit 1
}

# Already active?
$existing = Get-Item $target -ErrorAction SilentlyContinue
if ($existing -and $existing.LinkType -eq 'Junction') {
  Write-Host "ALREADY ACTIVE: $name"
  exit 0
}

# Remove if a real dir somehow exists at target
if (Test-Path $target) {
  Write-Host "WARNING: $target exists but is not a junction — skipping to avoid data loss"
  exit 1
}

# Create junction
& "$env:SystemRoot\System32\cmd.exe" /c "mklink /J `"$target`" `"$source`"" 2>&1
Write-Host "ACTIVATED: $name — takes effect on next message"
```

Run all activations in parallel if multiple names given, then report results together.

---

### /plugin deactivate \<name\> [name2 ...]

For each name provided, run:

```powershell
$name = "<plugin-name>"
$target = "C:\Users\kas41\.claude\plugins\local\$name"

$existing = Get-Item $target -ErrorAction SilentlyContinue

if (-not $existing) {
  Write-Host "NOT ACTIVE: $name"
  exit 0
}

if ($existing.LinkType -ne 'Junction') {
  Write-Host "ERROR: $target exists but is not a junction — refusing to delete real directory"
  exit 1
}

# Remove the junction only — source in .02_Plugins is untouched
Remove-Item $target -Force
Write-Host "DEACTIVATED: $name — removed on next message"
```

Run all deactivations in parallel if multiple names given, then report results together.

---

## Safety Rules

- **Never delete from `C:\.00_Governance\.02_Plugins\`** — only junctions in `plugins/local/` are touched
- **Never remove a non-junction** from `plugins/local/` — refuse and warn the user
- `rpi` and `toolchain-family` can be deactivated but warn the user that core skills (`/crank`, `/plan`, `/plugin` itself) will disappear on the next message

---

## Examples

### List all plugins

**User:** `/plugin list`

**Output:**
```
Plugin Families
============================================================
[ACTIVE]  rpi (17 skills)
           Full RPI lifecycle — discovery, plan, crank...

[ACTIVE]  toolchain-family (8 skills)
           Infra and toolchain authoring...

         architecture-family (8 skills)
           ADRs, design docs, module boundaries...

         security-family (8 skills)
           Threat modelling, secrets audit, hardening...

Active plugins load on next message. Edit skills in C:\.00_Governance\.02_Plugins\
```

### Activate a plugin

**User:** `/plugin activate security-family`

**Output:**
```
ACTIVATED: security-family — takes effect on next message
```

User sends any message → system-reminder now includes security-family skills.

### Deactivate a plugin

**User:** `/plugin deactivate architecture-family`

**Output:**
```
DEACTIVATED: architecture-family — removed on next message
```

### Activate multiple

**User:** `/plugin activate architecture-family docs-family release-family`

**Output:**
```
ACTIVATED: architecture-family — takes effect on next message
ACTIVATED: docs-family — takes effect on next message
ACTIVATED: release-family — takes effect on next message
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `mklink` fails with "Access denied" | Junction creation needs elevation on some Windows configs | Run Claude Code as administrator, or use `New-Item -ItemType Junction` in an elevated PowerShell |
| Plugin activated but skills not showing | Junction created but Claude didn't re-read yet | Send any message — skills appear in the next turn's system-reminder |
| `WARNING: exists but is not a junction` | A real directory exists at `plugins/local/<name>` | Investigate before deleting — it may contain real skill content not yet in governance |
| Plugin name not found | Typo or family not yet extracted to `.02_Plugins` | Run `/plugin list` to see exact names available |
