"""
Script để transcribe tất cả video trong tất cả folders
Sử dụng: python scripts/transcribe_all_folders.py
"""

import os
import sys

# Thêm parent directory vào path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from transcribe_existing_videos import transcribe_folder
from app.storage.file_manager import BASE

def transcribe_all_folders():
    """Transcribe tất cả folders trong uploads"""
    if not os.path.exists(BASE):
        print(f"❌ Thư mục uploads không tồn tại: {BASE}")
        return
    
    folders = [f for f in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, f))]
    
    if not folders:
        print("ℹ️  Không tìm thấy folder nào trong uploads")
        return
    
    print(f"📁 Tìm thấy {len(folders)} folder(s)\n")
    
    for folder_name in folders:
        print(f"{'='*60}")
        transcribe_folder(folder_name)
        print()

if __name__ == '__main__':
    transcribe_all_folders()

