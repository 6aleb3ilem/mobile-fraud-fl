#!/usr/bin/env bash
set -euo pipefail

python simulator/generate_transactions.py --samples 4000 --fraud-ratio 0.15 --output data/raw/transactions.csv
python edge/local_training.py --csv data/raw/transactions.csv
python -m streamlit run dashboard/app.py
