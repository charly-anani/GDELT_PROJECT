"""
Dashboard Streamlit — Bénin Insights Challenge
iSHEERO x DataCamp Donates 2026

Lancement local :
    streamlit run dashboard/app.py

Déploiement :
    1. Pousser sur GitHub
    2. Aller sur share.streamlit.io
    3. Connecter le repo, pointer sur dashboard/app.py
    4. Ajouter le secret GCP dans Settings > Secrets :
       [gcp_service_account]
       ... (contenu du JSON de service account)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import joblib
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bénin Insights 2025",
    page_icon="BJ",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT = 'gdelt-494812'
DATASET = 'benin_2025'

# ─── Connexion BigQuery ───────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    from google.cloud import bigquery
    try:
        # En production Streamlit Cloud : utilise les secrets
        import json
        from google.oauth2 import service_account
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        return bigquery.Client(credentials=creds, project=PROJECT)
    except Exception:
        # En local : utilise l'auth par défaut (gcloud auth application-default login)
        return bigquery.Client(project=PROJECT)

client = get_client()

def bq(sql):
    return client.query(sql).to_dataframe()

# ─── Chargement des données ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_events():
    df = bq(f"SELECT * FROM `{PROJECT}.{DATASET}.events_clean` LIMIT 100000")

    # Détecter colonnes automatiquement
    def fc(keywords):
        for kw in keywords:
            for c in df.columns:
                if kw.lower() in c.lower():
                    return c
        return None

    col_date  = fc(['date', 'sqldate'])
    col_tone  = fc(['tone', 'avgtone'])
    col_gold  = fc(['goldstein'])
    col_quad  = fc(['quadclass', 'quad_class', 'category'])
    col_lat   = fc(['lat', 'latitude'])
    col_lon   = fc(['lon', 'long', 'longitude'])
    col_loc   = fc(['location', 'fullname', 'geo_name'])
    col_act1  = fc(['actor1name', 'actor1'])
    col_act2  = fc(['actor2name', 'actor2'])
    col_ment  = fc(['nummentions', 'mentions'])

    meta = {
        'date': col_date, 'tone': col_tone, 'goldstein': col_gold,
        'quad': col_quad, 'lat': col_lat, 'lon': col_lon,
        'loc': col_loc, 'act1': col_act1, 'act2': col_act2, 'mentions': col_ment
    }

    # Préparer colonnes de travail
    if col_date:
        df['_date']  = pd.to_datetime(df[col_date].astype(str), errors='coerce')
        df['_month'] = df['_date'].dt.to_period('M').astype(str)
        df['_week']  = df['_date'].dt.to_period('W').astype(str)

    QUAD_MAP = {1: 'Coopération verbale', 2: 'Coopération matérielle',
                3: 'Conflit verbal', 4: 'Conflit matériel'}
    if col_quad:
        df[col_quad] = pd.to_numeric(df[col_quad], errors='coerce')
        df['_category'] = df[col_quad].map(QUAD_MAP).fillna('Inconnu')

    if col_tone:
        df[col_tone] = pd.to_numeric(df[col_tone], errors='coerce')
        df['_sentiment'] = pd.cut(
            df[col_tone], bins=[-999, -2, 2, 999],
            labels=['Negatif', 'Neutre', 'Positif']
        ).astype(str)

    if col_gold:
        df[col_gold] = pd.to_numeric(df[col_gold], errors='coerce')

    if col_lat:
        df[col_lat] = pd.to_numeric(df[col_lat], errors='coerce')
    if col_lon:
        df[col_lon] = pd.to_numeric(df[col_lon], errors='coerce')

    return df, meta

@st.cache_data(ttl=3600)
def load_gkg():
    return bq(f"SELECT * FROM `{PROJECT}.{DATASET}.gkg_clean` LIMIT 30000")

# ─── Chargement ───────────────────────────────────────────────────────────────
with st.spinner("Connexion à BigQuery en cours..."):
    df, meta = load_events()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.title("Filtres")
st.sidebar.caption(f"Source : `{PROJECT}.{DATASET}`")

# Filtre temporel
if '_month' in df.columns:
    months = sorted(df['_month'].dropna().unique())
    selected_months = st.sidebar.multiselect(
        "Mois", months, default=months,
        help="Sélectionner un ou plusieurs mois"
    )
else:
    selected_months = None

# Filtre catégorie
if '_category' in df.columns:
    cats = ['Toutes'] + sorted(df['_category'].dropna().unique().tolist())
    selected_cat = st.sidebar.selectbox("Type d'événement", cats)
else:
    selected_cat = 'Toutes'

# Filtre sentiment
if '_sentiment' in df.columns:
    sents = ['Tous'] + sorted(df['_sentiment'].dropna().unique().tolist())
    selected_sent = st.sidebar.selectbox("Sentiment", sents)
else:
    selected_sent = 'Tous'

# Appliquer filtres
dff = df.copy()
if selected_months and '_month' in dff.columns:
    dff = dff[dff['_month'].isin(selected_months)]
if selected_cat != 'Toutes' and '_category' in dff.columns:
    dff = dff[dff['_category'] == selected_cat]
if selected_sent != 'Tous' and '_sentiment' in dff.columns:
    dff = dff[dff['_sentiment'] == selected_sent]

# ─── En-tête ─────────────────────────────────────────────────────────────────
st.title("Bénin dans les médias mondiaux")
st.caption("Analyse GDELT 2025 · iSHEERO x DataCamp Donates Hackathon 2026")

# ─── KPIs ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Événements", f"{len(dff):,}")

if meta['tone'] and meta['tone'] in dff.columns:
    avg_tone = dff[meta['tone']].mean()
    k2.metric("Ton moyen", f"{avg_tone:.2f}",
              delta="Positif" if avg_tone > 0 else "Négatif",
              delta_color="normal" if avg_tone > 0 else "inverse")

if meta['goldstein'] and meta['goldstein'] in dff.columns:
    avg_gold = dff[meta['goldstein']].mean()
    k3.metric("Goldstein moyen", f"{avg_gold:.2f}",
              delta="Stabilisant" if avg_gold >= 0 else "Déstabilisant",
              delta_color="normal" if avg_gold >= 0 else "inverse")

if '_category' in dff.columns:
    dominant = dff['_category'].mode()
    k4.metric("Type dominant", dominant[0] if len(dominant) > 0 else "—")

if '_sentiment' in dff.columns:
    pct_pos = (dff['_sentiment'] == 'Positif').mean() * 100
    k5.metric("Couverture positive", f"{pct_pos:.1f}%")

st.divider()

# ─── VIZ 1 : Timeline ────────────────────────────────────────────────────────
st.subheader("Volume d'événements par mois")

col_a, col_b = st.columns([2, 1])
with col_a:
    if '_month' in dff.columns:
        monthly = dff.groupby('_month').size().reset_index(name='n')
        monthly = monthly.sort_values('_month')
        fig = px.line(monthly, x='_month', y='n', markers=True,
                      labels={'_month': 'Mois', 'n': "Événements"},
                      color_discrete_sequence=['#e91e8c'], height=300)
        fig.update_layout(xaxis_tickangle=-30, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    if '_category' in dff.columns:
        cat_c = dff['_category'].value_counts().reset_index()
        cat_c.columns = ['cat', 'n']
        fig2 = px.pie(cat_c, names='cat', values='n', hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Pastel,
                      height=300)
        fig2.update_layout(margin=dict(t=20), showlegend=True,
                            legend=dict(orientation='v', font_size=10))
        st.plotly_chart(fig2, use_container_width=True)

# ─── VIZ 2 : Ton + Goldstein ─────────────────────────────────────────────────
st.subheader("Évolution du ton médiatique et de la stabilité")

if '_month' in dff.columns and meta['tone'] and meta['goldstein']:
    agg = dff.groupby('_month').agg(
        tone=(meta['tone'], 'mean'),
        gold=(meta['goldstein'], 'mean')
    ).reset_index().sort_values('_month')

    fig3 = make_subplots(rows=1, cols=2,
        subplot_titles=['Ton médiatique moyen', 'Score de stabilité (Goldstein)'])
    fig3.add_trace(
        go.Bar(x=agg['_month'], y=agg['tone'],
               marker_color=['#e91e8c' if v < 0 else '#00b894' for v in agg['tone']],
               name='Ton'), row=1, col=1)
    fig3.add_trace(
        go.Bar(x=agg['_month'], y=agg['gold'],
               marker_color=['#e17055' if v < 0 else '#0984e3' for v in agg['gold']],
               name='Goldstein'), row=1, col=2)
    fig3.add_hline(y=0, line_dash='dash', line_color='black', row=1, col=1)
    fig3.add_hline(y=0, line_dash='dash', line_color='black', row=1, col=2)
    fig3.update_layout(height=350, showlegend=False)
    fig3.update_xaxes(tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

# ─── VIZ 3 : Carte ───────────────────────────────────────────────────────────
st.subheader("Carte des événements au Bénin")

if meta['lat'] and meta['lon']:
    geo = dff.dropna(subset=[meta['lat'], meta['lon']]).copy()
    geo = geo[geo[meta['lat']].between(6.0, 12.5) & geo[meta['lon']].between(0.5, 4.0)]

    if len(geo) > 0:
        fig4 = px.scatter_mapbox(
            geo.head(5000),
            lat=meta['lat'], lon=meta['lon'],
            color='_category' if '_category' in geo.columns else None,
            hover_name=meta['loc'] if meta['loc'] else None,
            size=meta['mentions'] if meta['mentions'] and meta['mentions'] in geo.columns else None,
            size_max=18,
            zoom=6.5, center={'lat': 9.3, 'lon': 2.3},
            mapbox_style='open-street-map',
            opacity=0.6, height=470
        )
        fig4.update_layout(margin=dict(t=10))
        st.plotly_chart(fig4, use_container_width=True)
        st.caption(f"{len(geo):,} événements géolocalisés dans la bounding box Bénin.")
    else:
        st.info("Aucun événement géolocalisé avec les filtres actuels.")
else:
    st.info("Coordonnées géographiques non disponibles.")

# ─── VIZ 4 : Top acteurs ─────────────────────────────────────────────────────
st.subheader("Acteurs les plus mentionnés")

col_c, col_d = st.columns([3, 2])
with col_c:
    if meta['act1'] or meta['act2']:
        parts = []
        if meta['act1'] and meta['act1'] in dff.columns:
            parts.append(dff[meta['act1']].dropna())
        if meta['act2'] and meta['act2'] in dff.columns:
            parts.append(dff[meta['act2']].dropna())
        actors = pd.concat(parts)
        actors = actors[actors.str.strip().str.len() > 2]
        top = actors.value_counts().head(15).reset_index()
        top.columns = ['acteur', 'n']
        fig5 = px.bar(top.sort_values('n'), x='n', y='acteur', orientation='h',
                      color='n', color_continuous_scale='Purples',
                      labels={'n': 'Mentions', 'acteur': ''}, height=420)
        fig5.update_layout(showlegend=False, margin=dict(t=10))
        st.plotly_chart(fig5, use_container_width=True)

with col_d:
    # Heatmap sentiment par catégorie
    if '_category' in dff.columns and '_sentiment' in dff.columns:
        heat = dff.groupby(['_category', '_sentiment']).size().reset_index(name='n')
        heat_piv = heat.pivot(index='_category', columns='_sentiment', values='n').fillna(0)
        fig6 = px.imshow(heat_piv, color_continuous_scale='RdYlGn',
                         title='Sentiment par type d\'événement',
                         text_auto=True, aspect='auto', height=420)
        fig6.update_layout(margin=dict(t=40))
        st.plotly_chart(fig6, use_container_width=True)

# ─── VIZ 5 : Thèmes GKG ──────────────────────────────────────────────────────
st.subheader("Thèmes dominants dans la presse mondiale (GKG)")

with st.expander("Charger les thèmes GDELT GKG (requête supplémentaire)"):
    if st.button("Charger"):
        with st.spinner("Chargement gkg_clean..."):
            gkg = load_gkg()
            col_themes = next((c for c in gkg.columns if 'theme' in c.lower() or 'topic' in c.lower()), None)
            if col_themes:
                sep = ';' if gkg[col_themes].dropna().iloc[0].count(';') > 0 else ','
                themes = gkg[col_themes].dropna().str.split(sep).explode().str.strip()
                themes = themes[themes.str.len() > 2]
                top_themes = themes.value_counts().head(20).reset_index()
                top_themes.columns = ['theme', 'n']
                fig7 = px.bar(top_themes.sort_values('n'), x='n', y='theme',
                              orientation='h', color='n',
                              color_continuous_scale='Blues',
                              title='Top 20 thèmes GDELT liés au Bénin',
                              labels={'n': 'Occurrences', 'theme': ''},
                              height=550)
                fig7.update_layout(showlegend=False)
                st.plotly_chart(fig7, use_container_width=True)
            else:
                st.warning("Colonne 'themes' non trouvée dans gkg_clean.")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
c1, c2 = st.columns(2)
c1.caption("Source : GDELT v2 — Global Database of Events, Language and Tone")
c2.caption("iSHEERO x DataCamp Donates Hackathon 2026 · [isheero.com](https://isheero.com)")
