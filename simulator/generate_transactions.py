"""Génère un dataset synthétique de transactions Mobile Money."""

from __future__ import annotations

import argparse
import random
from uuid import uuid4

import numpy as np
import pandas as pd

from common.config import RAW_DATA_DIR, REGIONS, TRANSACTION_TYPES
from common.schemas import TRANSACTION_COLUMNS


REGION_COORDS = {
    "Nouakchott": (18.0735, -15.9582),
    "Rosso": (16.5128, -15.8050),
    "Kaedi": (16.1518, -13.5037),
    "Nouadhibou": (20.9425, -17.0362),
    "Atar": (20.5177, -13.0486),
}


def _random_location(region: str) -> tuple[float, float]:
    base_lat, base_lon = REGION_COORDS[region]
    return (
        round(base_lat + np.random.normal(0, 0.05), 6),
        round(base_lon + np.random.normal(0, 0.05), 6),
    )


def generate_transactions(n_rows: int = 5000, n_agents: int = 12, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)

    records = []
    for _ in range(n_rows):
        region = random.choice(REGIONS)
        hour = np.random.randint(0, 24)
        amount = max(100, np.random.lognormal(mean=8.0, sigma=0.75))
        tx_1h = int(np.random.poisson(lam=2))
        avg_7d = max(100, np.random.normal(4500, 1500))
        deviation = abs(amount - avg_7d) / max(1, avg_7d)
        device_changed = int(np.random.binomial(1, 0.08))

        fraud_score = 0
        fraud_score += 2 if amount > 30000 else 0
        fraud_score += 2 if tx_1h > 8 else 0
        fraud_score += 1 if hour <= 5 else 0
        fraud_score += 1 if deviation > 2.5 else 0
        fraud_score += 1 if device_changed == 1 else 0

        label_fraud = 1 if fraud_score >= 3 or np.random.rand() < 0.02 else 0
        lat, lon = _random_location(region)

        records.append(
            {
                "transaction_id": str(uuid4()),
                "user_id": f"user_{np.random.randint(1, 1200):04d}",
                "agent_id": f"agent_{np.random.randint(1, n_agents + 1):03d}",
                "region": region,
                "amount": round(float(amount), 2),
                "hour": int(hour),
                "day_of_week": int(np.random.randint(0, 7)),
                "transaction_type": random.choice(TRANSACTION_TYPES),
                "latitude": lat,
                "longitude": lon,
                "transactions_last_1h": tx_1h,
                "avg_amount_7d": round(float(avg_7d), 2),
                "deviation_from_user_pattern": round(float(deviation), 3),
                "device_changed": device_changed,
                "label_fraud": label_fraud,
            }
        )

    return pd.DataFrame(records, columns=TRANSACTION_COLUMNS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--output", default=str(RAW_DATA_DIR / "transactions_synthetic.csv"))
    args = parser.parse_args()

    df = generate_transactions(n_rows=args.rows)
    df.to_csv(args.output, index=False)
    print(f"Dataset généré: {args.output} ({len(df)} lignes)")


if __name__ == "__main__":
    main()
