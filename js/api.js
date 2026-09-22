/* ==========================================================================
   Talking to the backend.

   The token is a signed JWT from /api/auth/login. It's kept in localStorage
   so a refresh doesn't sign you out. No password is ever stored client-side.
   ========================================================================== */

window.CC = window.CC || {};

CC.getToken = () => localStorage.getItem(CC.storageKeys.token);
CC.getUser = () => {
  try { return JSON.parse(localStorage.getItem(CC.storageKeys.user) || 'null'); }
  catch (e) { return null; }
};

CC.setSession = (token, user) => {
  localStorage.setItem(CC.storageKeys.token, token);
  localStorage.setItem(CC.storageKeys.user, JSON.stringify(user));
};

CC.clearSession = () => {
  localStorage.removeItem(CC.storageKeys.token);
  localStorage.removeItem(CC.storageKeys.user);
};

class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}
CC.ApiError = ApiError;

CC.api = async function (path, { method = 'GET', body, timeout = 30000, auth = true } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const token = CC.getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${CC.apiBase}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (err) {
    throw new ApiError('offline', 0);
  } finally {
    clearTimeout(timer);
  }

  let data = null;
  try { data = await res.json(); } catch (e) { /* empty body */ }

  if (!res.ok) {
    if (res.status === 401 && auth && token) CC.clearSession();
    throw new ApiError((data && data.error) || `Request failed (${res.status})`, res.status);
  }
  return data;
};

// Shared nav: show the right links for who's signed in.
CC.mountNav = function () {
  const user = CC.getUser();
  document.querySelectorAll('[data-when="signed-in"]').forEach((el) => {
    el.hidden = !user;
  });
  document.querySelectorAll('[data-when="signed-out"]').forEach((el) => {
    el.hidden = !!user;
  });
  document.querySelectorAll('[data-user-name]').forEach((el) => {
    if (user) el.textContent = user.name;
  });
  document.querySelectorAll('[data-signout]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      CC.clearSession();
      location.href = 'index.html';
    });
  });
  const dash = document.querySelector('[data-dashboard-link]');
  if (dash && user) {
    dash.hidden = user.role === 'student';
    dash.href = 'dashboard.html';
  }
};
