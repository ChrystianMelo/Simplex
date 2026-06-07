from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum


class ConstraintRelation(Enum):
    """Relação usada em uma restrição do problema de Programação Linear."""

    # Restrição de igualdade: a_i x = b_i.
    EQUAL = "=="

    # Restrição do tipo menor ou igual: a_i x <= b_i.
    LESS_OR_EQUAL = "<="

    # Restrição do tipo maior ou igual: a_i x >= b_i.
    GREATER_OR_EQUAL = ">="


class ProblemType(Enum):
    """Sentido de otimização da função objetivo."""

    # Problema de maximização: max z = c^T x.
    MAXIMIZATION = "max"

    # Problema de minimização: min z = c^T x.
    MINIMIZATION = "min"


class DecisionVariableSign(IntEnum):
    """Condição de sinal de uma variável de decisão."""

    # Variável positiva: x_j >= 0.
    POSITIVE = 1

    # Variável negativa: x_j <= 0.
    NEGATIVE = -1

    # Variável livre: sem restrição de sinal.
    FREE = 0


@dataclass
class Constraint:
    """Representa uma restrição linear do problema.

    A restrição tem a forma a_i x <= b_i, a_i x >= b_i ou a_i x = b_i,
    onde `coefficients` é a linha a_i da matriz de coeficientes e `result`
    é o membro direito b_i.
    """

    # Coeficientes das variáveis de decisão na restrição.
    coefficients: list[float]

    # Relação da restrição: <=, >= ou ==.
    relation: ConstraintRelation

    # Membro direito da restrição.
    result: float


@dataclass
class LinearProgram:
    """Modelo de entrada de um problema de Programação Linear.

    Guarda a função objetivo, as restrições e as condições de sinal das
    variáveis de decisão antes da conversão para a forma padrão.
    """

    # Número de variáveis de decisão do problema original.
    decision_variable_count: int

    # Número de restrições do problema original.
    constraint_count: int

    # Condição de sinal de cada variável de decisão.
    decision_variable_signs: list[DecisionVariableSign]

    # Tipo do problema: maximização ou minimização da função objetivo.
    problem_type: ProblemType

    # Coeficientes c_j da função objetivo z = c^T x.
    objective_function: list[float]

    # Lista das restrições lineares do problema.
    constraints: list[Constraint]

    def __init__(
        self,
        decision_variable_count: int,
        constraint_count: int,
        decision_variable_signs: list[DecisionVariableSign],
        problem_type: ProblemType,
        objective_function: list[float],
        constraints: list[Constraint],
    ) -> None:
        self.decision_variable_count = decision_variable_count
        self.constraint_count = constraint_count
        self.decision_variable_signs = decision_variable_signs
        self.problem_type = problem_type
        self.objective_function = objective_function
        self.constraints = constraints

    def increase_decision_variable_count(self):
        self.decision_variable_count += 1

        for constraint in self.constraints:
            constraint.coefficients.append(0)

        self.decision_variable_signs.append(DecisionVariableSign.POSITIVE)
        self.objective_function.append(0)
