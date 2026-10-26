let csrfToken = '';

function errorText(value) {
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) return value.map(errorText).join(' ');
  if (value && typeof value === 'object') return Object.entries(value).map(([key, item]) => `${key === 'detail' || key === 'non_field_errors' ? '' : key + ' : '}${errorText(item)}`).join(' ');
  return 'Une erreur est survenue.';
}

export async function api(path, options = {}) {
  let response;
  const multipart = options.body instanceof FormData;
  try {
    response = await fetch(path.startsWith('/api/') ? path : `/api/${path}`, {
      credentials: 'same-origin', ...options,
      headers: { ...(!multipart && { 'Content-Type': 'application/json' }), 'X-CSRFToken': csrfToken, ...options.headers },
      body: multipart ? options.body : options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new Error('Connexion au serveur impossible. Réessayez dans quelques instants.');
  }
  const payload = await response.json().catch(() => null);
  if (!response.ok) throw new Error(payload ? errorText(payload) : 'Le serveur est indisponible. Veuillez réessayer.');
  if (payload?.csrfToken) csrfToken = payload.csrfToken;
  return payload;
}

export async function listAll(resource) {
  let path = resource;
  const items = [];
  while (path) {
    const page = await api(path);
    items.push(...page.results);
    const next = page.next ? new URL(page.next, window.location.origin) : null;
    path = next ? next.pathname + next.search : null;
  }
  return items;
}
