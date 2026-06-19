from __future__ import annotations

from pathlib import Path

import pytest

from simplex.models import ProblemStatus
from simplex.parser import parse_input
from simplex.solver import (
    SimplexTraceEvent,
    find_negative_index,
    find_pivot_row,
    run_simplex,
)
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


def test_find_negative_index_implements_all_pivot_policies() -> None:
    reduced_costs = [-2.0, -5.0, -1.0, -5.0]

    assert find_negative_index(reduced_costs, "largest") == 1
    assert find_negative_index(reduced_costs, "smallest") == 2
    assert find_negative_index(reduced_costs, "bland") == 0


def test_find_pivot_row_uses_bland_to_break_minimum_ratio_ties() -> None:
    matrix = [
        [0.0, 0.0],
        [1.0, 2.0],
        [2.0, 4.0],
    ]

    pivot_row = find_pivot_row(
        matrix,
        pivot_col=0,
        start_row=1,
        end_row=2,
        basis=[8, 3],
    )

    assert pivot_row == 2


@pytest.mark.parametrize("policy", ["largest", "bland", "smallest"])
def test_run_simplex_terminates_on_degenerate_cycling_example(
    policy: str,
) -> None:
    linear_program = parse_input(
        """\
4
3
1 1 1 1
max 10 -57 -9 -24
0.5 -5.5 -2.5 9 <= 0
0.5 -1.5 -0.5 1 <= 0
1 0 0 0 <= 1
"""
    )
    to_standard_form(linear_program)

    objective, solutions, _, status = run_simplex(linear_program, policy)

    assert status == ProblemStatus.OPTIMAL
    assert objective == pytest.approx(1.0)
    assert solutions[0] == pytest.approx([1.0, 0.0, 1.0, 0.0])


def test_run_simplex_reports_two_distinct_multiple_optima() -> None:
    linear_program = parse_input(
        """\
2
3
1 1
max 1 1
1 1 <= 1
1 0 <= 1
0 1 <= 1
"""
    )
    to_standard_form(linear_program)

    objective, solutions, _, status = run_simplex(linear_program, "bland")

    assert status == ProblemStatus.OPTIMAL_MULTIPLE
    assert objective == pytest.approx(1.0)
    assert len(solutions) == 2
    assert solutions[0] != solutions[1]


def test_trace_contains_both_phases_and_alternate_optimum_pivot() -> None:
    linear_program = parse_input(
        """\
2
3
1 1
max 1 1
1 1 <= 1
1 0 <= 1
0 1 <= 1
"""
    )
    to_standard_form(linear_program)
    events: list[SimplexTraceEvent] = []

    run_simplex(linear_program, "bland", trace_callback=events.append)

    assert {event.phase for event in events} == {
        "Fase I (PL auxiliar)",
        "Fase II (PL original)",
    }
    assert any(event.action == "Pivoteamento" for event in events)
    assert any(
        event.action == "Pivoteamento para solucao otima alternativa"
        for event in events
    )
    assert all(event.column_labels[-1] == "b" for event in events)
