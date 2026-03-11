"""Couche Fog: consommation Kafka + micro-analytique via Spark."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime

from kafka import KafkaConsumer
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from common.config import settings


def main() -> None:
    os.makedirs("data/processed", exist_ok=True)

    spark = (
        SparkSession.builder.appName("fog-fraud-monitoring")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )

    consumer = KafkaConsumer(
        settings.transactions_topic,
        settings.alerts_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="latest",
        group_id="fog-streaming-group",
    )

    tx_buffer = []
    alert_buffer = []

    print("[FOG] Spark monitoring démarré")

    for msg in consumer:
        if msg.topic == settings.transactions_topic:
            tx_buffer.append(msg.value)
        elif msg.topic == settings.alerts_topic:
            alert_buffer.append(msg.value)

        if len(tx_buffer) >= 200:
            tx_df = spark.createDataFrame(tx_buffer)
            tx_stats = (
                tx_df.groupBy("region")
                .agg(
                    F.count("*").alias("total_transactions"),
                    F.sum(F.col("label_fraud")).alias("frauds_in_batch"),
                    F.avg("amount").alias("avg_amount"),
                )
                .orderBy(F.desc("frauds_in_batch"))
            )

            stats_rows = [r.asDict() for r in tx_stats.collect()]
            snapshot = {
                "timestamp": datetime.utcnow().isoformat(),
                "batch_size": len(tx_buffer),
                "regions": stats_rows,
                "alerts_in_buffer": len(alert_buffer),
            }

            with open("data/processed/fog_metrics_latest.json", "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)

            with open("data/processed/fog_metrics_history.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(snapshot) + "\n")

            tx_buffer = []
            alert_buffer = alert_buffer[-300:]
            print("[FOG] Snapshot métriques écrit")
            time.sleep(0.1)


if __name__ == "__main__":
    main()
