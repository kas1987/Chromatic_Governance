---
name: system-audit
description: 'Audits all configurable system properties and shows how they cascade into subsystems, pipelines, hooks, and ways of working. Supports pre-change preview, post-change report, and before/after diff via snapshots. Triggers: system audit, audit properties, property impact, what does X affect, settings cascade.'
skill_api_version: 1
context:
  window: inherit
  intent:
    mode: none
  intel_scope: none
metadata:
  tier: session
  dependencies: []
---

# System Audit Skill

> **Quick Ref:**
> - `/system-audit` — full report of all properties + impact map
> - `/system-audit preview defaultMode=bypassPermissions` — what flips if I change this?
> - `/system-audit snapshot` — freeze current state before a change
> - `/system-audit diff` — compare current state vs last snapshot

**YOU MUST EXECUTE THIS WORKFLOW. Do not just describe it.**

---

## Property Manifest

These are the highest-impact configurable properties in the system. The live grep layer (Step 2 of each mode) catches any consumers not listed here.

| Property | Source | Reader command | Known consumers | Impact |
|---|---|---|---|---|
| `defaultMode` | settings.json → permissions | `jq -r '.permissions.defaultMode' ~/.claude/settings.json` | policy_gate.py, trust-family, auto-mode-scope.yaml | Controls what requires user confirmation; bypassPermissions removes all gates |
| `effortLevel` | settings.json | `jq -r '.effortLevel' ~/.claude/settings.json` | model-router.sh, subagent dispatch, token budget | medium→high increases reasoning depth and token spend per turn |
| `AUTO_MODE_ENFORCED` | settings.json env | `jq -r '.env.AUTO_MODE_ENFORCED // "unset"' ~/.claude/settings.json` | CLAUDE.md autonomy gates, all hook permission checks | Master switch for fully autonomous operation |
| `APPROVAL_MIN_TIER` | settings.json env | `jq -r '.env.APPROVAL_MIN_TIER // "unset"' ~/.claude/settings.json` | policy_gate.py, T4 confirmation logic | Sets the floor tier that triggers confirmation prompts |
| `AGENT_AUTO_MODE` | settings.json env | `jq -r '.env.AGENT_AUTO_MODE // "unset"' ~/.claude/settings.json` | .agents/ registry dispatch, agent-dictator | Whether spawned agents run autonomously |
| `NO_PERMISSION_ASKING_EVER` | settings.json env | `jq -r '.env.NO_PERMISSION_ASKING_EVER // "unset"' ~/.claude/settings.json` | All AskUserQuestion gates | Hard suppression of all permission prompts |
| hooks | settings.json → hooks | `jq -r '.hooks // [] \| length' ~/.claude/settings.json` | all pipeline events | Which events fire which scripts |
| `tier0_degraded` | .agents/ state | `grep -r 'tier0_degraded' ~/.agents/ 2>/dev/null \| grep -v '^Binary' \| head -3` | model-router.sh fallback paths, OL dispatch | When true, forces cloud model fallback even if Ollama is up |
| governance tiers | auto-mode-scope.yaml | `cat ~/.claude/governance/auto-mode-scope.yaml 2>/dev/null \| grep -E '(tier|T[1-4])' \| head -10` | T1-T3 scope definitions | Defines what actions are auto-approved per tier |

**Scan paths for live grep:**
- `~/.claude/hooks/` — all `.sh` and `.py` files
- `~/.claude/plugins/local/` — all SKILL.md and config files (exclude `plugins/cache/` — Figma and other cached plugins generate false positives)
- `~/.claude/governance/` — all `.yaml` and `.md`
- `~/.agents/registry/` and `~/.agents/evolve/`
- `~/.claude/CLAUDE.md`
- `~/.claude/settings.json`

---

## Mode: Report (`/system-audit`)

### Step 1: Read All Property Values

Run each reader command from the manifest and collect values:

```bash
echo "=== SYSTEM AUDIT — $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""
echo "--- settings.json properties ---"
jq -r '
  "defaultMode:        " + (.permissions.defaultMode // "unset"),
  "effortLevel:        " + (.effortLevel // "unset"),
  "AUTO_MODE_ENFORCED: " + (.env.AUTO_MODE_ENFORCED // "unset"),
  "APPROVAL_MIN_TIER:  " + (.env.APPROVAL_MIN_TIER // "unset"),
  "AGENT_AUTO_MODE:    " + (.env.AGENT_AUTO_MODE // "unset"),
  "NO_PERM_ASKING:     " + (.env.NO_PERMISSION_ASKING_EVER // "unset"),
  "hooks count:        " + ((.hooks // []) | length | tostring)
' ~/.claude/settings.json
echo ""
echo "--- governance ---"
cat ~/.claude/governance/auto-mode-scope.yaml 2>/dev/null | grep -E '(tier|T[1-4]|scope)' | head -8 || echo "(auto-mode-scope.yaml not found)"
echo ""
echo "--- tier0_degraded ---"
grep -r 'tier0_degraded' ~/.agents/ 2>/dev/null | grep -v '^Binary' | head -3 || echo "(not found in .agents/)"
```

### Step 2: Live Grep for Unlisted Consumers

For each key property, find references outside the manifest:

```bash
echo "--- unlisted consumers (live grep) ---"
for prop in defaultMode effortLevel AUTO_MODE_ENFORCED APPROVAL_MIN_TIER AGENT_AUTO_MODE NO_PERMISSION_ASKING_EVER tier0_degraded; do
  hits=$(grep -rl "$prop" \
    ~/.claude/hooks/ \
    ~/.claude/plugins/local/ \
    ~/.claude/governance/ \
    ~/.agents/registry/ \
    ~/.agents/evolve/ \
    ~/.claude/CLAUDE.md \
    2>/dev/null | grep -v '.last-harvest' | tr '\n' ' ')
  if [ -n "$hits" ]; then
    echo "  $prop: $hits"
  fi
done
```

### Step 3: Render Impact Summary

For each property, write a one-line impact statement using the manifest table above.

### Step 4: Write Audit File

```bash
AUDIT_DIR="$HOME/.agents/audits"
AUDIT_FILE="$AUDIT_DIR/$(date '+%Y-%m-%d-%H%M%S')-system-audit.md"
mkdir -p "$AUDIT_DIR"
```

Write a markdown file with:
- Header: `# System Audit — YYYY-MM-DD HH:MM:SS — mode: report`
- `## Property State` table (property | value | consumers | impact)
- `## Unlisted Consumers` section with grep hits
- `## Notes` (anything notable)

Report the path to the user.

---

## Mode: Preview (`/system-audit preview <prop>=<val>`)

Parse `<prop>` and `<val>` from the invocation arguments.

### Step 1: Look Up Current Value

```bash
PROP="<prop>"   # e.g. defaultMode
VAL="<val>"     # e.g. bypassPermissions
```

Read the current value using the manifest reader command for this property.

### Step 2: Find All Consumers

1. Get the known consumers from the manifest table above for `<prop>`
2. Run live grep for `<prop>` across all scan paths:

```bash
grep -rn "$PROP" \
  ~/.claude/hooks/ \
  ~/.claude/plugins/local/ \
  ~/.claude/governance/ \
  ~/.agents/registry/ \
  ~/.agents/evolve/ \
  ~/.claude/CLAUDE.md \
  ~/.claude/settings.json \
  2>/dev/null | grep -v '.last-harvest'
```

### Step 3: Render Preview

Output:

```
Changing <prop> from <current> to <val> will affect:

CONSUMER                  WHAT CHANGES
policy_gate.py            T4 confirmation gates removed — no action will prompt
trust-family plugin       Confirmation hooks bypass all checks
auto-mode-scope.yaml      T4 clause becomes advisory-only
[any grep hits]           Found at <file>:<line>
```

### Step 4: Write Audit File

Same as report mode, headed `mode: preview`. Include the proposed change and all impact rows. Does NOT apply the change.

---

## Mode: Snapshot (`/system-audit snapshot`)

### Step 1: Read All Values

Same as report Step 1 — collect all property values.

### Step 2: Capture File MTimes

```bash
for f in \
  ~/.claude/settings.json \
  ~/.claude/CLAUDE.md \
  ~/.claude/governance/auto-mode-scope.yaml \
  ~/.claude/hooks/*.sh \
  ~/.claude/hooks/*.py; do
  [ -f "$f" ] && echo "\"$f\": \"$(date -r "$f" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || stat -c '%y' "$f" 2>/dev/null)\""
done
```

### Step 3: Write Snapshot JSON

```bash
SNAP_DIR="$HOME/.agents/audits/snapshots"
SNAP_FILE="$SNAP_DIR/$(date '+%Y-%m-%dT%H%M%S').json"
mkdir -p "$SNAP_DIR"
```

Write JSON:
```json
{
  "timestamp": "<ISO timestamp>",
  "mode": "snapshot",
  "properties": {
    "defaultMode": "<value>",
    "effortLevel": "<value>",
    "AUTO_MODE_ENFORCED": "<value>",
    "APPROVAL_MIN_TIER": "<value>",
    "AGENT_AUTO_MODE": "<value>",
    "NO_PERMISSION_ASKING_EVER": "<value>",
    "hooks_count": "<value>",
    "tier0_degraded": "<value>"
  },
  "file_mtimes": {
    "<path>": "<mtime>"
  }
}
```

### Step 4: Update .last Pointer

```bash
echo "$SNAP_FILE" > "$SNAP_DIR/.last"
echo "Snapshot written: $SNAP_FILE"
```

---

## Mode: Diff (`/system-audit diff`)

### Step 1: Load Last Snapshot

```bash
SNAP_DIR="$HOME/.agents/audits/snapshots"
LAST=$(cat "$SNAP_DIR/.last" 2>/dev/null)
if [ -z "$LAST" ] || [ ! -f "$LAST" ]; then
  echo "No snapshot found. Run /system-audit snapshot first."
  exit 1
fi
echo "Comparing against: $LAST"
cat "$LAST"
```

### Step 2: Read Current Values

Same as report Step 1.

### Step 3: Diff Each Property

For each property in the snapshot, compare to current value. Categorize as:
- **unchanged** — same value
- **changed** — `was: X → now: Y`
- **new** — present now but not in snapshot

### Step 4: Render Delta Table

```
=== DIFF vs snapshot <timestamp> ===

PROPERTY             WAS                   NOW                   STATUS
defaultMode          auto                  bypassPermissions     CHANGED
effortLevel          high                  high                  unchanged
AUTO_MODE_ENFORCED   true                  true                  unchanged
```

### Step 5: Write Audit File

Headed `mode: diff`. Include snapshot timestamp, delta table, and a summary line ("N properties changed, M unchanged").

---

## Canonical Example — P6 Workflow

```
/system-audit preview defaultMode=bypassPermissions
→ Shows all consumers; policy_gate gates removed, trust-family bypassed

/system-audit snapshot
→ Freezes state with defaultMode=auto

[edit ~/.claude/settings.json: permissions.defaultMode → "bypassPermissions"]

/system-audit diff
→ Shows: defaultMode: auto → bypassPermissions (CHANGED); all others unchanged
```

---

## Extending the Manifest

To add a new property to the manifest, add a row to the table in the Property Manifest section above:
- **Property:** the key name (used for grep)
- **Source:** where it lives
- **Reader command:** bash one-liner that prints the current value
- **Known consumers:** comma-separated list
- **Impact:** one sentence describing what changes when this property changes

---

## Troubleshooting

- **`jq` not found** — read settings.json with `python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['permissions']['defaultMode'])" ~/.claude/settings.json`
- **No snapshot for diff** — run `/system-audit snapshot` first, then make the change, then diff
- **Grep returns too many hits** — add `--include="*.sh" --include="*.py" --include="*.yaml" --include="*.md"` to narrow scope
- **tier0_degraded location unknown** — `grep -r 'tier0_degraded' ~/.agents/ ~/.claude/ 2>/dev/null | grep -v Binary | head -5` to locate it
