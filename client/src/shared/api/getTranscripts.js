import { API_BASE_URL } from '../config/api.config';

/**
 * API functions để lấy transcripts
 */

/**
 * Lấy tất cả transcripts của một session
 * @param {string} folder - Tên folder session (ví dụ: "05_12_2025_00_18_Anhh")
 * @returns {Promise<Object>} Response với transcripts
 */
export async function getTranscripts(folder) {
  const res = await fetch(`${API_BASE_URL}/api/transcripts/${folder}`);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to fetch transcripts' }));
    throw new Error(error.detail || 'Failed to fetch transcripts');
  }
  return res.json();
}

/**
 * Lấy transcript của một câu hỏi cụ thể
 * @param {string} folder - Tên folder session
 * @param {number} questionIndex - Số thứ tự câu hỏi (1, 2, 3, ...)
 * @returns {Promise<Object>} Response với transcript
 */
export async function getTranscript(folder, questionIndex) {
  const res = await fetch(`${API_BASE_URL}/api/transcripts/${folder}/${questionIndex}`);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to fetch transcript' }));
    throw new Error(error.detail || 'Failed to fetch transcript');
  }
  return res.json();
}

/**
 * Liệt kê tất cả sessions có transcripts
 * @returns {Promise<Object>} Response với danh sách sessions
 */
export async function listAllSessions() {
  const res = await fetch(`${API_BASE_URL}/api/transcripts`);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to list sessions' }));
    throw new Error(error.detail || 'Failed to list sessions');
  }
  return res.json();
}

