import { API_BASE_URL } from '../config/api.config';

export async function finishSession(token, folder, questionsCount) {
  const res = await fetch(`${API_BASE_URL}/api/session/finish`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, folder, questionsCount })
  });
  return res.json();
}