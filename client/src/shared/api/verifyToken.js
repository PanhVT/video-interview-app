import { API_BASE_URL } from '../config/api.config';

export async function verifyToken(token) {
  try {
  const res = await fetch(`${API_BASE_URL}/api/verify-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token })
  });
    
    if (!res.ok) {
      // Nếu response không OK, vẫn parse JSON để lấy error message
      const errorData = await res.json().catch(() => ({ ok: false }));
      return errorData;
    }
    
  return res.json();
  } catch (error) {
    // Network error hoặc server không chạy
    console.error("Verify token error:", error);
    return { ok: false, error: error.message || "Server unreachable" };
  }
}
