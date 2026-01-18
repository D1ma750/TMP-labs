#console_ui.py - консольный интерфейс
from typing import List, Optional
from datetime import datetime
from task_manager import TaskManager
from task import Task


class ConsoleUI:
    """Консольный пользовательский интерфейс."""

    def __init__(self, task_manager: TaskManager):
        self.manager = task_manager
        self.running = True
        self.commands = {
            '1': ('Показать все задачи', self.show_all_tasks),
            '2': ('Добавить задачу', self.add_task_interactive),
            '3': ('Завершить задачу', self.complete_task_interactive),
            '4': ('Удалить задачу', self.delete_task_interactive),
            '5': ('Поиск задач', self.search_tasks_interactive),
            '6': ('Показать активные задачи', self.show_pending_tasks),
            '7': ('Показать завершенные задачи', self.show_completed_tasks),
            '8': ('Статистика', self.show_statistics),
            '9': ('Выход', self.exit_app),
        }

    def display_menu(self) -> None:
        """Отображает меню."""
        print("\n" + "=" * 30)
        print("МЕНЕДЖЕР ЗАДАЧ")
        print("=" * 30)

        for key, (description, _) in self.commands.items():
            print(f"{key}. {description}")

    def show_all_tasks(self) -> None:
        """Показывает все задачи."""
        tasks = self.manager.get_all_tasks()

        if not tasks:
            print("\nНет задач.")
            return

        print(f"\n=== ВСЕ ЗАДАЧИ ({len(tasks)}) ===")
        self._print_tasks(tasks)

    def _print_tasks(self, tasks: List[Task]) -> None:
        """Выводит список задач в форматированном виде."""
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.completed else "◯"
            priority_stars = "★" * task.priority

            print(f"\n{i}. [{status}] {task.title} {priority_stars}")
            if task.description:
                print(f"   Описание: {task.description}")

            print(f"   ID: {task.id}")
            print(f"   Создано: {self._format_datetime(task.created_at)}")

            if task.completed:
                print(f"   Завершено: {self._format_datetime(task.completed_at)}")

    def _format_datetime(self, dt: Optional[datetime]) -> str:
        """Форматирует datetime для вывода."""
        if dt is None:
            return "Н/Д"
        return dt.strftime('%d.%m.%Y %H:%M')

    def add_task_interactive(self) -> None:
        """Интерактивное добавление задачи."""
        print("\n=== ДОБАВЛЕНИЕ ЗАДАЧИ ===")

        title = self._get_input("Название задачи", required=True)
        if title is None:
            return

        description = self._get_input("Описание", required=False)

        priority = self._get_priority_input()
        if priority is None:
            return

        try:
            task = self.manager.create_task(title, description, priority)
            print(f"\n✅ Задача добавлена! ID: {task.id}")
        except ValueError as e:
            print(f"\n❌ Ошибка: {e}")

    def complete_task_interactive(self) -> None:
        """Интерактивное завершение задачи."""
        task_id = self._get_task_id_input("Введите ID задачи для завершения")
        if task_id and self.manager.complete_task(task_id):
            print("\n✅ Задача завершена!")
        else:
            print("\n❌ Задача не найдена!")

    def delete_task_interactive(self) -> None:
        """Интерактивное удаление задачи."""
        task_id = self._get_task_id_input("Введите ID задачи для удаления")
        if task_id and self.manager.delete_task(task_id):
            print("\n✅ Задача удалена!")
        else:
            print("\n❌ Задача не найдена!")

    def search_tasks_interactive(self) -> None:
        """Интерактивный поиск задач."""
        keyword = self._get_input("Введите слово для поиска", required=True)
        if keyword is None:
            return

        results = self.manager.search_tasks(keyword)
        if results:
            print(f"\n=== НАЙДЕНО ЗАДАЧ: {len(results)} ===")
            self._print_tasks(results)
        else:
            print("\nЗадачи не найдены.")

    def show_pending_tasks(self) -> None:
        """Показывает незавершенные задачи."""
        tasks = self.manager.get_pending_tasks()
        print(f"\n=== АКТИВНЫЕ ЗАДАЧИ ({len(tasks)}) ===")
        self._print_tasks(tasks)

    def show_completed_tasks(self) -> None:
        """Показывает завершенные задачи."""
        tasks = self.manager.get_completed_tasks()
        print(f"\n=== ЗАВЕРШЕННЫЕ ЗАДАЧИ ({len(tasks)}) ===")
        self._print_tasks(tasks)

    def show_statistics(self) -> None:
        """Показывает статистику."""
        stats = self.manager.get_statistics()
        print("\n=== СТАТИСТИКА ===")
        print(f"Всего задач: {stats['total']}")
        print(f"Завершено: {stats['completed']}")
        print(f"Активных: {stats['pending']}")
        print(f"Процент выполнения: {stats['completion_rate']:.1f}%")

    def exit_app(self) -> None:
        """Завершает работу приложения."""
        self.running = False
        print("\n👋 До свидания!")

    def _get_input(self, prompt: str, required: bool = False) -> Optional[str]:
        """Получает ввод от пользователя."""
        full_prompt = f"{prompt}: "
        if not required and prompt != "Описание":
            full_prompt = f"{prompt} (Enter для пропуска): "

        value = input(full_prompt).strip()

        if required and not value:
            print("❌ Это поле обязательно для заполнения!")
            return None

        return value

    def _get_priority_input(self) -> Optional[int]:
        """Получает приоритет от пользователя."""
        while True:
            try:
                value = input("Приоритет (1-5, где 5 - самый высокий): ").strip()
                if not value:
                    return 1  # Значение по умолчанию

                priority = int(value)
                if 1 <= priority <= 5:
                    return priority
                else:
                    print("❌ Приоритет должен быть от 1 до 5!")
            except ValueError:
                print("❌ Введите число от 1 до 5!")
            except KeyboardInterrupt:
                return None

    def _get_task_id_input(self, prompt: str) -> Optional[str]:
        """Получает ID задачи от пользователя."""
        value = input(f"{prompt}: ").strip()
        if not value:
            print("❌ Введите ID задачи!")
            return None
        return value

    def run(self) -> None:
        """Запускает главный цикл приложения."""
        print("Добро пожаловать в Менеджер Задач!")

        while self.running:
            try:
                self.display_menu()
                choice = input("\nВыберите действие: ").strip()

                if choice in self.commands:
                    _, handler = self.commands[choice]
                    handler()
                else:
                    print("\n❌ Неверный выбор. Попробуйте снова.")

            except KeyboardInterrupt:
                print("\n\n⚠️  Принудительный выход...")
                self.running = False
            except Exception as e:
                print(f"\n❌ Произошла ошибка: {e}")