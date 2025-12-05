from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import verify_token, session_start, upload_one, session_finish, get_transcripts, transcription_status

app = FastAPI(title="Video Interview API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verify_token.router, prefix="/api")
app.include_router(session_start.router, prefix="/api")
app.include_router(upload_one.router, prefix="/api")
app.include_router(session_finish.router, prefix="/api")
app.include_router(get_transcripts.router, prefix="/api")
app.include_router(transcription_status.router, prefix="/api")