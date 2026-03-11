"""Dashboard Streamlit pour suivi des fraudes mobiles."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from common.config import FRAUD_RISK_THRESHOLD, MODELS_DIR, RAW_DATA_DIR

st.set_page_config(page_title="Mobile Fraud FL Dashboard", layout="wide")
st.title("Détection de fraude Mobile Money (Mauritanie) - Dashboard")
st.caption("Données 100% synthétiques (Bankily / Masrivi / Sadad cités uniquement comme contexte).")

def load_data() -> pd.DataFrame:
    path = RAW_DATA_DIR / "transactions.csv"
    if not path.exists():
        st.warning("Aucun dataset trouvé. Lancez d'abord la génération de données.")
        return pd.DataFrame()
    return pd.read_csv(path)


def compute_risk_score(df: pd.DataFrame) -> pd.Series:
    score = (
        0.35 * (df["amount"] / (df["avg_amount_7d"] + 1))
        + 0.25 * (df["transactions_last_1h"] / 10)
        + 0.20 * df["deviation_from_user_pattern"]
        + 0.20 * df["device_changed"]
    )
    return score.clip(lower=0, upper=1)


def load_global_metrics() -> dict:
    update_path = Path(MODELS_DIR) / "global_model_update.json"
    if update_path.exists():
        d = json.loads(update_path.read_text(encoding="utf-8"))
        return {
            "contributors": ", ".join(d.get("contributors", [])),
            "total_samples": d.get("total_samples", 0),
            "round": d.get("round", 0),
        }
    return {"contributors": "N/A", "total_samples": 0, "round": 0}


df = load_data()
if df.empty:
    st.stop()

df["risk_score"] = compute_risk_score(df)
df["is_suspect"] = (df["risk_score"] >= FRAUD_RISK_THRESHOLD).astype(int)
blocked = int(((df["is_suspect"] == 1) & (df["label_fraud"] == 1)).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Transactions totales", len(df))
c2.metric("Fraudes réelles (label)", int(df["label_fraud"].sum()))
c3.metric("Transactions suspectes", int(df["is_suspect"].sum()))
c4.metric("Fraudes bloquées (proxy)", blocked)

left, right = st.columns(2)
with left:
    st.subheader("Fraudes par région")
    fraud_region = df[df["label_fraud"] == 1].groupby("region").size().reset_index(name="count")
    st.plotly_chart(px.bar(fraud_region, x="region", y="count", color="region"), use_container_width=True)

with right:
    st.subheader("Distribution du score de risque")
    st.plotly_chart(px.histogram(df, x="risk_score", nbins=25, color="label_fraud"), use_container_width=True)

st.subheader("Dernières alertes")
alerts = df[df["is_suspect"] == 1].sort_values("transaction_id", ascending=False).head(20)
st.dataframe(alerts[["transaction_id", "region", "agent_id", "amount", "hour", "risk_score", "label_fraud"]])

st.subheader("Métriques modèle global (FedAvg)")
metrics = load_global_metrics()
st.json(metrics)
