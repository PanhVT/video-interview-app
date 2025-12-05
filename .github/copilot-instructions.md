<!-- Copilot / AI agent instructions for the Video Interview Template repo -->
# Project Snapshot

This repository is a small video-interview demo with two main parts:
- `client/` — React + Vite frontend (port 5173 by default)
- `server/` — FastAPI backend (uvicorn on port 8000). Server stores uploads under `uploads/`.

Key design choices an agent should know:
- Backend is FastAPI mounted at `/api/*` (see `server/app/main.py`). Frontend calls full URLs (no dev proxy).
- Authentication is a demo token check (`"12345"`) in `server/app/api/*` files. Replace in these files for real auth.
- Uploads are saved to `uploads/<folder>/` with a `meta.json` file managed by `server/app/storage/*`.

# Quick start (developer)

PowerShell-friendly commands:

1) Start the backend

```
cd server
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Note: `server/run.sh` runs `uvicorn app.main:app --reload --port 8000` for UNIX shells (use WSL/Git Bash on Windows).

2) Start the frontend

```
cd client
npm install
npm run dev
```

Open the app at `http://localhost:5173`. The frontend makes requests to `http://localhost:8000/api/...`.

# Important files & patterns (use these as entry points)

- Backend routing: `server/app/main.py` — mounts routers from `server/app/api/`.
- API endpoints:
  - `POST /api/verify-token` — payload `{ token }` (demo accepts `"12345"`).
  - `POST /api/session/start` — payload `{ token, userName }` -> returns `{ ok, folder }`.
  - `POST /api/upload-one` — multipart form: `token`, `folder`, `questionIndex`, `video` (file).
  - `POST /api/session/finish` — payload `{ token, folder, questionsCount }`.
- Storage: `server/app/storage/file_manager.py` and `metadata_manager.py` — manage `uploads/<folder>/meta.json` and `Q<N>.webm` files.
- Frontend API wrappers: `client/src/shared/api/*` — examples of fetch usage and exact endpoints the UI expects.
- Session state: `client/src/features/session/SessionContext.jsx` — token, userName, folder, questions array.
- Recorder: `client/src/shared/hooks/useRecorder.js` — MediaRecorder usage and blob creation used by `uploadOne`.

# Data shapes & runtime assumptions

- `meta.json` fields created by the server include: `userName`, `uploadedAt`, `timeZone`, `receivedQuestions` (list), `finishedAt`, `questionsCount`.
- The demo token is hard-coded as `"12345"` in `server/app/api/*`. Tests, dev flows, and the client use this value.
- CORS is allowed for `http://localhost:5173` in `server/app/main.py`; if you change client port, update CORS.

# Agent-specific guidance

- If you modify endpoints, also update `client/src/shared/api/*` to keep fetch URLs in sync (they are full `http://localhost:8000/...` URLs).
- To change where uploads are stored, update `BASE` in `server/app/storage/file_manager.py` and ensure existing `uploads/` examples remain valid.
- For local testing of uploads, use the `uploads/` folder that contains pre-made session folders and `meta.json` samples.
- The frontend does not use an HTTP proxy — the network layer assumes the backend runs on port 8000.

# Editing recommendations (practical checks an agent should do)

- Run the backend and call `POST /api/verify-token` with `{ "token": "12345" }` to confirm the server is reachable.
- After `session/start`, confirm `uploads/<folder>/meta.json` exists and contains `userName`.
- When uploading, verify `uploads/<folder>/Q<N>.webm` files are created and `receivedQuestions` is updated in `meta.json`.

# When submitting changes or generating code

- Prefer minimal, focused edits that preserve the demo flows (token, storage layout, API paths) unless the change intentionally adjusts those contracts.
- When adding async/await or fetch changes, mirror patterns used in `client/src/shared/api/*` for consistency.

---
If anything here looks incomplete or you want more detail about a particular area (e.g., storage, recorder, or CI), tell me what to expand and I'll update this file.
