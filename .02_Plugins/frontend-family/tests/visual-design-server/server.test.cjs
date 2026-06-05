/**
 * Integration tests for the visual-design companion server.
 *
 * Zero-dependency: uses node:test + a hand-rolled masked WebSocket client
 * (RFC 6455) instead of the `ws` package, matching the server's own
 * no-dependency design. Run with: node --test
 *
 * Covers: RFC accept-key, HTTP fragment wrapping + helper injection,
 * design-token round-trip -> tokens.json, click events, and the
 * events-cleared-on-new-screen behaviour.
 */

const { test, before, after } = require('node:test');
const assert = require('node:assert');
const { spawn } = require('node:child_process');
const net = require('node:net');
const http = require('node:http');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const SERVER_PATH = path.join(__dirname, '../../skills/visual-design/scripts/server.cjs');
const PORT = 53710;
const DIR = path.join(require('node:os').tmpdir(), 'vd-server-test-' + process.pid);
const CONTENT_DIR = path.join(DIR, 'content');
const STATE_DIR = path.join(DIR, 'state');

const { computeAcceptKey } = require(SERVER_PATH);

let srv;
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function httpGet(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => resolve({ status: res.statusCode, body }));
    }).on('error', reject);
  });
}

// Minimal masked client text frame (client->server frames MUST be masked).
function maskFrame(text) {
  const p = Buffer.from(text);
  assert.ok(p.length < 126, 'test frames stay under 126 bytes');
  const mask = crypto.randomBytes(4);
  const masked = Buffer.alloc(p.length);
  for (let i = 0; i < p.length; i++) masked[i] = p[i] ^ mask[i % 4];
  return Buffer.concat([Buffer.from([0x81, 0x80 | p.length]), mask, masked]);
}

// Open a WS connection, run fn(socket), then close.
function withWs(fn) {
  return new Promise((resolve, reject) => {
    const key = crypto.randomBytes(16).toString('base64');
    const sock = net.connect(PORT, '127.0.0.1', () => {
      sock.write(
        'GET / HTTP/1.1\r\nHost: x\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n' +
        'Sec-WebSocket-Key: ' + key + '\r\nSec-WebSocket-Version: 13\r\n\r\n'
      );
    });
    let handshook = false;
    sock.on('data', async (d) => {
      if (!handshook && d.toString().includes('101 Switching Protocols')) {
        handshook = true;
        try { await fn(sock); resolve(); }
        catch (e) { reject(e); }
        finally { sock.destroy(); }
      }
    });
    sock.on('error', reject);
  });
}

before(async () => {
  fs.mkdirSync(CONTENT_DIR, { recursive: true });
  srv = spawn('node', [SERVER_PATH], {
    env: { ...process.env, VISUAL_DESIGN_DIR: DIR, VISUAL_DESIGN_PORT: String(PORT), VISUAL_DESIGN_HOST: '127.0.0.1' }
  });
  await sleep(900);
});

after(() => {
  if (srv) srv.kill();
  fs.rmSync(DIR, { recursive: true, force: true });
});

test('computeAcceptKey matches RFC 6455 vector', () => {
  assert.strictEqual(
    computeAcceptKey('dGhlIHNhbXBsZSBub25jZQ=='),
    's3pPLMBiTxaQ9kYGzzhZRbK+xOo='
  );
});

test('serves a content fragment wrapped in the studio frame with helper injected', async () => {
  fs.writeFileSync(path.join(CONTENT_DIR, 'frag.html'),
    '<h2>Hi</h2><input type="color" data-token="accent" value="#112233">');
  await sleep(300);
  const res = await httpGet(`http://127.0.0.1:${PORT}/`);
  assert.strictEqual(res.status, 200);
  assert.match(res.body, /Visual Design Studio/);      // frame applied
  assert.match(res.body, /data-token="accent"/);        // our fragment present
  assert.match(res.body, /window\.visualDesign/);       // helper injected
});

test('design-token edits persist to tokens.json and events', async () => {
  await withWs(async (sock) => {
    sock.write(maskFrame(JSON.stringify({ type: 'token', name: 'accent', value: '#ff0066' })));
    sock.write(maskFrame(JSON.stringify({ type: 'token', name: 'radius', value: '18' })));
    await sleep(300);
  });
  const tokens = JSON.parse(fs.readFileSync(path.join(STATE_DIR, 'tokens.json'), 'utf8'));
  assert.strictEqual(tokens.accent, '#ff0066');
  assert.strictEqual(tokens.radius, '18');
  const events = fs.readFileSync(path.join(STATE_DIR, 'events'), 'utf8').trim().split('\n');
  assert.strictEqual(events.length, 2);
});

test('click events are appended to events log', async () => {
  await withWs(async (sock) => {
    sock.write(maskFrame(JSON.stringify({ type: 'click', choice: 'sidebar', text: 'Sidebar' })));
    await sleep(250);
  });
  const lines = fs.readFileSync(path.join(STATE_DIR, 'events'), 'utf8').trim().split('\n');
  const last = JSON.parse(lines[lines.length - 1]);
  assert.strictEqual(last.choice, 'sidebar');
});

test('pushing a new screen clears the events log', async () => {
  fs.writeFileSync(path.join(CONTENT_DIR, 'next.html'), '<h2>Next</h2>');
  await sleep(300);
  assert.strictEqual(fs.existsSync(path.join(STATE_DIR, 'events')), false);
});
