from __future__ import annotations

import pytest

from utils.matrixUtils import pivot_element


def assert_matrix_close(actual: list[list[float]], expected: list[list[float]]) -> None:
    assert len(actual) == len(expected)
    for actual_row, expected_row in zip(actual, expected):
        assert actual_row == pytest.approx(expected_row)


def test_pivot_element_normalizes_pivot_row_and_clears_pivot_column() -> None:
    matrix = [
        [2.0, 1.0, 1.0, 14.0],
        [4.0, 2.0, 3.0, 28.0],
        [2.0, 5.0, 5.0, 30.0],
    ]

    pivot_element(matrix, pivot_row=0, pivot_col=0)

    assert_matrix_close(
        matrix,
        [
            [1.0, 0.5, 0.5, 7.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 4.0, 4.0, 16.0],
        ],
    )


def test_pivot_element_updates_the_received_matrix_in_place() -> None:
    matrix = [
        [3.0, 6.0],
        [9.0, 12.0],
    ]
    same_matrix = matrix

    pivot_element(matrix, pivot_row=0, pivot_col=0)

    assert same_matrix is matrix
    assert_matrix_close(
        same_matrix,
        [
            [1.0, 2.0],
            [0.0, -6.0],
        ],
    )


def test_pivot_element_rejects_zero_pivot() -> None:
    matrix = [
        [0.0, 0.0, 3.0],
        [1.0, 2.0, 4.0],
    ]

    with pytest.raises(AssertionError):
        pivot_element(matrix, pivot_row=0, pivot_col=1)


def test_pivot_element_accepts_values_before_the_pivot_column() -> None:
    matrix = [
        [2.0, 4.0, 2.0],
        [3.0, 6.0, 1.0],
        [1.0, 2.0, 5.0],
    ]

    pivot_element(matrix, pivot_row=1, pivot_col=1)

    assert_matrix_close(
        matrix,
        [
            [0.0, 0.0, 4.0 / 3.0],
            [0.5, 1.0, 1.0 / 6.0],
            [0.0, 0.0, 14.0 / 3.0],
        ],
    )


def test_pivot_element_handles_fractional_values_with_float_tolerance() -> None:
    matrix = [
        [0.3, 1.0, -2.0],
        [0.7, 2.0, 4.0],
    ]

    pivot_element(matrix, pivot_row=0, pivot_col=0)

    assert_matrix_close(
        matrix,
        [
            [1.0, 10.0 / 3.0, -20.0 / 3.0],
            [0.0, -1.0 / 3.0, 26.0 / 3.0],
        ],
    )
