from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConstraintRelation(Enum):
    EQUAL = "=="
    LESS_OR_EQUAL = "<="
    GREATER_OR_EQUAL = ">="


class ProblemType(Enum):
    MAXIMIZATION = "max"
    MINIMIZATION = "min"


@dataclass(frozen=True)
class Constraint:
    coefficients: list[float]
    relation: ConstraintRelation
    result: float


@dataclass(frozen=True)
class LinearProgram:
    decision_variable_count: int
    constraint_count: int
    decision_variable_signs: list[int]
    problem_type: ProblemType
    objective_function: list[float]
    constraints: list[Constraint]


@dataclass(frozen=True)
class StandardFormLinearProgram:
    decision_variable_count: int
    constraint_count: int
    objective_function: list[float]
    constraint_matrix: list[list[float]]
    constraint_relations: list[ConstraintRelation]
    results: list[float]
    variable_sources: list[tuple[int, float]]
