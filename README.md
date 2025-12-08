# <img src="https://i.postimg.cc/0jSWvN6g/cat-logo.png" width="40"> Web Interview Recorder

This is a browser-based interview system with up to five questions.
For each question, the application records a short video (camera + microphone) and uploads it immediately to the backend server, and generate automated transcripts & analytics using AI.

The system follows a client-server architecture, communicates via HTTP/HTTPS, and requires camera/mic permissions from the browser.

## Features
### Frontend (Vite + React)
* Clean UI for interview sessions
* Camera & microphone recording using browser MediaRecorder API
* Timed questions
* Automatic upload after each response
* Session result page with recorded videos & transcripts
* Local preview before submission
* Responsive design

### Backend (FastAPI + Python)
* API to receive and store uploaded video files
* Session folders generated with timestamp
* Metadata + transcript generation
* Video storage under the `server/recordings/` directory

### AI Features
* Automatic transcription
* Structured output per question (Q1–Q5)
* Metadata saved to JSON

## Project Structure
```bash
video-interview-app-main/
│
├── client/                      # Frontend (Vite + React)
│   ├── src/
│   │   ├── app/                 # Main app components
│   │   ├── components/          # UI components
│   │   ├── hooks/               # Custom hooks
│   │   ├── styles/              # Tailwind & CSS
│   │   ├── utils/               # Helpers
│   │   └── main.jsx
│   ├── public/
│   ├── index.html
│   └── vite.config.js
│
├── server/                      # Backend (FastAPI)
│   ├── main.py                  # API routes
│   ├── requirements.txt
│   ├── recordings/              # Saved interview sessions
│   │   └── <timestamp>/
│   │       ├── Q1.webm
│   │       ├── Q2.webm
│   │       ├── …
│   │       ├── meta.json
│   │       └── transcripts.txt
│   └── ...
│
└── README.md                    # (this file)
