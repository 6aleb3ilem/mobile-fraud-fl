"""Envoie les transactions simulées vers Kafka."""

from __future__ import annotations

import argparse
import json
import time

import pandas as pd
from kafka import KafkaProducer

from common.config import KAFKA_BOOTSTRAP_SERVERS, TRANSACTIONS_TOPIC


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/transactions_synthetic.csv")
    parser.add_argument("--sleep", type=float, default=0.1)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    for row in df.to_dict(orient="records"):
        producer.send(TRANSACTIONS_TOPIC, row)
        time.sleep(args.sleep)

    producer.flush()
    print(f"{len(df)} transactions publiées vers {TRANSACTIONS_TOPIC}")


if __name__ == "__main__":
    main()
