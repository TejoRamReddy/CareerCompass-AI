/* ==========================================================================
   Dashboards.

   Teacher: the shape of a class — who has taken the interview, which careers
   keep coming up, which skills most of the class still needs. Never the
   transcript of what a student said.

   Parent: one card per linked child, with matches and next steps, only after
   the child hands over their share code.

   Student: their own share code and past runs.
   ========================================================================== */

const root = document.getElementById('dashRoot');

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString();
}

function fail(message) {
  root.innerHTML = `<p class="form-error">${escapeHtml(message)}</p>`;
}

// ------------------------------------------------------------------ teacher --

function fitChangeCell(change) {
  if (change === null || change === undefined) return '<span class="muted">—</span>';
  const sign = change > 0 ? '+' : '';
  const cls = change > 0 ? 'delta-up' : change < 0 ? 'delta-down' : 'muted';
  return `<span class="${cls}">${sign}${change}</span>`;
}

function workshopCard(workshops) {
  if (!workshops || !workshops.length) return '';
  const items = workshops.map((w) => `
    <li><strong>${escapeHtml(w.label)}</strong>
        <span class="count">${w.count}</span>
        <br><span class="muted">${escapeHtml(w.idea)}</span></li>`).join('');
  return `<div class="dash-card" style="margin-top:24px;">
    <h3>${CC.t('dash.workshops')}</h3>
    <ul class="workshop-list">${items}</ul>
  </div>`;
}

async function renderTeacher() {
  const data = await CC.api(`/api/teacher/class?lang=${CC.lang}`);

  const students = data.students.map((s) => `
    <tr>
      <td>${escapeHtml(s.name)}</td>
      <td>${escapeHtml(s.branch || '—')}</td>
      <td>${s.completed ? escapeHtml(s.topCareer) : `<span class="muted">${CC.t('dash.notTaken')}</span>`}</td>
      <td>${s.completed ? `${s.fit}%` : '—'}</td>
      <td>${s.attempts || 0}</td>
      <td>${fitChangeCell(s.fitChange)}</td>
      <td>${escapeHtml(formatDate(s.takenAt))}</td>
    </tr>`).join('');

  const careers = data.topCareers.map((c) => `
    <li><span>${escapeHtml(c.career)}</span><span class="count">${c.count}</span></li>`).join('');

  const gaps = data.commonGaps.map((g) => `
    <li><span>${escapeHtml(g.label)}</span><span class="count">${g.count}</span></li>`).join('');

  root.innerHTML = `
    <span class="section-tag">${escapeHtml(data.classCode)}</span>
    <h1>${CC.t('dash.teacher')}</h1>
    <p class="question-hint">
      ${data.studentCount} ${CC.t('dash.students')} · ${data.completedCount} ${CC.t('dash.completed')}
    </p>

    ${data.studentCount === 0 ? `<p class="empty-note">${CC.t('dash.noStudents')}</p>` : `
      <div class="dash-grid">
        <div class="dash-card">
          <h3>${CC.t('dash.topCareers')}</h3>
          <ul class="tally">${careers || '<li class="muted">—</li>'}</ul>
        </div>
        <div class="dash-card">
          <h3>${CC.t('dash.commonGaps')}</h3>
          <ul class="tally">${gaps || '<li class="muted">—</li>'}</ul>
        </div>
      </div>

      ${workshopCard(data.workshops)}

      <div class="table-wrap dash-card" style="margin-top:24px;">
        <table class="dash-table">
          <thead><tr>
            <th>${CC.t('auth.name')}</th><th>${CC.t('auth.branch')}</th>
            <th>${CC.t('results.tag')}</th><th>${CC.t('results.match')}</th>
            <th>${CC.t('dash.attempts')}</th><th>${CC.t('dash.fitChange')}</th><th></th>
          </tr></thead>
          <tbody>${students}</tbody>
        </table>
      </div>`}
  `;
}

// ------------------------------------------------------------------- parent --

function childCard(child) {
  if (!child.completed) {
    return `<div class="dash-card">
      <h3>${escapeHtml(child.name)}</h3>
      <p class="muted">${CC.t('dash.notTaken')}</p>
    </div>`;
  }
  const matches = child.matches.map((m, i) => `
    <li><span class="rank">${i + 1}</span>
        <span><strong>${escapeHtml(m.name)}</strong> — ${m.fit}% ${CC.t('results.match')}
        ${m.why ? `<br><span class="muted">${escapeHtml(m.why)}</span>` : ''}</span></li>`).join('');
  const steps = child.roadmap.map((r) => `<li>${escapeHtml(r)}</li>`).join('');

  const tips = (child.tips || []).map((t) => `<li>${escapeHtml(t)}</li>`).join('');

  const runs = (child.progress || []).map((r) => `
    <li><span class="muted">${escapeHtml(formatDate(r.takenAt))}</span>
        <span>${escapeHtml(r.topCareer)}</span>
        <span class="count">${r.fit}%</span></li>`).join('');

  const moves = (child.skillChange || []).map((m) => `
    <li><span>${escapeHtml(m.label)}</span>
        <span class="${m.change > 0 ? 'delta-up' : 'delta-down'}">${m.change > 0 ? '+' : ''}${m.change}</span></li>`).join('');

  const progress = child.attempts > 1 ? `
    <h4>${CC.t('dash.progress')}</h4>
    <ul class="tally">${runs}</ul>
    ${moves ? `<h4>${CC.t('dash.skillChange')}</h4><ul class="tally">${moves}</ul>` : ''}`
    : `<h4>${CC.t('dash.progress')}</h4><p class="muted">${CC.t('dash.noProgress')}</p>`;

  return `<div class="dash-card">
    <h3>${escapeHtml(child.name)}</h3>
    <p class="question-hint">${escapeHtml(child.branch || '')} ${child.college ? '· ' + escapeHtml(child.college) : ''} · ${escapeHtml(formatDate(child.takenAt))}</p>
    <p>${escapeHtml(child.summary || '')}</p>
    <ul class="child-matches">${matches}</ul>
    <h4>${CC.t('results.roadmap')}</h4>
    <ol class="roadmap-list">${steps}</ol>
    ${progress}
    <h4>${CC.t('dash.tips')}</h4>
    <ul class="tip-list">${tips}</ul>
  </div>`;
}

async function renderParent() {
  const data = await CC.api(`/api/parent/children?lang=${CC.lang}`);

  root.innerHTML = `
    <h1>${CC.t('dash.parent')}</h1>

    <div class="dash-card link-card">
      <h3>${CC.t('dash.linkTitle')}</h3>
      <p class="question-hint">${CC.t('dash.linkHint')}</p>
      <div class="link-row">
        <input type="text" id="shareCodeInput" maxlength="12" placeholder="A1B2C3">
        <button class="btn btn-primary" id="linkBtn">${CC.t('dash.linkButton')}</button>
      </div>
      <p class="form-error" id="linkError" hidden></p>
    </div>

    ${data.children.length
      ? `<div class="dash-stack">${data.children.map(childCard).join('')}</div>`
      : `<p class="empty-note">${CC.t('dash.noChildren')}</p>`}
  `;

  document.getElementById('linkBtn').addEventListener('click', async () => {
    const input = document.getElementById('shareCodeInput');
    const errorEl = document.getElementById('linkError');
    errorEl.hidden = true;
    try {
      await CC.api('/api/parent/link', {
        method: 'POST', body: { shareCode: input.value.trim().toUpperCase() },
      });
      renderParent();
    } catch (err) {
      errorEl.textContent = err.status === 0 ? 'Server not reachable.' : err.message;
      errorEl.hidden = false;
    }
  });
}

// ------------------------------------------------------------------ student --

async function renderStudent(user) {
  const history = await CC.api('/api/me/history');
  const rows = history.map((h) => `
    <tr>
      <td>${escapeHtml(formatDate(h.createdAt))}</td>
      <td>${escapeHtml(h.topCareer)}</td>
      <td>${h.fit}%</td>
      <td class="muted">${escapeHtml(h.engine)}</td>
    </tr>`).join('');

  root.innerHTML = `
    <h1>${escapeHtml(user.name)}</h1>
    <p class="question-hint">${escapeHtml(user.branch || '')} ${user.college ? '· ' + escapeHtml(user.college) : ''}</p>

    <div class="dash-card">
      <h3>${CC.t('dash.shareCode')}</h3>
      <p class="question-hint">${CC.t('dash.shareCodeHint')}</p>
      <p class="share-code">${escapeHtml(user.shareCode || '—')}</p>
    </div>

    ${history.length ? `
      <div class="table-wrap dash-card" style="margin-top:24px;">
        <table class="dash-table">
          <thead><tr><th></th><th>${CC.t('results.tag')}</th><th>${CC.t('results.match')}</th><th></th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`
      : `<p class="empty-note"><a href="demo.html">${CC.t('demo.start')}</a></p>`}
  `;
}

// --------------------------------------------------------------------- go --

async function render() {
  const user = CC.getUser();
  if (!user || !CC.getToken()) { location.href = 'login.html'; return; }

  try {
    if (user.role === 'teacher') await renderTeacher();
    else if (user.role === 'parent') await renderParent();
    else await renderStudent(user);
  } catch (err) {
    if (err.status === 401) { location.href = 'login.html'; return; }
    fail(err.status === 0 ? `Can't reach the server at ${CC.apiBase}.` : err.message);
  }
}

CC.applyI18n();
CC.mountLangToggle();
CC.mountNav();
render();
document.addEventListener('cc:langchange', render);
