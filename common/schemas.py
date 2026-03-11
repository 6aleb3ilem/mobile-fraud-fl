"""Schémas de données simplifiés."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TransactionRecord:
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
        return self.__dict__.copy()
