import os, json, datetime

# safe uploads base path (relative to project root)
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'uploads'))

def ensure_session_folder(folder):
    path = os.path.join(BASE, folder)
    os.makedirs(path, exist_ok=True)
    meta = {"userName": folder.split('_')[-1], "uploadedAt": None, "timeZone": "Asia/Bangkok", "receivedQuestions": []}
    with open(os.path.join(path, 'meta.json'), 'w') as f:
        json.dump(meta, f)

def save_question_file(folder, index, content_bytes):
    path = os.path.join(BASE, folder)
    if not os.path.exists(path):
        raise FileNotFoundError("Session folder not found")
    fname = os.path.join(path, f"Q{index}.webm")
    with open(fname, 'wb') as f:
        f.write(content_bytes)

def update_metadata(folder, index, transcript=None, confidence=None):
    path = os.path.join(BASE, folder)
    meta_path = os.path.join(path, 'meta.json')
    if not os.path.exists(meta_path):
        return
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    meta['uploadedAt'] = datetime.datetime.now().isoformat()
    if index not in meta.get('receivedQuestions', []):
        meta.setdefault('receivedQuestions', []).append(index)
    
    # Lưu transcript nếu có
    if transcript is not None:
        if 'transcripts' not in meta:
            meta['transcripts'] = {}
        meta['transcripts'][str(index)] = {
            'text': transcript,
            'confidence': confidence,
            'createdAt': datetime.datetime.now().isoformat()
        }
        
        # Tự động tạo file transcripts.txt trong folder uploads
        _create_transcripts_file(folder, meta)
    
    with open(meta_path, 'w') as f:
        json.dump(meta, f)

def _create_transcripts_file(folder, meta):
    """Tạo file transcripts.txt trong folder uploads"""
    try:
        folder_path = os.path.join(BASE, folder)
        transcripts = meta.get('transcripts', {})
        userName = meta.get('userName', folder.split('_')[-1] if '_' in folder else folder)
        
        if not transcripts:
            return
        
        # Tạo file transcripts.txt
        transcripts_file = os.path.join(folder_path, 'transcripts.txt')
        with open(transcripts_file, 'w', encoding='utf-8') as f:
            f.write(f"Interview Transcripts - {userName}\n")
            f.write(f"Folder: {folder}\n")
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
        
    except Exception as e:
        # Không fail nếu không tạo được file transcripts.txt
        print(f"⚠️  Warning: Could not create transcripts.txt: {e}")
