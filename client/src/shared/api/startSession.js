import { API_BASE_URL } from '../config/api.config';

export async function startSession(token, userName) {
  const res = await fetch(`${API_BASE_URL}/api/session/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, userName })
  });
  return res.json();
}