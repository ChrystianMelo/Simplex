@echo off
cd /d "%~dp0.."

REM ============================================================
REM  test.bat — Executa a suíte de testes do TP1 (pytest)
REM ============================================================

echo.
echo ============================================
echo    Iniciando execução dos testes (pytest)
echo ============================================
echo.

REM Ativa ambiente virtual, se existir
if exist venv (
    call venv\Scripts\activate
    echo Ambiente virtual ativado.
) else (
    echo Nenhum ambiente virtual encontrado.
    echo (Certifique-se de ter criado um com: python -m venv venv)
)

echo.
echo Limpando caches antigos...
for /d /r %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i"
del /s /q .pytest_cache >nul 2>&1

echo.
echo Executando pytest...
pytest -v tests

echo.
echo ============================================
echo     Execução dos testes finalizada.
echo ============================================
echo.

pause
