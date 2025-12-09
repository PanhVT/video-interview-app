# <img src="https://i.postimg.cc/0jSWvN6g/cat-logo.png" width="40"> Web Interview Recorder
A project for Computer Networks - Client-Server Video Recording System

## Overview
This project is a web-based interview recording system where each question is recorded separately and uploaded immediately to the server. 

The system demonstrates core client-server networking concepts such as HTTP communication, structured APIs, reliability (retry/backoff), secure storage, and Speech-to-Text processing.

## Features
### Frontend (Vite + React)
* Clean, minimal UI for interview sessions
* Sequential question (max 5 questions)
* Webcam & microphone recording via `MediaRecorder API`
* Real-time status: `recording → stopped → uploading → success/retry`
* Immediate per-question upload when pressing Next
* Automatic retry with exponential backoff + manual retry button
* Preview camera before starting session
* Responsive UI (desktop/laptop)
* Timed questions
* One-time re-record

### Backend (FastAPI + Python)
* Token verification (`verify-token`)
* Session initialization (`/session/start`) creates folder
* Per-question upload (`/upload-one`) with multipart/form-data
* Saves `Q1.webm → Q2.webm → … ` sequentially
* Creates metadata and updates it incrementally (`meta.json`)
* Session folder format (Asia/Bangkok timezone):
`DD_MM_YYYY_HH_mm_username/`
* Sanitizes username for safe filesystem use
* Stores videos and transcript under
`server/recordings/<session-folder>/`
* Includes logging with ISO timestamps

### AI / STT (Bonus)
* Per-question Speech-to-Text
* Generates `transcripts.txt` labeled by question
* STT data appended into metadata

### Client-Server Communication (Networking Layer)
- Communication over HTTP/HTTPS
- Uses a 4-step API flow: `verify-token → session/start → upload-one → session/finish`.
- Client cannot advance to the next question until upload succeeds
- Per-question upload ensures small file sizes and reduces network loss risk.
- Implements retry with exponential backoff when upload fails.
- Server validates token and sanitizes data before saving.
- HTTPS required when deployed publicly for camera/microphone access

## System Architecture
This is a client–server model over HTTP/HTTPS.
```bash
Browser (Client)
    ├── Requests camera & microphone
    ├── Records Q1 → upload-one
    ├── Records Q2 → upload-one
    ├── …
    └── Finish → session/finish

Backend (FastAPI Server)
    ├── validate token
    ├── create session folder
    ├── save video files
    ├── update metadata
    └── (Bonus) generate transcript
```
## Project Structure
```bash
video-interview-app/
│
├── client/                     # Frontend (React + Vite)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── app/                # App wrapper + router
│       ├── components/         # UI components
│       ├── hooks/              # Webcam + interview logic
│       ├── pages/              # Home, Interview, Results...
│       ├── styles/             # CSS/Tailwind
│       └── utils/              # API & helpers
│
├── server/                     # Backend (FastAPI)
│   ├── main.py                 # API endpoints
│   ├── requirements.txt
│   └── recordings/             # Saved interview sessions
│       └── <timestamp>/
│           ├── Q1.webm
│           ├── ...
│           ├── meta.json
│           └── transcripts.txt
│
└── README.md
```
## API Contract
### POST `/api/verify-token`
```bash
{ "token": "12345" }
```
### POST `/api/session/start`
Creates session folder → returns folder name: `DD_MM_YYYY_HH_mm_ten_user`

### POST `/api/upload-one`
Uploads video of question `i`.

### POST `/api/session/finish`
Finalizes metadata and closes session.

## Installation & Running
### 1. Frontend
```bash
cd client
npm install
npm run dev
```

### 2. Backend
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```
### URLS
* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`

## HTTPS Requirement
Public deployment requires HTTPS to access camera/microphone (browser security).

## Reliability & Retry Policy
* Upload failures → exponential backoff retry
* Minimum 2–3 automatic retry attempts
* Manual retry button available
* Cannot proceed to next question until upload succeeded

## Error Handling
* Invalid token → block start
* Camera/mic permission denied → show guidance
* Network loss → retry
* File too large/wrong MIME → error message
* Server storage error → notify user

## File Naming & Storage Format
Folder name format:
`DD_MM_YYYY_HH_mm_username/` (timezone Asia/Bangkok)
```bash
Q1.webm  
Q2.webm  
Q3.webm  
Q4.webm  
Q5.webm  
meta.json  
transcripts.txt 
```
## Speech-to-Text (STT)
The system automatically generates a transcript for each question after upload.
The backend extracts audio from each video file and produces a combined transcript file.
* Transcript is saved as `transcripts.txt`
* Organized per question (Q1 → Q5)
* Metadata includes STT results for further use
* Useful for reviewing interview content or building AI scoring in the future
Example format:
```bash
Question 1:
The candidate said...

Question 2:
The candidate said...
```

## Screenshots 
