#!/usr/bin/env bash
set -euo pipefail

python -m simulator.generate_transactions --rows 2000 --output data/raw/simulated_transactions.csv
python -m pytest -q

echo "Lancez ensuite: docker compose up --build"
