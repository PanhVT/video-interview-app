import { API_BASE_URL } from '../config/api.config';

export async function startSession(token, userName) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, userName }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return {
        ok: false,
        code: res.status,
        error: data.error || 'Failed to start session',
        guidance: res.status === 401 ? 'Invalid token. Please request a valid token.' : 'Check server logs.'
      };
    }

    return { ok: true, ...data };
  } catch (err) {
    console.error('startSession error:', err);
    return {
      ok: false,
      code: 0,
      error: err.message || 'Network error',
      guidance: 'Network error or server unreachable. Ensure backend is running.'
    };
  }
}