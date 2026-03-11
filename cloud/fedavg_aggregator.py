"""Agrégateur FedAvg simplifié côté Cloud."""

from __future__ import annotations

import json
import os
import time
from typing import List, Dict

import numpy as np
from kafka import KafkaConsumer

from common.config import settings
from common.utils import get_producer


def fedavg(updates: List[Dict]) -> Dict[str, list]:
    weights = np.array([u["n_samples"] for u in updates], dtype=float)
    weights = weights / weights.sum()

    coef_stack = np.array([u["coef"] for u in updates], dtype=float)
    intercept_stack = np.array([u["intercept"] for u in updates], dtype=float)

    coef_avg = np.tensordot(weights, coef_stack, axes=([0], [0]))
    intercept_avg = np.tensordot(weights, intercept_stack, axes=([0], [0]))

    return {"coef": coef_avg.tolist(), "intercept": intercept_avg.tolist()}


def main() -> None:
    os.makedirs("data/models", exist_ok=True)
    producer = get_producer(settings.kafka_bootstrap_servers)
    consumer = KafkaConsumer(
        settings.local_model_updates_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="latest",
        group_id="cloud-fedavg-group",
    )

    pending_updates = []
    print("[CLOUD] Agrégateur FedAvg démarré")

    for msg in consumer:
        pending_updates.append(msg.value)

        regions = {u["region"] for u in pending_updates}
        if len(regions) >= 3:
            global_params = fedavg(pending_updates)
            update = {
                "round": int(time.time()),
                "regions": sorted(list(regions)),
                "n_total": int(sum(u["n_samples"] for u in pending_updates)),
                "global_coef": global_params["coef"],
                "global_intercept": global_params["intercept"],
                "ts": time.time(),
            }
            producer.send(settings.global_model_updates_topic, update)

            with open("data/models/latest_global_update.json", "w", encoding="utf-8") as f:
                json.dump(update, f, indent=2)

            print(f"[CLOUD] Nouveau modèle global publié: round={update['round']}")
            pending_updates = []


if __name__ == "__main__":
    main()
