import os
import tempfile
import subprocess

# Lazy import để không crash nếu module chưa cài
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  openai package not installed. Transcription will be disabled.")

import io

def get_openai_client():
    """Khởi tạo OpenAI client"""
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        # Lấy API key từ environment variable
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  OPENAI_API_KEY not set. Transcription will be skipped.")
            return None
        
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"⚠️  Error initializing OpenAI client: {e}")
        return None

def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio từ video file sử dụng ffmpeg
    Returns True nếu thành công, False nếu thất bại
    """
    try:
        # Sử dụng ffmpeg để extract audio (MP3 format cho OpenAI Whisper)
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'mp3',  # MP3 codec
            '-ar', '16000',  # Sample rate 16kHz
            '-ac', '1',  # Mono channel
            '-y',  # Overwrite output file
            output_audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"⚠️  FFmpeg error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠️  FFmpeg not found. Please install FFmpeg and add it to PATH.")
        return False
    except Exception as e:
        print(f"⚠️  Error extracting audio: {e}")
        return False

def transcribe_video(video_bytes: bytes, language: str = "vi", translate_to_english: bool = False) -> dict:
    """
    Transcribe video sử dụng OpenAI Whisper API
    
    Args:
        video_bytes: Video file bytes (WebM format)
        language: Language code (default: "vi" for Vietnamese)
                   Có thể là: "vi", "en", "ja", "ko", "zh", etc.
                   Hoặc None để auto-detect
    
    Returns:
        dict với keys: 'success', 'transcript', 'confidence', 'error'
    """
    if not OPENAI_AVAILABLE:
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': 'openai package not installed'
        }
    
    client = get_openai_client()
    if not client:
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': 'Failed to initialize OpenAI client. Please check OPENAI_API_KEY.'
        }
    
    # Tạo temporary files
    temp_video = None
    temp_audio = None
    
    try:
        # Lưu video vào temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as f:
            f.write(video_bytes)
            temp_video = f.name
        
        # Extract audio từ video
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        if not extract_audio_from_video(temp_video, temp_audio):
            return {
                'success': False,
                'transcript': '',
                'confidence': 0.0,
                'error': 'Failed to extract audio from video. Make sure ffmpeg is installed and in PATH.'
            }
        
        # Đọc audio file
        with open(temp_audio, 'rb') as audio_file:
            audio_content = audio_file.read()
        
        # Gọi OpenAI Whisper API
        # OpenAI Whisper API yêu cầu file object hoặc file path
        audio_file_obj = io.BytesIO(audio_content)
        audio_file_obj.name = "audio.mp3"  # Cần set name cho API
        
        # Gọi OpenAI Whisper API
        if translate_to_english:
            # Translate to English
            response = client.audio.translations.create(
                model="whisper-1",
                file=audio_file_obj,
                response_format="verbose_json"
            )
        else:
            # Transcribe in original language
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_obj,
                language=language if language else None,  # None = auto-detect
                response_format="verbose_json"  # Để lấy thêm thông tin như confidence
            )
        
        # Xử lý kết quả
        transcript_text = response.text
        
        # OpenAI Whisper không trả về confidence score trực tiếp
        # Nhưng có thể dùng các metrics khác nếu có
        confidence = 1.0  # Whisper không có confidence score, set default
        
        return {
            'success': True,
            'transcript': transcript_text,
            'confidence': confidence,
            'error': None,
            'language': getattr(response, 'language', language)  # Language detected
        }
        
    except Exception as e:
        error_msg = str(e)
        # Xử lý các lỗi phổ biến
        if "rate_limit" in error_msg.lower():
            error_msg = "OpenAI API rate limit exceeded. Please try again later."
        elif "insufficient_quota" in error_msg.lower():
            error_msg = "OpenAI API quota exceeded. Please check your billing."
        elif "invalid_api_key" in error_msg.lower():
            error_msg = "Invalid OpenAI API key. Please check OPENAI_API_KEY."
        
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': error_msg
        }
    finally:
        # Cleanup temp files
        if temp_video and os.path.exists(temp_video):
            try:
                os.unlink(temp_video)
            except:
                pass
        if temp_audio and os.path.exists(temp_audio):
            try:
                os.unlink(temp_audio)
            except:
                pass

