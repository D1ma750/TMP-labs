import math
from scipy.special import gammaincc


def frequency_test(bit_string):
    """
    Частотный тест NIST.
    Проверяет частоту появления нулей и единиц в последовательности.
    :param
    bit_string (str): строка, состоящая из последовательности нулей и единиц.
    :returns
    res: результат теста.
    """
    sums = (bit_string.count("1") - bit_string.count("0")) / math.sqrt(len(bit_string))
    res = math.erfc(abs(sums) / math.sqrt(2))
    return res

def runs_test(bit_string):
    """
    Тест на одинаковые подряд идущие биты.
    Проверяет частоту смены знаков в последовательности.
    :param
    bit_string (str): строка, состоящая из последовательности нулей и единиц.
    :returns
    res: результат теста.
    """
    ones_counts = 0
    for bit in bit_string:
        if bit == "1":
            ones_counts += 1
    ones_counts = ones_counts / len(bit_string)

    if abs(ones_counts - 0.5) >= 2 / math.sqrt(len(bit_string)):
        return 0

    series = 0
    for i in range(len(bit_string) - 1):
        if bit_string[i] != bit_string[i + 1]:
            series += 1

    numerator = abs(series - 2 * len(bit_string) * ones_counts * (1 - ones_counts))
    denominator = 2 * math.sqrt(2 * len(bit_string)) * ones_counts * (1 - ones_counts)
    res = math.erfc(numerator / denominator)
    return res


def longest_run_test(bin_seq, block_size=8):
    """
    Тест на самую длинную последовательность единиц в блоке.
    Проверяет длину самой длинной последовательности единиц в каждом блоке.
    :param
    binary_sequence (str): строка, содержащая последовательность нулей и единиц.
    block_size (int): размер блока (по умолчанию 8).
    :returns
    res: p-значение теста.
    """
    n = len(bin_seq)
    if n % block_size != 0:
        raise ValueError(f"Длина последовательности ({n}) должна быть кратна размеру блока ({block_size})")

    num_blocks = n // block_size

    probabilities = [0.2148, 0.3672, 0.2305, 0.1875]

    category = [0, 0, 0, 0]

    for i in range(num_blocks):
        block = bin_seq[i * block_size: (i + 1) * block_size]
        max_run = 0
        cur_run = 0

        for bit in block:
            if bit == '1':
                cur_run += 1
                max_run = max(max_run, cur_run)
            else:
                cur_run = 0

        if max_run <= 1:
            category[0] += 1
        elif max_run == 2:
            category[1] += 1
        elif max_run == 3:
            category[2] += 1
        else:
            category[3] += 1

    hi_square = sum(
        (category[i] - num_blocks * probabilities[i]) ** 2 / (num_blocks * probabilities[i]) for i in range(4))

    res = gammaincc(1.5, hi_square / 2)

    return res