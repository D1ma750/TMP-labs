# main.py - точка входа в приложение
from task_manager import TaskManager
from console_ui import ConsoleUI


def main():
    """Точка входа в приложение."""
    try:
        manager = TaskManager()

        ui = ConsoleUI(manager)

        ui.run()

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())