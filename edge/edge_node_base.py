"""Base d'un noeud Edge: entraînement local + envoi mise à jour FedAvg."""

from __future__ import annotations

import json
import time
from typing import Optional

import numpy as np
import pandas as pd
from kafka import KafkaConsumer

from common.config import settings
from common.utils import get_producer
from edge.local_training import train_local_model, extract_linear_params


class EdgeNode:
    def __init__(self, region_name: str, batch_size: int = 200):
        self.region_name = region_name
        self.batch_size = batch_size
        self.producer = get_producer(settings.kafka_bootstrap_servers)

    def _consumer(self) -> KafkaConsumer:
        return KafkaConsumer(
            settings.transactions_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="latest",
            group_id=f"edge-{self.region_name.lower()}-group",
        )

    def _publish_local_update(self, payload: dict) -> None:
        self.producer.send(settings.local_model_updates_topic, payload)

    def run(self) -> None:
        consumer = self._consumer()
        buffer = []
        print(f"[EDGE-{self.region_name}] en écoute...")

        for msg in consumer:
            tx = msg.value
            if tx.get("region") != self.region_name:
                continue
            buffer.append(tx)

            if len(buffer) >= self.batch_size:
                df = pd.DataFrame(buffer)
                buffer = []

                model, metrics = train_local_model(df)
                params = extract_linear_params(model)

                local_update = {
                    "region": self.region_name,
                    "n_samples": int(len(df)),
                    "coef": params["coef"],
                    "intercept": params["intercept"],
                    "metrics": metrics,
                    "ts": time.time(),
                }
                self._publish_local_update(local_update)

                # Détection en temps réel: calcul du score sur dernières transactions du batch
                probs = model.predict_proba(df[model.feature_names_in_])[:, 1] if hasattr(model, "predict_proba") else np.zeros(len(df))
                risky = df.assign(risk_score=probs).query("risk_score >= @settings.risk_threshold")
                for _, r in risky.head(20).iterrows():
                    self.producer.send(
                        settings.alerts_topic,
                        {
                            "source": f"edge_{self.region_name.lower()}",
                            "transaction_id": r["transaction_id"],
                            "region": r["region"],
                            "risk_score": float(r["risk_score"]),
                            "message": "Transaction suspecte détectée en Edge",
                        },
                    )

                print(f"[EDGE-{self.region_name}] update envoyée | samples={len(df)} metrics={metrics}")
