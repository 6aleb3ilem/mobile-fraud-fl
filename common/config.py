"""Configuration centralisée du projet."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TRANSACTIONS_TOPIC = os.getenv("TRANSACTIONS_TOPIC", "transactions")
ALERTS_TOPIC = os.getenv("ALERTS_TOPIC", "alerts")
LOCAL_MODEL_UPDATES_TOPIC = os.getenv("LOCAL_MODEL_UPDATES_TOPIC", "local_model_updates")
GLOBAL_MODEL_UPDATES_TOPIC = os.getenv("GLOBAL_MODEL_UPDATES_TOPIC", "global_model_updates")

REGIONS = ["Nouakchott", "Rosso", "Kaedi", "Nouadhibou", "Atar"]
TRANSACTION_TYPES = ["cash_in", "cash_out", "p2p", "merchant_payment", "bill_payment"]

for folder in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
