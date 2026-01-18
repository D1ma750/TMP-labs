# storage.py - абстракция для хранения данных
from abc import ABC, abstractmethod
from typing import List, Optional
import json
import os
from task import Task


class TaskStorage(ABC):
    """Абстрактный класс для хранения задач."""

    @abstractmethod
    def save(self, tasks: List[Task]) -> None:
        """Сохраняет список задач."""
        pass

    @abstractmethod
    def load(self) -> List[Task]:
        """Загружает список задач."""
        pass


class JSONFileStorage(TaskStorage):
    """Реализация хранения задач в JSON файле."""

    def __init__(self, filepath: str = 'tasks.json'):
        self.filepath = filepath

    def save(self, tasks: List[Task]) -> None:
        """Сохраняет задачи в JSON файл."""
        data = [task.to_dict() for task in tasks]
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> List[Task]:
        """Загружает задачи из JSON файла."""
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Task.from_dict(task_data) for task_data in data]
        except (json.JSONDecodeError, KeyError, ValueError):
            # В случае ошибки файла возвращаем пустой список
            return []