from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum

from simplex.parser import parse_input
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
        return "%*.*f" % (self.digits, self.decimals, number)


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


if __name__ == "__main__":
    main()
