"""Configuration centralisée pour tout le projet."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
    transactions_topic: str = os.getenv("TRANSACTIONS_TOPIC", "transactions")
    alerts_topic: str = os.getenv("ALERTS_TOPIC", "alerts")
    local_model_updates_topic: str = os.getenv("LOCAL_MODEL_UPDATES_TOPIC", "local_model_updates")
    global_model_updates_topic: str = os.getenv("GLOBAL_MODEL_UPDATES_TOPIC", "global_model_updates")
    simulator_interval_seconds: float = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "0.4"))
    risk_threshold: float = float(os.getenv("RISK_THRESHOLD", "0.6"))


settings = Settings()
