from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum

from simplex.models import LinearProgram, ProblemStatus
from simplex.parser import parse_input
from simplex.solver import SimplexTraceEvent, run_simplex
from simplex.standard_form import to_standard_form


class PivotPolicy(Enum):
    LARGEST = "largest"
    BLAND = "bland"
    SMALLEST = "smallest"


@dataclass(frozen=True)
class RuntimeOptions:
    filename: str
    decimals: int
    digits: int
    pivot_policy: PivotPolicy

    def format_number(self, number: float) -> str:
        if abs(number) < 0.5 * 10 ** (-self.decimals):
            number = 0.0
        return "%*.*f" % (self.digits, self.decimals, number)


class ConsoleTracePrinter:
    """Apresenta as iterações produzidas pelo solver de forma legível."""

    def __init__(self, options: RuntimeOptions) -> None:
        self.options = options
        self.current_phase: str | None = None

    def __call__(self, event: SimplexTraceEvent) -> None:
        if event.phase != self.current_phase:
            self.current_phase = event.phase
            print(f"\n=== {event.phase} ===")

        print(f"\nIteracao {event.iteration}: {event.action}")
        if event.pivot_policy:
            print(f"Politica: {event.pivot_policy}")

        if event.entering_col is not None:
            entering = event.column_labels[event.entering_col]
            print(f"Entra na base: {entering}")
        if event.leaving_col is not None:
            leaving = event.column_labels[event.leaving_col]
            print(f"Sai da base: {leaving}")

        if event.action in {
            "Tableau inicial",
            "Pivoteamento",
            "Pivoteamento para solucao otima alternativa",
            "Ciclo detectado; continuando com a regra de Bland",
        }:
            self.print_tableau(event)

    def print_tableau(self, event: SimplexTraceEvent) -> None:
        label_width = max(
            4,
            *(len(label) for label in event.column_labels),
            *(len(event.column_labels[col]) for col in event.basis),
        )
        number_width = max(
            self.options.digits,
            self.options.decimals + 3,
            *(len(self.options.format_number(value)) for row in event.matrix for value in row),
        )

        header = "Base".rjust(label_width) + " | " + " ".join(
            label.rjust(number_width) for label in event.column_labels
        )
        print(header)
        print("-" * len(header))

        row_labels = ["z"] + [
            event.column_labels[basic_col] for basic_col in event.basis
        ]
        for row_label, row in zip(row_labels, event.matrix):
            values = " ".join(
                self.options.format_number(value).rjust(number_width)
                for value in row
            )
            print(f"{row_label.rjust(label_width)} | {values}")


def format_linear_expression(
    coefficients: list[float],
    options: RuntimeOptions,
) -> str:
    terms: list[str] = []

    for index, coefficient in enumerate(coefficients):
        if abs(coefficient) <= 1e-9:
            continue

        magnitude = options.format_number(abs(coefficient))
        term = f"{magnitude} x{index}"
        if not terms:
            terms.append(f"-{term}" if coefficient < 0 else term)
        else:
            operator = "-" if coefficient < 0 else "+"
            terms.append(f"{operator} {term}")

    return " ".join(terms) if terms else options.format_number(0.0)


def print_standard_form(
    linear_program: LinearProgram,
    options: RuntimeOptions,
) -> None:
    print("=== Forma Padrao (FPI) ===")
    objective = format_linear_expression(
        linear_program.objective_function,
        options,
    )
    print(f"max z = {objective}")
    print("sujeito a:")

    for constraint in linear_program.constraints:
        expression = format_linear_expression(
            constraint.coefficients,
            options,
        )
        result = options.format_number(constraint.result)
        print(f"  {expression} = {result}")

    variable_names = ", ".join(
        f"x{index}" for index in range(linear_program.decision_variable_count)
    )
    print(f"  {variable_names} >= 0")


def parse_arguments() -> RuntimeOptions:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Nome do arquivo lp de entrada")
    parser.add_argument(
        "--decimals",
        type=int,
        default=7,
        help="N. de casas decimais para imprimir valores numericos.",
    )
    parser.add_argument(
        "--digits",
        type=int,
        default=0,
        help="N. total de digitos para imprimir valores numericos.",
    )
    parser.add_argument(
        "--policy",
        choices=["largest", "bland", "smallest"],
        default="largest",
        help="Valores validos: 'largest' (default), 'bland', 'smallest'",
    )
    arguments = parser.parse_args()

    if arguments.decimals < 0:
        parser.error("--decimals deve ser maior ou igual a zero")
    if arguments.digits < 0:
        parser.error("--digits deve ser maior ou igual a zero")

    return RuntimeOptions(
        filename=arguments.filename,
        decimals=arguments.decimals,
        digits=arguments.digits,
        pivot_policy=PivotPolicy(arguments.policy),
    )


def main() -> None:
    arguments = parse_arguments()

    with open(arguments.filename, encoding="utf-8") as input_file:
        raw_input = input_file.read()

    if not raw_input.strip():
        return

    linear_program = parse_input(raw_input)
    to_standard_form(linear_program)
    print_standard_form(linear_program, arguments)

    objective, solutions, dual, status = run_simplex(
        linear_program,
        arguments.pivot_policy.value,
        trace_callback=ConsoleTracePrinter(arguments),
    )
    print("\n=== Resultado final ===")
    print(status)

    if status == ProblemStatus.INFEASIBLE:
        return

    if status == ProblemStatus.UNBOUNDED:
        return

    print(f"Objetivo: {arguments.format_number(objective)}")
    print(
        "Solucoes:"
        if status == ProblemStatus.OPTIMAL_MULTIPLE
        else "Solucao:"
    )
    for solution in solutions:
        print(
            " ".join(
                arguments.format_number(value)
                for value in solution
            )
        )

    print("Dual:")
    if dual:
        print(
            " ".join(
                arguments.format_number(value)
                for value in dual[0]
            )
        )


if __name__ == "__main__":
    main()
