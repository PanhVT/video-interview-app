import { API_BASE_URL } from '../config/api.config';

export async function uploadOne({ token, folder, questionIndex, blob }) {
  try {
    const form = new FormData();
    form.append('token', token);
    form.append('folder', folder);
    form.append('questionIndex', String(questionIndex));
    form.append('video', blob, `Q${questionIndex}.webm`);

    const res = await fetch(`${API_BASE_URL}/api/upload-one`, {
      method: 'POST',
      body: form,
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      let guidance = 'See server logs for details.';
      if (res.status === 401) guidance = 'Invalid or expired token. Please re-login or request a new token.';
      else if (res.status === 413) guidance = 'File too large. Try recording shorter answers or lower resolution. See README for size limits.';
      else if (res.status === 415) guidance = 'Unsupported media type. Record as `video/webm` or `video/mp4`.';
      else if (res.status === 400) guidance = 'Bad request. Ensure token, folder, questionIndex and video fields are present.';
      else if (res.status === 429) guidance = 'Too many requests. Wait a moment before retrying.';

      return {
        ok: false,
        code: res.status,
        error: data.error || data.detail || 'Upload failed',
        guidance,
      };
    }

    return { ok: true, ...data };
  } catch (err) {
    console.error('uploadOne error:', err);
    return {
      ok: false,
      code: 0,
      error: err.message || 'Network error',
      guidance: 'Network error or server unreachable. Check your connection and ensure the backend is running.'
    };
  }
}