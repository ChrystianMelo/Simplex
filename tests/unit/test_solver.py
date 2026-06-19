from __future__ import annotations

from pathlib import Path

import pytest

from simplex.models import ProblemStatus
from simplex.parser import parse_input
from simplex.solver import run_simplex
from simplex.standard_form import to_standard_form


MEDIA_INPUT_PATH = Path(__file__).resolve().parents[1] / "media" / "in"


def assert_matrix_close(
    actual: list[list[float]],
    expected: list[list[float]],
) -> None:
    assert len(actual) == len(expected)
    for actual_row, expected_row in zip(actual, expected):
        assert actual_row == pytest.approx(expected_row)


def solve_media_input(filename: str):
    linear_program = parse_input(
        (MEDIA_INPUT_PATH / filename).read_text(encoding="utf-8")
    )
    to_standard_form(linear_program)
    return run_simplex(linear_program)


def test_run_simplex_finds_optimal_primal_and_dual_solutions() -> None:
    objective, solutions, dual, status = solve_media_input("01")

    assert status == ProblemStatus.OPTIMAL
    assert objective == pytest.approx(14.0)
    assert_matrix_close(solutions, [[1.0, 1.0, 1.0]])
    assert_matrix_close(dual, [[2.0, 4.0, 8.0]])


def test_run_simplex_returns_infeasibility_certificate() -> None:
    _, solutions, certificate, status = solve_media_input("02")

    assert status == ProblemStatus.INFEASIBLE
    assert solutions == []
    assert_matrix_close(certificate, [[1.0, 1.0, 1.0, 1.0]])


def test_run_simplex_returns_unbounded_point_and_direction() -> None:
    objective, solutions, dual, status = solve_media_input("03")

    assert status == ProblemStatus.UNBOUNDED
    assert objective == float("inf")
    assert_matrix_close(
        solutions,
        [
            [0.0, 5.0, 7.0],
            [1.0, 1.0, 1.0],
        ],
    )
    assert dual == []


def test_run_simplex_handles_negative_right_hand_sides() -> None:
    objective, solutions, dual, status = solve_media_input("04")

    assert status == ProblemStatus.OPTIMAL_MULTIPLE
    assert objective == pytest.approx(50.0)
    assert solutions[0] == pytest.approx([0.0, 0.0, 10.0, 0.0])
    assert_matrix_close(dual, [[0.0, 0.0, 5.0, 0.0]])


def test_run_simplex_restores_minimization_objective() -> None:
    linear_program = parse_input(
        """\
1
1
1
min 1
1 >= 2
"""
    )
    to_standard_form(linear_program)

    objective, solutions, _, status = run_simplex(linear_program)

    assert status == ProblemStatus.OPTIMAL
    assert objective == pytest.approx(2.0)
    assert solutions == [[2.0]]


def test_run_simplex_deduplicates_free_variable_representations() -> None:
    linear_program = parse_input(
        """\
1
1
0
max 1
1 == 2
"""
    )
    to_standard_form(linear_program)

    objective, solutions, _, status = run_simplex(linear_program)

    assert status == ProblemStatus.OPTIMAL
    assert objective == pytest.approx(2.0)
    assert solutions == [[2.0]]
