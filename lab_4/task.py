# task.py - отдельный файл для модели задачи
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class Task:
    """Модель задачи."""
    title: str
    description: str = ""
    priority: int = 1
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if not 1 <= self.priority <= 5:
            raise ValueError("Priority must be between 1 and 5")

    @property
    def is_overdue(self) -> bool:
        """Проверяет, просрочена ли задача (заглушка для будущей функциональности)."""
        return False

    def complete(self) -> None:
        """Отмечает задачу как выполненную."""
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует задачу в словарь для сериализации."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Создает задачу из словаря."""
        task = cls(
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            id=data['id']
        )
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.completed = data['completed']
        if data['completed_at']:
            task.completed_at = datetime.fromisoformat(data['completed_at'])
        return task