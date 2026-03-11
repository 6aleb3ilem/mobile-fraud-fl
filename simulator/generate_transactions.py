"""Génération de données synthétiques Mobile Money pour la fraude."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from common.config import EDGE_REGIONS, RAW_DATA_DIR, RANDOM_SEED, TRANSACTION_TYPES


def _base_transaction(rng: np.random.Generator, idx: int) -> dict:
    region = rng.choice(list(EDGE_REGIONS.values()))
    amount = float(np.clip(rng.gamma(shape=2.2, scale=35), 2, 2500))
    hour = int(rng.integers(0, 24))
    tx_1h = int(rng.poisson(2))
    avg_7d = float(np.clip(amount * rng.uniform(0.5, 1.5), 5, 2000))
    return {
        "transaction_id": f"txn_{idx:08d}",
        "user_id": f"u_{rng.integers(1, 2500):05d}",
        "agent_id": f"a_{rng.integers(1, 180):04d}",
        "region": region,
        "amount": round(amount, 2),
        "hour": hour,
        "day_of_week": int(rng.integers(0, 7)),
        "transaction_type": str(rng.choice(TRANSACTION_TYPES, p=[0.22, 0.2, 0.38, 0.1, 0.1])),
        "latitude": round(float(15.5 + rng.normal(0, 1.1)), 6),
        "longitude": round(float(-10.2 + rng.normal(0, 1.4)), 6),
        "transactions_last_1h": tx_1h,
        "avg_amount_7d": round(avg_7d, 2),
        "deviation_from_user_pattern": round(abs(amount - avg_7d) / max(avg_7d, 1.0), 4),
        "device_changed": int(rng.choice([0, 1], p=[0.92, 0.08])),
        "label_fraud": 0,
        "fraud_scenario": "normal",
    }


def _inject_fraud(tx: dict, rng: np.random.Generator) -> dict:
    scenario = rng.choice(
        [
            "high_amount",
            "night_burst",
            "geo_inconsistency",
            "rapid_beneficiaries",
            "risky_agent",
        ]
    )
    tx["label_fraud"] = 1
    tx["fraud_scenario"] = scenario

    if scenario == "high_amount":
        tx["amount"] = round(float(rng.uniform(1500, 6000)), 2)
        tx["deviation_from_user_pattern"] = round(float(rng.uniform(2.5, 8.0)), 4)
    elif scenario == "night_burst":
        tx["hour"] = int(rng.choice([0, 1, 2, 3, 4]))
        tx["transactions_last_1h"] = int(rng.integers(8, 20))
    elif scenario == "geo_inconsistency":
        tx["latitude"] = round(float(20 + rng.normal(0, 0.2)), 6)
        tx["longitude"] = round(float(-5 + rng.normal(0, 0.2)), 6)
        tx["device_changed"] = 1
    elif scenario == "rapid_beneficiaries":
        tx["transaction_type"] = "p2p"
        tx["transactions_last_1h"] = int(rng.integers(10, 30))
    elif scenario == "risky_agent":
        tx["agent_id"] = f"risk_{rng.integers(1, 12):03d}"
        tx["hour"] = int(rng.choice([22, 23, 0, 1]))
        tx["device_changed"] = 1

    return tx


def generate_dataset(n_samples: int = 5000, fraud_ratio: float = 0.12, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    data = []
    for idx in range(n_samples):
        tx = _base_transaction(rng, idx)
        if rng.random() < fraud_ratio:
            tx = _inject_fraud(tx, rng)
        data.append(tx)
    return pd.DataFrame(data)


def save_dataset(df: pd.DataFrame, out_csv: Path, out_jsonl: Path | None = None) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    if out_jsonl:
        with out_jsonl.open("w", encoding="utf-8") as f:
            for row in df.to_dict(orient="records"):
                f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--fraud-ratio", type=float, default=0.12)
    parser.add_argument("--output", type=str, default=str(RAW_DATA_DIR / "transactions.csv"))
    args = parser.parse_args()

    df = generate_dataset(n_samples=args.samples, fraud_ratio=args.fraud_ratio)
    out_csv = Path(args.output)
    out_jsonl = out_csv.with_suffix(".jsonl")
    save_dataset(df, out_csv, out_jsonl)
    print(f"Dataset généré: {out_csv} ({len(df)} lignes)")
