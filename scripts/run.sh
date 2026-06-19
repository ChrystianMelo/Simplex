#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "Activating virtual environment..."
source venv/bin/activate

echo "Running project..."
python src/main.py "$@"
