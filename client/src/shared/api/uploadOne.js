import { API_BASE_URL } from '../config/api.config';

export async function uploadOne({ token, folder, questionIndex, blob }) {
  const form = new FormData();
  form.append('token', token);
  form.append('folder', folder);
  form.append('questionIndex', String(questionIndex));
  form.append('video', blob, `Q${questionIndex}.webm`);
  const res = await fetch(`${API_BASE_URL}/api/upload-one`, {
    method: "POST",
    body: form
  });
  return res.json();
}