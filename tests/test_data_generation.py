from simulator.generate_transactions import generate_transactions


def test_generate_transactions_has_expected_columns():
    df = generate_transactions(n_rows=100, seed=123)
    expected_cols = {
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
    assert expected_cols.issubset(set(df.columns))
    assert set(df["label_fraud"].unique()).issubset({0, 1})
    assert len(df) == 100
