#!/usr/bin/env bash
set -euo pipefail

python -m simulator.generate_transactions --rows 5000
python scripts/prepare_edge_datasets.py
python -m edge.edge_nouakchott
python -m edge.edge_rosso
python -m edge.edge_kaedi
python -m cloud.fedavg_aggregator --mode files
