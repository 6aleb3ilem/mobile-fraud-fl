"""Publie des transactions simulées vers Kafka."""
from __future__ import annotations

import argparse
import time

import pandas as pd

from common.config import KAFKA_TOPIC_TRANSACTIONS
from common.utils import build_producer, get_logger

logger = get_logger("producer_kafka")


def stream_transactions(csv_path: str, delay_s: float = 0.1) -> None:
    producer = build_producer()
    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        payload = row.to_dict()
        producer.send(KAFKA_TOPIC_TRANSACTIONS, key=payload["agent_id"], value=payload)
        logger.info("Transaction publiée: %s", payload["transaction_id"])
        time.sleep(delay_s)

    producer.flush()
    logger.info("Streaming terminé.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--delay", type=float, default=0.05)
    args = parser.parse_args()
    stream_transactions(args.csv, args.delay)
