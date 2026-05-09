import streamlit as st
from utils.data_loader import load_executive_kpis, load_timeline_data
import plotly.graph_objects as go
from utils.visualizations import apply_premium_layout

st.set_page_config(page_title="Executive Overview | Benin Intelligence", page_icon="📊", layout="wide")

lang = st.session_state.get('lang', 'fr')
def t(fr, en): return fr if lang == 'fr' else en

# --- 1. HEADER ---
title_text = t("Briefing National", "National Briefing")
st.markdown(f"""
<div class="status-header" style="border-left-color: #58a6ff;">
    <div class="status-text" style="color: #c9d1d9;">
        <div class="live-indicator" style="background-color: #58a6ff; box-shadow: 0 0 10px #58a6ff;"></div>
        {t("ÉTAT DES LIEUX GDELT", "GDELT STATUS")} | {title_text.upper()}
    </div>
    <div style="color: #8b949e; font-family: monospace; font-size: 0.9rem;">
        {t("MODE: Résumé Décisionnel", "MODE: Executive Summary")}
    </div>
</div>
""", unsafe_allow_html=True)

main_title = t("Vue d'Ensemble des Données Brutes", "Overview of Raw Data")
st.markdown(f"<h1 style='margin-top: 0;'>{main_title}</h1>", unsafe_allow_html=True)

desc_text = t("Que disent réellement les chiffres avant d'être interprétés par la presse ? Ce tableau de bord résume l'analyse de millions d'articles mondiaux compilés par le système GDELT.", "What do the numbers really say before being interpreted by the press? This dashboard summarizes the analysis of millions of global articles compiled by the GDELT system.")
st.markdown(f"<p style='color:#8b949e; font-size: 1.1rem;'>{desc_text}</p>", unsafe_allow_html=True)

# --- 2. EXECUTIVE SUMMARY (Simplified for non-coders) ---
p1 = t("L'exploration de nos données (réalisée via notre base de données BigQuery) a extrait tous les événements impliquant le Bénin. Nous avons comptabilisé chaque action, classé les acteurs (Gouvernement, Citoyens, ONG) et calculé un 'Score de Stabilité'.", "The exploration of our data (performed via our BigQuery database) extracted all events involving Benin. We counted each action, classified the actors (Government, Citizens, NGOs) and calculated a 'Stability Score'.")
p2 = t("Le constat principal est clair : <b>Le volume massif d'actions enregistrées est diplomatique et constructif.</b>", "The main observation is clear: <b>The massive volume of recorded actions is diplomatic and constructive.</b>")

st.markdown(f"""
<div class="insight-box" style="border-left-color: #58a6ff; margin-bottom: 30px;">
    <h4 style="color: #58a6ff; margin-top: 0;">{t("Que regardons-nous ici ?", "What are we looking at here?")}</h4>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 10px;">{p1}</p>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">{p2}</p>
</div>
""", unsafe_allow_html=True)

with st.spinner(t("Analyse du carnet de bord GDELT...", "Analyzing GDELT logbook...")):
    kpis = load_executive_kpis()
    timeline = load_timeline_data()
    
    total_events = kpis['total_events'].iloc[0]
    avg_goldstein = kpis['avg_goldstein'].iloc[0]
    coop_count = kpis['count_cooperation'].iloc[0]
    conflict_count = kpis['count_conflict'].iloc[0]

# --- 3. METRICS ---
tt_goldstein = t("Note de -10 à +10. Si c'est positif, c'est que le pays va bien.", "Score from -10 to +10. If positive, the country is doing well.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label=t("Événements Analysés", "Analyzed Events"), value=f"{total_events:,}")
with col2:
    st.metric(label=t("Score de Stabilité Général", "General Stability Score"), value=f"+{avg_goldstein:.1f}", delta=t("Majoritairement Positif", "Mostly Positive"), delta_color="normal", help=tt_goldstein)
with col3:
    st.metric(label=t("Actions de Coopération", "Cooperation Actions"), value=f"{coop_count:,}", delta=f"{(coop_count/total_events)*100:.1f}%", help=t("Accords, aides, diplomatie.", "Agreements, aid, diplomacy."))
with col4:
    st.metric(label=t("Actions de Tension", "Tension Actions"), value=f"{conflict_count:,}", delta=f"{(conflict_count/total_events)*100:.1f}%", delta_color="inverse", help=t("Menaces, protestations, incidents.", "Threats, protests, incidents."))

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. THE PULSE CHART (Visually Stunning Dual-Axis Graph) ---
pulse_title = t("La Pulsation Nationale", "The National Pulse")
st.markdown(f"### 📈 {pulse_title}")

pulse_desc = t("Ce graphique combine deux informations : <b>Les barres bleues</b> montrent la quantité d'événements (l'activité). <b>La ligne verte lumineuse</b> montre le niveau de stabilité (Score Goldstein). Vous remarquerez que même quand l'activité augmente fortement, la ligne verte reste stable ou monte, preuve de la robustesse du pays.", "This chart combines two pieces of information: <b>Blue bars</b> show the quantity of events (activity). <b>The glowing green line</b> shows the stability level (Goldstein Score). You will notice that even when activity increases sharply, the green line remains stable or rises, proof of the country's robustness.")
st.markdown(f"<p style='color: #8b949e; font-size: 0.95rem; margin-bottom: 20px;'>{pulse_desc}</p>", unsafe_allow_html=True)

# Create Dual Axis Chart
fig = go.Figure()

# Volume (Bars)
fig.add_trace(
    go.Bar(
        x=timeline['date'],
        y=timeline['daily_events'],
        name=t("Activité (Volume)", "Activity (Volume)"),
        marker_color='rgba(88, 166, 255, 0.4)',
        marker_line_color='rgba(88, 166, 255, 1)',
        marker_line_width=1,
        yaxis="y1"
    )
)

# Stability Score (Glowing Line)
fig.add_trace(
    go.Scatter(
        x=timeline['date'],
        y=timeline['daily_goldstein'],
        name=t("Niveau de Stabilité", "Stability Level"),
        mode='lines',
        line=dict(color='#3fb950', width=4, shape='spline'), # Smooth glowing green line
        yaxis="y2"
    )
)

# Layout adjustments for dual axis
fig.update_layout(
    height=450,
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor='rgba(13, 17, 23, 0)',
    paper_bgcolor='rgba(13, 17, 23, 0)',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    yaxis=dict(
        title=t("Volume d'Événements", "Event Volume"),
        title_font=dict(color="#58a6ff"),
        tickfont=dict(color="#58a6ff"),
        gridcolor="rgba(48, 54, 61, 0.5)"
    ),
    yaxis2=dict(
        title=t("Score de Stabilité", "Stability Score"),
        title_font=dict(color="#3fb950"),
        tickfont=dict(color="#3fb950"),
        anchor="x",
        overlaying="y",
        side="right",
        range=[0, 3] # Adjusted for visualization
    ),
    xaxis=dict(
        gridcolor="rgba(48, 54, 61, 0.3)",
        showgrid=True
    )
)

st.plotly_chart(fig, use_container_width=True)
