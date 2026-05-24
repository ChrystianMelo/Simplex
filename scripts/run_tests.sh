#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo
echo "============================================"
echo "   Iniciando execução dos testes (pytest)"
echo "============================================"
echo

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Ambiente virtual ativado."
else
    echo "Nenhum ambiente virtual encontrado."
    echo "(Certifique-se de ter criado um com: python3 -m venv venv)"
fi

echo
echo "Limpando caches antigos..."
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf .pytest_cache

echo
echo "Executando pytest..."
pytest -v tests

echo
echo "============================================"
echo "    Execução dos testes finalizada."
echo "============================================"
echo
