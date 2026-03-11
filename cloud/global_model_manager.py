"""Consomme les updates globales et maintient un fichier de métriques simplifié."""

from __future__ import annotations

import json
import os
from datetime import datetime

from kafka import KafkaConsumer

from common.config import settings


def main() -> None:
    os.makedirs("data/models", exist_ok=True)
    consumer = KafkaConsumer(
        settings.global_model_updates_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="latest",
        group_id="global-model-manager-group",
    )

    history_path = "data/models/global_metrics_history.jsonl"
    print("[CLOUD] Global model manager actif")

    for msg in consumer:
        payload = msg.value
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "round": payload["round"],
            "n_total": payload["n_total"],
            # Approximation pédagogique: pseudo score croissant selon le volume.
            "global_accuracy_proxy": min(0.99, 0.62 + 0.02 * (payload["n_total"] / 500.0)),
        }
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        with open("data/models/current_global_model.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        print(f"[CLOUD] Historique mis à jour, round={payload['round']}")


if __name__ == "__main__":
    main()
