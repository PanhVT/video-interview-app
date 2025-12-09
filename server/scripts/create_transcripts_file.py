"""
Create `transcripts.txt` files for folders that have transcripts in `meta.json`.

Usage: `python scripts/create_transcripts_file.py [folder_name]`
If `folder_name` is not provided, the script will process all folders.
"""

import os
import sys
import json

# Add parent directory to path so local modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.storage.file_manager import BASE

def create_transcripts_file(folder_path, meta):
    """Create `transcripts.txt` in the given folder."""
    try:
        transcripts = meta.get('transcripts', {})
        userName = meta.get('userName', 'Unknown')
        folder_name = os.path.basename(folder_path)
        
        if not transcripts:
            return False
        
        # Write transcripts.txt
        transcripts_file = os.path.join(folder_path, 'transcripts.txt')
        with open(transcripts_file, 'w', encoding='utf-8') as f:
            f.write(f"Interview Transcripts - {userName}\n")
            f.write(f"Folder: {folder_name}\n")
            f.write(f"Date: {meta.get('uploadedAt', 'N/A')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Sort by question index
            for q_idx in sorted(transcripts.keys(), key=int):
                transcript_data = transcripts[q_idx]
                f.write(f"Question {q_idx}:\n")
                f.write("-" * 60 + "\n")
                f.write(f"{transcript_data['text']}\n")
                f.write(f"\nConfidence: {transcript_data.get('confidence', 0):.2%}\n")
                f.write(f"Created: {transcript_data.get('createdAt', 'N/A')}\n")
                f.write("\n" + "=" * 60 + "\n\n")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error creating transcripts.txt for {os.path.basename(folder_path)}: {e}")
        return False

def process_folder(folder_name):
    """Process a specific folder."""
    folder_path = os.path.join(BASE, folder_name)
    meta_path = os.path.join(folder_path, 'meta.json')
    
    if not os.path.exists(meta_path):
        print(f"❌ meta.json not found: {folder_name}")
        return False
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        transcripts = meta.get('transcripts', {})
        if not transcripts:
            print(f"⚠️  Folder {folder_name} has no transcripts")
            return False
        
        if create_transcripts_file(folder_path, meta):
            print(f"✅ Created transcripts.txt for folder: {folder_name}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error processing {folder_name}: {e}")
        return False

def process_all_folders():
    """Process all folders under uploads base directory."""
    if not os.path.exists(BASE):
        print(f"❌ Uploads directory not found: {BASE}")
        return
    
    folders = [f for f in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, f))]
    
    if not folders:
        print("ℹ️  No folders found in uploads")
        return
    
    print(f"📁 Found {len(folders)} folder(s)\n")
    
    success_count = 0
    for folder_name in folders:
        print(f"{'='*60}")
        if process_folder(folder_name):
            success_count += 1
        print()
    
    print(f"✅ Done! Created transcripts.txt for {success_count}/{len(folders)} folder(s)")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Xử lý một folder cụ thể
        folder_name = sys.argv[1]
        process_folder(folder_name)
    else:
        # Xử lý tất cả folders
        process_all_folders()

