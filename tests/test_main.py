from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from main import main


def run_main(
    input_path: Path,
    capsys: pytest.CaptureFixture[str],
    *,
    policy: str = "bland",
) -> str:
    with patch.object(
        sys,
        "argv",
        [
            "main.py",
            str(input_path),
            "--decimals",
            "3",
            "--digits",
            "7",
            "--policy",
            policy,
        ],
    ):
        main()

    return capsys.readouterr().out


def write_lp(tmp_path: Path, content: str) -> Path:
    input_path = tmp_path / "problem.lp"
    input_path.write_text(content, encoding="utf-8")
    return input_path


def final_output(output: str) -> str:
    return output.split("=== Resultado final ===", maxsplit=1)[1].strip()


def test_main_prints_fpi_iterations_and_optimal_result(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_path = write_lp(
        tmp_path,
        """\
2
3
1 1
1 1
1 0 <= 1
0 1 <= 1
1 1 <= 1.5
""",
    )

    output = run_main(input_path, capsys)

    assert "=== Forma Padrao (FPI) ===" in output
    assert "x0, x1" in output
    assert "=== Fase I (PL auxiliar) ===" in output
    assert "=== Fase II (PL original) ===" in output
    assert "Iteracao 0: Tableau inicial" in output
    assert "Entra na base: x" in output
    assert "Sai da base: " in output
    assert "Status: otimo (multiplos)" in final_output(output)
    assert "Objetivo:   1.500" in final_output(output)
    assert "Solucoes:" in final_output(output)
    assert "Dual:" in final_output(output)


@pytest.mark.parametrize(
    ("problem", "expected_status"),
    [
        (
            """\
1
2
1
max 1
1 <= 0
1 >= 1
""",
            "Status: inviavel",
        ),
        (
            """\
1
1
1
max 1
-1 <= 0
""",
            "Status: ilimitado",
        ),
    ],
)
def test_main_prints_only_required_final_status_for_non_optimal_problems(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    problem: str,
    expected_status: str,
) -> None:
    input_path = write_lp(tmp_path, problem)

    output = run_main(input_path, capsys)

    assert final_output(output) == expected_status


def test_main_prints_the_additional_iteration_for_multiple_optima(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_path = write_lp(
        tmp_path,
        """\
2
3
1 1
max 1 1
1 1 <= 1
1 0 <= 1
0 1 <= 1
""",
    )

    output = run_main(input_path, capsys)

    assert "Pivoteamento para solucao otima alternativa" in output
    result = final_output(output)
    assert result.startswith("Status: otimo (multiplos)")
    assert result.count("  0.000   1.000") + result.count(
        "  1.000   0.000"
    ) >= 2
