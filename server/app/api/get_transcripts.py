from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from app.storage.file_manager import BASE
import os
import json
import csv
import tempfile

router = APIRouter()

@router.get('/transcripts/{folder_name}')
def get_transcripts(folder_name: str):
    """
    Lấy tất cả transcripts của một session
    
    Args:
        folder_name: Tên folder session (ví dụ: "05_12_2025_00_18_Anhh")
    
    Returns:
        {
            "ok": true,
            "folder": "...",
            "userName": "...",
            "transcripts": {
                "1": {...},
                "2": {...}
            }
        }
    """
    meta_path = os.path.join(BASE, folder_name, 'meta.json')
    
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail=f"Session '{folder_name}' not found")
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        transcripts = meta.get('transcripts', {})
        
        return {
            "ok": True,
            "folder": folder_name,
            "userName": meta.get('userName', 'Unknown'),
            "uploadedAt": meta.get('uploadedAt'),
            "finishedAt": meta.get('finishedAt'),
            "questionsCount": meta.get('questionsCount', 0),
            "receivedQuestions": meta.get('receivedQuestions', []),
            "transcripts": transcripts,
            "transcriptsCount": len(transcripts)
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in meta.json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading metadata: {str(e)}")


@router.get('/transcripts/{folder_name}/{question_index}')
def get_transcript(folder_name: str, question_index: int):
    """
    Lấy transcript của một câu hỏi cụ thể
    
    Args:
        folder_name: Tên folder session
        question_index: Số thứ tự câu hỏi (1, 2, 3, ...)
    
    Returns:
        {
            "ok": true,
            "folder": "...",
            "questionIndex": 1,
            "transcript": {
                "text": "...",
                "confidence": 0.95,
                "createdAt": "..."
            }
        }
    """
    meta_path = os.path.join(BASE, folder_name, 'meta.json')
    
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail=f"Session '{folder_name}' not found")
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        transcripts = meta.get('transcripts', {})
        transcript = transcripts.get(str(question_index))
        
        if not transcript:
            raise HTTPException(
                status_code=404, 
                detail=f"Transcript for question {question_index} not found in session '{folder_name}'"
            )
        
        return {
            "ok": True,
            "folder": folder_name,
            "userName": meta.get('userName', 'Unknown'),
            "questionIndex": question_index,
            "transcript": transcript
        }
    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in meta.json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading metadata: {str(e)}")


@router.get('/transcripts')
def list_all_sessions():
    """
    Liệt kê tất cả sessions có transcripts
    
    Returns:
        {
            "ok": true,
            "sessions": [
                {
                    "folder": "...",
                    "userName": "...",
                    "transcriptsCount": 5,
                    "uploadedAt": "..."
                }
            ]
        }
    """
    if not os.path.exists(BASE):
        return {
            "ok": True,
            "sessions": []
        }
    
    sessions = []
    
    try:
        for folder_name in os.listdir(BASE):
            folder_path = os.path.join(BASE, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            meta_path = os.path.join(folder_path, 'meta.json')
            if not os.path.exists(meta_path):
                continue
            
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                transcripts = meta.get('transcripts', {})
                if transcripts:  # Chỉ thêm sessions có transcripts
                    sessions.append({
                        "folder": folder_name,
                        "userName": meta.get('userName', 'Unknown'),
                        "transcriptsCount": len(transcripts),
                        "questionsCount": meta.get('questionsCount', 0),
                        "uploadedAt": meta.get('uploadedAt'),
                        "finishedAt": meta.get('finishedAt')
                    })
            except:
                continue  # Bỏ qua nếu không đọc được
        
        # Sắp xếp theo uploadedAt (mới nhất trước)
        sessions.sort(key=lambda x: x.get('uploadedAt', ''), reverse=True)
        
        return {
            "ok": True,
            "sessions": sessions,
            "totalSessions": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.get('/transcripts/{folder_name}/export')
def export_transcripts(folder_name: str, format: str = "txt"):
    """
    Export transcripts ra file và download
    
    Args:
        folder_name: Tên folder session
        format: Format file - "txt", "csv", hoặc "json" (default: "txt")
    
    Returns:
        File download
    """
    meta_path = os.path.join(BASE, folder_name, 'meta.json')
    
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail=f"Session '{folder_name}' not found")
    
    if format not in ["txt", "csv", "json"]:
        raise HTTPException(status_code=400, detail="Format must be 'txt', 'csv', or 'json'")
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        transcripts = meta.get('transcripts', {})
        userName = meta.get('userName', folder_name)
        
        if not transcripts:
            raise HTTPException(status_code=404, detail=f"No transcripts found in session '{folder_name}'")
        
        # Tạo temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format}', encoding='utf-8')
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            if format == "txt":
                # Export ra file text
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(f"Interview Transcripts - {userName}\n")
                    f.write(f"Folder: {folder_name}\n")
                    f.write(f"Date: {meta.get('uploadedAt', 'N/A')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for q_idx in sorted(transcripts.keys(), key=int):
                        transcript = transcripts[q_idx]
                        f.write(f"Question {q_idx}:\n")
                        f.write("-" * 60 + "\n")
                        f.write(f"{transcript['text']}\n")
                        f.write(f"\nConfidence: {transcript.get('confidence', 0):.2%}\n")
                        f.write(f"Created: {transcript.get('createdAt', 'N/A')}\n")
                        f.write("\n" + "=" * 60 + "\n\n")
                
                media_type = "text/plain"
            
            elif format == "csv":
                # Export ra file CSV
                with open(temp_path, 'w', newline='', encoding='utf-8') as f:
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
                
                media_type = "text/csv"
            
            elif format == "json":
                # Export ra file JSON
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
                
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                media_type = "application/json"
            
            filename = f"{folder_name}_transcripts.{format}"
            
            return FileResponse(
                temp_path,
                media_type=media_type,
                filename=filename,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        except Exception as e:
            # Cleanup temp file nếu có lỗi
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(status_code=500, detail=f"Error creating export file: {str(e)}")
    
    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in meta.json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting transcripts: {str(e)}")

