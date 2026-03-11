"""Producteur Kafka de transactions synthétiques."""

from __future__ import annotations

import json
import time

from common.config import settings
from common.utils import get_producer
from simulator.generate_transactions import generate_dataset


def main() -> None:
    producer = get_producer(settings.kafka_bootstrap_servers)
    df = generate_dataset(n_rows=20000, fraud_ratio=0.16, seed=11)

    for row in df.to_dict(orient="records"):
        producer.send(settings.transactions_topic, row)
        if row["label_fraud"] == 1:
            producer.send(
                settings.alerts_topic,
                {
                    "source": "simulator",
                    "transaction_id": row["transaction_id"],
                    "region": row["region"],
                    "risk_score": 0.95,
                    "message": "Fraude simulée injectée",
                },
            )
        print(json.dumps({"topic": settings.transactions_topic, "transaction_id": row["transaction_id"]}))
        time.sleep(settings.simulator_interval_seconds)


if __name__ == "__main__":
    main()
