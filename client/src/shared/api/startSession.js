export async function startSession(token, userName) {
  const res = await fetch("http://localhost:8000/api/session/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, userName })
  });
  return res.json();
}