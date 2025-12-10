import { API_BASE_URL } from '../config/api.config';

export async function verifyToken(token) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/verify-token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return {
        ok: false,
        code: res.status,
        error: data.error || data.detail || 'Invalid token or verification failed',
        guidance:
          res.status === 401
            ? 'Token invalid or expired. Ask your instructor/administrator for a valid token.'
            : 'Check server logs or network connectivity.'
      };
    }

    return { ok: true, ...data };
  } catch (error) {
    console.error('Verify token error:', error);
    return {
      ok: false,
      code: 0,
      error: error.message || 'Server unreachable',
      guidance: 'Cannot reach server. Ensure backend is running and reachable from the client.'
    };
  }
}
