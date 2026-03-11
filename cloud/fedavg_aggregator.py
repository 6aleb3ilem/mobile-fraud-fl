"""Agrégation FedAvg simplifiée pour modèle linéaire (SGDClassifier log_loss)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import numpy as np

from common.config import KAFKA_TOPIC_GLOBAL_MODEL_UPDATES, KAFKA_TOPIC_LOCAL_MODEL_UPDATES, MODELS_DIR
from common.utils import build_consumer, build_producer, get_logger

logger = get_logger("fedavg_aggregator")


def fedavg(updates: List[dict]) -> dict:
    if not updates:
        raise ValueError("Aucune update locale reçue")

    total_samples = sum(u["sample_count"] for u in updates)
    coef_matrix = np.array([u["coefficients"] for u in updates], dtype=float)
    intercepts = np.array([u["intercept"] for u in updates], dtype=float)
    weights = np.array([u["sample_count"] / total_samples for u in updates])

    global_coef = np.average(coef_matrix, axis=0, weights=weights)
    global_intercept = float(np.average(intercepts, weights=weights))

    return {
        "round": 1,
        "total_samples": int(total_samples),
        "global_coefficients": global_coef.tolist(),
        "global_intercept": global_intercept,
        "contributors": [u["edge_node_id"] for u in updates],
    }


def run_once(expected_updates: int = 3) -> dict:
    consumer = build_consumer(KAFKA_TOPIC_LOCAL_MODEL_UPDATES, group_id="cloud_aggregator")
    updates = []
    logger.info("Attente de %s updates locales...", expected_updates)

    for msg in consumer:
        updates.append(msg.value)
        logger.info("Update reçue de %s", msg.value.get("edge_node_id"))
        if len(updates) >= expected_updates:
            break

    result = fedavg(updates)
    out_path = Path(MODELS_DIR) / "global_model_update.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    producer = build_producer()
    producer.send(KAFKA_TOPIC_GLOBAL_MODEL_UPDATES, key="cloud", value=result)
    producer.flush()

    logger.info("Modèle global agrégé et publié.")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-updates", type=int, default=3)
    args = parser.parse_args()
    run_once(expected_updates=args.expected_updates)
