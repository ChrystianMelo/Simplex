from __future__ import annotations

import logging

from simplex.models import (
    ConstraintRelation,
    DecisionVariableSign,
    LinearProgram,
    ProblemType
)


def to_standard_form(lp: LinearProgram) -> None:
    # Padronizando o tipo do problema para maximização
    if (lp.problem_type == ProblemType.MINIMIZATION):
        lp.objective_function = [-c for c in lp.objective_function]
        lp.problem_type = ProblemType.MAXIMIZATION
        logging.info(
            "Convertendo funcao objetivo de minimizacao para maximizacao")

    # Padronizando as restrições para igualdades
    for constraint in lp.constraints:
        if (constraint.relation == ConstraintRelation.LESS_OR_EQUAL):
            lp.increase_decision_variable_count()
            constraint.coefficients[lp.decision_variable_count - 1] = 1

            constraint.relation = ConstraintRelation.EQUAL
        elif (constraint.relation == ConstraintRelation.GREATER_OR_EQUAL):
            lp.increase_decision_variable_count()
            constraint.coefficients[lp.decision_variable_count - 1] = -1

            constraint.relation = ConstraintRelation.EQUAL

    # Padronizando o sinal das variáveis de decisão para x_j >= 0
    for i, sign in enumerate(lp.decision_variable_signs):

        if (sign == DecisionVariableSign.NEGATIVE):
            lp.objective_function[i] *= -1
            lp.decision_variable_signs[i] = DecisionVariableSign.POSITIVE

            # Xi = -Xi
            for constraint in lp.constraints:
                constraint.coefficients[i] *= -1

        elif (sign == DecisionVariableSign.FREE):
            lp.decision_variable_count += 1
            lp.decision_variable_signs[i] = DecisionVariableSign.POSITIVE
            lp.decision_variable_signs.insert(
                i+1, DecisionVariableSign.POSITIVE)

            # k [Xi] = k [ (Xi+) - (Xi-)] Nas restrições
            for constraint in lp.constraints:
                coefficient = constraint.coefficients[i]
                constraint.coefficients.insert(i+1, -coefficient)

            # k [Xi] = k [ (Xi+) - (Xi-)] Na função objetivo
            lp.objective_function.insert(i+1, -lp.objective_function[i])
