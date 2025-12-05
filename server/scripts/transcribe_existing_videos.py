"""
Script để transcribe các video đã upload trước đó
Sử dụng: python scripts/transcribe_existing_videos.py <folder_name>
Ví dụ: python scripts/transcribe_existing_videos.py 05_12_2025_00_18_Anhh
"""

import os
import sys
import json
import datetime

# Thêm parent directory vào path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Ưu tiên: Whisper Local (MIỄN PHÍ) > OpenAI API > Google
try:
    from app.services.whisper_local_transcription import transcribe_video
    print("✅ Using Whisper Local for transcription (FREE!)")
except ImportError:
    try:
        from app.services.openai_transcription import transcribe_video
        print("✅ Using OpenAI Whisper API for transcription")
    except ImportError:
        try:
            from app.services.speech_transcription import transcribe_video
            print("✅ Using Google Speech-to-Text for transcription")
        except ImportError:
            print("❌ No transcription service available!")
            print("Please install one of:")
            print("  - openai-whisper (FREE, recommended)")
            print("  - openai (for API)")
            print("  - google-cloud-speech")
            sys.exit(1)
from app.storage.file_manager import BASE

def transcribe_folder(folder_name: str):
    """Transcribe tất cả video trong folder và cập nhật meta.json"""
    folder_path = os.path.join(BASE, folder_name)
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder không tồn tại: {folder_path}")
        return
    
    meta_path = os.path.join(folder_path, 'meta.json')
    if not os.path.exists(meta_path):
        print(f"❌ meta.json không tồn tại: {meta_path}")
        return
    
    # Đọc meta.json
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    # Lấy danh sách questions đã upload
    received_questions = meta.get('receivedQuestions', [])
    
    if not received_questions:
        print(f"⚠️  Không có video nào trong folder {folder_name}")
        return
    
    print(f"📁 Đang xử lý folder: {folder_name}")
    print(f"📹 Tìm thấy {len(received_questions)} video(s): {received_questions}\n")
    
    transcripts = meta.get('transcripts', {})
    updated = False
    
    # Transcribe từng video
    for question_index in received_questions:
        video_file = os.path.join(folder_path, f"Q{question_index}.webm")
        
        if not os.path.exists(video_file):
            print(f"⚠️  Video Q{question_index}.webm không tồn tại, bỏ qua...")
            continue
        
        # Kiểm tra xem đã có transcript chưa
        if str(question_index) in transcripts:
            print(f"✓ Q{question_index} đã có transcript, bỏ qua...")
            continue
        
        print(f"🔄 Đang transcribe Q{question_index}...")
        
        try:
            # Đọc video file
            with open(video_file, 'rb') as f:
                video_bytes = f.read()
            
            # Transcribe (translate sang tiếng Anh)
            # Dùng model "medium" cho chất lượng tốt nhất
            # Để transcribe tiếng Việt, đổi translate_to_english=False
            import inspect
            sig = inspect.signature(transcribe_video)
            if "model_size" in sig.parameters:
                result = transcribe_video(video_bytes, language="vi", translate_to_english=True, model_size="medium")
            else:
                result = transcribe_video(video_bytes, language="vi", translate_to_english=True)
            
            if result.get('success'):
                transcript_text = result.get('transcript', '')
                confidence = result.get('confidence', 0.0)
                
                # Cập nhật transcripts trong meta
                if 'transcripts' not in meta:
                    meta['transcripts'] = {}
                
                meta['transcripts'][str(question_index)] = {
                    'text': transcript_text,
                    'confidence': confidence,
                    'createdAt': datetime.datetime.now().isoformat()
                }
                
                updated = True
                print(f"✅ Q{question_index} - Transcript: {transcript_text[:100]}...")
                print(f"   Confidence: {confidence:.2%}\n")
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ Q{question_index} - Lỗi: {error}\n")
                
        except Exception as e:
            print(f"❌ Q{question_index} - Exception: {e}\n")
    
    # Lưu meta.json nếu có cập nhật
    if updated:
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        print(f"✅ Đã cập nhật meta.json với transcripts!")
        
        # Tạo file transcripts.txt trong folder
        _create_transcripts_file(folder_path, meta)
    else:
        print("ℹ️  Không có transcript mới nào được thêm.")

def _create_transcripts_file(folder_path, meta):
    """Tạo file transcripts.txt trong folder uploads"""
    try:
        transcripts = meta.get('transcripts', {})
        userName = meta.get('userName', 'Unknown')
        folder_name = os.path.basename(folder_path)
        
        if not transcripts:
            return
        
        # Tạo file transcripts.txt
        transcripts_file = os.path.join(folder_path, 'transcripts.txt')
        with open(transcripts_file, 'w', encoding='utf-8') as f:
            f.write(f"Interview Transcripts - {userName}\n")
            f.write(f"Folder: {folder_name}\n")
            f.write(f"Date: {meta.get('uploadedAt', 'N/A')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Sắp xếp theo thứ tự câu hỏi
            for q_idx in sorted(transcripts.keys(), key=int):
                transcript_data = transcripts[q_idx]
                f.write(f"Question {q_idx}:\n")
                f.write("-" * 60 + "\n")
                f.write(f"{transcript_data['text']}\n")
                f.write(f"\nConfidence: {transcript_data.get('confidence', 0):.2%}\n")
                f.write(f"Created: {transcript_data.get('createdAt', 'N/A')}\n")
                f.write("\n" + "=" * 60 + "\n\n")
        
        print(f"✅ Đã tạo file transcripts.txt trong folder!")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not create transcripts.txt: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Thiếu tham số folder_name")
        print("Sử dụng: python scripts/transcribe_existing_videos.py <folder_name>")
        print("Ví dụ: python scripts/transcribe_existing_videos.py 05_12_2025_00_18_Anhh")
        sys.exit(1)
    
    folder_name = sys.argv[1]
    transcribe_folder(folder_name)

