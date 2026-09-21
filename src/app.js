/* Agent Lab — original, dependency-free educational simulation.
 * No LLM requests, network calls, personal data, real publications or real credits.
 * All cases are synthetic. Persisted state contains only completed station IDs.
 */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const STORAGE = 'billel-agent-lab.v1';
  const PROJECTS = {
    doksima: { name: 'Doksima', index: '01', color: '#b7f4ca', tagline: 'Vérifier avant de conclure.', description: 'Comparez deux pièces fictives. Une incohérence n’est pas une preuve de fraude ; une pièce absente impose de s’abstenir.' },
    agentflow: { name: 'AgentFlow', index: '02', color: '#a0c5f7', tagline: 'Une panne n’efface pas le travail.', description: 'Lancez le workflow fictif, observez une panne puis reprenez au checkpoint. Le journal montre ce qui est exécuté.' },
    echotrust: { name: 'EchoTrust', index: '03', color: '#eec197', tagline: 'L’IA rédige. L’humain valide.', description: 'Bloquez une promesse non sourcée, générez un brouillon prudent, puis donnez votre validation humaine. Rien ne sera réellement publié.' },
    pixellight: { name: 'PixelLight', index: '04', color: '#c5b6f4', tagline: 'Le repli fait partie du système.', description: 'Le fournisseur A peut tomber en panne. Le routeur fictif ne bascule vers B que si le budget de la démo le permet.' }
  };
  const ids = Object.keys(PROJECTS);
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  /** @type {{selected:string, completed:Set<string>, epoch:number, paused:boolean}} */
  const state = { selected: 'doksima', completed: new Set(), epoch: 0, paused: motionPreference.matches };
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE) || '[]');
    if (Array.isArray(saved)) saved.forEach(id => { if (ids.includes(id)) state.completed.add(id); });
  } catch (_) { /* Private mode or invalid storage must never prevent playing. */ }
  const scene = $('#scene');
  const exercise = $('#exercise');
  const player = { x: 500, y: 310, target: null, walking: false };
  const held = new Set();
  let toastTimer;
  function toast(message) {
    const node = $('#toast'); node.textContent = message; node.classList.add('visible');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove('visible'), 3500);
  }
  function log(message, kind = '') {
    const line = document.createElement('li'); line.textContent = message; line.className = kind;
    const node = $('#trace'); node.append(line);
    while (node.childElementCount > 12) node.firstElementChild.remove();
    node.scrollTop = node.scrollHeight;
  }
  function refreshProgress() {
    $('#score').textContent = `${state.completed.size} / 4`;
    $$('.segments i').forEach((node, index) => node.classList.toggle('active', index < state.completed.size));
    $$('.station').forEach(node => {
      const id = node.dataset.station;
      node.classList.toggle('done', state.completed.has(id));
      node.setAttribute('aria-label', `${PROJECTS[id].name} : ${PROJECTS[id].tagline}${state.completed.has(id) ? ' Station validée.' : ''}`);
    });
    $('#mission-status').textContent = state.completed.has(state.selected) ? 'VALIDÉE ✓' : 'À EXPLORER';
    $('#success').hidden = state.completed.size !== 4;
    $('#progress-title').textContent = state.completed.size === 4 ? 'RELEASE VÉRIFIÉE · 4 PRINCIPES EXPLORÉS' : 'OBJECTIF : UNE RELEASE VÉRIFIÉE';
  }
  function complete(id) {
    const isNew = !state.completed.has(id);
    state.completed.add(id);
    try { localStorage.setItem(STORAGE, JSON.stringify([...state.completed])); } catch (_) { /* In-memory fallback. */ }
    refreshProgress();
    if (isNew) toast(state.completed.size === 4 ? '✓ Les quatre stations sont validées. Release sécurisée !' : `✓ ${PROJECTS[id].name} : station validée (${state.completed.size}/4)`);
  }
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const alive = epoch => epoch === state.epoch;
  function startRun() { return ++state.epoch; }
  function boundsFor(id) {
    const b = $(`[data-station="${id}"]`).getBoundingClientRect();
    const s = scene.getBoundingClientRect();
    return { x: (b.left - s.left) / s.width * 1000, y: (b.top - s.top) / s.height * 620, w: b.width / s.width * 1000, h: b.height / s.height * 620 };
  }
  function dockFor(id) {
    const b = boundsFor(id);
    return { x: b.x + b.w / 2, y: b.y < 310 ? b.y + b.h + 37 : b.y - 33 };
  }
  function goTo(id) {
    player.target = dockFor(id);
    if (state.paused) { player.x = player.target.x; player.y = player.target.y; player.target = null; }
  }
  function selectStation(id, move = true) {
    if (!Object.hasOwn(PROJECTS, id)) return;
    ++state.epoch; // Any asynchronous run for the previous station is now invalid.
    state.selected = id;
    const p = PROJECTS[id];
    $('#mission-index').textContent = `STATION ${p.index}`;
    $('#mission-name').textContent = p.name;
    $('#mission-tagline').textContent = p.tagline;
    $('#mission-description').textContent = p.description;
    $('.inspector').style.setProperty('--accent', p.color);
    $$('.station').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.station === id)));
    $('#trace').replaceChildren();
    if (move) goTo(id);
    ({ doksima: renderDoksima, agentflow: renderAgentFlow, echotrust: renderEchoTrust, pixellight: renderPixelLight })[id]();
    refreshProgress();
  }

  // 1. Evidence: compare integer cents, distinguish inconsistency from missing evidence.
  function renderDoksima() {
    const cases = {
      mismatch: { payroll: 240000, bank: 270000, answer: 'mismatch' },
      aligned: { payroll: 240000, bank: 240000, answer: 'aligned' },
      missing: { payroll: 240000, bank: null, answer: 'abstain' }
    };
    exercise.innerHTML = `<label class="field-label" for="doc-case">DOSSIER FICTIF</label>
      <select id="doc-case"><option value="mismatch">Cas A · montants différents</option><option value="aligned">Cas B · montants concordants</option><option value="missing">Cas C · pièce manquante</option></select>
      <div class="doc-values"><div><span>BULLETIN / LIGNE 12</span><strong id="payroll"></strong><small>Net payé · pièce fictive A</small></div><div><span>RELEVÉ / LIGNE 08</span><strong id="bank"></strong><small>Virement · pièce fictive B</small></div></div>
      <p class="exercise-note">Quel constat est justifié par ces pièces ?</p>
      <div class="button-row"><button class="choice" data-verdict="aligned">Concordance</button><button class="choice" data-verdict="mismatch">Incohérence</button><button class="choice" data-verdict="abstain">S’abstenir</button></div>`;
    const money = cents => cents === null ? 'Absente' : (cents / 100).toLocaleString('fr-FR') + ' €';
    function refreshCase() {
      const c = cases[$('#doc-case').value] || cases.mismatch;
      $('#payroll').textContent = money(c.payroll); $('#bank').textContent = money(c.bank);
      $$('.choice', exercise).forEach(button => button.setAttribute('aria-pressed', 'false'));
      $('#trace').replaceChildren(); log('Deux sources fictives. Un constat à justifier.');
    }
    $('#doc-case').addEventListener('change', refreshCase);
    $$('[data-verdict]', exercise).forEach(button => button.addEventListener('click', () => {
      const c = cases[$('#doc-case').value] || cases.mismatch;
      if (button.dataset.verdict !== c.answer) {
        log(c.bank === null ? 'Pièce absente : impossible de comparer. Abstention requise.' : 'Relisez les montants. Le constat doit découler des sources.', 'warn');
        return;
      }
      button.setAttribute('aria-pressed', 'true');
      if (c.answer === 'abstain') log('Preuve indisponible → abstention. Aucun verdict forcé.', 'ok');
      else if (c.answer === 'mismatch') {
        log(`Écart recalculé : ${money(Math.abs(c.payroll - c.bank))}. Sources : A/12 et B/08.`, 'ok');
        log('Incohérence relevée, pas de conclusion automatique de fraude.');
      } else log('Écart = 0 €. Montants concordants ; pas de garantie d’authenticité.', 'ok');
      complete('doksima');
    }));
    refreshCase();
  }

  // 2. Orchestration: a failed tool step is retried; completed plan is not repeated.
  function renderAgentFlow() {
    exercise.innerHTML = `<label class="checkbox-label"><input type="checkbox" id="worker-failure" checked> Injecter une panne de l’outil</label>
      <div class="pipeline" aria-label="Étapes du workflow"><span>Planifier</span><span>Outil</span><span>Vérifier</span><span>Terminer</span></div>
      <div class="button-row"><button class="action-btn" id="run-flow">Lancer le workflow</button><button class="action-btn secondary" id="resume-flow" hidden>Reprendre au checkpoint</button></div>
      <p class="exercise-note">Le checkpoint est en mémoire dans cette démo. Aucun worker distant n’est exécuté.</p>`;
    log('Workflow prêt. Plan → outil → vérification → fin.');
    let resumeAt = 0;
    const steps = () => $$('.pipeline span', exercise);
    async function run(resume = false) {
      const epoch = startRun();
      $('#run-flow').disabled = true; $('#resume-flow').hidden = true; $('#worker-failure').disabled = true;
      const fail = $('#worker-failure').checked && !resume;
      if (!resume) { steps().forEach(node => node.className = ''); resumeAt = 0; log('Exécution fictive démarrée.'); }
      else log('Reprise : plan conservé, seul l’outil est rejoué.', 'ok');
      for (let i = resumeAt; i < 4; i++) {
        if (!alive(epoch)) return;
        const node = steps()[i]; node.className = 'current';
        log(['Planification…', 'Appel d’outil fictif…', 'Contrôle du résultat…', 'Finalisation…'][i]);
        await sleep(450); if (!alive(epoch)) return;
        if (i === 1 && fail) {
          node.className = 'failed'; resumeAt = 1;
          log('TIMEOUT simulé. Checkpoint 1 conservé.', 'warn');
          $('#resume-flow').hidden = false;
          return;
        }
        node.className = 'finished'; resumeAt = i + 1;
      }
      log('Workflow terminé. Trace complète, résultat contrôlé.', 'ok');
      $('#run-flow').disabled = false; $('#worker-failure').disabled = false;
      $('#run-flow').textContent = 'Relancer le workflow';
      complete('agentflow');
    }
    $('#run-flow').addEventListener('click', () => { void run(false); });
    $('#resume-flow').addEventListener('click', () => { void run(true); });
  }

  // 3. Human review: publication is a local UI state, never a network operation.
  function renderEchoTrust() {
    exercise.innerHTML = `<div class="review">AVIS FICTIF<br>« Bon accueil, mais ma demande est restée sans réponse. »</div>
      <label class="checkbox-label"><input type="checkbox" id="unsafe-promise" checked> Ajouter une promesse non sourcée</label>
      <button class="action-btn" id="generate-draft">Générer un brouillon fictif</button>
      <div class="draft" id="draft" aria-live="polite">Le brouillon sera affiché ici.</div>
      <label class="checkbox-label"><input type="checkbox" id="human-review" disabled> J’ai relu et validé cette réponse</label>
      <button class="action-btn secondary" id="publish-draft" disabled>Simuler la publication</button>`;
    let safe = false;
    log('Une validation humaine sera obligatoire.');
    function invalidate() {
      safe = false; $('#human-review').checked = false; $('#human-review').disabled = true;
      $('#publish-draft').disabled = true; $('#draft').textContent = 'Paramètre modifié. Générez un nouveau brouillon.';
    }
    $('#unsafe-promise').addEventListener('change', invalidate);
    $('#generate-draft').addEventListener('click', () => {
      $('#human-review').checked = false; $('#publish-draft').disabled = true;
      if ($('#unsafe-promise').checked) {
        safe = false; $('#human-review').disabled = true;
        $('#draft').textContent = '« Nous garantissons un remboursement sous 24 h. »';
        log('BLOQUÉ : la promesse de remboursement n’a aucune source.', 'warn');
        log('Retirez la promesse, puis régénérez le brouillon.');
      } else {
        safe = true; $('#human-review').disabled = false;
        $('#draft').textContent = '« Merci pour votre retour. Contactez notre équipe pour que nous puissions examiner votre demande. »';
        log('Brouillon prudent. En attente de validation humaine.', 'ok');
      }
    });
    $('#human-review').addEventListener('change', () => {
      $('#publish-draft').disabled = !(safe && $('#human-review').checked);
    });
    $('#publish-draft').addEventListener('click', () => {
      if (!safe || !$('#human-review').checked || $('#unsafe-promise').checked) return;
      log('Validation humaine reçue. Publication SIMULÉE.', 'ok');
      log('Aucun avis publié, aucun service externe appelé.');
      $('#publish-draft').disabled = true;
      complete('echotrust');
    });
  }

  // 4. Resilience: invented provider costs, enforced budget, deterministic pixel art.
  function renderPixelLight() {
    exercise.innerHTML = `<label class="checkbox-label"><input type="checkbox" id="provider-failure" checked> Mettre le fournisseur A en panne</label>
      <div class="provider-row"><span id="provider-a">A · 1 crédit</span><span id="provider-b">B · 2 crédits</span></div>
      <label class="field-label" for="budget">BUDGET FICTIF MAXIMUM</label><div class="budget"><input id="budget" type="range" min="1" max="5" step="1" value="3"><output for="budget" id="budget-value">3 crédits</output></div>
      <button class="action-btn" id="run-router">Lancer le routage fictif</button><div class="pixel-output" id="pixel-output" role="img" aria-label="Mosaïque générée localement, sans IA"></div>
      <p class="exercise-note">Crédits inventés pour le jeu. Un appel en panne ne coûte rien dans ce scénario uniquement.</p>`;
    $('#budget').addEventListener('input', () => $('#budget-value').textContent = `${$('#budget').value} crédit${$('#budget').value === '1' ? '' : 's'}`);
    log('Routeur prêt. A prioritaire, B en repli.');
    $('#run-router').addEventListener('click', async () => {
      const epoch = startRun();
      const budget = Number($('#budget').value); const fail = $('#provider-failure').checked;
      $('#run-router').disabled = true; $('#budget').disabled = true; $('#provider-failure').disabled = true;
      $('#provider-a').className = ''; $('#provider-b').className = '';
      $('#pixel-output').style.display = 'none';
      log(`Budget de la démo : ${budget} crédit(s). Appel de A…`);
      await sleep(500); if (!alive(epoch)) return;
      let provider = 'A', cost = 1;
      if (fail) {
        $('#provider-a').className = 'failed';
        log('A indisponible (panne simulée). Examen du repli B.', 'warn');
        if (budget < 2) {
          log('B trop coûteux → arrêt sûr. 0 crédit consommé.', 'ok');
          $('#run-router').disabled = false; $('#budget').disabled = false; $('#provider-failure').disabled = false;
          complete('pixellight'); return;
        }
        provider = 'B'; cost = 2;
        await sleep(500); if (!alive(epoch)) return;
      }
      $(`#provider-${provider.toLowerCase()}`).className = 'finished';
      const palette = ['#283729', '#3f6550', '#658f6c', '#b7f4ca', '#eec197', '#c5b6f4', '#57536a'];
      const output = $('#pixel-output'); output.replaceChildren();
      for (let y = 0; y < 5; y++) for (let x = 0; x < 16; x++) {
        const pixel = document.createElement('i');
        pixel.style.background = palette[(Math.floor(x / 2) + y * 2 + (x % 3)) % palette.length];
        output.append(pixel);
      }
      output.style.display = 'grid';
      log(`${provider} sélectionné. Coût fictif ${cost}/${budget}. Budget respecté.`, 'ok');
      log('Mosaïque locale dessinée par le code, sans IA.');
      $('#run-router').disabled = false; $('#budget').disabled = false; $('#provider-failure').disabled = false;
      complete('pixellight');
    });
  }

  $$('.station').forEach(button => button.addEventListener('click', () => {
    selectStation(button.dataset.station);
    if (window.innerWidth <= 880) $('.inspector').scrollIntoView({ behavior: motionPreference.matches ? 'instant' : 'smooth', block: 'start' });
    else scene.focus({ preventScroll: true });
  }));
  $('#enter-lab').addEventListener('click', () => scene.focus({ preventScroll: true }));
  function setPaused(paused) {
    state.paused = paused; document.documentElement.classList.toggle('paused', paused);
    const node = $('#motion'); node.setAttribute('aria-pressed', String(paused));
    node.setAttribute('aria-label', paused ? 'Reprendre les animations' : 'Mettre les animations en pause');
    node.innerHTML = paused ? '▷ <span>Animer</span>' : 'Ⅱ <span>Pause</span>';
  }
  $('#motion').addEventListener('click', () => setPaused(!state.paused));
  motionPreference.addEventListener('change', event => setPaused(event.matches));
  $('#reset').addEventListener('click', () => {
    if (!window.confirm('Effacer uniquement la progression de ce mini-jeu dans ce navigateur ?')) return;
    state.completed.clear();
    try { localStorage.removeItem(STORAGE); } catch (_) { /* Nothing to remove. */ }
    held.clear(); player.x = 500; player.y = 310; player.target = null;
    selectStation('doksima', false); toast('Progression remise à zéro. Le labo est prêt.');
  });
  function interact() {
    let near = null, distance = Infinity;
    ids.forEach(id => { const p = dockFor(id), d = Math.hypot(p.x - player.x, p.y - player.y); if (d < distance) { near = id; distance = d; } });
    if (near && distance < 160) {
      selectStation(near, false);
      if (window.innerWidth <= 880) $('.inspector').scrollIntoView({ behavior: motionPreference.matches ? 'instant' : 'smooth', block: 'start' });
    } else toast('Approchez-vous d’une station, ou cliquez directement dessus.');
  }
  const keyDirection = { ArrowUp: [0, -1], w: [0, -1], z: [0, -1], ArrowDown: [0, 1], s: [0, 1], ArrowLeft: [-1, 0], a: [-1, 0], q: [-1, 0], ArrowRight: [1, 0], d: [1, 0] };
  const normalizeKey = key => key.length === 1 ? key.toLowerCase() : key;
  document.addEventListener('keydown', event => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    if (document.activeElement !== scene) return;
    const key = normalizeKey(event.key);
    if (Object.hasOwn(keyDirection, key)) { event.preventDefault(); held.add(key); player.target = null; }
    if (key === 'e' && !event.repeat) { event.preventDefault(); interact(); }
  });
  document.addEventListener('keyup', event => held.delete(normalizeKey(event.key)));
  window.addEventListener('blur', () => held.clear());
  document.addEventListener('visibilitychange', () => held.clear());
  scene.addEventListener('blur', () => held.clear());
  $$('[data-dir]').forEach(button => {
    button.addEventListener('pointerdown', event => { event.preventDefault(); button.setPointerCapture(event.pointerId); held.add(button.dataset.dir); player.target = null; });
    const clear = () => held.delete(button.dataset.dir);
    button.addEventListener('pointerup', clear); button.addEventListener('pointercancel', clear); button.addEventListener('lostpointercapture', clear);
  });
  $('#interact').addEventListener('click', interact);

  // Canvas is decorative; native buttons and textual descriptions remain usable without it.
  const canvas = $('#world'); const ctx = canvas.getContext('2d');
  let hitBoxes = [];
  function resize() {
    const rect = scene.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(rect.width * ratio); canvas.height = Math.round(rect.height * ratio);
    hitBoxes = ids.map(boundsFor);
  }
  const resizeObserver = new ResizeObserver(resize); resizeObserver.observe(scene);
  const walkable = (x, y) => x > 28 && x < 972 && y > 42 && y < 600 && !hitBoxes.some(b => x > b.x - 12 && x < b.x + b.w + 12 && y > b.y - 8 && y < b.y + b.h + 14);
  scene.addEventListener('pointerdown', event => {
    if (event.target !== canvas && event.target !== scene) return;
    const r = scene.getBoundingClientRect(), x = (event.clientX - r.left) / r.width * 1000, y = (event.clientY - r.top) / r.height * 620;
    if (walkable(x, y)) { player.target = { x, y }; if (state.paused) { player.x = x; player.y = y; player.target = null; } }
    scene.focus({ preventScroll: true });
  });
  function rounded(x, y, w, h, radius = 5) { ctx.beginPath(); ctx.roundRect(x, y, w, h, radius); }
  function line(points, color, width = 1) {
    ctx.beginPath(); points.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke();
  }
  function robot(x, y, color, label, frame, scale = 1) {
    ctx.save(); ctx.translate(Math.round(x), Math.round(y)); ctx.scale(scale, scale);
    ctx.fillStyle = '#0005'; ctx.beginPath(); ctx.ellipse(0, 17, 19, 6, 0, 0, Math.PI * 2); ctx.fill();
    const step = frame ? Math.sin(frame * 9) * 3 : 0;
    ctx.fillStyle = '#6d8183'; ctx.fillRect(-9, 7 + step, 6, 9); ctx.fillRect(3, 7 - step, 6, 9);
    ctx.fillStyle = '#253c35'; ctx.fillRect(-13, -6, 26, 19);
    ctx.fillStyle = color; ctx.fillRect(-10, -7, 20, 16); ctx.fillRect(-13, -26, 26, 20);
    ctx.fillStyle = '#18252b'; ctx.fillRect(-9, -22, 18, 10); ctx.fillRect(-14, -3, 4, 11); ctx.fillRect(10, -3, 4, 11);
    ctx.fillStyle = color; ctx.fillRect(-6, -19, 4, 4); ctx.fillRect(3, -19, 4, 4); ctx.fillRect(-1, -32, 2, 7); ctx.fillRect(-3, -34, 6, 4);
    ctx.fillStyle = '#e9efe144'; ctx.fillRect(-7, -4, 5, 3);
    ctx.font = '11px ui-monospace,monospace'; ctx.textAlign = 'center';
    const w = ctx.measureText(label).width + 16;
    ctx.fillStyle = '#0a141be8'; rounded(-w / 2, 25, w, 19, 4); ctx.fill(); ctx.strokeStyle = color + '55'; ctx.lineWidth = .8; ctx.stroke();
    ctx.fillStyle = color; ctx.fillText(label, 0, 38); ctx.restore();
  }
  function update(dt) {
    let dx = 0, dy = 0;
    held.forEach(key => { const d = keyDirection[key]; if (d) { dx += d[0]; dy += d[1]; } });
    player.walking = false;
    if (dx || dy) {
      const norm = Math.hypot(dx, dy); dx = dx / norm * 205 * dt; dy = dy / norm * 205 * dt;
      if (walkable(player.x + dx, player.y)) player.x += dx;
      if (walkable(player.x, player.y + dy)) player.y += dy;
      player.walking = true;
    } else if (player.target) {
      dx = player.target.x - player.x; dy = player.target.y - player.y; const d = Math.hypot(dx, dy);
      if (d < 5 || state.paused) { player.x = player.target.x; player.y = player.target.y; player.target = null; }
      else { const step = Math.min(d, 235 * dt); player.x += dx / d * step; player.y += dy / d * step; player.walking = true; }
    }
  }
  function draw(t) {
    if (!ctx) return;
    ctx.setTransform(canvas.width / 1000, 0, 0, canvas.height / 620, 0, 0); ctx.clearRect(0, 0, 1000, 620);
    // Quiet blueprint grid and an isometric floor; original programmatic artwork.
    ctx.fillStyle = '#304a4a';
    for (let x = 25; x < 1000; x += 25) for (let y = 45; y < 620; y += 25) ctx.fillRect(x, y, 1, 1);
    ctx.save(); ctx.beginPath(); ctx.moveTo(500, 110); ctx.lineTo(930, 340); ctx.lineTo(500, 580); ctx.lineTo(70, 340); ctx.closePath(); ctx.clip();
    for (let i = -650; i < 1500; i += 70) { line([[i, 80], [i + 1050, 660]], '#3e585832'); line([[i, 80], [i - 1050, 660]], '#3e585832'); }
    ctx.restore();
    const hub = { x: 500, y: 323 };
    const docks = ids.map(dockFor);
    docks.forEach((p, i) => {
      ctx.setLineDash([5, 8]); ctx.lineDashOffset = -t * 11;
      line([[hub.x, hub.y], [p.x, hub.y], [p.x, p.y]], state.completed.has(ids[i]) ? '#9bc3a666' : '#71918645', 1.3); ctx.setLineDash([]);
      ctx.strokeStyle = PROJECTS[ids[i]].color + '77'; ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(p.x, p.y + 8, 23, 8, 0, 0, Math.PI * 2); ctx.stroke();
      const f = (t * .17 + i * .22) % 1, tx = hub.x + (p.x - hub.x) * f;
      ctx.fillStyle = PROJECTS[ids[i]].color; ctx.fillRect(tx - 2, hub.y - 2, 4, 4);
    });
    ctx.strokeStyle = '#597363'; ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(hub.x, hub.y + 7, 76, 26, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = '#92ba9b33'; ctx.beginPath(); ctx.ellipse(hub.x, hub.y + 7, 91, 33, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = '#92bca1'; ctx.font = '11px ui-monospace,monospace'; ctx.textAlign = 'center'; ctx.fillText('RELEASE GATE', 500, 406);
    ctx.fillStyle = '#7e9e8d'; ctx.font = '9px ui-monospace,monospace'; ctx.fillText(`${state.completed.size} / 4 contrôles validés`, 500, 423);
    const botDefs = [ { color: '#a0c5f7', label: 'PLAN', offset: 0, dock: 1 }, { color: '#eec197', label: 'BUILD', offset: 1.7, dock: 2 }, { color: '#c5b6f4', label: 'CHECK', offset: 3.1, dock: 3 } ];
    const sprites = botDefs.map((bot, i) => {
      const p = docks[bot.dock], k = .5 + Math.sin(t * .42 + bot.offset) * .38;
      return { x: 500 + (p.x - 500) * k, y: 293 + (i - 1) * 21 + Math.sin(t * .8 + i) * 9, color: bot.color, label: bot.label, frame: t, scale: .82 };
    });
    sprites.push({ x: player.x, y: player.y, color: '#b7f4ca', label: 'VOUS', frame: player.walking ? t : 0, scale: 1.05 });
    sprites.sort((a, b) => a.y - b.y).forEach(sprite => robot(sprite.x, sprite.y, sprite.color, sprite.label, sprite.frame, sprite.scale));
  }
  let previous = performance.now(), lastDraw = 0, animationTime = 0, lastCoord = 0;
  function frame(now) {
    const dt = Math.min((now - previous) / 1000, .05); previous = now;
    if (!document.hidden) {
      update(dt);
      if (!state.paused) animationTime += dt;
      if (now - lastDraw > 1000 / 30) { draw(animationTime); lastDraw = now; }
      if (now - lastCoord > 180) { $('#coord-x').textContent = Math.round(player.x); $('#coord-y').textContent = Math.round(player.y); lastCoord = now; }
    }
    requestAnimationFrame(frame);
  }
  setPaused(state.paused); selectStation('doksima', false); resize(); draw(0); requestAnimationFrame(frame);
})();
