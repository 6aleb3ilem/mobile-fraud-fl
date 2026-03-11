"""Entraînement local Edge avec SGDClassifier (logistic regression)."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common.config import MODELS_DIR
from common.metrics import binary_classification_metrics

NUMERIC_FEATURES = [
    "amount",
    "hour",
    "day_of_week",
    "latitude",
    "longitude",
    "transactions_last_1h",
    "avg_amount_7d",
    "deviation_from_user_pattern",
    "device_changed",
]
CATEGORICAL_FEATURES = ["agent_id", "region", "transaction_type"]


def train_local_model(df: pd.DataFrame, edge_name: str) -> dict:
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["label_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = SGDClassifier(loss="log_loss", random_state=42, max_iter=1000, tol=1e-3)

    pipe = Pipeline([("preprocessor", preprocessor), ("model", model)])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    metrics = binary_classification_metrics(y_test, y_pred)

    artifact = {
        "edge_name": edge_name,
        "n_samples": int(len(df)),
        "metrics": metrics,
        "coef": pipe.named_steps["model"].coef_.tolist(),
        "intercept": pipe.named_steps["model"].intercept_.tolist(),
        "classes": pipe.named_steps["model"].classes_.tolist(),
    }

    model_path = MODELS_DIR / f"{edge_name}_pipeline.joblib"
    joblib.dump(pipe, model_path)

    update_path = MODELS_DIR / f"{edge_name}_update.joblib"
    joblib.dump(artifact, update_path)

    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edge", required=True)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    artifact = train_local_model(df, args.edge)
    print(f"Modèle entraîné pour {args.edge}: {artifact['metrics']}")


if __name__ == "__main__":
    main()
