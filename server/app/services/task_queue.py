"""
Task Queue for background transcription tracking
Stores status of transcription tasks and allows querying progress
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
import asyncio


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class TranscriptionTask:
    """Single transcription task"""
    question_index: int
    status: TaskStatus = TaskStatus.PENDING
    transcript: str = ""
    confidence: float = 0.0
    error: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class SessionTranscriptionJob:
    """Represents entire session transcription job"""
    folder: str
    questions_count: int
    status: TaskStatus = TaskStatus.PENDING
    tasks: Dict[int, TranscriptionTask] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def get_progress(self) -> tuple[int, int]:
        """Returns (completed, total)"""
        completed = sum(
            1 for t in self.tasks.values()
            if t.status in [TaskStatus.SUCCESS, TaskStatus.FAILED]
        )
        return completed, self.questions_count
    
    def get_success_count(self) -> int:
        """Get number of successfully transcribed videos"""
        return sum(
            1 for t in self.tasks.values()
            if t.status == TaskStatus.SUCCESS
        )
    
    def get_failed_tasks(self) -> List[int]:
        """Get list of failed task indices"""
        return [
            idx for idx, t in self.tasks.items()
            if t.status == TaskStatus.FAILED
        ]
    
    def is_complete(self) -> bool:
        """Check if all tasks are done"""
        return all(
            t.status in [TaskStatus.SUCCESS, TaskStatus.FAILED]
            for t in self.tasks.values()
        )
    
    def to_dict(self):
        return {
            'folder': self.folder,
            'questions_count': self.questions_count,
            'status': self.status.value,
            'progress': self.get_progress(),
            'success_count': self.get_success_count(),
            'failed_count': len(self.get_failed_tasks()),
            'failed_indices': self.get_failed_tasks(),
            'tasks': {
                str(k): {
                    'question_index': v.question_index,
                    'status': v.status.value,
                    'transcript': v.transcript if v.status == TaskStatus.SUCCESS else "",
                    'confidence': v.confidence,
                    'error': v.error,
                    'started_at': v.started_at,
                    'completed_at': v.completed_at,
                }
                for k, v in self.tasks.items()
            },
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
        }


class TaskQueue:
    """Global task queue for managing transcription jobs"""
    
    _instance = None
    _jobs: Dict[str, SessionTranscriptionJob] = {}
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def create_job(self, folder: str, questions_count: int) -> SessionTranscriptionJob:
        """Create new transcription job for session"""
        async with self._lock:
            if folder in self._jobs:
                # Return existing job (in case of retry)
                return self._jobs[folder]
            
            job = SessionTranscriptionJob(
                folder=folder,
                questions_count=questions_count
            )
            
            # Initialize tasks for each question
            for i in range(1, questions_count + 1):
                job.tasks[i] = TranscriptionTask(question_index=i)
            
            self._jobs[folder] = job
            print(f"📋 Created transcription job for {folder}")
            return job
    
    async def get_job(self, folder: str) -> Optional[SessionTranscriptionJob]:
        """Get job by folder"""
        async with self._lock:
            return self._jobs.get(folder)
    
    async def start_job(self, folder: str):
        """Mark job as started"""
        async with self._lock:
            if folder in self._jobs:
                job = self._jobs[folder]
                job.status = TaskStatus.PROCESSING
                job.started_at = datetime.now().isoformat()
                print(f"🚀 Started transcription job for {folder}")
    
    async def update_task(
        self,
        folder: str,
        question_index: int,
        status: TaskStatus,
        transcript: str = "",
        confidence: float = 0.0,
        error: str = ""
    ):
        """Update single task status"""
        async with self._lock:
            if folder not in self._jobs:
                print(f"⚠️  Job not found for {folder}")
                return
            
            job = self._jobs[folder]
            if question_index not in job.tasks:
                print(f"⚠️  Task Q{question_index} not found")
                return
            
            task = job.tasks[question_index]
            task.status = status
            task.transcript = transcript
            task.confidence = confidence
            task.error = error
            
            if status == TaskStatus.PROCESSING and not task.started_at:
                task.started_at = datetime.now().isoformat()
            elif status in [TaskStatus.SUCCESS, TaskStatus.FAILED]:
                task.completed_at = datetime.now().isoformat()
            
            # Check if job is complete
            if job.is_complete() and job.status != TaskStatus.SUCCESS:
                job.status = TaskStatus.SUCCESS if len(job.get_failed_tasks()) == 0 else TaskStatus.FAILED
                job.completed_at = datetime.now().isoformat()
                print(f"✅ Job completed for {folder}")
    
    async def complete_job(self, folder: str):
        """Mark entire job as complete"""
        async with self._lock:
            if folder in self._jobs:
                job = self._jobs[folder]
                job.status = TaskStatus.SUCCESS if len(job.get_failed_tasks()) == 0 else TaskStatus.FAILED
                job.completed_at = datetime.now().isoformat()
                print(f"✅ Completed job for {folder}")
    
    async def get_progress(self, folder: str) -> Optional[Dict]:
        """Get progress of transcription job"""
        async with self._lock:
            if folder not in self._jobs:
                return None
            return self._jobs[folder].to_dict()
    
    async def clear_job(self, folder: str):
        """Clear completed job from memory (keep in DB if needed)"""
        async with self._lock:
            if folder in self._jobs:
                del self._jobs[folder]
                print(f"🗑️  Cleared job for {folder}")


# Global instance
queue = TaskQueue()
