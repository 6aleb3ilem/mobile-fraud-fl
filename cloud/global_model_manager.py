"""Utilitaires simples pour charger et utiliser le modèle global agrégé."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from common.config import MODELS_DIR


def load_global_update(path: str | None = None) -> dict:
    update_path = Path(path) if path else MODELS_DIR / "global_model_update.json"
    return json.loads(update_path.read_text(encoding="utf-8"))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def score_transactions(feature_matrix: np.ndarray, global_update: dict) -> np.ndarray:
    coef = np.array(global_update["global_coefficients"])
    intercept = float(global_update["global_intercept"])
    logits = feature_matrix @ coef + intercept
    return sigmoid(logits)
