/* ==========================================================================
   Where the API lives.

   The old build hard-coded http://localhost:5000, so the deployed site could
   never reach a backend. Resolution order now:

     1. ?api=https://...            (handy for testing one deploy against another)
     2. <meta name="cc-api-base">   (set it once in the HTML)
     3. localhost during local dev
     4. PRODUCTION_API_BASE below   ← set this to your Render URL

   Nothing secret lives here. The Gemini key stays on the server.
   ========================================================================== */

// 👇 EDIT THIS ONE LINE after you deploy the backend to Render.
const PRODUCTION_API_BASE = 'https://careercompass-ai-api.onrender.com';

function resolveApiBase() {
  const fromQuery = new URLSearchParams(location.search).get('api');
  if (fromQuery) return fromQuery.replace(/\/$/, '');

  const meta = document.querySelector('meta[name="cc-api-base"]');
  if (meta && meta.content.trim()) return meta.content.trim().replace(/\/$/, '');

  const host = location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '') {
    return 'http://localhost:5000';
  }
  return PRODUCTION_API_BASE.replace(/\/$/, '');
}

window.CC = window.CC || {};
window.CC.apiBase = resolveApiBase();
window.CC.storageKeys = { token: 'cc_token', user: 'cc_user', lang: 'cc_lang' };
