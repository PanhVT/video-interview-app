"""
Ví dụ implementation an toàn cho upload_one với Speech-to-Text
Sử dụng lazy import và error handling để không crash server
"""

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from app.storage.file_manager import save_question_file, update_metadata
import asyncio

router = APIRouter()

# Optional import - không crash nếu module chưa có
SPEECH_AVAILABLE = False
try:
    from app.services.speech_transcription import transcribe_video
    SPEECH_AVAILABLE = True
except ImportError:
    # Module chưa được cài hoặc chưa tồn tại
    print("⚠️  Speech transcription module not available. Upload will work without transcription.")
except Exception as e:
    # Lỗi khác khi import
    print(f"⚠️  Error importing speech module: {e}. Upload will work without transcription.")


@router.post('/upload-one')
async def upload_one(token: str = Form(...), folder: str = Form(...), questionIndex: str = Form(...), video: UploadFile = File(...)):
    if token != "12345":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    contents = await video.read()
    save_question_file(folder, int(questionIndex), contents)
    
    # Chỉ transcribe nếu module available
    transcript_result = None
    if SPEECH_AVAILABLE:
        try:
            # Chạy transcription trong thread pool để không block event loop
            transcript_result = await asyncio.to_thread(transcribe_video, contents)
            
            if transcript_result and transcript_result.get('success'):
                update_metadata(
                    folder, 
                    int(questionIndex), 
                    transcript=transcript_result.get('transcript'),
                    confidence=transcript_result.get('confidence')
                )
            else:
                # Log error nhưng không fail upload
                error_msg = transcript_result.get('error', 'Unknown error') if transcript_result else 'No result'
                print(f"⚠️  Transcription failed for Q{questionIndex}: {error_msg}")
                # Update metadata không có transcript
                update_metadata(folder, int(questionIndex))
        except Exception as e:
            # Nếu transcription fail, vẫn cho phép upload thành công
            print(f"⚠️  Transcription error: {e}")
            transcript_result = {'success': False, 'error': str(e)}
            update_metadata(folder, int(questionIndex))
    else:
        # Module không available, chỉ update metadata bình thường
        update_metadata(folder, int(questionIndex))
    
    response = {
        "ok": True, 
        "savedAs": f"Q{questionIndex}.webm"
    }
    
    # Thêm transcript vào response nếu có
    if transcript_result and transcript_result.get('success'):
        response['transcript'] = transcript_result.get('transcript')
        response['confidence'] = transcript_result.get('confidence')
    
    return response



