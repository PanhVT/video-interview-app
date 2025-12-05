from fastapi import APIRouter, HTTPException
from app.services.task_queue import queue

router = APIRouter()


@router.get('/transcription-status/{folder_name}')
async def get_transcription_status(folder_name: str):
    """
    Get transcription progress for a session
    
    Returns:
    {
        "ok": true,
        "folder": "05_12_2025_00_18_Anhh",
        "status": "processing" | "success" | "failed" | "pending",
        "progress": [3, 5],  # [completed, total]
        "success_count": 3,
        "failed_count": 0,
        "failed_indices": [],
        "tasks": {
            "1": {"status": "success", "transcript": "...", "confidence": 0.95, "error": ""},
            "2": {"status": "processing", ...},
            "3": {"status": "failed", "error": "File not found", ...},
        },
        "timestamps": {
            "created_at": "2025-12-05T00:18:00",
            "started_at": "2025-12-05T00:20:00",
            "completed_at": "2025-12-05T00:25:00"
        }
    }
    """
    progress = await queue.get_progress(folder_name)
    
    if progress is None:
        raise HTTPException(
            status_code=404,
            detail=f"No transcription job found for folder '{folder_name}'"
        )
    
    return {
        "ok": True,
        "folder": folder_name,
        "status": progress["status"],
        "progress": progress["progress"],
        "success_count": progress["success_count"],
        "failed_count": progress["failed_count"],
        "failed_indices": progress["failed_indices"],
        "questions_count": progress["questions_count"],
        "tasks": progress["tasks"],
        "timestamps": {
            "created_at": progress["created_at"],
            "started_at": progress["started_at"],
            "completed_at": progress["completed_at"],
        }
    }
