import csv
import re
import json
from checksum import calculate_checksum, serialize_result

CSV_FILE_PATH = "4.csv"
VARIANT_NUMBER = 4


def load_patterns():
    """Загрузка regex из JSON файла"""
    with open("regular.json", "r", encoding="utf-8") as f:
        return json.load(f)


def validate_row(row_data: dict, patterns: dict) -> bool:
    """
    Проверяет соответствие полей и их регулярных выражений.
    """
    for key, value in row_data.items():
        if key in patterns and not re.fullmatch(patterns[key], str(value).strip()):
            return False
    return True


def main():
    """
    Основная функция: читает CSV-файл, валидирует строки и считает контрольную сумму.
    """
    # Загружаем regex
    REGEX_PATTERNS = load_patterns()

    invalid_rows_indices = []

    try:
        with open(CSV_FILE_PATH, "r", encoding="utf-16") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=";")
            for i, row in enumerate(reader):
                if not validate_row(row, REGEX_PATTERNS):
                    invalid_rows_indices.append(i)

    except FileNotFoundError:
        print(f"Ошибка: Файл '{CSV_FILE_PATH}' не найден.")
        return
    except Exception as e:
        print(f"Произошла ошибка при чтении или обработке файла: {e}")
        return

    checksum = calculate_checksum(invalid_rows_indices)

    print(f"Найдено невалидных строк: {len(invalid_rows_indices)}")
    print(f"Контрольная сумма: {checksum}")

    # Сохраняем результат
    serialize_result(VARIANT_NUMBER, checksum)
    print(f"Результат успешно записан в файл 'result.json'")


if __name__ == "__main__":
    main()