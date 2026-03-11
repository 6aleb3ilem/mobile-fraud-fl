"""Job Spark Structured Streaming pour monitoring temps réel des transactions."""
from __future__ import annotations

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

from common.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_TRANSACTIONS


schema = StructType(
    [
        StructField("transaction_id", StringType()),
        StructField("user_id", StringType()),
        StructField("agent_id", StringType()),
        StructField("region", StringType()),
        StructField("amount", DoubleType()),
        StructField("hour", IntegerType()),
        StructField("day_of_week", IntegerType()),
        StructField("transaction_type", StringType()),
        StructField("latitude", DoubleType()),
        StructField("longitude", DoubleType()),
        StructField("transactions_last_1h", IntegerType()),
        StructField("avg_amount_7d", DoubleType()),
        StructField("deviation_from_user_pattern", DoubleType()),
        StructField("device_changed", IntegerType()),
        StructField("label_fraud", IntegerType()),
        StructField("fraud_scenario", StringType()),
    ]
)


def main() -> None:
    spark = (
        SparkSession.builder.appName("fog_fraud_monitoring")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    raw_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC_TRANSACTIONS)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed_df = raw_df.selectExpr("CAST(value AS STRING) as json_str", "timestamp").select(
        from_json(col("json_str"), schema).alias("d"), col("timestamp")
    )
    tx_df = parsed_df.select("d.*", "timestamp")

    stats_df = tx_df.groupBy(window(col("timestamp"), "1 minute"), col("region")).agg(
        {"amount": "avg", "transaction_id": "count", "label_fraud": "sum"}
    )

    query = (
        stats_df.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", False)
        .option("numRows", 30)
        .start()
    )
    query.awaitTermination()


if __name__ == "__main__":
    main()
