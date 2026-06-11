// Shared front-end helpers for the AI Interview Assistant.

/**
 * Thin fetch wrapper. Cookies carry the JWT, so credentials are included.
 * Returns { ok, status, data }.
 */
async function api(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
  };
  if (body !== null) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  let data = {};
  try { data = await res.json(); } catch (_) { /* no body */ }
  return { ok: res.ok, status: res.status, data };
}

/** Render a dismissible Bootstrap alert at the top of the page. */
function showAlert(message, type = 'info') {
  const box = document.getElementById('alerts');
  if (!box) return;
  box.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${escapeHtml(message)}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
}

/** Escape user-controlled strings before injecting into innerHTML (XSS guard). */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Logout button (present in the navbar when authenticated).
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('logoutBtn');
  if (btn) {
    btn.addEventListener('click', async () => {
      await api('/api/auth/logout', 'POST');
      window.location = '/';
    });
  }
});
