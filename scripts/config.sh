#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip and installing requirements..."
pip install -e .
pip install -r requirements.txt

echo "Deleting previous results..."
rm -rf data/result

echo "Setup complete!"
