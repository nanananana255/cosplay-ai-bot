import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
import time

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class GenerationTask:
    id: str
    image: bytes
    style: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[bytes] = None
    error: Optional[str] = None
    created_at: float = time.time()

class GenerationQueue:
    def __init__(self):
        self.tasks: Dict[str, GenerationTask] = {}
    
    def add_task(self, image: bytes, style: str) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = GenerationTask(
            id=task_id,
            image=image,
            style=style
        )
        return task_id
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.PROCESSING
                return {
                    "id": task.id,
                    "image": task.image,
                    "style": task.style
                }
        return None
    
    def set_result(self, task_id: str, result: bytes):
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].result = result
    
    def set_error(self, task_id: str, error: str):
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.tasks[task_id].error = error
    
    def get_status(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            return {"status": "not_found"}
        
        return {
            "status": task.status.value,
            "result": task.result if task.status == TaskStatus.COMPLETED else None,
            "error": task.error if task.status == TaskStatus.FAILED else None
        }