(function() {
  const WS_URL = 'ws://' + window.location.host;
  let ws = null;
  let eventQueue = [];

  function connect() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      eventQueue.forEach(e => ws.send(JSON.stringify(e)));
      eventQueue = [];
    };

    ws.onmessage = (msg) => {
      const data = JSON.parse(msg.data);
      if (data.type === 'reload') {
        window.location.reload();
      }
    };

    ws.onclose = () => {
      setTimeout(connect, 1000);
    };
  }

  function sendEvent(event) {
    event.timestamp = Date.now();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(event));
    } else {
      eventQueue.push(event);
    }
  }

  // Capture clicks on choice elements
  document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-choice]');
    if (!target) return;

    sendEvent({
      type: 'click',
      text: target.textContent.trim(),
      choice: target.dataset.choice,
      id: target.id || null
    });

    // Update indicator bar (defer so toggleSelect runs first)
    setTimeout(() => {
      const indicator = document.getElementById('indicator-text');
      if (!indicator) return;
      const container = target.closest('.options') || target.closest('.cards');
      const selected = container ? container.querySelectorAll('.selected') : [];
      if (selected.length === 0) {
        indicator.textContent = 'Click an option above, then return to the terminal';
      } else if (selected.length === 1) {
        const label = selected[0].querySelector('h3, .content h3, .card-body h3')?.textContent?.trim() || selected[0].dataset.choice;
        indicator.innerHTML = '<span class="selected-text">' + label + ' selected</span> — return to terminal to continue';
      } else {
        indicator.innerHTML = '<span class="selected-text">' + selected.length + ' selected</span> — return to terminal to continue';
      }
    }, 0);
  });

  // ===== Design-token capture =====
  // Any [data-token="<name>"] input (color picker, range slider, select,
  // text field) streams its value back as a {type:"token"} event. The
  // server folds these into state/tokens.json keyed by name so the agent
  // reads the final chosen values without replaying the event stream.
  const tokenTimers = {};

  function emitToken(el) {
    const name = el.dataset.token;
    if (!name) return;
    sendEvent({ type: 'token', name: name, value: el.value });

    // Live-apply to a CSS custom property if the page opted in via
    // data-token-css (defaults to --<name>) and reflect any paired output.
    const cssVar = el.dataset.tokenCss || ('--' + name);
    document.documentElement.style.setProperty(cssVar, el.value);
    const out = document.querySelector('[data-token-output="' + name + '"]');
    if (out) out.textContent = el.value;

    // Update indicator
    const indicator = document.getElementById('indicator-text');
    if (indicator) {
      indicator.innerHTML = '<span class="selected-text">' + name + ' = ' + el.value + '</span> — adjust freely, then return to terminal';
    }
  }

  document.addEventListener('input', (e) => {
    const el = e.target.closest('[data-token]');
    if (!el) return;
    // Debounce continuous inputs (range/color drag) to ~120ms.
    const name = el.dataset.token;
    if (tokenTimers[name]) clearTimeout(tokenTimers[name]);
    tokenTimers[name] = setTimeout(() => emitToken(el), 120);
  });
  // change fires for selects and on commit — emit immediately.
  document.addEventListener('change', (e) => {
    const el = e.target.closest('[data-token]');
    if (!el) return;
    if (tokenTimers[el.dataset.token]) clearTimeout(tokenTimers[el.dataset.token]);
    emitToken(el);
  });

  // Frame UI: selection tracking
  window.selectedChoice = null;
  window.selectedChoices = [];

  window.toggleSelect = function(el) {
    const container = el.closest('.options') || el.closest('.cards');
    const multi = container && container.dataset.multiselect !== undefined;
    if (container && !multi) {
      container.querySelectorAll('.option, .card').forEach(o => o.classList.remove('selected'));
    }
    if (multi) {
      el.classList.toggle('selected');
    } else {
      el.classList.add('selected');
    }
    window.selectedChoice = el.dataset.choice;
    if (container) {
      window.selectedChoices = Array.from(container.querySelectorAll('.option.selected, .card.selected'))
        .map(o => o.dataset.choice);
    }
  };

  // Expose API for explicit use
  window.visualDesign = {
    send: sendEvent,
    choice: (value, metadata = {}) => sendEvent({ type: 'choice', value, ...metadata }),
    token: (name, value) => sendEvent({ type: 'token', name, value })
  };

  connect();
})();
