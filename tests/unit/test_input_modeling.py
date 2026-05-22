from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from main import PivotPolicy, parse_arguments
from simplex.models import ConstraintRelation, ProblemType
from simplex.parser import parse_input


MEDIA_INPUT_PATH = Path(__file__).resolve().parents[1] / "media" / "in"


def test_parse_arguments_reads_execution_options() -> None:
    filename = MEDIA_INPUT_PATH / "01"

    with patch.object(
        sys,
        "argv",
        [
            "main.py",
            str(filename),
            "--decimals",
            "3",
            "--digits",
            "7",
            "--policy",
            "bland",
        ],
    ):
        options = parse_arguments()

    assert options.filename == str(filename)
    assert options.decimals == 3
    assert options.digits == 7
    assert options.pivot_policy == PivotPolicy.BLAND
    assert options.format_number(1.2) == "  1.200"


@pytest.mark.parametrize(
    (
        "filename",
        "constraint_count",
        "objective_function",
        "constraint_coefficients",
        "constraint_relations",
        "results",
    ),
    [
        (
            "01",
            3,
            [2.0, 4.0, 8.0],
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            [
                ConstraintRelation.LESS_OR_EQUAL,
                ConstraintRelation.LESS_OR_EQUAL,
                ConstraintRelation.LESS_OR_EQUAL,
            ],
            [1.0, 1.0, 1.0],
        ),
        (
            "02",
            4,
            [1.0, 1.0, 1.0],
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 1.0, 1.0],
            ],
            [
                ConstraintRelation.LESS_OR_EQUAL,
                ConstraintRelation.LESS_OR_EQUAL,
                ConstraintRelation.LESS_OR_EQUAL,
                ConstraintRelation.LESS_OR_EQUAL,
            ],
            [-1.0, -1.0, -1.0, -1.0],
        ),
        (
            "03",
            2,
            [1.0, 0.0, 0.0],
            [
                [-1.0, 1.0, 0.0],
                [-1.0, 0.0, 1.0],
            ],
            [
                ConstraintRelation.LESS_OR_EQUAL,
                ConstraintRelation.LESS_OR_EQUAL,
            ],
            [5.0, 7.0],
        ),
    ],
)
def test_first_input_files_are_parsed_as_linear_program(
    filename: str,
    constraint_count: int,
    objective_function: list[float],
    constraint_coefficients: list[list[float]],
    constraint_relations: list[ConstraintRelation],
    results: list[float],
) -> None:
    raw_input = (MEDIA_INPUT_PATH / filename).read_text(encoding="utf-8")

    linear_program = parse_input(raw_input)

    assert linear_program.decision_variable_count == 3
    assert linear_program.constraint_count == constraint_count
    assert linear_program.decision_variable_signs == [1, 1, 1]
    assert linear_program.problem_type == ProblemType.MAXIMIZATION
    assert linear_program.objective_function == objective_function
    assert [constraint.coefficients for constraint in linear_program.constraints] == (
        constraint_coefficients
    )
    assert [constraint.relation for constraint in linear_program.constraints] == (
        constraint_relations
    )
    assert [constraint.result for constraint in linear_program.constraints] == results
