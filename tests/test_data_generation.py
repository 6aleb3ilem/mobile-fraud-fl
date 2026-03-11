import pandas as pd

from simulator.generate_transactions import generate_dataset


REQUIRED_COLUMNS = {
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
}


def test_generate_dataset_has_expected_columns_and_fraud_ratio():
    df = generate_dataset(n_samples=1000, fraud_ratio=0.2, seed=123)
    assert isinstance(df, pd.DataFrame)
    assert REQUIRED_COLUMNS.issubset(set(df.columns))

    fraud_ratio_observed = df["label_fraud"].mean()
    assert 0.1 <= fraud_ratio_observed <= 0.3
