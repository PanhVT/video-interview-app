import os
import tempfile
import subprocess

# Lazy import để không crash nếu module chưa cài
try:
    from google.cloud import speech_v1
    from google.cloud.speech_v1 import types
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False
    print("⚠️  google-cloud-speech not installed. Transcription will be disabled.")

import io

def get_speech_client():
    """Khởi tạo Google Speech-to-Text client"""
    if not GOOGLE_SPEECH_AVAILABLE:
        return None
    
    try:
        # Kiểm tra xem có credentials không
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set or file not found. Transcription will be skipped.")
            return None
        return speech_v1.SpeechClient()
    except Exception as e:
        print(f"⚠️  Error initializing Speech client: {e}")
        return None

def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio từ video file sử dụng ffmpeg
    Returns True nếu thành công, False nếu thất bại
    """
    try:
        # Sử dụng ffmpeg để extract audio (FLAC format cho Google Speech-to-Text)
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'flac',  # FLAC codec
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

def transcribe_video(video_bytes: bytes, language_code: str = "vi-VN", translate_to_english: bool = False) -> dict:
    """
    Transcribe video sử dụng Google Speech-to-Text API
    
    Args:
        video_bytes: Video file bytes (WebM format)
        language_code: Language code (default: vi-VN for Vietnamese)
    
    Returns:
        dict với keys: 'success', 'transcript', 'confidence', 'error'
    """
    if not GOOGLE_SPEECH_AVAILABLE:
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': 'google-cloud-speech module not installed'
        }
    
    client = get_speech_client()
    if not client:
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': 'Failed to initialize Speech client. Please check GOOGLE_APPLICATION_CREDENTIALS.'
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
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.flac').name
        if not extract_audio_from_video(temp_video, temp_audio):
            return {
                'success': False,
                'transcript': '',
                'confidence': 0.0,
                'error': 'Failed to extract audio from video. Make sure ffmpeg is installed and in PATH.'
            }
        
        # Đọc audio file
        with io.open(temp_audio, 'rb') as audio_file:
            audio_content = audio_file.read()
        
        # Cấu hình cho Google Speech-to-Text
        # Nếu translate_to_english, dùng language_code="en-US"
        target_language = "en-US" if translate_to_english else language_code
        
        config = types.RecognitionConfig(
            encoding=types.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=16000,
            language_code=target_language,
            enable_automatic_punctuation=True,
            model='latest_long',  # Sử dụng model tốt nhất cho long-form audio
        )
        
        audio = types.RecognitionAudio(content=audio_content)
        
        # Gọi API
        response = client.recognize(config=config, audio=audio)
        
        # Xử lý kết quả
        transcript_parts = []
        confidence_scores = []
        
        for result in response.results:
            if result.alternatives:
                alternative = result.alternatives[0]
                transcript_parts.append(alternative.transcript)
                confidence_scores.append(alternative.confidence)
        
        full_transcript = ' '.join(transcript_parts)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            'success': True,
            'transcript': full_transcript,
            'confidence': avg_confidence,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': str(e)
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

