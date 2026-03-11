"""Schemas simples de payloads échangés via Kafka."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class TransactionEvent:
    transaction_id: str
    user_id: str
    agent_id: str
    region: str
    amount: float
    hour: int
    day_of_week: int
    transaction_type: str
    latitude: float
    longitude: float
    transactions_last_1h: int
    avg_amount_7d: float
    deviation_from_user_pattern: float
    device_changed: int
    label_fraud: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LocalModelUpdate:
    edge_node_id: str
    sample_count: int
    coefficients: list[float]
    intercept: float
    metrics: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
