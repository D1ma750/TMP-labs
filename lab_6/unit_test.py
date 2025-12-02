import pytest
from nist_test import frequency_test, runs_test, longest_run_test


def test_frequency_balanced_sequence():
    """Test with balanced sequence of zeros and ones"""
    bit_string = "0101010101"
    result = frequency_test(bit_string)
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_frequency_all_ones():
    """Test with sequence containing only ones"""
    bit_string = "1111111111"
    result = frequency_test(bit_string)
    assert isinstance(result, float)
    assert result < 0.05


def test_runs_alternating_sequence():
    """Test with perfectly alternating sequence"""
    bit_string = "0101010101"
    result = runs_test(bit_string)
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_longest_run_valid_sequence():
    """Test with valid sequence that divides evenly into blocks"""
    bit_string = "11001100011100001111" * 4
    result = longest_run_test(bit_string, block_size=8)
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_longest_run_invalid_length():
    """Test with sequence length not divisible by block size"""
    bit_string = "11001100"
    with pytest.raises(ValueError, match="Длина последовательности.*кратна"):
        longest_run_test(bit_string, block_size=3)


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
    result = frequency_test(bit_string)
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
            longest_run_test(bit_string, block_size)
    else:
        result = longest_run_test(bit_string, block_size)
        assert isinstance(result, float)
        assert 0 <= result <= 1


@pytest.mark.parametrize("sequence_func,test_func", [
    (lambda: "01" * 50, frequency_test),
    (lambda: "1100" * 25, runs_test),
    (lambda: "1" * 80, frequency_test),
    (lambda: "000111000111" * 10, runs_test),
])
def test_multiple_functions_same_sequence(sequence_func, test_func):
    """Test multiple functions with dynamically generated sequences"""
    bit_string = sequence_func()
    result = test_func(bit_string)

    assert isinstance(result, float)
    assert 0 <= result <= 1

    if test_func == longest_run_test:
        adjusted_length = (len(bit_string) // 8) * 8
        if adjusted_length > 0:
            adjusted_bit_string = bit_string[:adjusted_length]
            result = longest_run_test(adjusted_bit_string, block_size=8)
            assert isinstance(result, float)
            assert 0 <= result <= 1