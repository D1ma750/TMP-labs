# todo_app_with_logging.py - приложение для управления задачами с логированием

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional


# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    # Создаем логгер
    logger = logging.getLogger('todo_app')
    logger.setLevel(logging.DEBUG)

    # Проверяем, нет ли уже обработчиков (чтобы избежать дублирования)
    if not logger.handlers:
        # Форматтер для логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Обработчик для файла
        file_handler = logging.FileHandler('todo_app.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Добавляем обработчики к логгеру
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# Инициализируем логгер
logger = setup_logging()


class Task:
    def __init__(self, title: str, description: str = "", priority: int = 1):
        logger.debug(f"Создание новой задачи: {title}")
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.priority = priority
        self.created_at = datetime.now()
        self.completed = False
        self.completed_at = None

        logger.info(f"Задача создана: ID={self.id}, название='{title}', приоритет={priority}")

    def _generate_id(self) -> int:
        return int(datetime.now().timestamp() * 1000)

    def complete(self):
        """Отметить задачу как выполненную"""
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now()
            logger.info(f"Задача завершена: ID={self.id}, название='{self.title}'")
        else:
            logger.warning(f"Попытка повторно завершить уже завершенную задачу: ID={self.id}")

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
        logger.debug(f"Десериализация задачи из словаря: ID={data.get('id')}")
        task = Task(data['title'], data['description'], data['priority'])
        task.id = data['id']
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.completed = data['completed']
        if data['completed_at']:
            task.completed_at = datetime.fromisoformat(data['completed_at'])
        return task


class TaskManager:
    def __init__(self, storage_file: str = 'tasks.json'):
        logger.info(f"Инициализация TaskManager с файлом хранения: {storage_file}")
        self.storage_file = storage_file
        self.tasks: List[Task] = []
        self._load_tasks()

    def _load_tasks(self):
        """Загрузка задач из файла"""
        logger.debug(f"Попытка загрузить задачи из файла: {self.storage_file}")
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
                logger.info(f"Успешно загружено {len(self.tasks)} задач из файла")
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON файла {self.storage_file}: {e}")
                self.tasks = []
            except KeyError as e:
                logger.error(f"Отсутствует обязательное поле в данных задачи: {e}")
                self.tasks = []
            except Exception as e:
                logger.error(f"Неожиданная ошибка при загрузке задач: {e}")
                self.tasks = []
        else:
            logger.info(f"Файл {self.storage_file} не найден. Будет создан новый.")
            self.tasks = []

    def _save_tasks(self):
        """Сохранение задач в файл"""
        logger.debug(f"Сохранение {len(self.tasks)} задач в файл")
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2, ensure_ascii=False)
            logger.info(f"Задачи успешно сохранены в файл {self.storage_file}")
        except IOError as e:
            logger.error(f"Ошибка записи в файл {self.storage_file}: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при сохранении задач: {e}")

    def add_task(self, title: str, description: str = "", priority: int = 1) -> Task:
        """Добавление новой задачи"""
        logger.debug(f"Добавление задачи: название='{title}', приоритет={priority}")

        if priority < 1 or priority > 5:
            error_msg = f"Некорректный приоритет: {priority}. Должен быть от 1 до 5"
            logger.error(error_msg)
            raise ValueError(error_msg)

        task = Task(title, description, priority)
        self.tasks.append(task)
        self._save_tasks()

        logger.info(f"Задача успешно добавлена: ID={task.id}, название='{title}'")
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Получение задачи по ID"""
        for task in self.tasks:
            if task.id == task_id:
                logger.debug(f"Задача найдена по ID={task_id}")
                return task

        logger.debug(f"Задача с ID={task_id} не найдена")
        return None

    def complete_task(self, task_id: int) -> bool:
        """Завершение задачи по ID"""
        logger.debug(f"Попытка завершить задачу с ID={task_id}")
        task = self.get_task(task_id)
        if task:
            task.complete()
            self._save_tasks()
            logger.info(f"Задача ID={task_id} успешно завершена")
            return True

        logger.warning(f"Попытка завершить несуществующую задачу с ID={task_id}")
        return False

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи по ID"""
        logger.debug(f"Попытка удалить задачу с ID={task_id}")
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self._save_tasks()
                logger.info(f"Задача ID={task_id} успешно удалена")
                return True

        logger.warning(f"Попытка удалить несуществующую задачу с ID={task_id}")
        return False

    def get_all_tasks(self) -> List[Task]:
        """Получение всех задач"""
        logger.debug(f"Запрос всех задач. Всего задач: {len(self.tasks)}")
        return sorted(self.tasks, key=lambda x: (-x.priority, x.created_at))

    def get_pending_tasks(self) -> List[Task]:
        """Получение активных (незавершенных) задач"""
        pending = [task for task in self.tasks if not task.completed]
        logger.debug(f"Запрос активных задач. Найдено: {len(pending)}")
        return pending

    def get_completed_tasks(self) -> List[Task]:
        """Получение завершенных задач"""
        completed = [task for task in self.tasks if task.completed]
        logger.debug(f"Запрос завершенных задач. Найдено: {len(completed)}")
        return completed

    def search_tasks(self, keyword: str) -> List[Task]:
        """Поиск задач по ключевому слову"""
        logger.debug(f"Поиск задач по ключевому слову: '{keyword}'")
        keyword = keyword.lower()
        results = [task for task in self.tasks
                   if keyword in task.title.lower() or keyword in task.description.lower()]
        logger.info(f"Поиск по '{keyword}' завершен. Найдено задач: {len(results)}")
        return results


class TodoApp:
    def __init__(self):
        logger.info("Запуск TodoApp")
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
        """Отображение всех задач"""
        logger.debug("Отображение всех задач")
        tasks = self.manager.get_all_tasks()
        if not tasks:
            print("Нет задач.")
            logger.info("Показаны все задачи: список пуст")
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

        logger.info(f"Показаны все задачи: всего {len(tasks)} задач")

    def add_task_interactive(self):
        """Интерактивное добавление задачи"""
        logger.debug("Начало процесса добавления задачи")
        print("\n=== Добавление задачи ===")
        title = input("Название задачи: ").strip()

        if not title:
            print("Название не может быть пустым!")
            logger.warning("Попытка добавления задачи с пустым названием")
            return

        description = input("Описание (необязательно): ").strip()

        while True:
            try:
                priority_input = input("Приоритет (1-5, где 5 - самый высокий): ").strip()
                priority = int(priority_input) if priority_input else 1

                if 1 <= priority <= 5:
                    break
                else:
                    print("Приоритет должен быть от 1 до 5!")
                    logger.warning(f"Пользователь ввел недопустимый приоритет: {priority}")
            except ValueError:
                print("Введите число от 1 до 5!")
                logger.warning(f"Пользователь ввел некорректный приоритет: {priority_input}")

        try:
            task = self.manager.add_task(title, description, priority)
            print(f"Задача добавлена с ID: {task.id}")
            logger.info(f"Пользователь добавил новую задачу: ID={task.id}, название='{title}'")
        except ValueError as e:
            print(f"Ошибка: {e}")
            logger.error(f"Ошибка при добавлении задачи: {e}")

    def complete_task_interactive(self):
        """Интерактивное завершение задачи"""
        logger.debug("Начало процесса завершения задачи")
        task_id = self._get_task_id_input("Введите ID задачи для завершения: ")
        if task_id:
            if self.manager.complete_task(task_id):
                print("Задача завершена!")
                logger.info(f"Пользователь завершил задачу с ID={task_id}")
            else:
                print("Задача не найдена!")
                logger.warning(f"Пользователь пытался завершить несуществующую задачу ID={task_id}")

    def delete_task_interactive(self):
        """Интерактивное удаление задачи"""
        logger.debug("Начало процесса удаления задачи")
        task_id = self._get_task_id_input("Введите ID задачи для удаления: ")
        if task_id:
            if self.manager.delete_task(task_id):
                print("Задача удалена!")
                logger.info(f"Пользователь удалил задачу с ID={task_id}")
            else:
                print("Задача не найдена!")
                logger.warning(f"Пользователь пытался удалить несуществующую задачу ID={task_id}")

    def search_tasks_interactive(self):
        """Интерактивный поиск задач"""
        logger.debug("Начало процесса поиска задач")
        keyword = input("Введите слово для поиска: ").strip()
        if not keyword:
            print("Введите ключевое слово для поиска!")
            logger.warning("Попытка поиска с пустым ключевым словом")
            return

        results = self.manager.search_tasks(keyword)
        if results:
            print(f"\n=== Найдено {len(results)} задач ===")
            for i, task in enumerate(results, 1):
                status = "✓" if task.completed else "○"
                print(f"{i}. [{status}] {task.title}")
            logger.info(f"Пользователь искал '{keyword}', найдено {len(results)} задач")
        else:
            print("Задачи не найдены.")
            logger.info(f"Поиск по '{keyword}' не дал результатов")

    def _get_task_id_input(self, prompt: str) -> Optional[int]:
        """Получение ID задачи от пользователя"""
        try:
            input_str = input(prompt).strip()
            task_id = int(input_str)
            logger.debug(f"Пользователь ввел ID задачи: {task_id}")
            return task_id
        except ValueError:
            print("Введите корректный ID (число)!")
            logger.warning(f"Пользователь ввел некорректный ID: '{input_str}'")
            return None

    def run(self):
        """Основной цикл приложения"""
        logger.info("Запуск основного цикла приложения")

        while self.running:
            self.display_menu()
            try:
                choice = input("\nВыберите действие: ").strip()
                logger.debug(f"Пользователь выбрал действие: {choice}")

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
                    logger.debug(f"Показаны активные задачи: {len(tasks)} задач")
                elif choice == '7':
                    tasks = self.manager.get_completed_tasks()
                    print(f"\n=== Завершенные задачи: {len(tasks)} ===")
                    for task in tasks:
                        print(f"- {task.title} (Завершено: {task.completed_at.strftime('%Y-%m-%d %H:%M')})")
                    logger.debug(f"Показаны завершенные задачи: {len(tasks)} задач")
                elif choice == '8':
                    self.running = False
                    print("Выход из приложения...")
                    logger.info("Завершение работы приложения по команде пользователя")
                else:
                    print("Неверный выбор. Попробуйте снова.")
                    logger.warning(f"Пользователь ввел неверный выбор: {choice}")

            except KeyboardInterrupt:
                print("\n\nПринудительный выход...")
                logger.warning("Принудительное завершение работы (KeyboardInterrupt)")
                self.running = False
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                logger.error(f"Неожиданная ошибка в основном цикле: {e}", exc_info=True)

        logger.info("Приложение завершило работу")


if __name__ == "__main__":
    print("=== Todo App с логированием ===")
    print("Логи записываются в файл 'todo_app.log'")
    print("Уровни логирования: DEBUG, INFO, WARNING, ERROR")
    print("=" * 40)

    app = TodoApp()
    app.run()