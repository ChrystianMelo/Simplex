from __future__ import annotations

from simplex.models import (
    Constraint,
    ConstraintRelation,
    DecisionVariableSign,
    LinearProgram,
    ProblemType,
)
from simplex.standard_form import to_standard_form


def standardize(linear_program: LinearProgram) -> LinearProgram:
    standard_form = to_standard_form(linear_program)
    return linear_program if standard_form is None else standard_form


def assert_all_variables_are_non_negative(linear_program: LinearProgram) -> None:
    assert linear_program.decision_variable_signs == [
        DecisionVariableSign.POSITIVE
    ] * linear_program.decision_variable_count


def assert_all_constraints_are_equalities(linear_program: LinearProgram) -> None:
    assert [constraint.relation for constraint in linear_program.constraints] == [
        ConstraintRelation.EQUAL
    ] * linear_program.constraint_count


def test_to_standard_form_converts_minimization_to_maximization() -> None:
    linear_program = LinearProgram(
        decision_variable_count=2,
        constraint_count=1,
        decision_variable_signs=[
            DecisionVariableSign.POSITIVE,
            DecisionVariableSign.POSITIVE,
        ],
        problem_type=ProblemType.MINIMIZATION,
        objective_function=[3.0, -4.0],
        constraints=[
            Constraint(
                coefficients=[1.0, 2.0],
                relation=ConstraintRelation.EQUAL,
                result=5.0,
            )
        ],
    )

    standard_form = standardize(linear_program)

    assert standard_form.problem_type == ProblemType.MAXIMIZATION
    assert standard_form.objective_function == [-3.0, 4.0]
    assert standard_form.decision_variable_count == 2
    assert [constraint.coefficients for constraint in standard_form.constraints] == [
        [1.0, 2.0]
    ]
    assert_all_variables_are_non_negative(standard_form)
    assert_all_constraints_are_equalities(standard_form)


def test_to_standard_form_adds_slack_variables_to_less_or_equal_constraints() -> None:
    linear_program = LinearProgram(
        decision_variable_count=2,
        constraint_count=2,
        decision_variable_signs=[
            DecisionVariableSign.POSITIVE,
            DecisionVariableSign.POSITIVE,
        ],
        problem_type=ProblemType.MAXIMIZATION,
        objective_function=[5.0, 7.0],
        constraints=[
            Constraint(
                coefficients=[2.0, 1.0],
                relation=ConstraintRelation.LESS_OR_EQUAL,
                result=8.0,
            ),
            Constraint(
                coefficients=[-1.0, 3.0],
                relation=ConstraintRelation.LESS_OR_EQUAL,
                result=6.0,
            ),
        ],
    )

    standard_form = standardize(linear_program)

    assert standard_form.decision_variable_count == 4
    assert standard_form.objective_function == [5.0, 7.0, 0.0, 0.0]
    assert [constraint.coefficients for constraint in standard_form.constraints] == [
        [2.0, 1.0, 1.0, 0.0],
        [-1.0, 3.0, 0.0, 1.0],
    ]
    assert [constraint.result for constraint in standard_form.constraints] == [8.0, 6.0]
    assert_all_variables_are_non_negative(standard_form)
    assert_all_constraints_are_equalities(standard_form)


def test_to_standard_form_adds_surplus_variables() -> None:
    linear_program = LinearProgram(
        decision_variable_count=2,
        constraint_count=2,
        decision_variable_signs=[
            DecisionVariableSign.POSITIVE,
            DecisionVariableSign.POSITIVE,
        ],
        problem_type=ProblemType.MAXIMIZATION,
        objective_function=[1.0, 4.0],
        constraints=[
            Constraint(
                coefficients=[3.0, 2.0],
                relation=ConstraintRelation.GREATER_OR_EQUAL,
                result=12.0,
            ),
            Constraint(
                coefficients=[1.0, -1.0],
                relation=ConstraintRelation.EQUAL,
                result=2.0,
            ),
        ],
    )

    standard_form = standardize(linear_program)

    assert standard_form.decision_variable_count == 3
    assert standard_form.objective_function == [1.0, 4.0, 0.0]
    assert [constraint.coefficients for constraint in standard_form.constraints] == [
        [3.0, 2.0, -1.0],
        [1.0, -1.0, 0.0],
    ]
    assert [constraint.result for constraint in standard_form.constraints] == [
        12.0,
        2.0,
    ]
    assert_all_variables_are_non_negative(standard_form)
    assert_all_constraints_are_equalities(standard_form)


def test_to_standard_form_flips_negative_decision_variable_columns() -> None:
    linear_program = LinearProgram(
        decision_variable_count=2,
        constraint_count=2,
        decision_variable_signs=[
            DecisionVariableSign.POSITIVE,
            DecisionVariableSign.NEGATIVE,
        ],
        problem_type=ProblemType.MAXIMIZATION,
        objective_function=[2.0, -5.0],
        constraints=[
            Constraint(
                coefficients=[3.0, 4.0],
                relation=ConstraintRelation.EQUAL,
                result=7.0,
            ),
            Constraint(
                coefficients=[-1.0, -2.0],
                relation=ConstraintRelation.EQUAL,
                result=-3.0,
            ),
        ],
    )

    standard_form = standardize(linear_program)

    assert standard_form.decision_variable_count == 2
    assert standard_form.objective_function == [2.0, 5.0]
    assert [constraint.coefficients for constraint in standard_form.constraints] == [
        [3.0, -4.0],
        [-1.0, 2.0],
    ]
    assert [constraint.result for constraint in standard_form.constraints] == [
        7.0,
        -3.0,
    ]
    assert_all_variables_are_non_negative(standard_form)
    assert_all_constraints_are_equalities(standard_form)


def test_to_standard_form_splits_free_decision_variables() -> None:
    linear_program = LinearProgram(
        decision_variable_count=2,
        constraint_count=1,
        decision_variable_signs=[
            DecisionVariableSign.POSITIVE,
            DecisionVariableSign.FREE,
        ],
        problem_type=ProblemType.MAXIMIZATION,
        objective_function=[1.0, 3.0],
        constraints=[
            Constraint(
                coefficients=[2.0, -4.0],
                relation=ConstraintRelation.EQUAL,
                result=8.0,
            )
        ],
    )

    standard_form = standardize(linear_program)

    assert standard_form.decision_variable_count == 3
    assert standard_form.objective_function == [1.0, 3.0, -3.0]
    assert [constraint.coefficients for constraint in standard_form.constraints] == [
        [2.0, -4.0, 4.0]
    ]
    assert [constraint.result for constraint in standard_form.constraints] == [8.0]
    assert_all_variables_are_non_negative(standard_form)
    assert_all_constraints_are_equalities(standard_form)
