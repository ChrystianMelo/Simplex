from __future__ import annotations

from simplex.models import (
    ConstraintRelation,
    LinearProgram,
    ProblemType,
    StandardFormLinearProgram,
)


def to_standard_form(problem: LinearProgram) -> StandardFormLinearProgram:
    objective_function = problem.objective_function[:]
    if problem.problem_type == ProblemType.MINIMIZATION:
        objective_function = [-value for value in objective_function]

    constraint_matrix: list[list[float]] = []
    for constraint in problem.constraints:
        constraint_matrix.append(constraint.coefficients[:])

    standard_objective_function: list[float] = []
    standard_constraint_matrix: list[list[float]] = [
        [] for _ in range(problem.constraint_count)
    ]
    variable_sources: list[tuple[int, float]] = []

    for column, sign in enumerate(problem.decision_variable_signs):
        if sign == 1:
            scales = [1.0]
        elif sign == -1:
            scales = [-1.0]
        elif sign == 0:
            scales = [1.0, -1.0]
        else:
            raise ValueError("Sinal de variavel deve ser -1, 0 ou 1.")

        for scale in scales:
            standard_objective_function.append(objective_function[column] * scale)
            variable_sources.append((column, scale))
            for row in range(problem.constraint_count):
                standard_constraint_matrix[row].append(
                    constraint_matrix[row][column] * scale
                )

    constraint_relations = []
    results = []
    for row, constraint in enumerate(problem.constraints):
        if constraint.relation == ConstraintRelation.GREATER_OR_EQUAL:
            standard_constraint_matrix[row] = [
                -value for value in standard_constraint_matrix[row]
            ]
            constraint_relations.append(ConstraintRelation.LESS_OR_EQUAL)
            results.append(-constraint.result)
        else:
            constraint_relations.append(constraint.relation)
            results.append(constraint.result)

    return StandardFormLinearProgram(
        decision_variable_count=len(standard_objective_function),
        constraint_count=problem.constraint_count,
        objective_function=standard_objective_function,
        constraint_matrix=standard_constraint_matrix,
        constraint_relations=constraint_relations,
        results=results,
        variable_sources=variable_sources,
    )
