"""Utilitaires communs (sérialisation, Kafka helpers, etc.)."""
from __future__ import annotations

import json
import logging
from typing import Any

from kafka import KafkaConsumer, KafkaProducer

from common.config import KAFKA_BOOTSTRAP_SERVERS


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def json_serializer(value: Any) -> bytes:
    return json.dumps(value).encode("utf-8")


def json_deserializer(value: bytes) -> Any:
    return json.loads(value.decode("utf-8"))


def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=json_serializer,
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
    )


def build_consumer(topic: str, group_id: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=json_deserializer,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
    )
