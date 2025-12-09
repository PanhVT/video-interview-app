from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.storage.metadata_manager import finalize_metadata
from app.services.transcription_manager import (
    is_transcription_available,
    get_transcription_engine,
    transcribe_batch_videos
)
from app.services.task_queue import queue, TaskStatus
from app.storage.file_manager import BASE, update_metadata
import os
import asyncio

router = APIRouter()

class FinishRequest(BaseModel):
    token: str
    folder: str
    questionsCount: int


async def _transcribe_in_background(folder: str, questions_count: int):
    """Background transcription task"""
    try:
        # Create transcription job
        await queue.create_job(folder, questions_count)
        await queue.start_job(folder)
        
        from app.storage.file_manager import BASE
        folder_path = os.path.join(BASE, folder)
        
        # Collect video files
        video_files = []
        for i in range(1, questions_count + 1):
            video_file = os.path.join(folder_path, f"Q{i}.webm")
            video_files.append((i, video_file))
        
        print(f"🔄 Starting transcription for {questions_count} videos in {folder}")
        
        # Transcribe all videos with progress callback
        async def on_progress(question_index, success, transcript, error):
            if success:
                await queue.update_task(
                    folder, question_index, TaskStatus.SUCCESS,
                    transcript=transcript, confidence=0.95
                )
                # Update metadata immediately
                update_metadata(folder, question_index, transcript=transcript, confidence=0.95)
            else:
                await queue.update_task(
                    folder, question_index, TaskStatus.FAILED,
                    error=error
                )
        
        await transcribe_batch_videos(
            video_files,
            language="en",
            translate_to_english=False,
            model_size="medium",
            on_progress=on_progress
        )
        
        # Mark job as complete
        await queue.complete_job(folder)
        print(f"✅ Transcription completed for {folder}")
    
    except Exception as e:
        print(f"⚠️  Transcription background task failed: {e}")
        await queue.complete_job(folder)


@router.post('/session/finish')
async def session_finish(req: FinishRequest):
    """Finish interview session and start background transcription"""
    if req.token != "12345":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Finalize metadata
    finalize_metadata(req.folder, req.questionsCount)
    
    # Start transcription in background (non-blocking)
    if is_transcription_available():
        asyncio.create_task(_transcribe_in_background(req.folder, req.questionsCount))
        return {
            "ok": True,
            "transcribing": True,
            "engine": get_transcription_engine()
        }
    else:
        return {
            "ok": True,
            "transcribing": False,
            "message": "No transcription engine available"
        }