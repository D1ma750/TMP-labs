import nist_test
import constants


def read_file(filename: str):
    """
    Читает содержимое файла и возвращает его как строку.
    :param
    filename (str): имя файла для чтения.
    :returns
    str: содержимое файла.
    """
    with open(filename, "r") as file:
        sequence = file.read()
    return sequence


def write_results(frequency_cpp, frequency_java,
                  runs_cpp, runs_java,
                  longest_run_cpp, longest_run_java,
                  results: str):
    """
    Записывает результаты тестов в файл.
    :param
    frequency_cpp (float): результат частотного теста для C++.
    frequency_java (float): результат частотного теста для Java.
    runs_cpp (float): результат теста на одинаковые подряд идущие биты для C++.
    runs_java (float): результат теста на одинаковые подряд идущие биты для Java.
    long_cpp (float): результат теста на самую длинную последовательность единиц в блоке для C++.
    long_java (float): результат теста на самую длинную последовательность единиц в блоке для Java.
    results (str): имя файла для записи результатов.
    """
    with open(results, 'w') as file:
        file.write("Frequency test:\n")
        file.write(f"c++: {frequency_cpp}\n")
        file.write(f"java: {frequency_java}\n\n")

        file.write("A test for identical consecutive bits:\n")
        file.write(f"c++: {runs_cpp}\n")
        file.write(f"java: {runs_java}\n\n")

        file.write("Test for the longest sequence of units in a block:\n")
        file.write(f"c++: {longest_run_cpp}\n")
        file.write(f"java: {longest_run_java}\n")


def main():
    """
    Основная функция программы.
    Выполняет тесты NIST для последовательностей из C++ и Java,
    записывает результаты в файл.
    """
    frequency_cpp = nist_test.test_frequency(read_file(constants.bin_cpp))
    frequency_java = nist_test.test_frequency(read_file(constants.bin_java))
    runs_cpp = nist_test.test_runs(read_file(constants.bin_cpp))
    runs_java = nist_test.test_runs(read_file(constants.bin_java))
    longest_run_cpp = nist_test.test_longest_run(read_file(constants.bin_cpp))
    longest_run_java = nist_test.test_longest_run(read_file(constants.bin_java))
    write_results(frequency_cpp, frequency_java, runs_cpp, runs_java, longest_run_cpp, longest_run_java,
                  constants.result)


if __name__ == "__main__":
    main()
