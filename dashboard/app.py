"""Streamlit dashboard entrypoint."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ENRICHED_DIR = ROOT / "data" / "enriched"

st.set_page_config(page_title="GDELT Dashboard", layout="wide")
st.title("Dashboard GDELT")
st.write("Espace de visualisation pour les données enrichies du projet.")
st.info(f"Les fichiers attendus se trouvent dans : {ENRICHED_DIR}")
st.caption("Ajoute ici les métriques, filtres et graphiques au fur et à mesure du projet.")
