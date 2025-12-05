"""
Centralized Transcription Manager
Handles detection, initialization, and execution of transcription tasks
"""

import os
import inspect
from typing import Optional, Dict, Tuple
import asyncio

# Lazy imports - try to load available transcription engines
TRANSCRIBE_FUNC = None
TRANSCRIBE_ENGINE = None
TRANSCRIBE_AVAILABLE = False


def _init_transcription_engine():
    """Initialize transcription engine once (cached)"""
    global TRANSCRIBE_FUNC, TRANSCRIBE_ENGINE, TRANSCRIBE_AVAILABLE
    
    if TRANSCRIBE_AVAILABLE:
        return  # Already initialized
    
    # Priority: Whisper Local (FREE) > OpenAI API > Google Speech-to-Text
    engines = [
        ('whisper_local_transcription', 'Whisper Local (FREE)'),
        ('openai_transcription', 'OpenAI Whisper API'),
        ('speech_transcription', 'Google Speech-to-Text'),
    ]
    
    for module_name, engine_name in engines:
        try:
            module = __import__(
                f'app.services.{module_name}',
                fromlist=['transcribe_video']
            )
            TRANSCRIBE_FUNC = module.transcribe_video
            TRANSCRIBE_ENGINE = engine_name
            TRANSCRIBE_AVAILABLE = True
            print(f"✅ {engine_name} transcription available")
            return
        except (ImportError, AttributeError):
            continue
        except Exception as e:
            print(f"⚠️  Error loading {engine_name}: {e}")
            continue
    
    print("⚠️  No transcription module available. Transcription will be skipped.")


def is_transcription_available() -> bool:
    """Check if transcription is available"""
    if not TRANSCRIBE_AVAILABLE:
        _init_transcription_engine()
    return TRANSCRIBE_AVAILABLE


def get_transcription_engine() -> str:
    """Get current transcription engine name"""
    if not TRANSCRIBE_AVAILABLE:
        _init_transcription_engine()
    return TRANSCRIBE_ENGINE or "None"


def _get_transcribe_signature() -> Dict[str, bool]:
    """Check transcribe function signature once (cached)"""
    if not hasattr(_get_transcribe_signature, '_signature_cache'):
        sig = inspect.signature(TRANSCRIBE_FUNC)
        _get_transcribe_signature._signature_cache = {
            'has_model_size': 'model_size' in sig.parameters,
            'has_language': 'language' in sig.parameters,
            'has_translate': 'translate_to_english' in sig.parameters,
        }
    return _get_transcribe_signature._signature_cache


async def transcribe_single_video(
    video_bytes: bytes,
    language: str = "vi",
    translate_to_english: bool = False,
    model_size: str = "small"
) -> Dict:
    """
    Transcribe a single video
    
    Args:
        video_bytes: Video file bytes
        language: Language code (vi, en, etc.)
        translate_to_english: Whether to translate to English
        model_size: Model size for Whisper (tiny, base, small, medium, large)
    
    Returns:
        {
            'success': bool,
            'transcript': str,
            'confidence': float,
            'error': str (if failed)
        }
    """
    if not is_transcription_available():
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': 'No transcription engine available'
        }
    
    try:
        sig_info = _get_transcribe_signature()
        
        # Build kwargs based on what function supports
        kwargs = {}
        if sig_info['has_language']:
            kwargs['language'] = language
        if sig_info['has_translate']:
            kwargs['translate_to_english'] = translate_to_english
        if sig_info['has_model_size']:
            kwargs['model_size'] = model_size
        
        # Run transcription in thread pool (non-blocking)
        result = await asyncio.to_thread(
            TRANSCRIBE_FUNC,
            video_bytes,
            **kwargs
        )
        
        return result
    except Exception as e:
        print(f"⚠️  Transcription error: {e}")
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'error': str(e)
        }


async def transcribe_batch_videos(
    video_files: list[Tuple[int, str]],
    language: str = "vi",
    translate_to_english: bool = False,
    model_size: str = "small",
    on_progress=None
) -> Dict[int, Dict]:
    """
    Transcribe multiple videos
    
    Args:
        video_files: List of (question_index, video_path) tuples
        language: Language code
        translate_to_english: Whether to translate
        model_size: Model size for Whisper
        on_progress: Callback function(question_index, success, transcript, error)
    
    Returns:
        {
            1: {'success': True, 'transcript': '...', 'confidence': 0.95},
            2: {'success': False, 'error': 'File not found'},
            ...
        }
    """
    results = {}
    
    for question_index, video_path in video_files:
        try:
            # Check if file exists
            if not os.path.exists(video_path):
                error = f"Video file not found: {video_path}"
                print(f"⚠️  Q{question_index}: {error}")
                results[question_index] = {
                    'success': False,
                    'transcript': '',
                    'confidence': 0.0,
                    'error': error
                }
                if on_progress:
                    await _safe_callback(on_progress, question_index, False, '', error)
                continue
            
            # Read video file
            with open(video_path, 'rb') as f:
                video_bytes = f.read()
            
            # Transcribe
            print(f"🔄 Transcribing Q{question_index}...")
            result = await transcribe_single_video(
                video_bytes,
                language=language,
                translate_to_english=translate_to_english,
                model_size=model_size
            )
            
            results[question_index] = result
            
            if result['success']:
                print(f"✅ Q{question_index} transcribed successfully")
            else:
                print(f"⚠️  Q{question_index} transcription failed: {result.get('error')}")
            
            if on_progress:
                await _safe_callback(
                    on_progress,
                    question_index,
                    result['success'],
                    result.get('transcript', ''),
                    result.get('error', '')
                )
        
        except Exception as e:
            print(f"⚠️  Error processing Q{question_index}: {e}")
            results[question_index] = {
                'success': False,
                'transcript': '',
                'confidence': 0.0,
                'error': str(e)
            }
            if on_progress:
                await _safe_callback(on_progress, question_index, False, '', str(e))
    
    return results


async def _safe_callback(callback, *args):
    """Call callback safely (handle both sync and async)"""
    try:
        if inspect.iscoroutinefunction(callback):
            await callback(*args)
        else:
            callback(*args)
    except Exception as e:
        print(f"⚠️  Callback error: {e}")


# Initialize on import
_init_transcription_engine()
