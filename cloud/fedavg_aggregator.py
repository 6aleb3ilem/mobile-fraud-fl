"""Agrégation FedAvg simplifiée pour modèles logistiques (SGDClassifier)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from kafka import KafkaConsumer, KafkaProducer

from common.config import (
    GLOBAL_MODEL_UPDATES_TOPIC,
    KAFKA_BOOTSTRAP_SERVERS,
    LOCAL_MODEL_UPDATES_TOPIC,
    MODELS_DIR,
)


def fedavg(updates: list[dict]) -> dict:
    total_samples = sum(item["n_samples"] for item in updates)
    coef = np.zeros_like(np.array(updates[0]["coef"], dtype=float))
    intercept = np.zeros_like(np.array(updates[0]["intercept"], dtype=float))

    for item in updates:
        weight = item["n_samples"] / total_samples
        coef += weight * np.array(item["coef"], dtype=float)
        intercept += weight * np.array(item["intercept"], dtype=float)

    metrics = {
        "avg_accuracy": float(np.mean([u["metrics"]["accuracy"] for u in updates])),
        "avg_precision": float(np.mean([u["metrics"]["precision"] for u in updates])),
        "avg_recall": float(np.mean([u["metrics"]["recall"] for u in updates])),
        "avg_f1": float(np.mean([u["metrics"]["f1"] for u in updates])),
    }

    return {
        "n_edges": len(updates),
        "total_samples": int(total_samples),
        "coef": coef.tolist(),
        "intercept": intercept.tolist(),
        "metrics": metrics,
    }


def aggregate_from_files(pattern: str = "data/models/*_update.joblib") -> dict:
    files = sorted(Path().glob(pattern))
    updates = [joblib.load(p) for p in files]
    if not updates:
        raise ValueError("Aucune mise à jour locale trouvée.")
    return fedavg(updates)


def aggregate_from_kafka(expected_updates: int = 3) -> dict:
    consumer = KafkaConsumer(
        LOCAL_MODEL_UPDATES_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="cloud-aggregator",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    updates = []
    for msg in consumer:
        updates.append(msg.value)
        if len(updates) >= expected_updates:
            break

    if not updates:
        raise ValueError("Aucune update reçue depuis Kafka.")

    return fedavg(updates)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["files", "kafka"], default="files")
    parser.add_argument("--expected-updates", type=int, default=3)
    args = parser.parse_args()

    global_update = (
        aggregate_from_files()
        if args.mode == "files"
        else aggregate_from_kafka(expected_updates=args.expected_updates)
    )

    output_path = MODELS_DIR / "global_model_update.json"
    output_path.write_text(json.dumps(global_update, indent=2), encoding="utf-8")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send(GLOBAL_MODEL_UPDATES_TOPIC, global_update)
    producer.flush()

    print(f"Global update enregistrée: {output_path}")


if __name__ == "__main__":
    main()
