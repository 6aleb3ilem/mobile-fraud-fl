"""Configuration centrale du projet mobile-fraud-fl."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_TRANSACTIONS = os.getenv("KAFKA_TOPIC_TRANSACTIONS", "transactions")
KAFKA_TOPIC_ALERTS = os.getenv("KAFKA_TOPIC_ALERTS", "alerts")
KAFKA_TOPIC_LOCAL_MODEL_UPDATES = os.getenv("KAFKA_TOPIC_LOCAL_MODEL_UPDATES", "local_model_updates")
KAFKA_TOPIC_GLOBAL_MODEL_UPDATES = os.getenv("KAFKA_TOPIC_GLOBAL_MODEL_UPDATES", "global_model_updates")

FRAUD_RISK_THRESHOLD = float(os.getenv("FRAUD_RISK_THRESHOLD", "0.65"))
RANDOM_SEED = 42

EDGE_REGIONS = {
    "edge_nouakchott": "Nouakchott",
    "edge_rosso": "Rosso",
    "edge_kaedi": "Kaédi",
}

TRANSACTION_TYPES = ["cash_in", "cash_out", "p2p", "bill_payment", "merchant_payment"]
