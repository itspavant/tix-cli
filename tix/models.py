from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Task:
    """Task model with all necessary properties"""
    id: int
    text: str
    priority: str = 'medium'
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)  

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'text': self.text,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'tags': self.tags,
            'attachments': self.attachments,
            'links': self.links,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create task from dictionary (handles old tasks safely)"""
        return cls(
            id=data['id'],
            text=data['text'],
            priority=data.get('priority', 'medium'),
            completed=data.get('completed', False),
            created_at=data.get('created_at', datetime.now().isoformat()),
            completed_at=data.get('completed_at'),
            tags=data.get('tags', []),
            attachments=data.get('attachments', []),  
            links=data.get('links', [])               
        )

    def mark_done(self):
        """Mark task as completed with timestamp"""
        self.completed = True
        self.completed_at = datetime.now().isoformat()

    def add_tag(self, tag: str):
        """Add a tag to the task"""
        if tag not in self.tags:
            self.tags.append(tag)
    

@dataclass
class Context:
    """Context model for managing separate workspaces"""
    name: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    description: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert context to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'created_at': self.created_at,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create context from dictionary"""
        return cls(**data)
    
    