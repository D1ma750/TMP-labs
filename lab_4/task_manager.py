# task_manager.py - менеджер задач с улучшенной архитектурой
from typing import List, Optional, Iterator
from datetime import datetime
from task import Task
from storage import TaskStorage, JSONFileStorage


class TaskRepository:
    """Репозиторий для работы с задачами."""

    def __init__(self, storage: TaskStorage = None):
        self.storage = storage or JSONFileStorage()
        self._tasks: List[Task] = self.storage.load()
        self._task_index = {task.id: task for task in self._tasks}

    def add(self, task: Task) -> None:
        """Добавляет новую задачу."""
        self._tasks.append(task)
        self._task_index[task.id] = task
        self._save()

    def get(self, task_id: str) -> Optional[Task]:
        """Получает задачу по ID."""
        return self._task_index.get(task_id)

    def get_all(self) -> List[Task]:
        """Возвращает все задачи."""
        return self._tasks.copy()

    def update(self, task: Task) -> None:
        """Обновляет задачу."""
        if task.id in self._task_index:
            self._task_index[task.id] = task
            for i, t in enumerate(self._tasks):
                if t.id == task.id:
                    self._tasks[i] = task
                    break
            self._save()

    def delete(self, task_id: str) -> bool:
        """Удаляет задачу по ID."""
        if task_id in self._task_index:
            del self._task_index[task_id]
            self._tasks = [t for t in self._tasks if t.id != task_id]
            self._save()
            return True
        return False

    def find_by_title(self, keyword: str) -> Iterator[Task]:
        """Ищет задачи по ключевому слову в заголовке."""
        keyword_lower = keyword.lower()
        return (task for task in self._tasks
                if keyword_lower in task.title.lower())

    def find_by_description(self, keyword: str) -> Iterator[Task]:
        """Ищет задачи по ключевому слову в описании."""
        keyword_lower = keyword.lower()
        return (task for task in self._tasks
                if keyword_lower in task.description.lower())

    def _save(self) -> None:
        """Сохраняет задачи в хранилище."""
        self.storage.save(self._tasks)


class TaskManager:
    """Менеджер задач с бизнес-логикой."""

    def __init__(self, repository: TaskRepository = None):
        self.repository = repository or TaskRepository()

    def create_task(self, title: str, description: str = "",
                    priority: int = 1) -> Task:
        """Создает новую задачу."""
        task = Task(title=title, description=description, priority=priority)
        self.repository.add(task)
        return task

    def complete_task(self, task_id: str) -> bool:
        """Отмечает задачу как выполненную."""
        task = self.repository.get(task_id)
        if task and not task.completed:
            task.complete()
            self.repository.update(task)
            return True
        return False

    def delete_task(self, task_id: str) -> bool:
        """Удаляет задачу."""
        return self.repository.delete(task_id)

    def get_all_tasks(self, sort_by: str = "priority") -> List[Task]:
        """Возвращает все задачи с сортировкой."""
        tasks = self.repository.get_all()

        if sort_by == "priority":
            return sorted(tasks, key=lambda x: (-x.priority, x.created_at))
        elif sort_by == "created":
            return sorted(tasks, key=lambda x: x.created_at)
        elif sort_by == "title":
            return sorted(tasks, key=lambda x: x.title.lower())
        else:
            return tasks

    def get_pending_tasks(self) -> List[Task]:
        """Возвращает незавершенные задачи."""
        return [task for task in self.repository.get_all()
                if not task.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Возвращает завершенные задачи."""
        return [task for task in self.repository.get_all()
                if task.completed]

    def search_tasks(self, keyword: str) -> List[Task]:
        """Ищет задачи по ключевому слову."""
        if not keyword:
            return []

        # Объединяем результаты поиска по заголовку и описанию
        title_results = set(self.repository.find_by_title(keyword))
        desc_results = set(self.repository.find_by_description(keyword))
        return list(title_results.union(desc_results))

    def get_statistics(self) -> dict:
        """Возвращает статистику по задачам."""
        tasks = self.repository.get_all()
        total = len(tasks)
        completed = sum(1 for task in tasks if task.completed)

        return {
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }