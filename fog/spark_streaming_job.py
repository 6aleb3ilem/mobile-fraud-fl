"""Job Spark Structured Streaming pour monitoring des transactions."""

from __future__ import annotations

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, from_json, sum as spark_sum
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

from common.config import KAFKA_BOOTSTRAP_SERVERS, TRANSACTIONS_TOPIC


def main() -> None:
    spark = (
        SparkSession.builder.appName("FraudMonitoringStreaming")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )

    schema = StructType(
        [
            StructField("transaction_id", StringType()),
            StructField("agent_id", StringType()),
            StructField("region", StringType()),
            StructField("amount", DoubleType()),
            StructField("hour", IntegerType()),
            StructField("label_fraud", IntegerType()),
        ]
    )

    raw_stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TRANSACTIONS_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    tx_stream = raw_stream.select(from_json(col("value").cast("string"), schema).alias("tx")).select("tx.*")

    regional_stats = tx_stream.groupBy("region").agg(
        count("transaction_id").alias("transactions"),
        spark_sum("label_fraud").alias("suspected_fraud"),
    )

    query = (
        regional_stats.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", False)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
