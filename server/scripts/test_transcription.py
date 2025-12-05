"""
Script test transcription với một video file
Sử dụng: python scripts/test_transcription.py <video_path>
Ví dụ: python scripts/test_transcription.py ../uploads/05_12_2025_00_18_Anhh/Q1.webm
"""

import os
import sys
import time

# Thêm parent directory vào path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import transcription function (tự động chọn service có sẵn)
TRANSCRIBE_FUNC = None
SERVICE_NAME = "Unknown"

# Ưu tiên: Whisper Local > OpenAI API > Google
try:
    from app.services.whisper_local_transcription import transcribe_video
    TRANSCRIBE_FUNC = transcribe_video
    SERVICE_NAME = "Whisper Local (FREE)"
except ImportError:
    try:
        from app.services.openai_transcription import transcribe_video
        TRANSCRIBE_FUNC = transcribe_video
        SERVICE_NAME = "OpenAI Whisper API"
    except ImportError:
        try:
            from app.services.speech_transcription import transcribe_video
            TRANSCRIBE_FUNC = transcribe_video
            SERVICE_NAME = "Google Speech-to-Text"
        except ImportError:
            print("❌ No transcription service available!")
            print("Please install one of:")
            print("  - openai-whisper (FREE, recommended)")
            print("  - openai (for API)")
            print("  - google-cloud-speech")
            sys.exit(1)

def test_transcription(video_path: str):
    """Test transcription với một video file"""
    
    if not os.path.exists(video_path):
        print(f"❌ Video file không tồn tại: {video_path}")
        return
    
    print(f"📹 Video file: {video_path}")
    print(f"🔧 Service: {SERVICE_NAME}")
    print(f"📊 File size: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")
    print()
    
    # Đọc video file
    print("📖 Đang đọc video file...")
    with open(video_path, 'rb') as f:
        video_bytes = f.read()
    
    print(f"✅ Đã đọc {len(video_bytes) / 1024 / 1024:.2f} MB")
    print()
    
    # Transcribe
    print("🔄 Đang transcribe (có thể mất vài phút)...")
    start_time = time.time()
    
    # Parse arguments
    translate_to_en = "--translate" in sys.argv or "-t" in sys.argv
    model_size = "medium"  # Default - dùng medium cho chất lượng tốt nhất
    
    # Check for model size argument
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model_size = sys.argv[idx + 1]
    
    try:
        # Check if function supports model_size parameter
        import inspect
        sig = inspect.signature(transcribe_video)
        if "model_size" in sig.parameters:
            result = transcribe_video(video_bytes, language="vi", translate_to_english=translate_to_en, model_size=model_size)
        else:
            result = transcribe_video(video_bytes, language="vi", translate_to_english=translate_to_en)
        
        elapsed_time = time.time() - start_time
        
        print()
        print("=" * 60)
        print("📝 KẾT QUẢ TRANSCRIPTION")
        print("=" * 60)
        
        if result.get('success'):
            transcript = result.get('transcript', '')
            confidence = result.get('confidence', 0.0)
            language = result.get('language', 'N/A')
            
            print(f"✅ Status: Thành công")
            print(f"⏱️  Thời gian: {elapsed_time:.2f} giây")
            print(f"🌐 Language: {language}")
            print(f"📊 Confidence: {confidence:.2%}")
            print()
            print("📄 Transcript:")
            print("-" * 60)
            print(transcript)
            print("-" * 60)
            print()
            print(f"📏 Độ dài: {len(transcript)} ký tự")
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ Status: Thất bại")
            print(f"⏱️  Thời gian: {elapsed_time:.2f} giây")
            print(f"❌ Error: {error}")
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print()
        print("=" * 60)
        print("❌ LỖI")
        print("=" * 60)
        print(f"⏱️  Thời gian: {elapsed_time:.2f} giây")
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Thiếu tham số video_path")
        print()
        print("Sử dụng: python scripts/test_transcription.py <video_path> [--translate|-t]")
        print()
        print("Ví dụ:")
        print("  python scripts/test_transcription.py uploads/05_12_2025_00_18_Anhh/Q1.webm")
        print("  python scripts/test_transcription.py uploads/05_12_2025_00_18_Anhh/Q1.webm --translate")
        print("  python scripts/test_transcription.py uploads/05_12_2025_00_18_Anhh/Q1.webm -t")
        print()
        print("Options:")
        print("  --translate, -t    Translate to English instead of transcribing")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Convert relative path to absolute
    if not os.path.isabs(video_path):
        # Nếu là relative path, tính từ server directory
        server_dir = os.path.join(os.path.dirname(__file__), '..')
        video_path = os.path.abspath(os.path.join(server_dir, video_path))
    
    test_transcription(video_path)

