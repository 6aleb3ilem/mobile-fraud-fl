"""Script de lancement du training local sur plusieurs Edge nodes."""
from __future__ import annotations

import argparse

import pandas as pd

from common.config import EDGE_REGIONS
from common.utils import get_logger
from edge.edge_node_base import EdgeNodeTrainer

logger = get_logger("local_training")


def run_training(csv_path: str, publish: bool = False):
    df = pd.read_csv(csv_path)
    results = []
    for node_id, region in EDGE_REGIONS.items():
        trainer = EdgeNodeTrainer(edge_node_id=node_id, region=region)
        result = trainer.train(df)
        if publish:
            trainer.publish_update(result)
        results.append(result)
    logger.info("%s noeuds entraînés", len(results))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    run_training(args.csv, publish=args.publish)
