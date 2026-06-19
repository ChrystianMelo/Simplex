from __future__ import annotations

from simplex.models import (
    Constraint,
    ConstraintRelation,
    DecisionVariableSign,
    LinearProgram,
    ProblemType,
)


def parse_number(value: str) -> float:
    return float(value)


def parse_constraint_relation(value: str) -> ConstraintRelation:
    try:
        return ConstraintRelation(value)
    except ValueError as error:
        raise ValueError(f"Relacao de restricao invalida: '{value}'.") from error


def parse_problem_type(value: str) -> ProblemType:
    try:
        return ProblemType(value.lower())
    except ValueError as error:
        raise ValueError("Funcao objetivo deve comecar com 'max' ou 'min'.") from error


def parse_decision_variable_sign(value: str) -> DecisionVariableSign:
    try:
        return DecisionVariableSign(int(value))
    except ValueError as error:
        raise ValueError(
            "Sinal de variavel de decisao invalido: esperado 1, -1 ou 0."
        ) from error


def parse_input(raw_input: str) -> LinearProgram:
    lines = [line.strip() for line in raw_input.splitlines() if line.strip()]
    if len(lines) < 4:
        raise ValueError("Entrada incompleta: esperado cabecalho e funcao objetivo.")

    decision_variable_count = int(lines[0])
    constraint_count = int(lines[1])

    decision_variable_signs = [
        parse_decision_variable_sign(value) for value in lines[2].split()
    ]
    if len(decision_variable_signs) != decision_variable_count:
        raise ValueError(
            "Quantidade de sinais das variaveis diferente do numero de variaveis."
        )

    objective_tokens = lines[3].split()
    if len(objective_tokens) == decision_variable_count:
        # O formato mostrado no enunciado traz apenas os coeficientes e
        # apresenta a PL como maximização.
        problem_type = ProblemType.MAXIMIZATION
        coefficient_tokens = objective_tokens
    else:
        problem_type = parse_problem_type(objective_tokens[0])
        coefficient_tokens = objective_tokens[1:]

    objective_function = [parse_number(value) for value in coefficient_tokens]
    if len(objective_function) != decision_variable_count:
        raise ValueError(
            "Quantidade de coeficientes da funcao objetivo diferente do numero de "
            "variaveis."
        )

    constraint_lines = lines[4:]
    if len(constraint_lines) != constraint_count:
        raise ValueError(
            "Quantidade de restricoes diferente do numero informado no cabecalho."
        )

    constraints = []
    for line in constraint_lines:
        tokens = line.split()
        if len(tokens) != decision_variable_count + 2:
            raise ValueError(f"Restricao invalida: '{line}'.")

        relation = parse_constraint_relation(tokens[decision_variable_count])

        constraints.append(
            Constraint(
                coefficients=[
                    parse_number(value) for value in tokens[:decision_variable_count]
                ],
                relation=relation,
                result=parse_number(tokens[-1]),
            )
        )

    return LinearProgram(
        decision_variable_count=decision_variable_count,
        constraint_count=constraint_count,
        decision_variable_signs=decision_variable_signs,
        problem_type=problem_type,
        objective_function=objective_function,
        constraints=constraints,
    )
