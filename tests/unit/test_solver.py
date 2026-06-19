from __future__ import annotations

from pathlib import Path

import pytest

from simplex.models import ProblemStatus
from simplex.parser import parse_input
from simplex.solver import run_simplex
from simplex.standard_form import to_standard_form


MEDIA_PATH = Path(__file__).resolve().parents[1] / "media"
MEDIA_INPUT_PATH = MEDIA_PATH / "in"
MEDIA_OUTPUT_PATH = MEDIA_PATH / "out"
MEDIA_CASES = sorted(
    input_path
    for input_path in MEDIA_INPUT_PATH.iterdir()
    if (MEDIA_OUTPUT_PATH / input_path.name).is_file()
)
OUTPUT_STATUS = {
    ProblemStatus.INFEASIBLE: "inviavel",
    ProblemStatus.UNBOUNDED: "ilimitada",
    ProblemStatus.OPTIMAL: "otima",
    ProblemStatus.OPTIMAL_MULTIPLE: "otima",
}


def assert_vector_close(
    actual: list[float],
    expected: list[float],
) -> None:
    assert actual == pytest.approx(expected, rel=0, abs=1e-7)


def solve_media_input(input_path: Path):
    linear_program = parse_input(input_path.read_text(encoding="utf-8"))
    to_standard_form(linear_program)
    return run_simplex(linear_program)


def read_expected_output(input_path: Path) -> list[list[str]]:
    output_path = MEDIA_OUTPUT_PATH / input_path.name
    return [
        line.split()
        for line in output_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.mark.parametrize(
    "input_path",
    MEDIA_CASES,
    ids=lambda input_path: input_path.name,
)
def test_run_simplex_matches_media_output(input_path: Path) -> None:
    expected_lines = read_expected_output(input_path)
    objective, solutions, dual, status = solve_media_input(input_path)

    expected_status = expected_lines[0][0]
    assert OUTPUT_STATUS[status] == expected_status

    if status == ProblemStatus.INFEASIBLE:
        _, expected_certificate = expected_lines
        assert solutions == []
        assert_vector_close(dual[0], [float(value) for value in expected_certificate])
        return

    if status == ProblemStatus.UNBOUNDED:
        _, expected_point, expected_direction = expected_lines
        assert dual == []
        assert_vector_close(solutions[0], [float(value) for value in expected_point])
        assert_vector_close(
            solutions[1],
            [float(value) for value in expected_direction],
        )
        return

    _, expected_objective, expected_solution, expected_dual = expected_lines
    assert objective == pytest.approx(
        float(expected_objective[0]),
        rel=0,
        abs=1e-7,
    )
    assert_vector_close(solutions[0], [float(value) for value in expected_solution])
    assert_vector_close(dual[0], [float(value) for value in expected_dual])


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
