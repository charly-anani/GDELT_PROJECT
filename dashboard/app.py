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

# ─── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bénin Insights 2025",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT = 'gdelt-494812'
DATASET = 'benin_2025'

# ─── Palette cohérente avec le notebook ──────────────────────────────────────
COLOR_COOP_DARK  = "#F5A800"
COLOR_COOP_LIGHT = "#FFD166"
COLOR_CONF_DARK  = "#E45756"
COLOR_CONF_LIGHT = "#FF9E9E"
COLOR_LINE       = "#2F6BFF"
COLOR_POS        = "#2CB1A1"
COLOR_NEG        = "#E45756"

QUAD_MAP = {
    1: 'Coopération verbale',
    2: 'Coopération matérielle',
    3: 'Conflit verbal',
    4: 'Conflit matériel'
}

# ─── Connexion BigQuery ───────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    from google.cloud import bigquery
    try:
        import json
        from google.oauth2 import service_account
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        return bigquery.Client(credentials=creds, project=PROJECT)
    except Exception:
        return bigquery.Client(project=PROJECT)

client = get_client()

def bq(sql):
    return client.query(sql).to_dataframe()

# ─── Chargement des données ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_events():
    # CORRECTION : utilise MonthYear (nom réel dans BigQuery, confirmé par le notebook)
    # et récupère les colonnes réelles identifiées dans l'exploration
    df = bq(f"""
        SELECT
            GLOBALEVENTID,
            MonthYear,
            Year,
            QuadClass                          AS quad_class,
            QuadClass_Label,
            interaction_type,
            GoldsteinScale,
            AvgTone,
            Actor1Name,
            Actor2Name,
            ActionGeo_FullName                 AS geo_name,
            ActionGeo_Lat                      AS lat,
            ActionGeo_Long                     AS lon,
            ActionGeo_CountryCode,
            NumMentions,
            EventCategory
        FROM `{PROJECT}.{DATASET}.events_clean`
        WHERE CAST(Year AS INT64) = 2025
        LIMIT 100000
    """)

    # ── Dates ─────────────────────────────────────────────────────────────────
    # MonthYear est un entier YYYYMM (ex: 202501) → conversion correcte
    df['_date'] = pd.to_datetime(df['MonthYear'].astype(str), format='%Y%m', errors='coerce')
    df = df[df['_date'].notna()]
    df['_month'] = df['_date'].dt.to_period('M').astype(str)

    # ── Catégorie (QuadClass) ──────────────────────────────────────────────────
    # Utilise QuadClass_Label en priorité (déjà lisible), sinon mappe QuadClass
    if 'QuadClass_Label' in df.columns and df['QuadClass_Label'].notna().any():
        df['_category'] = df['QuadClass_Label'].fillna('Inconnu')
    else:
        df['quad_class'] = pd.to_numeric(df['quad_class'], errors='coerce')
        df['_category'] = df['quad_class'].map(QUAD_MAP).fillna('Inconnu')

    # ── Type d'interaction ────────────────────────────────────────────────────
    # interaction_type existe dans BigQuery (confirmé notebook) : 'Cooperation' / 'Conflict'
    if 'interaction_type' not in df.columns or df['interaction_type'].isna().all():
        # Fallback calculé depuis QuadClass si la colonne est absente
        df['interaction_type'] = df['quad_class'].apply(
            lambda x: 'Cooperation' if x in [1, 2] else ('Conflict' if x in [3, 4] else np.nan)
        )

    # ── Sentiment (AvgTone) ───────────────────────────────────────────────────
    df['AvgTone'] = pd.to_numeric(df['AvgTone'], errors='coerce')
    df['_sentiment'] = np.select(
        [df['AvgTone'] < -2, df['AvgTone'] > 2],
        ['Négatif', 'Positif'],
        default='Neutre'
    )
    df.loc[df['AvgTone'].isna(), '_sentiment'] = np.nan

    # ── Goldstein ─────────────────────────────────────────────────────────────
    df['GoldsteinScale'] = pd.to_numeric(df['GoldsteinScale'], errors='coerce')

    # ── Coordonnées ───────────────────────────────────────────────────────────
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df['NumMentions'] = pd.to_numeric(df['NumMentions'], errors='coerce')

    return df


@st.cache_data(ttl=3600)
def load_gkg():
    # CORRECTION : requête alignée sur le notebook — V2Tone et tone_category existent
    return bq(f"""
        SELECT
            DATE,
            V2Tone,
            tone_category,
            V2Themes
        FROM `{PROJECT}.{DATASET}.gkg_clean`
        WHERE DATE IS NOT NULL AND V2Tone IS NOT NULL
        LIMIT 30000
    """)


@st.cache_data(ttl=3600)
def load_mentions_lang():
    """Répartition des langues — nouvelle section inspirée du notebook."""
    return bq(f"""
        SELECT
            m.source_language AS langue,
            COUNT(*)          AS nb_mentions
        FROM `{PROJECT}.{DATASET}.mentions_clean` m
        JOIN `{PROJECT}.{DATASET}.events_clean`   e
          ON m.GLOBALEVENTID = e.GLOBALEVENTID
        WHERE e.ActionGeo_CountryCode = 'BN'
          AND CAST(e.Year AS INT64) = 2025
          AND m.source_language IS NOT NULL
        GROUP BY langue
        ORDER BY nb_mentions DESC
        LIMIT 8
    """)


# ─── Chargement ───────────────────────────────────────────────────────────────
with st.spinner("Connexion à BigQuery en cours..."):
    df = load_events()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.title("Filtres")
st.sidebar.caption(f"Source : `{PROJECT}.{DATASET}`")

# Filtre temporel
months = sorted(df['_month'].dropna().unique())
selected_months = st.sidebar.multiselect(
    "Mois", months, default=months,
    help="Sélectionner un ou plusieurs mois"
)

# Filtre catégorie
cats = ['Toutes'] + sorted(df['_category'].dropna().unique().tolist())
selected_cat = st.sidebar.selectbox("Type d'événement", cats)

# Filtre interaction (nouveau — confirmé par le notebook)
interaction_opts = ['Tous'] + sorted(df['interaction_type'].dropna().unique().tolist())
selected_interaction = st.sidebar.selectbox("Interaction", interaction_opts)

# Filtre sentiment
sents = ['Tous'] + sorted(df['_sentiment'].dropna().unique().tolist())
selected_sent = st.sidebar.selectbox("Sentiment", sents)

# Appliquer filtres
dff = df.copy()
if selected_months:
    dff = dff[dff['_month'].isin(selected_months)]
if selected_cat != 'Toutes':
    dff = dff[dff['_category'] == selected_cat]
if selected_interaction != 'Tous':
    dff = dff[dff['interaction_type'] == selected_interaction]
if selected_sent != 'Tous':
    dff = dff[dff['_sentiment'] == selected_sent]

# ─── En-tête ─────────────────────────────────────────────────────────────────
st.title("🇧🇯 Bénin dans les médias mondiaux")
st.caption("Analyse GDELT 2025 · iSHEERO x DataCamp Donates Hackathon 2026")

# ─── KPIs ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Événements", f"{len(dff):,}")

if 'AvgTone' in dff.columns:
    avg_tone = dff['AvgTone'].mean()
    if pd.notna(avg_tone):
        k2.metric(
            "Ton moyen",
            f"{avg_tone:.2f}",
            delta="Positif" if avg_tone > 0 else "Négatif",
            delta_color="normal" if avg_tone > 0 else "inverse"
        )

if 'GoldsteinScale' in dff.columns:
    avg_gold = dff['GoldsteinScale'].mean()
    if pd.notna(avg_gold):
        k3.metric(
            "Goldstein moyen",
            f"{avg_gold:.2f}",
            delta="Stabilisant" if avg_gold >= 0 else "Déstabilisant",
            delta_color="normal" if avg_gold >= 0 else "inverse"
        )

if 'interaction_type' in dff.columns:
    # AMÉLIORATION : ratio coopération/conflit (insight clé du notebook : 2.9:1)
    coop_n = (dff['interaction_type'] == 'Cooperation').sum()
    conf_n = (dff['interaction_type'] == 'Conflict').sum()
    ratio = coop_n / conf_n if conf_n > 0 else float('inf')
    k4.metric("Ratio Coop/Conflit", f"{ratio:.1f}x",
              help="Nombre d'événements coopératifs pour 1 conflit")

if '_sentiment' in dff.columns:
    pct_pos = (dff['_sentiment'] == 'Positif').mean() * 100
    k5.metric("Couverture positive", f"{pct_pos:.1f}%")

st.divider()

# ─── VIZ 1 : Timeline + Répartition ─────────────────────────────────────────
st.subheader("Volume d'événements par mois")

col_a, col_b = st.columns([2, 1])
with col_a:
    monthly = dff.groupby('_month').size().reset_index(name='n').sort_values('_month')
    # AMÉLIORATION : colorer le pic (déc) et le creux (juin) comme dans le notebook
    max_idx = monthly['n'].idxmax()
    min_idx = monthly['n'].idxmin()
    colors_bar = ['#E45756' if i == max_idx else ('#FFD166' if i == min_idx else '#2F6BFF')
                  for i in monthly.index]
    fig = go.Figure(go.Bar(
        x=monthly['_month'], y=monthly['n'],
        marker_color=colors_bar,
        hovertemplate="<b>%{x}</b><br>Événements : %{y:,}<extra></extra>"
    ))
    fig.update_layout(
        xaxis_tickangle=-30, margin=dict(t=20), height=300,
        xaxis_title="Mois", yaxis_title="Événements"
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    # CORRECTION : utilise interaction_type (données réelles) au lieu du donut QuadClass
    if 'interaction_type' in dff.columns:
        it_counts = dff['interaction_type'].value_counts().reset_index()
        it_counts.columns = ['type', 'n']
        fig_donut = px.pie(
            it_counts, names='type', values='n', hole=0.45,
            color='type',
            color_discrete_map={'Cooperation': COLOR_COOP_DARK, 'Conflict': COLOR_CONF_DARK},
            height=300
        )
        fig_donut.update_layout(margin=dict(t=20), showlegend=True,
                                 legend=dict(orientation='v', font_size=10))
        total_donut = it_counts['n'].sum()
        fig_donut.add_annotation(
            text=f"<b>{total_donut:,}</b><br>évts",
            x=0.5, y=0.5, showarrow=False, font=dict(size=11)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

# ─── VIZ 2 : Ton + Goldstein ─────────────────────────────────────────────────
st.subheader("Évolution du ton médiatique et de la stabilité")

agg = dff.groupby('_month').agg(
    tone=('AvgTone', 'mean'),
    gold=('GoldsteinScale', 'mean')
).reset_index().sort_values('_month')

fig3 = make_subplots(rows=1, cols=2,
    subplot_titles=['Ton médiatique moyen (AvgTone)', 'Score de stabilité (Goldstein)'])
fig3.add_trace(
    go.Bar(x=agg['_month'], y=agg['tone'],
           marker_color=[COLOR_NEG if v < 0 else COLOR_POS for v in agg['tone']],
           hovertemplate="<b>%{x}</b><br>Ton : %{y:.2f}<extra></extra>",
           name='Ton'), row=1, col=1)
fig3.add_trace(
    go.Bar(x=agg['_month'], y=agg['gold'],
           marker_color=['#e17055' if v < 0 else '#0984e3' for v in agg['gold']],
           hovertemplate="<b>%{x}</b><br>Goldstein : %{y:.2f}<extra></extra>",
           name='Goldstein'), row=1, col=2)
fig3.add_hline(y=0, line_dash='dash', line_color='gray', row=1, col=1)
fig3.add_hline(y=0, line_dash='dash', line_color='gray', row=1, col=2)
fig3.update_layout(height=350, showlegend=False)
fig3.update_xaxes(tickangle=-30)
st.plotly_chart(fig3, use_container_width=True)

# ─── VIZ 3 : Coopération vs Conflit dans le temps (NOUVELLE — notebook Q2) ───
st.subheader("Coopération vs Conflit — Évolution mensuelle")

if 'interaction_type' in dff.columns:
    coop_time = dff.groupby(['_month', 'interaction_type']).size().reset_index(name='n')
    coop_time = coop_time.sort_values('_month')
    fig_coop = px.line(
        coop_time, x='_month', y='n', color='interaction_type',
        markers=True,
        color_discrete_map={'Cooperation': COLOR_COOP_DARK, 'Conflict': COLOR_CONF_DARK},
        labels={'_month': 'Mois', 'n': 'Événements', 'interaction_type': "Type d'interaction"},
        height=320
    )
    fig_coop.update_traces(line=dict(width=2.5), marker=dict(size=7))
    fig_coop.update_layout(hovermode='x unified', xaxis_tickangle=-30, margin=dict(t=10))
    st.plotly_chart(fig_coop, use_container_width=True)
    st.caption("📌 La coopération domine chaque mois (ratio min 2:1). Décembre : explosion simultanée des deux dynamiques.")

# ─── VIZ 4 : Carte ───────────────────────────────────────────────────────────
st.subheader("Carte des événements au Bénin")

geo = dff.dropna(subset=['lat', 'lon']).copy()
# CORRECTION : bounding box précise du Bénin (confirmée notebook)
geo = geo[geo['lat'].between(6.0, 12.5) & geo['lon'].between(0.5, 4.0)]

if len(geo) > 0:
    fig4 = px.scatter_mapbox(
        geo.head(5000),
        lat='lat', lon='lon',
        color='interaction_type',  # CORRECTION : colonne réelle
        color_discrete_map={'Cooperation': COLOR_COOP_DARK, 'Conflict': COLOR_CONF_DARK},
        hover_name='geo_name',
        size='NumMentions',
        size_max=18,
        zoom=6.5, center={'lat': 9.3, 'lon': 2.3},
        mapbox_style='open-street-map',
        opacity=0.65, height=480,
        labels={'interaction_type': "Type"}
    )
    fig4.update_layout(margin=dict(t=10))
    st.plotly_chart(fig4, use_container_width=True)
    st.caption(
        f"{len(geo):,} événements géolocalisés dans la bounding box Bénin. "
        "⚠️ ~93% des événements GDELT sont au centroïde national (9.5°N, 2.25°E) — "
        "filtrez avec zoom pour voir les villes précises."
    )
else:
    st.info("Aucun événement géolocalisé avec les filtres actuels.")

# ─── VIZ 5 : Top acteurs ─────────────────────────────────────────────────────
st.subheader("Acteurs les plus mentionnés")

col_c, col_d = st.columns([3, 2])
with col_c:
    parts = []
    for col in ['Actor1Name', 'Actor2Name']:
        if col in dff.columns:
            parts.append(dff[col].dropna().astype(str))
    if parts:
        actors = pd.concat(parts)
        actors = actors[actors.str.strip().str.len() > 2]
        top = actors.value_counts().head(15).reset_index()
        top.columns = ['acteur', 'n']
        fig5 = px.bar(
            top.sort_values('n'), x='n', y='acteur', orientation='h',
            color='n', color_continuous_scale='Purples',
            labels={'n': 'Mentions', 'acteur': ''}, height=420
        )
        fig5.update_layout(showlegend=False, margin=dict(t=10))
        st.plotly_chart(fig5, use_container_width=True)

with col_d:
    # Heatmap sentiment par catégorie
    if '_category' in dff.columns and '_sentiment' in dff.columns:
        heat = dff.groupby(['_category', '_sentiment']).size().reset_index(name='n')
        heat_piv = heat.pivot(index='_category', columns='_sentiment', values='n').fillna(0)
        fig6 = px.imshow(
            heat_piv, color_continuous_scale='RdYlGn',
            title="Sentiment par type d'événement",
            text_auto=True, aspect='auto', height=420
        )
        fig6.update_layout(margin=dict(t=40))
        st.plotly_chart(fig6, use_container_width=True)

# ─── VIZ 6 : Catégories d'événements (NOUVELLE — notebook Q8) ────────────────
st.subheader("Catégories d'événements GDELT")

if 'EventCategory' in dff.columns:
    cat_counts = dff['EventCategory'].value_counts().reset_index()
    cat_counts.columns = ['EventCategory', 'nb_occurrences']
    fig_cat = px.bar(
        cat_counts.sort_values('nb_occurrences', ascending=True),
        x='nb_occurrences', y='EventCategory', orientation='h',
        color='nb_occurrences', color_continuous_scale='RdYlGn',
        labels={'nb_occurrences': "Nombre d'événements", 'EventCategory': ''},
        height=max(400, len(cat_counts) * 28)
    )
    fig_cat.update_layout(
        showlegend=False, coloraxis_showscale=False,
        margin=dict(l=20, r=120, t=20, b=40)
    )
    fig_cat.update_traces(
        hovertemplate="<b>%{y}</b><br>Événements : %{x:,}<extra></extra>"
    )
    st.plotly_chart(fig_cat, use_container_width=True)
    st.caption("📌 La communication diplomatique et les consultations dominent (~54% des événements).")

# ─── VIZ 7 : Thèmes GKG ──────────────────────────────────────────────────────
st.subheader("Thèmes dominants dans la presse mondiale (GKG)")

with st.expander("Charger les thèmes GDELT GKG (requête supplémentaire)"):
    if st.button("Charger"):
        with st.spinner("Chargement gkg_clean..."):
            gkg = load_gkg()
            # La colonne s'appelle V2Themes dans BigQuery (pas Themes)
            col_themes = next(
                (c for c in gkg.columns if 'theme' in c.lower()),
                None
            )
            if col_themes:
                _themes_raw = gkg[col_themes].dropna().astype(str)
                _themes_raw = _themes_raw[_themes_raw.str.strip() != '']
                _sample = _themes_raw.head(100)
                sep = ';' if _sample.str.contains(';').sum() > _sample.str.contains(',').sum() else ','
                themes = _themes_raw.str.split(sep).explode().str.strip()
                themes = themes[themes.str.len() > 2]
                top_themes = themes.value_counts().head(20).reset_index()
                top_themes.columns = ['theme', 'n']
                fig7 = px.bar(
                    top_themes.sort_values('n'), x='n', y='theme',
                    orientation='h', color='n', color_continuous_scale='Blues',
                    title='Top 20 thèmes GDELT liés au Bénin',
                    labels={'n': 'Occurrences', 'theme': ''},
                    height=550
                )
                fig7.update_layout(showlegend=False)
                st.plotly_chart(fig7, use_container_width=True)
            else:
                st.warning("Colonne V2Themes non trouvée dans gkg_clean.")

            # BONUS : distribution du ton GKG (notebook Q3)
            if 'tone_category' in gkg.columns:
                tone_dist = gkg['tone_category'].value_counts().reset_index()
                tone_dist.columns = ['tone_category', 'n']
                color_map_tone = {
                    "Very Negative": "#8B0000", "Negative": "#E45756",
                    "Neutral": "#A6ACAF", "Positive": "#2CB1A1", "Very Positive": "#00C853"
                }
                fig_td = px.pie(
                    tone_dist, names='tone_category', values='n', hole=0.45,
                    title="Distribution du ton médiatique (GKG)",
                    color='tone_category', color_discrete_map=color_map_tone
                )
                fig_td.update_layout(margin=dict(t=40))
                st.plotly_chart(fig_td, use_container_width=True)
                st.caption("📌 ~59% des articles ont un ton négatif ou très négatif — biais de négativité médiatique structurel.")

# ─── VIZ 8 : Langues des sources (NOUVELLE — notebook Q6) ────────────────────
st.subheader("Langues des sources médiatiques")

with st.expander("Charger la répartition linguistique (requête mentions)"):
    if st.button("Charger langues"):
        with st.spinner("Requête mentions_clean..."):
            try:
                df_lang = load_mentions_lang()
                df_lang['pct'] = (df_lang['nb_mentions'] / df_lang['nb_mentions'].sum() * 100).round(1)
                bar_colors = ["#4f98a3", "#e8af34", "#6daa45", "#fdab43", "#a86fdf",
                              "#e45756", "#00b894", "#636e72"]
                fig_lang = go.Figure(go.Bar(
                    x=df_lang['langue'], y=df_lang['pct'],
                    marker_color=bar_colors[:len(df_lang)],
                    text=df_lang['pct'].astype(str) + '%',
                    textposition='outside',
                    hovertemplate="%{x} : <b>%{y}%</b><extra></extra>"
                ))
                fig_lang.update_layout(
                    title="Top langues des sources (% des mentions)",
                    yaxis_title="% des mentions",
                    height=400, margin=dict(t=50)
                )
                st.plotly_chart(fig_lang, use_container_width=True)
                st.caption("📌 ~80% des mentions proviennent de sources anglophones, 15% francophones.")
            except Exception as e:
                st.error(f"Erreur lors du chargement : {e}")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
c1, c2 = st.columns(2)
c1.caption("Source : GDELT v2 — Global Database of Events, Language and Tone")
c2.caption("iSHEERO x DataCamp Donates Hackathon 2026 · [isheero.com](https://isheero.com)")
