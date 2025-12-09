import os
import tempfile
import subprocess

# Lazy import to avoid crash if module is not installed
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
    Load Whisper model (loads once and caches for subsequent calls).
    model_size: "tiny", "base", "small", "medium", "large"
    - tiny: ~39M params, fastest, lowest quality
    - base: ~74M params, good balance
    - small: ~244M params, better quality
    - medium: ~769M params, high quality (recommended for best accuracy)
    - large: ~1550M params, best quality, slowest
    """
    if not WHISPER_AVAILABLE:
        return None
    
    # Cache model to avoid reloading on every call
    if not hasattr(get_whisper_model, '_model_cache'):
        get_whisper_model._model_cache = {}
    
    if model_size not in get_whisper_model._model_cache:
        try:
            print(f"📥 Loading Whisper model: {model_size} (first time only, may take a moment)...")
            model = whisper.load_model(model_size)
            # Log some internals of the loaded model to help debug model selection
            try:
                device = getattr(model, 'device', None)
                dims = getattr(model, 'dims', None)
                print(f"ℹ️  Loaded Whisper model object: type={type(model)}, device={device}, dims={dims}")
            except Exception:
                # If introspection fails, continue silently
                pass
            get_whisper_model._model_cache[model_size] = model
            print(f"✅ Whisper model {model_size} loaded successfully!")
        except Exception as e:
            print(f"⚠️  Error loading Whisper model: {e}")
            return None
    
    return get_whisper_model._model_cache[model_size]

def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio from video file using ffmpeg.
    Returns True on success, False on failure.
    """
    try:
        # Whisper supports many formats; using MP3 for simplicity
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
    Transcribe video using Whisper local (FREE!).

    Args:
        video_bytes: Video file bytes (WebM format)
        language: Language code (default: "en" for English)
                  Can be: "vi", "en", "ja", "ko", "zh", etc.
                  Or None to auto-detect
        model_size: Model size - "tiny", "base", "small", "medium", "large"
                    Default: "medium" (recommended for best accuracy)

    Returns:
        dict with keys: 'success', 'transcript', 'confidence', 'error'
    """
    if not WHISPER_AVAILABLE:
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': 'whisper package not installed. Install with: pip install openai-whisper'
        }
    
    # Create temporary files
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
        
        # Write video bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as f:
            f.write(video_bytes)
            temp_video = f.name
        
        # Extract audio from video
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        if not extract_audio_from_video(temp_video, temp_audio):
            return {
                'success': False,
                'transcript': '',
                'confidence': 0.0,
                'error': 'Failed to extract audio from video. Make sure ffmpeg is installed and in PATH.'
            }
        
        # Transcribe using Whisper
        task = "translate" if translate_to_english else "transcribe"
        task_text = "Translating to English" if translate_to_english else "Transcribing"
        print(f"🔄 {task_text} with Whisper {model_size}...")

        result = model.transcribe(
            temp_audio,
            language=language if (language and not translate_to_english) else None,  # None = auto-detect, or skip if translating
            task=task,  # "transcribe" or "translate" (translate = translate to English)
            verbose=False,  # Do not print progress
            fp16=False,  # Use float32 for better CPU compatibility
            condition_on_previous_text=True,  # Improves accuracy with context
            initial_prompt=None,  # Can be added to improve results
            word_timestamps=False,  # Not needed; saves time
            temperature=0.0  # Deterministic output, better for transcription
        )
        
        transcript_text = result["text"].strip()

        # Whisper does not provide direct confidence scores
        # Calculate average logprob from ALL segments (not just the first)
        segments = result.get("segments", [])
        if segments:
            # Get average logprob from all segments
            logprobs = [seg.get("avg_logprob", -1.0) for seg in segments if "avg_logprob" in seg]
            if logprobs:
                avg_logprob = sum(logprobs) / len(logprobs)
                # Convert logprob to approximate confidence (0-1 scale)
                # logprob typically ranges from -1.0 (poor) to 0.0 (good)
                # Normalize: (-1.0 -> 0.0), (-0.5 -> 0.5), (0.0 -> 1.0)
                confidence = min(1.0, max(0.0, (avg_logprob + 1.0)))
            else:
                confidence = 0.85  # Default if no logprob available
        else:
            confidence = 0.85  # Default if no segments
        
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
        # Clean up temporary files
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

