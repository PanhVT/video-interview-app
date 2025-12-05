export async function finishSession(token, folder, questionsCount) {
  const res = await fetch("http://localhost:8000/api/session/finish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, folder, questionsCount })
  });
  return res.json();
}