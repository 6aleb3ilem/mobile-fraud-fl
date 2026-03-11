import pandas as pd

from simulator.generate_transactions import generate_dataset


EXPECTED_COLS = {
    "transaction_id",
    "user_id",
    "agent_id",
    "region",
    "amount",
    "hour",
    "day_of_week",
    "transaction_type",
    "latitude",
    "longitude",
    "transactions_last_1h",
    "avg_amount_7d",
    "deviation_from_user_pattern",
    "device_changed",
    "label_fraud",
    "fraud_signals",
}


def test_generate_dataset_schema_and_labels():
    df = generate_dataset(n_rows=500, fraud_ratio=0.2, seed=1)
    assert isinstance(df, pd.DataFrame)
    assert EXPECTED_COLS.issubset(df.columns)
    assert set(df["label_fraud"].unique()).issubset({0, 1})
    assert df["label_fraud"].mean() > 0.05
