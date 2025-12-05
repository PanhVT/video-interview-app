"""
Export transcripts ra file text hoặc CSV
Sử dụng: python scripts/export_transcripts.py <folder_name> [--format txt|csv]
Ví dụ: python scripts/export_transcripts.py 05_12_2025_00_18_Anhh --format txt
"""

import os
import sys
import json
import csv

# Thêm parent directory vào path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.storage.file_manager import BASE

def export_transcripts(folder_name: str, format: str = "txt"):
    """Export transcripts ra file"""
    meta_path = os.path.join(BASE, folder_name, 'meta.json')
    
    if not os.path.exists(meta_path):
        print(f"❌ Folder không tồn tại: {folder_name}")
        return
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    transcripts = meta.get('transcripts', {})
    userName = meta.get('userName', folder_name)
    
    if not transcripts:
        print(f"⚠️  Không có transcripts trong folder {folder_name}")
        return
    
    output_dir = os.path.join(BASE, folder_name)
    
    if format == "txt":
        # Export ra file text
        output_file = os.path.join(output_dir, f"{folder_name}_transcripts.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Interview Transcripts - {userName}\n")
            f.write(f"Folder: {folder_name}\n")
            f.write("=" * 60 + "\n\n")
            
            for q_idx in sorted(transcripts.keys(), key=int):
                transcript = transcripts[q_idx]
                f.write(f"Question {q_idx}:\n")
                f.write("-" * 60 + "\n")
                f.write(f"{transcript['text']}\n")
                f.write(f"\nConfidence: {transcript.get('confidence', 0):.2%}\n")
                f.write(f"Created: {transcript.get('createdAt', 'N/A')}\n")
                f.write("\n" + "=" * 60 + "\n\n")
        
        print(f"✅ Đã export transcripts ra: {output_file}")
    
    elif format == "json":
        # Export ra file JSON
        output_file = os.path.join(output_dir, f"{folder_name}_transcripts.json")
        export_data = {
            "userName": userName,
            "folder": folder_name,
            "uploadedAt": meta.get('uploadedAt'),
            "finishedAt": meta.get('finishedAt'),
            "questionsCount": meta.get('questionsCount', 0),
            "transcripts": {}
        }
        
        for q_idx in sorted(transcripts.keys(), key=int):
            export_data["transcripts"][f"Q{q_idx}"] = transcripts[q_idx]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Đã export transcripts ra: {output_file}")
    
    elif format == "csv":
        # Export ra file CSV
        output_file = os.path.join(output_dir, f"{folder_name}_transcripts.csv")
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Question', 'Transcript', 'Confidence', 'Created At'])
            
            for q_idx in sorted(transcripts.keys(), key=int):
                transcript = transcripts[q_idx]
                writer.writerow([
                    f"Q{q_idx}",
                    transcript['text'],
                    f"{transcript.get('confidence', 0):.2%}",
                    transcript.get('createdAt', 'N/A')
                ])
        
        print(f"✅ Đã export transcripts ra: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Thiếu tham số folder_name")
        print()
        print("Sử dụng: python scripts/export_transcripts.py <folder_name> [--format txt|csv|json]")
        print()
        print("Ví dụ:")
        print("  python scripts/export_transcripts.py 05_12_2025_00_18_Anhh")
        print("  python scripts/export_transcripts.py 05_12_2025_00_18_Anhh --format txt")
        print("  python scripts/export_transcripts.py 05_12_2025_00_18_Anhh --format csv")
        print("  python scripts/export_transcripts.py 05_12_2025_00_18_Anhh --format json")
        sys.exit(1)
    
    folder_name = sys.argv[1]
    format = "txt"
    
    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            format = sys.argv[idx + 1]
    
    if format not in ["txt", "csv", "json"]:
        print("❌ Format phải là 'txt', 'csv', hoặc 'json'")
        sys.exit(1)
    
    export_transcripts(folder_name, format)

