# Visual Companion Guide (Visual Design Studio)

Browser-based companion for live front-end design: layout A/B, real component
previews, and interactive design-token tuning. Adapted from superpowers/brainstorming.

## How It Works

A zero-dependency Node HTTP+WebSocket server watches a `content/` directory and
serves the **newest** `.html` file to the browser. You write HTML with the Write
tool; the server pushes a reload over WebSocket; the user interacts; their actions
land in `state/` for you to read next turn.

Two kinds of user feedback come back:

- **Clicks** on `[data-choice]` elements → appended to `state/events` (JSONL)
- **Design-token changes** on `[data-token]` inputs (color/range/select) → appended to
  `state/events` AND folded into a keyed snapshot at `state/tokens.json`

**Content fragments vs full documents:** if your file starts with `<!DOCTYPE`/`<html`,
it's served as-is. Otherwise the server wraps it in the studio frame (header, theme,
indicator bar, all the CSS classes below) and injects the helper script. **Write
fragments by default.** Tailwind utilities are available in the frame (preflight
disabled, so they won't reset the frame styling).

## Starting the Server

```bash
scripts/start-server.sh --project-dir /path/to/project
# Returns: {"type":"server-started","port":52341,"url":"http://localhost:52341",
#           "screen_dir":".../.frontend/visual-design/<id>/content",
#           "state_dir":".../.frontend/visual-design/<id>/state"}
```

Save `screen_dir` and `state_dir`. Tell the user to open the URL.

**Windows (this machine):** the script auto-detects Git Bash and runs foreground.
**Call it with `run_in_background: true` on the Bash tool** so the server survives
across turns, then read `$STATE_DIR/server-info` next turn for the URL/port.

Without `--project-dir`, files go to `/tmp` and are cleaned on stop. With it, screens
and `tokens.json` persist under `.frontend/visual-design/`. Remind the user to add
`.frontend/` to `.gitignore`.

If the URL is unreachable (remote/containerized), bind non-loopback:
```bash
scripts/start-server.sh --project-dir /path --host 0.0.0.0 --url-host localhost
```

## The Loop

1. **Check the server is alive** (`$STATE_DIR/server-info` exists; no `server-stopped`),
   then **Write** a new HTML file to `screen_dir`:
   - Semantic, never-reused filenames: `layout.html`, `card-preview.html`, `tokens.html`, `layout-v2.html`
   - Use the Write tool — never cat/heredoc (dumps noise into the terminal)
   - The server serves the newest file automatically
2. **End your turn** with: a URL reminder, a one-line summary of what's on screen, and a
   prompt to respond in the terminal ("click an option / drag the controls, then tell me").
3. **Next turn:** read `$STATE_DIR/events` (clicks + token edits) and, for token screens,
   `$STATE_DIR/tokens.json` (final chosen values). Merge with the user's terminal text.
4. **Iterate or advance** — new screen for changes (`layout-v2.html`); only move on when the
   current decision is settled.
5. **Unload when returning to terminal** — push a `waiting.html` so the user isn't staring at
   a resolved screen.

## Screen Recipes

### Layout / wireframe A-B (clicks)
```html
<h2>Which dashboard layout fits?</h2>
<p class="subtitle">Consider scanning order and density</p>
<div class="cards">
  <div class="card" data-choice="sidebar" onclick="toggleSelect(this)">
    <div class="card-image"><div class="mock-nav">Logo</div></div>
    <div class="card-body"><h3>Sidebar + grid</h3><p>Persistent nav, dense cards</p></div>
  </div>
  <div class="card" data-choice="topbar" onclick="toggleSelect(this)">
    <div class="card-image"><div class="mock-nav">Logo | Home | Reports</div></div>
    <div class="card-body"><h3>Top bar + feed</h3><p>Linear, content-first</p></div>
  </div>
</div>
```
Add `data-multiselect` to `.cards`/`.options` to allow multiple picks.

### Live component preview
Render the real thing on a neutral stage. Tailwind classes work here.
```html
<h2>Primary button — does this feel right?</h2>
<div class="preview-stage">
  <button class="px-4 py-2 rounded-lg font-semibold text-white" style="background: var(--accent)">
    Get started
  </button>
  <button class="px-4 py-2 rounded-lg font-semibold border" style="border-color: var(--accent); color: var(--accent)">
    Learn more
  </button>
</div>
```
Use `<div data-frame="component">…</div>` as the outer element when you want a clean,
chrome-free render the content fully controls.

### Design-token tuning (values stream back)
Each `[data-token="<name>"]` input emits `{type:"token", name, value}`. The helper also
live-applies the value to CSS var `--<name>` (override with `data-token-css`) and mirrors
it into any `[data-token-output="<name>"]`. Read final values from `state/tokens.json`.
```html
<h2>Tune the core tokens</h2>
<p class="subtitle">Drag — the preview updates live. Final values are saved for me.</p>

<div class="tokens">
  <div class="token-row">
    <label>Accent <span class="token-value" data-token-output="accent">#6d4aff</span></label>
    <input type="color" data-token="accent" value="#6d4aff">
  </div>
  <div class="token-row">
    <label>Radius <span class="token-value" data-token-output="radius">12px</span></label>
    <input type="range" min="0" max="28" value="12" data-token="radius" data-token-css="--radius">
  </div>
  <div class="token-row">
    <label>Base font</label>
    <select data-token="font">
      <option>system-ui</option><option>Inter</option><option>Georgia</option>
    </select>
  </div>
</div>

<div class="preview-stage">
  <div style="background:var(--bg-secondary);border:1px solid var(--border);
              border-radius:var(--radius,12px);padding:1.25rem 1.5rem;font-family:var(--font,system-ui)">
    <h3 style="color:var(--accent)">Live card</h3>
    <p class="subtitle" style="margin:0">Reflects your token choices in real time.</p>
  </div>
</div>
```

## CSS Classes Provided by the Frame

- **Choices:** `.options` / `.option` (with `.letter`,`.content`); `.cards` / `.card` (with `.card-image`,`.card-body`) — both selectable via `onclick="toggleSelect(this)"`, `data-multiselect` for multi
- **Mockups:** `.mockup`/`.mockup-header`/`.mockup-body`, `.split`, `.placeholder`
- **Wireframe bits:** `.mock-nav`, `.mock-sidebar`, `.mock-content`, `.mock-button`, `.mock-input`
- **Preview:** `.preview-stage` (`data-bg="muted"`, `data-align="start"`)
- **Tokens:** `.tokens`, `.token-row`, `.token-value`, `.swatch`
- **Type/sections:** `h2`,`h3`,`.subtitle`,`.section`,`.label`
- **Theme vars:** `--bg-primary/secondary/tertiary`, `--border`, `--text-primary/secondary/tertiary`, `--accent`, `--success/warning/error`

## State Files (read these next turn)

```
state/server-info      # connection JSON; absence => server down, restart
state/server-stopped   # written on shutdown (reason)
state/events           # JSONL of clicks + token edits for the CURRENT screen (cleared on new screen)
state/tokens.json      # keyed final token values, e.g. {"accent":"#3344ff","radius":"16"}
```

Event examples:
```jsonl
{"type":"click","choice":"sidebar","text":"Sidebar + grid","timestamp":1706000101}
{"type":"token","name":"accent","value":"#3344ff","timestamp":1706000120}
```

If `state/events` is absent the user didn't touch the browser — use terminal text only.

## Cleaning Up

```bash
scripts/stop-server.sh $SESSION_DIR
```
`/tmp` sessions are deleted; `--project-dir` sessions keep their screens and `tokens.json`.

## Reference
- Frame/CSS: `scripts/frame-template.html`
- Client helper: `scripts/helper.js`
- Server: `scripts/server.cjs`
