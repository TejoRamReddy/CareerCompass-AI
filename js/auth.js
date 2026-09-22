/* ==========================================================================
   Sign in / sign up.

   The password is sent once over HTTPS and is never stored in the browser;
   what comes back is a signed token. The server stores only a PBKDF2 hash.
   ========================================================================== */

const form = document.getElementById('authForm');
const errorEl = document.getElementById('formError');
const submitBtn = document.getElementById('submitBtn');
const roleSelect = document.getElementById('role');
const classCodeHint = document.getElementById('classCodeHint');

let mode = new URLSearchParams(location.search).get('mode') === 'signup' ? 'signup' : 'signin';

function paintMode() {
  const signup = mode === 'signup';
  document.querySelectorAll('.signup-only').forEach((el) => { el.hidden = !signup; });
  document.getElementById('authTitle').dataset.i18n = signup ? 'auth.signup' : 'auth.signin';
  submitBtn.dataset.i18n = signup ? 'auth.signup' : 'auth.signin';
  document.getElementById('toggleMode').dataset.i18n = signup ? 'auth.haveAccount' : 'auth.noAccount';
  document.getElementById('password').autocomplete = signup ? 'new-password' : 'current-password';
  if (signup) paintRole();
  CC.applyI18n();
}

function paintRole() {
  if (mode !== 'signup') return;
  const role = roleSelect.value;
  document.querySelectorAll('.student-only').forEach((el) => { el.hidden = role !== 'student'; });
  const codeField = document.querySelector('.class-code-field');
  codeField.hidden = role === 'parent';
  classCodeHint.textContent = CC.t(
    role === 'teacher' ? 'auth.classCodeHintTeacher' : 'auth.classCodeHintStudent'
  );
}

function showError(message) {
  errorEl.textContent = message || '';
  errorEl.hidden = !message;
}

function landingFor(user) {
  if (user.role === 'student') return 'demo.html';
  return 'dashboard.html';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  showError('');
  submitBtn.disabled = true;
  const originalKey = submitBtn.dataset.i18n;
  submitBtn.textContent = CC.t('auth.working');

  const body = {
    email: document.getElementById('email').value.trim(),
    password: document.getElementById('password').value,
  };

  if (mode === 'signup') {
    Object.assign(body, {
      name: document.getElementById('name').value.trim(),
      role: roleSelect.value,
      branch: document.getElementById('branch').value.trim(),
      college: document.getElementById('college').value.trim(),
      classCode: document.getElementById('classCode').value.trim(),
      language: CC.lang,
    });
  }

  try {
    const path = mode === 'signup' ? '/api/auth/register' : '/api/auth/login';
    const data = await CC.api(path, { method: 'POST', body, auth: false });
    CC.setSession(data.token, data.user);
    location.href = landingFor(data.user);
  } catch (err) {
    showError(err.status === 0
      ? `Can't reach the server at ${CC.apiBase}. Is the backend running?`
      : err.message);
    submitBtn.disabled = false;
    submitBtn.dataset.i18n = originalKey;
    CC.applyI18n();
  }
});

document.getElementById('toggleMode').addEventListener('click', () => {
  mode = mode === 'signup' ? 'signin' : 'signup';
  showError('');
  paintMode();
});

roleSelect.addEventListener('change', paintRole);
document.addEventListener('cc:langchange', () => paintMode());

CC.applyI18n();
CC.mountLangToggle();
paintMode();

// Already signed in? Go where you were headed.
if (CC.getToken() && CC.getUser()) location.href = landingFor(CC.getUser());
