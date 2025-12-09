import os
import tempfile
import subprocess

# Lazy import để không crash nếu module chưa cài
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  whisper package not installed. Local transcription will be disabled.")
    print("   Install with: pip install openai-whisper")

import io

def get_whisper_model(model_size: str = "medium"):
    """
    Load Whisper model (chỉ load 1 lần, cache lại)
    model_size: "tiny", "base", "small", "medium", "large"
    - tiny: ~39M params, fastest, lowest quality
    - base: ~74M params, good balance
    - small: ~244M params, better quality
    - medium: ~769M params, high quality (recommended for best accuracy)
    - large: ~1550M params, best quality, slowest
    """
    if not WHISPER_AVAILABLE:
        return None
    
    # Cache model để không load lại mỗi lần
    if not hasattr(get_whisper_model, '_model_cache'):
        get_whisper_model._model_cache = {}
    
    if model_size not in get_whisper_model._model_cache:
        try:
            print(f"📥 Loading Whisper model: {model_size} (first time only, may take a moment)...")
            model = whisper.load_model(model_size)
            get_whisper_model._model_cache[model_size] = model
            print(f"✅ Whisper model {model_size} loaded successfully!")
        except Exception as e:
            print(f"⚠️  Error loading Whisper model: {e}")
            return None
    
    return get_whisper_model._model_cache[model_size]

def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio từ video file sử dụng ffmpeg
    Returns True nếu thành công, False nếu thất bại
    """
    try:
        # Whisper hỗ trợ nhiều format, dùng MP3 cho đơn giản
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'mp3',  # MP3 codec
            '-ar', '16000',  # Sample rate 16kHz (Whisper recommended)
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

def transcribe_video(video_bytes: bytes, language: str = "en", model_size: str = "medium", translate_to_english: bool = False) -> dict:
    """
    Transcribe video sử dụng Whisper local (MIỄN PHÍ!)
    
    Args:
        video_bytes: Video file bytes (WebM format)
        language: Language code (default: "vi" for Vietnamese)
                  Có thể là: "vi", "en", "ja", "ko", "zh", etc.
                  Hoặc None để auto-detect
        model_size: Model size - "tiny", "base", "small", "medium", "large"
                    Default: "base" (good balance)
    
    Returns:
        dict với keys: 'success', 'transcript', 'confidence', 'error'
    """
    if not WHISPER_AVAILABLE:
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': 'whisper package not installed. Install with: pip install openai-whisper'
        }
    
    # Tạo temporary files
    temp_video = None
    temp_audio = None
    
    try:
        # Load model
        model = get_whisper_model(model_size)
        if not model:
            return {
                'success': False,
                'transcript': '',
                'confidence': 0.0,
                'error': 'Failed to load Whisper model'
            }
        
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
        
        # Transcribe bằng Whisper
        task = "translate" if translate_to_english else "transcribe"
        task_text = "Translating to English" if translate_to_english else "Transcribing"
        print(f"🔄 {task_text} with Whisper {model_size}...")
        
        result = model.transcribe(
            temp_audio,
            language=language if (language and not translate_to_english) else None,  # None = auto-detect, hoặc bỏ qua nếu translate
            task=task,  # "transcribe" hoặc "translate" (translate = translate to English)
            verbose=False,  # Không in progress
            fp16=False,  # Dùng float32 để tương thích tốt hơn (CPU)
            condition_on_previous_text=True,  # Cải thiện độ chính xác với context
            initial_prompt=None,  # Có thể thêm prompt để cải thiện
            word_timestamps=False,  # Không cần word timestamps để nhanh hơn
            temperature=0.0  # Deterministic output, tốt hơn cho transcription
        )
        
        transcript_text = result["text"].strip()
        
        # Whisper không có confidence score trực tiếp
        # Tính average logprob từ TẤT CẢ segments (không chỉ segment đầu)
        segments = result.get("segments", [])
        if segments:
            # Lấy average logprob từ tất cả segments
            logprobs = [seg.get("avg_logprob", -1.0) for seg in segments if "avg_logprob" in seg]
            if logprobs:
                avg_logprob = sum(logprobs) / len(logprobs)
                # Convert logprob to approximate confidence (0-1 scale)
                # logprob thường từ -1.0 (kém) đến 0.0 (tốt)
                # Normalize: (-1.0 -> 0.0), (-0.5 -> 0.5), (0.0 -> 1.0)
                confidence = min(1.0, max(0.0, (avg_logprob + 1.0)))
            else:
                confidence = 0.85  # Default nếu không có logprob
        else:
            confidence = 0.85  # Default nếu không có segments
        
        detected_language = result.get("language", language)
        
        return {
            'success': True,
            'transcript': transcript_text,
            'confidence': confidence,
            'error': None,
            'language': detected_language,
            'model': model_size
        }
        
    except Exception as e:
        error_msg = str(e)
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': f'Transcription error: {error_msg}'
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

