"""Base commune pour lancer un nœud Edge."""

from __future__ import annotations

import argparse

import joblib
from kafka import KafkaProducer

from common.config import KAFKA_BOOTSTRAP_SERVERS, LOCAL_MODEL_UPDATES_TOPIC
from edge.local_training import train_local_model


def run_edge(edge_name: str, input_path: str) -> None:
    import json
    import pandas as pd

    df = pd.read_csv(input_path)
    artifact = train_local_model(df, edge_name)

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send(LOCAL_MODEL_UPDATES_TOPIC, artifact)
    producer.flush()

    joblib.dump(artifact, f"data/models/{edge_name}_last_update.joblib")
    print(f"Update envoyée: {edge_name} -> {LOCAL_MODEL_UPDATES_TOPIC}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edge", required=True)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    run_edge(edge_name=args.edge, input_path=args.input)


if __name__ == "__main__":
    main()
