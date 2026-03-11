"""Générateur de transactions synthétiques Mobile Money (Mauritanie)."""

from __future__ import annotations

import argparse
import random
import uuid
from typing import List

import numpy as np
import pandas as pd

REGIONS = {
    "Nouakchott": (18.0735, -15.9582),
    "Rosso": (16.5138, -15.8050),
    "Kaedi": (16.1500, -13.5000),
    "Nouadhibou": (20.9425, -17.0362),
}

TRANSACTION_TYPES = ["cash_in", "cash_out", "merchant_payment", "p2p_transfer", "bill_payment"]
RISKY_AGENTS = {"AGENT-ROSSO-3", "AGENT-KAEDI-2"}


def _generate_one(index: int, fraud_ratio: float) -> dict:
    region = random.choice(list(REGIONS.keys()))
    lat0, lon0 = REGIONS[region]

    user_id = f"USR-{random.randint(1, 1200):04d}"
    agent_id = f"AGENT-{region.upper()}-{random.randint(1, 5)}"
    hour = random.randint(0, 23)
    dow = random.randint(0, 6)

    base_amount = max(50, np.random.lognormal(mean=4.2, sigma=0.75))
    tx_last_1h = np.random.poisson(2)
    avg_amount_7d = max(30, np.random.lognormal(mean=4.0, sigma=0.55))
    deviation = abs(base_amount - avg_amount_7d) / max(avg_amount_7d, 1)
    device_changed = np.random.binomial(1, 0.08)

    fraud = 0
    fraud_signals = []

    if random.random() < fraud_ratio:
        fraud = 1
        fraud_case = random.choice(
            [
                "high_amount",
                "burst_transactions",
                "night_activity",
                "location_shift",
                "rapid_multi_beneficiary",
                "risky_agent_profile",
                "hour_location_frequency_incoherence",
            ]
        )

        if fraud_case == "high_amount":
            base_amount *= random.uniform(4, 8)
            fraud_signals.append("montant_anormalement_eleve")
        elif fraud_case == "burst_transactions":
            tx_last_1h += random.randint(12, 25)
            fraud_signals.append("forte_frequence")
        elif fraud_case == "night_activity":
            hour = random.choice([0, 1, 2, 3, 4])
            fraud_signals.append("transaction_nocturne")
        elif fraud_case == "location_shift":
            lat0 += random.uniform(0.8, 1.8)
            lon0 += random.uniform(0.8, 1.8)
            fraud_signals.append("localisation_inhabituelle")
        elif fraud_case == "rapid_multi_beneficiary":
            tx_last_1h += random.randint(10, 20)
            base_amount *= random.uniform(1.2, 2.0)
            fraud_signals.append("beneficiaires_multiples_rapides")
        elif fraud_case == "risky_agent_profile":
            agent_id = random.choice(list(RISKY_AGENTS))
            fraud_signals.append("agent_a_risque")
        elif fraud_case == "hour_location_frequency_incoherence":
            hour = random.choice([1, 2, 3, 4])
            tx_last_1h += random.randint(8, 15)
            lat0 += random.uniform(0.5, 1.4)
            fraud_signals.append("incoherence_multifactor")

    return {
        "transaction_id": f"TX-{index:08d}-{uuid.uuid4().hex[:6]}",
        "user_id": user_id,
        "agent_id": agent_id,
        "region": region,
        "amount": round(float(base_amount), 2),
        "hour": hour,
        "day_of_week": dow,
        "transaction_type": random.choice(TRANSACTION_TYPES),
        "latitude": round(lat0 + random.uniform(-0.04, 0.04), 6),
        "longitude": round(lon0 + random.uniform(-0.04, 0.04), 6),
        "transactions_last_1h": int(tx_last_1h),
        "avg_amount_7d": round(float(avg_amount_7d), 2),
        "deviation_from_user_pattern": round(float(deviation), 3),
        "device_changed": int(device_changed),
        "label_fraud": int(fraud),
        "fraud_signals": fraud_signals,
    }


def generate_dataset(n_rows: int = 5000, fraud_ratio: float = 0.15, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)
    rows: List[dict] = [_generate_one(i, fraud_ratio) for i in range(n_rows)]
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--fraud-ratio", type=float, default=0.15)
    parser.add_argument("--output", type=str, default="data/raw/simulated_transactions.csv")
    args = parser.parse_args()

    df = generate_dataset(args.rows, args.fraud_ratio)
    df.to_csv(args.output, index=False)
    print(f"Dataset généré: {args.output} ({len(df)} lignes)")


if __name__ == "__main__":
    main()
