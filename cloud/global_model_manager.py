"""Gestionnaire simple du modèle global (lecture des updates)."""

from __future__ import annotations

import json
from pathlib import Path

from common.config import MODELS_DIR


def load_global_update() -> dict:
    path = MODELS_DIR / "global_model_update.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_global_metrics_snapshot() -> Path:
    update = load_global_update()
    snapshot_path = MODELS_DIR / "global_metrics_snapshot.json"
    payload = update.get("metrics", {})
    snapshot_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return snapshot_path


if __name__ == "__main__":
    print(load_global_update())
