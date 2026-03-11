"""Utilitaires partagés (Kafka, sérialisation, horodatage)."""

from __future__ import annotations

import json
import time
from typing import Dict, Any

from kafka import KafkaProducer


def json_serializer(data: Dict[str, Any]) -> bytes:
    return json.dumps(data).encode("utf-8")


def get_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=json_serializer)


def now_ts() -> float:
    return time.time()
