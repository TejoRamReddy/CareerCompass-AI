/* ==========================================================================
   The interview.

   Every question comes from the backend, one at a time, written in response
   to the previous answer. There is no fixed question list in this file and
   no option-to-score lookup table: the profile is built server-side from the
   conversation itself.
   ========================================================================== */

const el = (id) => document.getElementById(id);

const startCard = el('startCard');
const interviewCard = el('interviewCard');
const academicsCard = el('academicsCard');
const resultsWrap = el('resultsWrap');
const transcriptEl = el('transcript');
const answerInput = el('answerInput');
const sendBtn = el('sendBtn');
const progressLabel = el('progressLabel');
const errorEl = el('interviewError');
const badge = el('modeBadge');
const explainer = el('modeExplainer');
const engineNote = el('engineNote');

const MARK_FIELDS = [
  { key: 'math', en: 'Mathematics', ta: 'கணிதம்' },
  { key: 'science', en: 'Science', ta: 'அறிவியல்' },
  { key: 'language', en: 'English / Language', ta: 'ஆங்கிலம் / மொழி' },
  { key: 'social', en: 'Social science', ta: 'சமூக அறிவியல்' },
  { key: 'computer', en: 'Computer science', ta: 'கணினி அறிவியல்' },
];

const state = {
  sessionId: null, engine: null, turn: 0, maxTurns: 7, busy: false, online: false,
  confidenceBefore: null,
  feedback: { rating: null, confidenceAfter: null, wouldAct: null },
};

// -------------------------------------------------------- 1-5 / yes-no pickers --

function buildScale(containerId, options, onPick, initial = null) {
  const container = el(containerId);
  container.innerHTML = '';
  let current = initial;
  options.forEach((opt) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    const isOn = current !== null && String(current) === String(opt.value);
    btn.className = 'scale-btn' + (isOn ? ' selected' : '');
    btn.setAttribute('role', 'radio');
    btn.setAttribute('aria-checked', isOn ? 'true' : 'false');
    btn.dataset.value = opt.value;
    btn.textContent = opt.label;
    btn.addEventListener('click', () => {
      // Clicking the selected one again clears it, so every scale stays optional.
      current = current === opt.value ? null : opt.value;
      container.querySelectorAll('.scale-btn').forEach((b) => {
        const on = b.dataset.value === String(current);
        b.classList.toggle('selected', on);
        b.setAttribute('aria-checked', on ? 'true' : 'false');
      });
      onPick(current);
    });
    container.appendChild(btn);
  });
}

const oneToFive = [1, 2, 3, 4, 5].map((n) => ({ value: n, label: String(n) }));

function buildAllScales() {
  // Every scale redraws from state, so a language switch never loses a selection.
  buildScale('confidenceBefore', oneToFive,
    (v) => { state.confidenceBefore = v; }, state.confidenceBefore);
  buildScale('ratingScale', oneToFive,
    (v) => { state.feedback.rating = v; }, state.feedback.rating);
  buildScale('confidenceAfterScale', oneToFive,
    (v) => { state.feedback.confidenceAfter = v; }, state.feedback.confidenceAfter);
  buildScale('wouldActScale', [
    { value: 'yes', label: CC.t('feedback.yes') },
    { value: 'maybe', label: CC.t('feedback.maybe') },
    { value: 'no', label: CC.t('feedback.no') },
  ], (v) => { state.feedback.wouldAct = v; }, state.feedback.wouldAct);
}

// --------------------------------------------------------------- transcript --

function bubble(who, text) {
  const div = document.createElement('div');
  div.className = 'bubble' + (who === 'ai' ? ' ai' : '');
  div.innerHTML = '<span class="who"></span><p></p>';
  div.querySelector('.who').textContent = CC.t(who === 'ai' ? 'demo.ai' : 'demo.you');
  div.querySelector('p').textContent = text;
  transcriptEl.appendChild(div);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'bubble ai';
  div.id = 'typingBubble';
  div.innerHTML = `<span class="who">${CC.t('demo.ai')}</span><div class="typing"><span></span><span></span><span></span></div>`;
  transcriptEl.appendChild(div);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

function hideTyping() {
  const t = el('typingBubble');
  if (t) t.remove();
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = !message;
}

// ------------------------------------------------------------ mode banner --

function paintMode(mode) {
  badge.textContent = CC.t(`demo.badge.${mode}`);
  explainer.innerHTML = CC.t(`demo.explain.${mode}`);
  if (mode === 'gemini') {
    badge.style.background = 'var(--teal-soft)';
    badge.style.color = 'var(--teal)';
  } else if (mode === 'fallback' || mode === 'degraded') {
    badge.style.background = '#F2E9D8';
    badge.style.color = 'var(--gold-dark)';
  } else {
    badge.style.background = '#F6E3E3';
    badge.style.color = '#8B3A3A';
  }
}

async function checkBackend() {
  try {
    const health = await CC.api('/api/health', { timeout: 8000, auth: false });
    state.online = true;
    if (health.geminiReachable) state.engine = 'gemini';
    else if (health.geminiConfigured) state.engine = 'degraded';
    else state.engine = 'fallback';
    paintMode(state.engine);
    el('startBtn').disabled = false;
    engineNote.textContent = '';
  } catch (err) {
    state.online = false;
    paintMode('offline');
    el('startBtn').disabled = true;
    engineNote.textContent = `${CC.apiBase} — no response.`;
  }
}

// ------------------------------------------------------------- interview --

function setBusy(busy) {
  state.busy = busy;
  sendBtn.disabled = busy;
  answerInput.disabled = busy;
  sendBtn.textContent = busy ? CC.t('demo.thinking') : CC.t('demo.send');
}

function updateProgress() {
  progressLabel.textContent =
    `${CC.t('demo.question')} ${state.turn + 1} ${CC.t('demo.of')} ${state.maxTurns}`;
}

async function startInterview() {
  showError('');
  try {
    const data = await CC.api('/api/interview/start', {
      method: 'POST',
      body: { language: CC.lang, confidenceBefore: state.confidenceBefore },
    });
    state.sessionId = data.sessionId;
    state.engine = data.engine;
    state.maxTurns = data.maxTurns || 7;
    state.turn = 0;

    startCard.hidden = true;
    interviewCard.hidden = false;
    transcriptEl.innerHTML = '';
    bubble('ai', data.question);
    updateProgress();
    answerInput.focus();
  } catch (err) {
    paintMode('offline');
    showError(CC.t('demo.offline'));
  }
}

async function sendAnswer() {
  if (state.busy) return;
  const answer = answerInput.value.trim();
  if (!answer) { showError(CC.t('demo.emptyAnswer')); return; }

  showError('');
  bubble('student', answer);
  answerInput.value = '';
  setBusy(true);
  showTyping();

  try {
    const data = await CC.api('/api/interview/reply', {
      method: 'POST',
      body: { sessionId: state.sessionId, answer },
    });
    hideTyping();
    state.turn = data.turn;
    state.engine = data.engine;

    if (data.done) {
      interviewCard.hidden = true;
      showAcademics();
    } else {
      bubble('ai', data.question);
      updateProgress();
      answerInput.focus();
    }
  } catch (err) {
    hideTyping();
    showError(err.status === 0 ? CC.t('demo.offline') : err.message);
  } finally {
    setBusy(false);
  }
}

// ------------------------------------------------------------- academics --

function showAcademics() {
  const grid = el('marksGrid');
  grid.innerHTML = '';
  MARK_FIELDS.forEach((field) => {
    const wrap = document.createElement('label');
    wrap.className = 'mark-field';
    wrap.innerHTML = `
      <span>${CC.lang === 'ta' ? field.ta : field.en}</span>
      <input type="number" min="0" max="100" inputmode="numeric"
             data-mark="${field.key}" placeholder="—">
    `;
    grid.appendChild(wrap);
  });
  academicsCard.hidden = false;
  academicsCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function collectMarks() {
  const marks = {};
  document.querySelectorAll('[data-mark]').forEach((input) => {
    const value = input.value.trim();
    if (value === '') return;
    const num = Number(value);
    if (!Number.isNaN(num)) marks[input.dataset.mark] = Math.max(0, Math.min(100, num));
  });
  return Object.keys(marks).length ? marks : null;
}

async function finish(academics) {
  academicsCard.hidden = true;
  interviewCard.hidden = false;
  showTyping();
  setBusy(true);

  try {
    const data = await CC.api('/api/interview/finish', {
      method: 'POST',
      body: { sessionId: state.sessionId, language: CC.lang, academics },
    });
    hideTyping();
    renderResults(data);
  } catch (err) {
    hideTyping();
    interviewCard.hidden = false;
    showError(err.status === 0 ? CC.t('demo.offline') : err.message);
  } finally {
    setBusy(false);
  }
}

// --------------------------------------------------------------- results --

function renderResults(data) {
  el('resultsIntro').textContent = data.summary || '';

  const note = el('saveNote');
  note.textContent = data.saved ? CC.t('results.saved') : CC.t('results.notSaved');
  note.className = data.saved ? 'save-note saved' : 'save-note';

  const chip = el('engineChip');
  chip.textContent = CC.t(data.engine === 'gemini' ? 'results.engine.gemini' : 'results.engine.fallback');
  chip.className = 'engine-chip ' + (data.engine === 'gemini' ? 'is-gemini' : 'is-fallback');

  renderConsistency(data.consistency, data.engine);
  resetFeedback();

  const list = el('matchList');
  list.innerHTML = '';
  data.matches.forEach((career, i) => {
    const card = document.createElement('div');
    card.className = 'match-card' + (i === 0 ? ' rank-1' : '');

    const why = career.why
      ? `<p class="match-why"><strong>${CC.t('results.why')}:</strong> <span></span></p>`
      : '';

    card.innerHTML = `
      <div class="match-rank">${i + 1}</div>
      <div class="match-body">
        <h4></h4>
        <p class="match-blurb"></p>
        ${why}
      </div>
      <div class="match-score">
        <span class="score-value">${career.fit}%</span>
        <span class="score-label">${CC.t('results.match')}</span>
        <span class="score-sub">${career.similarity}% ${CC.t('results.similarity')}</span>
      </div>
    `;
    card.querySelector('h4').textContent = career.name;
    card.querySelector('.match-blurb').textContent = career.blurb;
    if (career.why) card.querySelector('.match-why span').textContent = career.why;
    list.appendChild(card);
  });

  el('gapTitle').textContent = `${CC.t('results.gap')} — ${data.gap.careerName}`;
  const bars = el('gapBars');
  bars.innerHTML = '';
  data.gap.rows.forEach((row) => {
    const havePct = Math.max(0, Math.min(100, Math.round((row.have / row.need) * 100)));
    const div = document.createElement('div');
    div.className = 'gap-row';
    div.innerHTML = `
      <div class="gap-label"><span></span><span>${row.have} / ${row.need} ${CC.t('results.needed')}</span></div>
      <div class="gap-track"><div class="gap-fill-have" style="width:${havePct}%"></div><div class="gap-fill-need" style="width:${100 - havePct}%"></div></div>
    `;
    div.querySelector('.gap-label span').textContent = row.label;
    bars.appendChild(div);
  });

  const roadmap = el('roadmapList');
  roadmap.innerHTML = '';
  data.roadmap.forEach((action) => {
    const li = document.createElement('li');
    li.textContent = action;
    roadmap.appendChild(li);
  });

  interviewCard.hidden = true;
  resultsWrap.hidden = false;
  resultsWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderConsistency(consistency, engine) {
  const card = el('consistencyCard');
  const text = el('consistencyText');
  const flags = el('consistencyFlags');
  flags.innerHTML = '';
  card.hidden = false;
  card.dataset.level = consistency ? consistency.level : 'none';

  if (!consistency) {
    // Be straight about it: the scripted engine cannot cross-check.
    text.textContent = CC.t('results.consistency.none');
    return;
  }
  text.textContent = CC.t(`results.consistency.${consistency.level}`);
  consistency.flags.forEach((flag) => {
    const li = document.createElement('li');
    li.textContent = flag;
    flags.appendChild(li);
  });
}

function resetFeedback() {
  state.feedback = { rating: null, confidenceAfter: null, wouldAct: null };
  buildAllScales();
  el('feedbackComment').value = '';
  el('feedbackError').hidden = true;
  el('feedbackThanks').hidden = true;
  el('feedbackBtn').hidden = false;
  el('feedbackBtn').disabled = false;
}

async function sendFeedback() {
  const errorBox = el('feedbackError');
  errorBox.hidden = true;
  if (!state.feedback.rating) {
    errorBox.textContent = CC.t('feedback.pickRating');
    errorBox.hidden = false;
    return;
  }
  el('feedbackBtn').disabled = true;
  try {
    await CC.api('/api/feedback', {
      method: 'POST',
      body: {
        sessionId: state.sessionId,
        rating: state.feedback.rating,
        confidenceAfter: state.feedback.confidenceAfter,
        wouldAct: state.feedback.wouldAct,
        comment: el('feedbackComment').value.trim(),
      },
    });
    el('feedbackBtn').hidden = true;
    el('feedbackThanks').hidden = false;
  } catch (err) {
    errorBox.textContent = err.status === 0 ? CC.t('demo.offline') : err.message;
    errorBox.hidden = false;
    el('feedbackBtn').disabled = false;
  }
}

function reset() {
  state.sessionId = null;
  state.turn = 0;
  state.confidenceBefore = null;
  buildAllScales();
  transcriptEl.innerHTML = '';
  answerInput.value = '';
  showError('');
  resultsWrap.hidden = true;
  academicsCard.hidden = true;
  interviewCard.hidden = true;
  startCard.hidden = false;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ------------------------------------------------------------------ wire --

document.addEventListener('DOMContentLoaded', () => {
  CC.applyI18n();
  CC.mountLangToggle();
  CC.mountNav();
  buildAllScales();
  checkBackend();
  el('feedbackBtn').addEventListener('click', sendFeedback);

  el('startBtn').addEventListener('click', startInterview);
  sendBtn.addEventListener('click', sendAnswer);
  el('useMarksBtn').addEventListener('click', () => finish(collectMarks()));
  el('skipMarksBtn').addEventListener('click', () => finish(null));
  el('retakeBtn').addEventListener('click', reset);

  // Enter sends, Shift+Enter makes a new line.
  answerInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendAnswer();
    }
  });

  document.addEventListener('cc:langchange', () => {
    buildAllScales();
    if (state.online) paintMode(state.engine || 'fallback');
    if (!interviewCard.hidden) updateProgress();
  });
});
