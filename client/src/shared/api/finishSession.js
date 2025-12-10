import { API_BASE_URL } from '../config/api.config';

export async function finishSession(token, folder, questionsCount) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/session/finish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, folder, questionsCount }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return {
        ok: false,
        code: res.status,
        error: data.error || 'Failed to finish session',
        guidance: res.status === 401
          ? 'Invalid token when finishing session. Re-login or request a valid token.'
          : 'Server error. Check backend logs.'
      };
    }

    return { ok: true, ...data };
  } catch (err) {
    console.error('finishSession error:', err);
    return {
      ok: false,
      code: 0,
      error: err.message || 'Network error',
      guidance: 'Network error or server unreachable. Ensure the backend is running.'
    };
  }
}