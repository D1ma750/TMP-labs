import pytest
from nist_test import test_frequency, test_runs, test_longest_run


def test_frequency_balanced_sequence():
    """Test with balanced sequence of zeros and ones"""
    bit_string = "0101010101"
    result = test_frequency(bit_string)
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_frequency_all_ones():
    """Test with sequence containing only ones"""
    bit_string = "1111111111"
    result = test_frequency(bit_string)
    assert isinstance(result, float)
    assert result < 0.05


def test_runs_alternating_sequence():
    """Test with perfectly alternating sequence"""
    bit_string = "0101010101"
    result = test_runs(bit_string)
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_longest_run_valid_sequence():
    """Test with valid sequence that divides evenly into blocks"""
    bit_string = "11001100011100001111" * 4
    result = test_longest_run(bit_string, block_size=8)
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_longest_run_invalid_length():
    """Test with sequence length not divisible by block size"""
    bit_string = "11001100"
    with pytest.raises(ValueError, match="Длина последовательности.*кратна"):
        test_longest_run(bit_string, block_size=3)


@pytest.mark.parametrize("bit_string,expected_type", [
    ("0101010101", float),
    ("1111100000", float),
    ("0000011111", float),
    ("1100110011", float),
    ("1" * 20, float),
    ("0" * 20, float),
])
def test_frequency_parameterized(bit_string, expected_type):
    """Parameterized test for frequency function with various inputs"""
    result = test_frequency(bit_string)
    assert isinstance(result, expected_type)
    assert 0 <= result <= 1


@pytest.mark.parametrize("bit_string,block_size,expected_error", [
    ("11001100", 3, True),
    ("01010101", 8, False),
    ("010101010", 3, False),
    ("01", 2, False),
    ("1" * 16, 4, False),
])
def test_longest_run_comprehensive(bit_string, block_size, expected_error):
    """Comprehensive parameterized test for longest_run with various scenarios"""
    if expected_error:
        with pytest.raises(ValueError):
            test_longest_run(bit_string, block_size)
    else:
        result = test_longest_run(bit_string, block_size)
        assert isinstance(result, float)
        assert 0 <= result <= 1


@pytest.mark.parametrize("sequence_func,test_func", [
    (lambda: "01" * 50, test_frequency),
    (lambda: "1100" * 25, test_runs),
    (lambda: "1" * 80, test_frequency),
    (lambda: "000111000111" * 10, test_runs),
])
def test_multiple_functions_same_sequence(sequence_func, test_func):
    """Test multiple functions with dynamically generated sequences"""
    bit_string = sequence_func()
    result = test_func(bit_string)

    assert isinstance(result, float)
    assert 0 <= result <= 1

    if test_func == test_longest_run:
        adjusted_length = (len(bit_string) // 8) * 8
        if adjusted_length > 0:
            adjusted_bit_string = bit_string[:adjusted_length]
            result = test_longest_run(adjusted_bit_string, block_size=8)
            assert isinstance(result, float)
            assert 0 <= result <= 1