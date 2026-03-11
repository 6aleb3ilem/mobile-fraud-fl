"""Classe de base d'un noeud Edge pour entraînement local."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common.config import KAFKA_TOPIC_LOCAL_MODEL_UPDATES, MODELS_DIR
from common.metrics import classification_metrics
from common.utils import build_producer, get_logger

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
FEATURES_CAT = ["transaction_type"]
TARGET = "label_fraud"


@dataclass
class EdgeTrainingResult:
    edge_node_id: str
    sample_count: int
    metrics: dict
    coefficients: list
    intercept: float


class EdgeNodeTrainer:
    def __init__(self, edge_node_id: str, region: str):
        self.edge_node_id = edge_node_id
        self.region = region
        self.logger = get_logger(edge_node_id)
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.model = SGDClassifier(loss="log_loss", random_state=42, max_iter=1200, tol=1e-3)

    def _filter_region(self, df: pd.DataFrame) -> pd.DataFrame:
        regional_df = df[df["region"] == self.region].copy()
        self.logger.info("%s échantillons pour %s", len(regional_df), self.region)
        return regional_df

    def _prepare_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        x_num = df[FEATURES_NUM].to_numpy(dtype=float)
        x_cat = df[FEATURES_CAT]

        if fit:
            x_num_scaled = self.scaler.fit_transform(x_num)
            x_cat_encoded = self.encoder.fit_transform(x_cat)
        else:
            x_num_scaled = self.scaler.transform(x_num)
            x_cat_encoded = self.encoder.transform(x_cat)
        return np.hstack([x_num_scaled, x_cat_encoded])

    def train(self, full_df: pd.DataFrame) -> EdgeTrainingResult:
        df = self._filter_region(full_df)
        if len(df) < 30:
            raise ValueError(f"Pas assez de données pour {self.edge_node_id}")

        y = df[TARGET].astype(int).values
        x_train, x_test, y_train, y_test = train_test_split(df, y, test_size=0.25, random_state=42, stratify=y)

        x_train_prepared = self._prepare_features(x_train, fit=True)
        x_test_prepared = self._prepare_features(x_test, fit=False)

        self.model.fit(x_train_prepared, y_train)
        y_pred = self.model.predict(x_test_prepared)
        metrics = classification_metrics(y_test, y_pred)

        model_bundle = {
            "model": self.model,
            "scaler": self.scaler,
            "encoder": self.encoder,
            "features_num": FEATURES_NUM,
            "features_cat": FEATURES_CAT,
        }
        model_path = MODELS_DIR / f"{self.edge_node_id}.joblib"
        joblib.dump(model_bundle, model_path)

        result = EdgeTrainingResult(
            edge_node_id=self.edge_node_id,
            sample_count=len(df),
            metrics=metrics,
            coefficients=self.model.coef_[0].tolist(),
            intercept=float(self.model.intercept_[0]),
        )
        self.logger.info("Entraînement terminé %s => %s", self.edge_node_id, metrics)
        return result

    def publish_update(self, result: EdgeTrainingResult) -> None:
        producer = build_producer()
        payload = asdict(result)
        producer.send(KAFKA_TOPIC_LOCAL_MODEL_UPDATES, key=result.edge_node_id, value=payload)
        producer.flush()
        self.logger.info("Update local publié pour %s", self.edge_node_id)
