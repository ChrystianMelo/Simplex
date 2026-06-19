from __future__ import annotations

from simplex.models import (
    DecisionVariableSign,
    LinearProgram,
    ProblemStatus,
    ProblemType,
)
from utils.matrixUtils import pivot_element

MatrixPosition = tuple[int, int]
TOLERANCE = 1e-9


def find_negative_index(
    row_slice: list[float],
    pivot_policy: str = "bland",
    tol: float = TOLERANCE,
) -> int:
    """Retorna o índice de um custo reduzido negativo ou -1."""
    negative_indices = [
        index for index, coefficient in enumerate(row_slice)
        if coefficient < -tol
    ]

    if not negative_indices:
        return -1

    if pivot_policy == "largest":
        return min(negative_indices, key=lambda index: row_slice[index])
    if pivot_policy == "smallest":
        return max(negative_indices, key=lambda index: row_slice[index])

    return negative_indices[0]


def is_one_row(
    matrix: list[list[float]],
    column: int,
    tol: float = TOLERANCE,
) -> bool:
    one_count = 0

    for row in matrix:
        value = row[column]

        if abs(value - 1.0) <= tol:
            one_count += 1
        elif abs(value) > tol:
            return False

    return one_count == 1


def extract_solution(
    combined_matrix: list[list[float]],
    variable_start_col: int,
    variable_count: int,
    constraint_start_row: int,
    constraint_end_row: int,
    basis: list[int] | None = None,
    tol: float = TOLERANCE,
) -> list[float]:
    solution = [0.0] * variable_count

    if basis is not None:
        for basis_index, basic_col in enumerate(basis):
            variable_index = basic_col - variable_start_col
            if 0 <= variable_index < variable_count:
                row = constraint_start_row + basis_index
                solution[variable_index] = combined_matrix[row][-1]
        return solution

    for variable_index in range(variable_count):
        col = variable_start_col + variable_index
        one_row = None
        is_basic = True

        for row in range(constraint_start_row, constraint_end_row + 1):
            value = combined_matrix[row][col]

            if abs(value - 1.0) <= tol:
                if one_row is not None:
                    is_basic = False
                    break
                one_row = row
            elif abs(value) > tol:
                is_basic = False
                break

        if is_basic and one_row is not None:
            solution[variable_index] = combined_matrix[one_row][-1]

    return solution


def find_pivot_row(
    matrix: list[list[float]],
    pivot_col: int,
    start_row: int,
    end_row: int,
    tol: float = TOLERANCE,
) -> int:
    """Retorna a linha do teste da razão mínima ou -1 se não houver."""
    pivot_row = -1
    minimum_ratio = float("inf")

    for row in range(start_row, end_row + 1):
        pivot_value = matrix[row][pivot_col]

        if pivot_value <= tol:
            continue

        ratio = matrix[row][-1] / pivot_value
        if ratio < -tol:
            continue

        ratio = max(0.0, ratio)
        if ratio < minimum_ratio - tol:
            minimum_ratio = ratio
            pivot_row = row

    return pivot_row


def build_combined_matrix(lp: LinearProgram) -> list[list[float]]:
    """Monta o tableau estendido da Fase I."""
    constraint_count = lp.constraint_count
    variable_count = lp.decision_variable_count
    combined_matrix: list[list[float]] = [
        [0.0] * (constraint_count + variable_count + constraint_count + 1)
    ]

    for constraint_index, constraint in enumerate(lp.constraints):
        multiplier = -1.0 if constraint.result < 0 else 1.0

        dual_row = [0.0] * constraint_count
        dual_row[constraint_index] = multiplier

        matrix_row = [
            multiplier * coefficient
            for coefficient in constraint.coefficients
        ]
        artificial_row = [
            1.0 if constraint_index == column else 0.0
            for column in range(constraint_count)
        ]

        combined_matrix.append(
            dual_row
            + matrix_row
            + artificial_row
            + [multiplier * constraint.result]
        )

    return combined_matrix


def set_objective_function(
    combined_matrix: list[list[float]],
    objective_function: list[float],
    basis: list[int],
    variable_start_col: int,
    tol: float = TOLERANCE,
) -> None:
    """Coloca uma função objetivo em forma canônica para a base atual."""
    combined_matrix[0] = [0.0] * len(combined_matrix[0])

    for variable_index, coefficient in enumerate(objective_function):
        combined_matrix[0][variable_start_col + variable_index] = -coefficient

    for basis_index, basic_col in enumerate(basis):
        objective_index = basic_col - variable_start_col
        if not 0 <= objective_index < len(objective_function):
            continue

        basic_cost = objective_function[objective_index]
        if abs(basic_cost) <= tol:
            continue

        constraint_row = combined_matrix[basis_index + 1]
        for col in range(len(combined_matrix[0])):
            combined_matrix[0][col] += basic_cost * constraint_row[col]

    for col, value in enumerate(combined_matrix[0]):
        if abs(value) <= tol:
            combined_matrix[0][col] = 0.0


def pivot_initial_solution(
    combined_matrix: list[list[float]],
    objective_function_start: MatrixPosition,
    objective_function_end: MatrixPosition,
    constraint_matrix_start: MatrixPosition,
    constraint_matrix_end: MatrixPosition,
    basis: list[int],
    pivot_policy: str = "bland",
) -> tuple[ProblemStatus, int | None]:
    """Executa iterações do Simplex primal para a função objetivo atual."""
    while True:
        pivot_col_index = find_negative_index(
            combined_matrix[objective_function_start[0]][
                objective_function_start[1]:objective_function_end[1]
            ],
            pivot_policy=pivot_policy,
        )

        if pivot_col_index == -1:
            return ProblemStatus.OPTIMAL, None

        pivot_col = objective_function_start[1] + pivot_col_index
        pivot_row = find_pivot_row(
            combined_matrix,
            pivot_col=pivot_col,
            start_row=constraint_matrix_start[0],
            end_row=constraint_matrix_end[0],
        )

        if pivot_row == -1:
            return ProblemStatus.UNBOUNDED, pivot_col

        pivot_element(
            combined_matrix,
            pivot_row=pivot_row,
            pivot_col=pivot_col,
        )
        basis[pivot_row - constraint_matrix_start[0]] = pivot_col


def remove_artificial_variables(
    combined_matrix: list[list[float]],
    basis: list[int],
    variable_start_col: int,
    variable_count: int,
    artificial_start_col: int,
    artificial_count: int,
    tol: float = TOLERANCE,
) -> None:
    """Retira variáveis artificiais da base e do tableau."""
    basis_index = 0

    while basis_index < len(basis):
        basic_col = basis[basis_index]
        row = basis_index + 1

        if artificial_start_col <= basic_col < (
            artificial_start_col + artificial_count
        ):
            basic_columns = set(basis)
            pivot_col = -1

            for col in range(
                variable_start_col,
                variable_start_col + variable_count,
            ):
                if col not in basic_columns and abs(combined_matrix[row][col]) > tol:
                    pivot_col = col
                    break

            if pivot_col == -1:
                del combined_matrix[row]
                del basis[basis_index]
                continue

            pivot_element(
                combined_matrix,
                pivot_row=row,
                pivot_col=pivot_col,
            )
            basis[basis_index] = pivot_col

        basis_index += 1

    artificial_end_col = artificial_start_col + artificial_count
    for row in combined_matrix:
        del row[artificial_start_col:artificial_end_col]


def extract_unbounded_direction(
    combined_matrix: list[list[float]],
    basis: list[int],
    pivot_col: int,
    variable_start_col: int,
    variable_count: int,
) -> list[float]:
    direction = [0.0] * variable_count
    entering_index = pivot_col - variable_start_col
    direction[entering_index] = 1.0

    for basis_index, basic_col in enumerate(basis):
        variable_index = basic_col - variable_start_col
        if 0 <= variable_index < variable_count:
            direction[variable_index] = -combined_matrix[basis_index + 1][pivot_col]

    return direction


def find_optimal_solutions(
    combined_matrix: list[list[float]],
    objective_function_start: MatrixPosition,
    objective_function_end: MatrixPosition,
    constraint_matrix_start: MatrixPosition,
    constraint_matrix_end: MatrixPosition,
    basis: list[int],
    variable_count: int,
    tol: float = TOLERANCE,
) -> tuple[dict[tuple[float, ...], list[int]], ProblemStatus]:
    solutions: dict[tuple[float, ...], list[int]] = {}

    solution = extract_solution(
        combined_matrix,
        variable_start_col=objective_function_start[1],
        variable_count=variable_count,
        constraint_start_row=constraint_matrix_start[0],
        constraint_end_row=constraint_matrix_end[0],
        basis=basis,
    )
    solutions[tuple(solution)] = basis.copy()

    basic_columns = set(basis)
    for col in range(
        objective_function_start[1],
        objective_function_start[1] + variable_count,
    ):
        reduced_cost = combined_matrix[objective_function_start[0]][col]

        if col in basic_columns or abs(reduced_cost) > tol:
            continue

        pivot_row = find_pivot_row(
            combined_matrix,
            pivot_col=col,
            start_row=constraint_matrix_start[0],
            end_row=constraint_matrix_end[0],
        )

        if pivot_row == -1:
            direction = extract_unbounded_direction(
                combined_matrix,
                basis,
                col,
                objective_function_start[1],
                variable_count,
            )
            alternate_solution = [
                value + direction_value
                for value, direction_value in zip(solution, direction)
            ]
            solutions[tuple(alternate_solution)] = basis.copy()
            return solutions, ProblemStatus.OPTIMAL_MULTIPLE

        alternate_matrix = [row.copy() for row in combined_matrix]
        alternate_basis = basis.copy()
        pivot_element(
            alternate_matrix,
            pivot_row=pivot_row,
            pivot_col=col,
        )
        alternate_basis[pivot_row - constraint_matrix_start[0]] = col

        alternate_solution = extract_solution(
            alternate_matrix,
            variable_start_col=objective_function_start[1],
            variable_count=variable_count,
            constraint_start_row=constraint_matrix_start[0],
            constraint_end_row=constraint_matrix_end[0],
            basis=alternate_basis,
        )
        solutions[tuple(alternate_solution)] = alternate_basis

        if len(solutions) > 1:
            return solutions, ProblemStatus.OPTIMAL_MULTIPLE

    return solutions, ProblemStatus.OPTIMAL


def restore_original_variables(
    lp: LinearProgram,
    standard_solution: list[float],
) -> list[float]:
    original_signs = getattr(
        lp,
        "original_decision_variable_signs",
        lp.decision_variable_signs,
    )
    original_solution: list[float] = []
    standard_index = 0

    for sign in original_signs:
        if sign == DecisionVariableSign.FREE:
            original_solution.append(
                standard_solution[standard_index]
                - standard_solution[standard_index + 1]
            )
            standard_index += 2
        elif sign == DecisionVariableSign.NEGATIVE:
            original_solution.append(-standard_solution[standard_index])
            standard_index += 1
        else:
            original_solution.append(standard_solution[standard_index])
            standard_index += 1

    return original_solution


def run_simplex(
    lp: LinearProgram,
    pivot_policy: str = "bland",
) -> tuple[float, list[list[float]], list[list[float]], ProblemStatus]:
    """Resolve uma PL em forma padrão pelo Simplex primal de duas fases.

    Retorna:
    - valor objetivo;
    - soluções primais ou ponto e direção de ilimitada;
    - solução dual ou certificado de inviabilidade;
    - status da resolução.
    """
    pivot_policy = getattr(pivot_policy, "value", pivot_policy)
    combined_matrix = build_combined_matrix(lp)

    constraint_count = lp.constraint_count
    variable_count = lp.decision_variable_count
    dual_block_width = constraint_count
    variable_start_col = dual_block_width
    artificial_start_col = variable_start_col + variable_count

    basis = [
        artificial_start_col + constraint_index
        for constraint_index in range(constraint_count)
    ]

    phase_one_objective = (
        [0.0] * variable_count
        + [-1.0] * constraint_count
    )
    set_objective_function(
        combined_matrix,
        phase_one_objective,
        basis,
        variable_start_col,
    )

    row_count = len(combined_matrix)
    col_count = len(combined_matrix[0])
    objective_function_start = (0, variable_start_col)
    objective_function_end = (0, col_count - 1)
    constraint_matrix_start = (1, variable_start_col)
    constraint_matrix_end = (row_count - 1, col_count - 1)

    phase_one_status, _ = pivot_initial_solution(
        combined_matrix,
        objective_function_start,
        objective_function_end,
        constraint_matrix_start,
        constraint_matrix_end,
        basis,
        pivot_policy,
    )

    if (
        phase_one_status == ProblemStatus.UNBOUNDED
        or combined_matrix[0][-1] < -TOLERANCE
    ):
        infeasibility_certificate = combined_matrix[0][:dual_block_width]
        return (
            0.0,
            [],
            [infeasibility_certificate],
            ProblemStatus.INFEASIBLE,
        )

    remove_artificial_variables(
        combined_matrix,
        basis,
        variable_start_col,
        variable_count,
        artificial_start_col,
        constraint_count,
    )

    set_objective_function(
        combined_matrix,
        lp.objective_function,
        basis,
        variable_start_col,
    )

    row_count = len(combined_matrix)
    col_count = len(combined_matrix[0])
    objective_function_end = (0, col_count - 1)
    constraint_matrix_end = (row_count - 1, col_count - 1)

    phase_two_status, unbounded_col = pivot_initial_solution(
        combined_matrix,
        objective_function_start,
        objective_function_end,
        constraint_matrix_start,
        constraint_matrix_end,
        basis,
        pivot_policy,
    )

    if phase_two_status == ProblemStatus.UNBOUNDED and unbounded_col is not None:
        standard_solution = extract_solution(
            combined_matrix,
            variable_start_col,
            variable_count,
            constraint_matrix_start[0],
            constraint_matrix_end[0],
            basis=basis,
        )
        standard_direction = extract_unbounded_direction(
            combined_matrix,
            basis,
            unbounded_col,
            variable_start_col,
            variable_count,
        )
        return (
            float("inf"),
            [
                restore_original_variables(lp, standard_solution),
                restore_original_variables(lp, standard_direction),
            ],
            [],
            ProblemStatus.UNBOUNDED,
        )

    solutions, status = find_optimal_solutions(
        combined_matrix,
        objective_function_start,
        objective_function_end,
        constraint_matrix_start,
        constraint_matrix_end,
        basis,
        variable_count,
    )

    original_solutions_by_value: dict[tuple[float, ...], list[float]] = {}
    for solution in solutions:
        original_solution = restore_original_variables(lp, list(solution))
        normalized_solution = tuple(
            0.0 if abs(value) <= TOLERANCE else value
            for value in original_solution
        )
        original_solutions_by_value[normalized_solution] = list(
            normalized_solution
        )

    original_solutions = list(original_solutions_by_value.values())
    if (
        status == ProblemStatus.OPTIMAL_MULTIPLE
        and len(original_solutions) == 1
    ):
        status = ProblemStatus.OPTIMAL

    objective_value = combined_matrix[0][-1]
    original_problem_type = getattr(
        lp,
        "original_problem_type",
        lp.problem_type,
    )
    if original_problem_type == ProblemType.MINIMIZATION:
        objective_value *= -1

    dual_solution = combined_matrix[0][:dual_block_width]
    if original_problem_type == ProblemType.MINIMIZATION:
        dual_solution = [-value for value in dual_solution]

    return (
        objective_value,
        original_solutions,
        [dual_solution],
        status,
    )
