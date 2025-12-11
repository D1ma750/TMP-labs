# todo_app.py - приложение для управления задачами

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Task:
    def __init__(self, title: str, description: str = "", priority: int = 1):
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.priority = priority
        self.created_at = datetime.now()
        self.completed = False
        self.completed_at = None

    def _generate_id(self) -> int:
        return int(datetime.now().timestamp() * 1000)

    def complete(self):
        self.completed = True
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        task = Task(data['title'], data['description'], data['priority'])
        task.id = data['id']
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.completed = data['completed']
        if data['completed_at']:
            task.completed_at = datetime.fromisoformat(data['completed_at'])
        return task


class TaskManager:
    def __init__(self, storage_file: str = 'tasks.json'):
        self.storage_file = storage_file
        self.tasks: List[Task] = []
        self._load_tasks()

    def _load_tasks(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
                except (json.JSONDecodeError, KeyError):
                    self.tasks = []
        else:
            self.tasks = []

    def _save_tasks(self):
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2, ensure_ascii=False)

    def add_task(self, title: str, description: str = "", priority: int = 1) -> Task:
        if priority < 1 or priority > 5:
            raise ValueError("Priority must be between 1 and 5")

        task = Task(title, description, priority)
        self.tasks.append(task)
        self._save_tasks()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def complete_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if task:
            task.complete()
            self._save_tasks()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self._save_tasks()
                return True
        return False

    def get_all_tasks(self) -> List[Task]:
        return sorted(self.tasks, key=lambda x: (-x.priority, x.created_at))

    def get_pending_tasks(self) -> List[Task]:
        return [task for task in self.tasks if not task.completed]

    def get_completed_tasks(self) -> List[Task]:
        return [task for task in self.tasks if task.completed]

    def search_tasks(self, keyword: str) -> List[Task]:
        keyword = keyword.lower()
        return [task for task in self.tasks
                if keyword in task.title.lower() or keyword in task.description.lower()]


class TodoApp:
    def __init__(self):
        self.manager = TaskManager()
        self.running = True

    def display_menu(self):
        print("\n=== Менеджер задач ===")
        print("1. Показать все задачи")
        print("2. Добавить задачу")
        print("3. Завершить задачу")
        print("4. Удалить задачу")
        print("5. Поиск задач")
        print("6. Показать активные задачи")
        print("7. Показать завершенные задачи")
        print("8. Выход")

    def show_all_tasks(self):
        tasks = self.manager.get_all_tasks()
        if not tasks:
            print("Нет задач.")
            return

        print("\n=== Все задачи ===")
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.completed else "○"
            print(f"{i}. [{status}] {task.title} (Приоритет: {task.priority})")
            if task.description:
                print(f"   Описание: {task.description}")
            print(f"   Создано: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
            if task.completed:
                print(f"   Завершено: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")
            print()

    def add_task_interactive(self):
        print("\n=== Добавление задачи ===")
        title = input("Название задачи: ").strip()
        if not title:
            print("Название не может быть пустым!")
            return

        description = input("Описание (необязательно): ").strip()

        while True:
            try:
                priority = int(input("Приоритет (1-5, где 5 - самый высокий): ").strip())
                if 1 <= priority <= 5:
                    break
                else:
                    print("Приоритет должен быть от 1 до 5!")
            except ValueError:
                print("Введите число от 1 до 5!")

        try:
            task = self.manager.add_task(title, description, priority)
            print(f"Задача добавлена с ID: {task.id}")
        except ValueError as e:
            print(f"Ошибка: {e}")

    def complete_task_interactive(self):
        task_id = self._get_task_id_input("Введите ID задачи для завершения: ")
        if task_id:
            if self.manager.complete_task(task_id):
                print("Задача завершена!")
            else:
                print("Задача не найдена!")

    def delete_task_interactive(self):
        task_id = self._get_task_id_input("Введите ID задачи для удаления: ")
        if task_id:
            if self.manager.delete_task(task_id):
                print("Задача удалена!")
            else:
                print("Задача не найдена!")

    def search_tasks_interactive(self):
        keyword = input("Введите слово для поиска: ").strip()
        if not keyword:
            print("Введите ключевое слово для поиска!")
            return

        results = self.manager.search_tasks(keyword)
        if results:
            print(f"\n=== Найдено {len(results)} задач ===")
            for i, task in enumerate(results, 1):
                status = "✓" if task.completed else "○"
                print(f"{i}. [{status}] {task.title}")
        else:
            print("Задачи не найдены.")

    def _get_task_id_input(self, prompt: str) -> Optional[int]:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Введите корректный ID (число)!")
            return None

    def run(self):
        while self.running:
            self.display_menu()
            try:
                choice = input("\nВыберите действие: ").strip()

                if choice == '1':
                    self.show_all_tasks()
                elif choice == '2':
                    self.add_task_interactive()
                elif choice == '3':
                    self.complete_task_interactive()
                elif choice == '4':
                    self.delete_task_interactive()
                elif choice == '5':
                    self.search_tasks_interactive()
                elif choice == '6':
                    tasks = self.manager.get_pending_tasks()
                    print(f"\n=== Активные задачи: {len(tasks)} ===")
                    for task in tasks:
                        print(f"- {task.title} (Приоритет: {task.priority})")
                elif choice == '7':
                    tasks = self.manager.get_completed_tasks()
                    print(f"\n=== Завершенные задачи: {len(tasks)} ===")
                    for task in tasks:
                        print(f"- {task.title} (Завершено: {task.completed_at.strftime('%Y-%m-%d %H:%M')})")
                elif choice == '8':
                    self.running = False
                    print("Выход из приложения...")
                else:
                    print("Неверный выбор. Попробуйте снова.")
            except KeyboardInterrupt:
                print("\n\nПринудительный выход...")
                self.running = False
            except Exception as e:
                print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    app = TodoApp()
    app.run()