"""Dashboard Streamlit pour visualiser fraude et performance FL."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = Path("data/raw/transactions_synthetic.csv")
GLOBAL_UPDATE_FILE = Path("data/models/global_model_update.json")

st.set_page_config(page_title="Mobile Fraud FL Dashboard", layout="wide")
st.title("Détection de fraude Mobile Money (Mauritanie) - Dashboard")

if not DATA_FILE.exists():
    st.warning("Dataset introuvable. Lancez d'abord le simulateur.")
    st.stop()

df = pd.read_csv(DATA_FILE)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transactions", len(df))
col2.metric("Fraudes détectées", int(df["label_fraud"].sum()))
col3.metric("Taux fraude", f"{(df['label_fraud'].mean()*100):.2f}%")
col4.metric("Agents uniques", df["agent_id"].nunique())

left, right = st.columns(2)
with left:
    st.subheader("Fraudes par région")
    fraud_by_region = df.groupby("region", as_index=False)["label_fraud"].sum()
    st.plotly_chart(px.bar(fraud_by_region, x="region", y="label_fraud"), use_container_width=True)

with right:
    st.subheader("Distribution des montants")
    st.plotly_chart(
        px.histogram(df, x="amount", nbins=40, color="label_fraud", barmode="overlay"),
        use_container_width=True,
    )

st.subheader("Dernières transactions suspectes")
st.dataframe(df[df["label_fraud"] == 1].tail(20), use_container_width=True)

st.subheader("Métriques du modèle global")
if GLOBAL_UPDATE_FILE.exists():
    payload = json.loads(GLOBAL_UPDATE_FILE.read_text(encoding="utf-8"))
    st.json(payload.get("metrics", {}))
else:
    st.info("Aucune agrégation globale disponible pour le moment.")
