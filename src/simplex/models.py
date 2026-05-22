from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class LinearProgram:
    """Modelo de entrada de um problema de Programação Linear.

    Guarda a função objetivo, as restrições e as condições de sinal das
    variáveis de decisão antes da conversão para a forma padrão.
    """

    # Número de variáveis de decisão do problema original.
    decision_variable_count: int

    # Número de restrições do problema original.
    constraint_count: int

    # Condição de sinal de cada variável: 1 para x_j >= 0,
    # -1 para x_j <= 0 e 0 para variável livre.
    decision_variable_signs: list[int]

    # Tipo do problema: maximização ou minimização da função objetivo.
    problem_type: ProblemType

    # Coeficientes c_j da função objetivo z = c^T x.
    objective_function: list[float]

    # Lista das restrições lineares do problema.
    constraints: list[Constraint]


@dataclass(frozen=True)
class StandardFormLinearProgram:
    """Problema de Programação Linear escrito na forma padrão.

    Nesta representação, as variáveis já foram ajustadas para obedecer às
    condições de não negatividade, e as restrições ficam organizadas pela
    matriz de coeficientes A, pelas relações e pelo vetor de resultados b.
    """

    # Número de variáveis na forma padrão.
    decision_variable_count: int

    # Número de restrições na forma padrão.
    constraint_count: int

    # Coeficientes da função objetivo na forma padrão.
    objective_function: list[float]

    # Matriz de coeficientes A das restrições.
    constraint_matrix: list[list[float]]

    # Relações das restrições após a padronização.
    constraint_relations: list[ConstraintRelation]

    # Vetor b, isto é, os membros direitos das restrições.
    results: list[float]

    # Origem de cada variável padronizada: índice da variável original
    # e fator usado na transformação.
    variable_sources: list[tuple[int, float]]
