# <img src="https://i.postimg.cc/0jSWvN6g/cat-logo.png" width="40"> SnapCat - Web Interview Recorder
An application that records interview answers **one question at a time** (maximum 5 questions).

## 1. Objectives & Scope
* Record interview videos per question; after stopping, each question is uploaded immediately (**per-question upload**). The system does not move to the next question until the current upload succeeds.
* API workflow includes 4 steps: `verify-token → session/start → upload-one → session/finish`
* Storage folder is named using the **Asia/Bangkok timezone** format:
`DD_MM_YYYY_HH_mm_username/`, containing `meta.json`, files `Qi.webm`, and `transcripts.txt`.
* Supports camera/microphone preview, a 2-minute countdown per question, and one **re-record** attempt for each question.
* HTTPS is required for public deployment so that browsers allow access to the camera and microphone.

## 2. System Architecture Overview
This is a client–server model over HTTP.
```bash
Browser (Client) -REST→ FastAPI server
    ├── getUserMedia + MediaRecorder (video/webm)
    ├── records Q1 → /api/upload-one (multipart/form-data)
    └── Finish → /api/session/finish

FastAPI
    ├── /api/verify-token: validates token (demo: 12345)
    ├── /api/session/start: creates session folder and meta.json
    ├── /api/upload-one: saves Q{i}.webm and updates metadata
    ├── /api/session/finish: finalizes metadata and optionally starts STT
    └── /api/transcripts: read/export transcript, monitor STT progress

Storage: server/uploads/<DD_MM_YYYY_HH_mm_username>/
```

## 3. Project Structure
```bash
video-interview-app-main/
├── client/                     # Frontend (React + Vite)
│   └── src/
│  ├── app/                     # Router
│       ├── features/           # login, preview, interview, finish
│       ├── shared/api/         # call REST endpoints
│       └── shared/hooks/       # useRecorder (MediaRecorder)
│
├── server/                     # Backend FastAPI
│   ├── app/main.py             # register router
│   ├── app/api/                # verify_token, session_start, upload_one, ...
│   ├── app/storage/            # file_manager, metadata_manager
│   ├── app/services/           # transcription (Whisper local)
│   └── uploads/                # location to save interview sessions (created at runtime)
└── README.md
```

## 4. Installation & Running
### Frontend
```bash
cd client
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### Backend
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
### Access
* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`

## 5. User Flow
1. **Login**: Enter the token and name. Only valid tokens (demo: `12345`) are allowed to continue.
2. **Preview**: Request camera/microphone permissions; show instructions for handling device-permission errors.
3. **Instructions**: Display the 5 questions, the 2-minute limit per question, and how to stop & upload each recording.
4. **Interview**:
   - Press Start to record (MediaRecorder `video/webm;codecs=vp8,opus`), start a 120-second countdown, and automatically stop & upload when time is up.
   - When Stop is pressed, the client sends a multipart request to `/api/upload-one` with the token, folder, questionIndex, and video.
   - The next question is unlocked only after a successful upload; a Reload Upload button is available to resend the last blob if needed.
   - Each question allows **one retake** after a successful upload.
5. **Finish**: After all questions have been uploaded, call `/api/session/finish` → redirect to the thank-you page and display the session folder name.

## 6. API Contract
- `POST /api/verify-token`  
  Body: `{ "token": "12345" }` → `{ ok: true }` or 401.

- `POST /api/session/start`  
  Body: `{ token, userName }`  
  Return: `{ ok, folder, sanitizedUserName }`, creates the folder in `server/uploads/`.

- `POST /api/upload-one` (multipart/form-data)  
  Fields: `token`, `folder`, `questionIndex`, `video` (file).  
  Return: `{ ok: true, savedAs: "Q<index>.webm" }`, update `meta.json`.

- `POST /api/session/finish`  
  Body: `{ token, folder, questionsCount }`  
  Return: `{ ok: true, transcribing: <bool>, engine? }`, starts the STT process if available.

- `GET /api/transcription-status/{folder}`: checks the STT progress.
- `GET /api/transcripts`, `/api/transcripts/{folder}`, `/api/transcripts/{folder}/{question}`, `/api/transcripts/{folder}/export?format=txt|csv|json`.

## 7. Storage & Naming
- Base directory: `server/uploads/`.
- Session folder: `DD_MM_YYYY_HH_mm_<username_sanitized>/` (Asia/Bangkok timezone, see `app/core/time_utils.py`).
- Inside each session directory:
    - `Q1.webm ... Q5.webm`
    - `meta.json` (userName, uploadedAt, finishedAt, timeZone, receivedQuestions, transcripts, questionsCount)
    - `transcripts.txt` generated when STT results are available.

## 8. Limits & Recommended MIME Types
* Recording uses `video/webm` (VP8/Opus). The browser/MediaRecorder sets this MIME type automatically.
* File size: no hard limit on the server yet; recommended to keep each video < 100 MB and duration ≤ 2 minutes to avoid 413/timeout errors in production. Adjust limits as needed in the reverse proxy or FastAPI.

## 9. Reliability & Retry/Backoff
* Default: each question is uploaded once; if an error occurs, the UI shows a banner and a **Reload Upload** button to resend the last blob.
* Auto backoff is not enabled yet; retry logic with exponential backoff can be added to `uploadOne` on the client (e.g., 3 attempts with 1s → 2s → 4s delays).
* The next question cannot be accessed until the current upload is successful.

## 10. HTTPS & Device Permissions
* When deployed publicly, HTTPS is required for browsers to allow camera/microphone access.
* For LAN testing, HTTP is acceptable (browsers allow access on localhost/private IPs), but production environments should always use HTTPS.

## 11. Speech-to-Text
* The server includes an STT pipeline (local Whisper) implemented in `app/services/transcription_manager.py`.
* When `/session/finish` is called and the engine is available, the server runs a background process: it reads each `Qi.webm`, updates transcript fields in `meta.json`, and generates `transcripts.txt`.
* Progress can be queried via `/api/transcription-status/{folder}`, results can be downloaded through `/api/transcripts/`....

## 12. Design Rationale (Networking Perspective)
* Per-question segmentation (≤5) reduces data-loss risk and fits the client–server model for partial HTTP uploads.
* Token validation is handled on the server to prevent spoofing (client-side checks only improve UX).
* Folder naming is sanitized and timestamped in the Asia/Bangkok timezone for consistent logging and review.
* Clear state transitions: permission → recording → uploading → error/success; network failures support manual retry.
