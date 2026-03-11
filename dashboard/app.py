"""Dashboard Streamlit pour visualiser alertes et métriques FL."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mobile Fraud FL", layout="wide")
st.title("Détection de fraude Mobile Money (Mauritanie) - Edge/Fog/Cloud")

fog_latest = Path("data/processed/fog_metrics_latest.json")
global_history = Path("data/models/global_metrics_history.jsonl")

col1, col2, col3, col4 = st.columns(4)

if fog_latest.exists():
    data = json.loads(fog_latest.read_text(encoding="utf-8"))
    total_tx = sum(item["total_transactions"] for item in data["regions"])
    total_frauds = sum(item["frauds_in_batch"] for item in data["regions"])
    hotspots = sorted(data["regions"], key=lambda x: x["frauds_in_batch"], reverse=True)

    col1.metric("Transactions observées", int(total_tx))
    col2.metric("Fraudes détectées (batch)", int(total_frauds))
    col3.metric("Alertes en tampon", int(data.get("alerts_in_buffer", 0)))
    col4.metric("Région la plus touchée", hotspots[0]["region"] if hotspots else "N/A")

    df_region = pd.DataFrame(data["regions"])
    if not df_region.empty:
        fig = px.bar(df_region, x="region", y=["total_transactions", "frauds_in_batch"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Détails régionaux")
        st.dataframe(df_region, use_container_width=True)
else:
    st.warning("Pas encore de métriques Fog disponibles. Lancez les services et attendez un batch.")

st.subheader("Évolution métrique du modèle global")
if global_history.exists():
    rows = [json.loads(line) for line in global_history.read_text(encoding="utf-8").splitlines() if line.strip()]
    df_global = pd.DataFrame(rows)
    if not df_global.empty:
        fig2 = px.line(df_global, x="timestamp", y="global_accuracy_proxy", markers=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(df_global.tail(20), use_container_width=True)
else:
    st.info("Aucune agrégation globale enregistrée pour l'instant.")

st.caption("Données 100% synthétiques, inspirées des usages Mobile Money en Mauritanie (Bankily, Masrivi, Sadad).")
