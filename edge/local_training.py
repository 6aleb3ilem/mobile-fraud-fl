"""Entraînement local simplifié pour un noeud Edge."""

from __future__ import annotations

import base64
import io
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common.metrics import binary_metrics

FEATURES_NUM = [
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
FEATURES_CAT = ["transaction_type", "region"]
TARGET = "label_fraud"


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), FEATURES_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
        ]
    )
    model = SGDClassifier(loss="log_loss", random_state=42, class_weight="balanced", max_iter=1000)
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def train_local_model(df: pd.DataFrame) -> Tuple[Pipeline, Dict[str, float]]:
    if df[TARGET].nunique() < 2:
        # Protection pédagogique: si un batch local ne contient qu'une classe,
        # on force un petit échantillon synthétique pour éviter un crash.
        additional = df.sample(min(20, len(df)), replace=True).copy()
        additional[TARGET] = 1 - additional[TARGET]
        df = pd.concat([df, additional], ignore_index=True)

    X = df[FEATURES_NUM + FEATURES_CAT]
    y = df[TARGET]

    pipeline = build_pipeline()
    pipeline.fit(X, y)
    pred = pipeline.predict(X)
    return pipeline, binary_metrics(y, pred)


def serialize_pipeline(pipeline: Pipeline) -> str:
    bytes_buffer = io.BytesIO()
    joblib.dump(pipeline, bytes_buffer)
    return base64.b64encode(bytes_buffer.getvalue()).decode("utf-8")


def deserialize_pipeline(encoded: str) -> Pipeline:
    raw = base64.b64decode(encoded.encode("utf-8"))
    return joblib.load(io.BytesIO(raw))


def extract_linear_params(pipeline: Pipeline) -> Dict[str, list]:
    model = pipeline.named_steps["model"]
    return {"coef": model.coef_.tolist(), "intercept": model.intercept_.tolist()}


def inject_linear_params(pipeline: Pipeline, coef: np.ndarray, intercept: np.ndarray) -> Pipeline:
    model = pipeline.named_steps["model"]
    model.coef_ = coef
    model.intercept_ = intercept
    return pipeline
