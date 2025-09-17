import json
from pathlib import Path
from typing import List, Optional
from tix.models import Task


class TaskStorage:
    """JSON-based storage for tasks"""

    def __init__(self, storage_path: Path = None):
        """Initialize storage with default or custom path"""
        self.storage_path = storage_path or (Path.home() / ".tix" / "tasks.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()

    def _ensure_file(self):
        """Ensure storage file exists"""
        if not self.storage_path.exists():
            self.storage_path.write_text('[]')

    def load_tasks(self) -> List[Task]:
        """Load all tasks from storage"""
        try:
            data = json.loads(self.storage_path.read_text())
            return [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_tasks(self, tasks: List[Task]):
        """Save all tasks to storage"""
        data = [task.to_dict() for task in tasks]
        self.storage_path.write_text(json.dumps(data, indent=2))

    def add_task(self, text: str, priority: str = 'medium', tags: List[str] = None) -> Task:
        """Add a new task and return it"""
        tasks = self.load_tasks()
        new_id = max([t.id for t in tasks], default=0) + 1
        new_task = Task(id=new_id, text=text, priority=priority, tags=tags or [])
        tasks.append(new_task)
        self.save_tasks(tasks)
        return new_task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID"""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task: Task):
        """Update an existing task"""
        tasks = self.load_tasks()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                self.save_tasks(tasks)
                return

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID, return True if deleted"""
        tasks = self.load_tasks()
        original_count = len(tasks)
        tasks = [t for t in tasks if t.id != task_id]
        if len(tasks) < original_count:
            self.save_tasks(tasks)
            return True
        return False

    def get_active_tasks(self) -> List[Task]:
        """Get all incomplete tasks"""
        return [t for t in self.load_tasks() if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [t for t in self.load_tasks() if t.completed]