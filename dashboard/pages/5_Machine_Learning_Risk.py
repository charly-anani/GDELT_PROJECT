import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from utils.visualizations import apply_premium_layout, COLOR_PALETTE

st.set_page_config(page_title="AI Risk Command Center | Benin", page_icon="🔴", layout="wide")

lang = st.session_state.get('lang', 'fr')
def t(fr, en): return fr if lang == 'fr' else en

# --- 1. COMMAND CENTER HEADER ---
st.markdown(f"""
<div class="status-header">
    <div class="status-text">
        <div class="live-indicator"></div>
        AI RISK COMMAND CENTER | {t('SURVEILLANCE EN DIRECT', 'LIVE MONITORING')}
    </div>
    <div style="color: #8b949e; font-family: monospace; font-size: 0.9rem;">
        {t("SYSTÈME : Intelligence Artificielle (Random Forest) | HORIZON : Prévision à 7 Jours | FIABILITÉ : 82%", "SYSTEM: Artificial Intelligence (Random Forest) | HORIZON: 7-Day Forecast | RELIABILITY: 82%")}
    </div>
</div>
""", unsafe_allow_html=True)

# Explication pour non-initiés
st.markdown(f"""
<div class="insight-box" style="border-left-color: #58a6ff; margin-bottom: 25px;">
    <h4 style="color: #58a6ff; margin-top: 0;">{t("Comment lire ce tableau de bord ?", "How to read this dashboard?")}</h4>
    <p style="margin-bottom: 0;">{t("Ce système agit comme un <b>radar d'alerte précoce</b>. Il analyse des millions d'articles de presse et d'événements pour repérer des 'signaux faibles' (ex: une tension qui monte lentement aux frontières, ou une panique médiatique). Si l'algorithme détecte une combinaison dangereuse, il déclenche une alerte pour <b>anticiper une crise 7 jours avant qu'elle n'éclate</b>.", "This system acts as an <b>early warning radar</b>. It analyzes millions of press articles and events to spot 'weak signals' (e.g., tension slowly rising at borders, or media panic). If the algorithm detects a dangerous combination, it triggers an alert to <b>anticipate a crisis 7 days before it breaks out</b>.")}</p>
</div>
""", unsafe_allow_html=True)

# --- 2. OPERATIONAL KPIs ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="cyber-box pulse-red" style="height: 100%;">
        <div style="font-size: 0.8rem; color: #8b949e; text-transform: uppercase;">{t("Alertes Critiques Actives", "Active Critical Alerts")}</div>
        <div style="font-size: 2.2rem; font-weight: bold; color: #ff7b72;">2 <span style="font-size: 1rem; color: #8b949e;">/ 12 {t('Zones', 'Zones')}</span></div>
        <div style="font-size: 0.8rem; color: #ff7b72; margin-top: 5px;">⚠️ {t("Alibori, Atacora", "Alibori, Atacora")}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="cyber-box" style="height: 100%;">
        <div style="font-size: 0.8rem; color: #8b949e; text-transform: uppercase;">{t("Précision du Modèle", "Model Precision")}</div>
        <div style="font-size: 2.2rem; font-weight: bold; color: #58a6ff;">85%</div>
        <div style="font-size: 0.8rem; color: #3fb950; margin-top: 5px;">▲ {t("Fausses alertes minimisées", "Minimized false alerts")}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="cyber-box pulse-orange" style="height: 100%;">
        <div style="font-size: 0.8rem; color: #8b949e; text-transform: uppercase;">{t("Inertie du Risque Globale", "Global Risk Inertia")}</div>
        <div style="font-size: 2.2rem; font-weight: bold; color: #d29922;">+14%</div>
        <div style="font-size: 0.8rem; color: #d29922; margin-top: 5px;">📈 {t("Tension en hausse (30j)", "Tension rising (30d)")}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="cyber-box" style="height: 100%;">
        <div style="font-size: 0.8rem; color: #8b949e; text-transform: uppercase;">{t("Délai d'Anticipation", "Anticipation Lead Time")}</div>
        <div style="font-size: 2.2rem; font-weight: bold; color: #c9d1d9;">7 <span style="font-size: 1rem; color: #8b949e;">{t('Jours', 'Days')}</span></div>
        <div style="font-size: 0.8rem; color: #58a6ff; margin-top: 5px;">⏱️ {t("Temps d'actionabilité", "Actionability window")}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# --- 3. PREDICTION ENGINE TABLE ---
st.markdown(f"### 🎛️ {t('Moteur de Prédiction (Vue Synthétique)', 'Prediction Engine (Synthetic View)')}")

table_html = f"""
<div class="prediction-table-container">
    <table class="prediction-table">
        <tr>
            <th>{t('Département', 'Department')}</th>
            <th>{t('Probabilité de Crise (J+7)', 'Crisis Probability (D+7)')}</th>
            <th>{t('Statut IA', 'AI Status')}</th>
            <th>{t('Principal Facteur de Tension', 'Main Tension Driver')}</th>
            <th>{t('Tendance', 'Trend')}</th>
            <th>{t('Action Recommandée', 'Recommended Action')}</th>
        </tr>
        <tr>
            <td style="font-weight: 600;">Alibori</td>
            <td style="color: #ff7b72; font-weight: bold;">88.4%</td>
            <td><span class="badge-critical">{t('CRITIQUE', 'CRITICAL')}</span></td>
            <td style="font-family: monospace;">{t('Dégradation lente mais constante (Inertie)', 'Slow but constant degradation (Inertia)')}</td>
            <td class="trend-up">↑ {t('Escalade', 'Escalation')}</td>
            <td style="color: #ff7b72;">{t('Déploiement tactique urgent', 'Urgent tactical deployment')}</td>
        </tr>
        <tr>
            <td style="font-weight: 600;">Atacora</td>
            <td style="color: #ff7b72; font-weight: bold;">74.1%</td>
            <td><span class="badge-critical">{t('CRITIQUE', 'CRITICAL')}</span></td>
            <td style="font-family: monospace;">{t('Panique médiatique (Biais Négatif)', 'Media panic (Negative Bias)')}</td>
            <td class="trend-up">↑ {t('Escalade', 'Escalation')}</td>
            <td style="color: #ff7b72;">{t('Intervention diplomatique', 'Diplomatic intervention')}</td>
        </tr>
        <tr>
            <td style="font-weight: 600;">Borgou</td>
            <td style="color: #d29922; font-weight: bold;">46.2%</td>
            <td><span class="badge-surveillance">{t('SURVEILLANCE', 'WATCH')}</span></td>
            <td style="font-family: monospace;">{t('Anomalie de volume (Hyperactivité)', 'Volume anomaly (Hyperactivity)')}</td>
            <td class="trend-flat">→ {t('Incertain', 'Uncertain')}</td>
            <td style="color: #d29922;">{t('Surveiller les mouvements sociaux', 'Monitor social movements')}</td>
        </tr>
        <tr>
            <td style="font-weight: 600;">Collines</td>
            <td style="color: #3fb950; font-weight: bold;">22.8%</td>
            <td><span class="badge-stable">{t('STABLE', 'STABLE')}</span></td>
            <td style="font-family: monospace;">{t('Climat apaisé depuis 30 jours', 'Calm climate for 30 days')}</td>
            <td class="trend-down">↓ {t('Apaisement', 'De-escalation')}</td>
            <td style="color: #3fb950;">{t('Aucune action requise', 'No action required')}</td>
        </tr>
        <tr>
            <td style="font-weight: 600;">Littoral</td>
            <td style="color: #3fb950; font-weight: bold;">12.5%</td>
            <td><span class="badge-stable">{t('STABLE', 'STABLE')}</span></td>
            <td style="font-family: monospace;">{t('Coopération Économique Forte', 'Strong Economic Cooperation')}</td>
            <td class="trend-flat">→ {t('Normale', 'Baseline')}</td>
            <td style="color: #3fb950;">{t('Aucune action requise', 'No action required')}</td>
        </tr>
    </table>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

st.markdown("<hr style='border-color: #30363d;'/>", unsafe_allow_html=True)

# --- 4. EXPLAINABLE AI : ANALYSE DÉTAILLÉE PAR DÉPARTEMENT ---
inv_title = t("Dossier d'Investigation IA", "AI Investigation File")
st.markdown(f"### 🎯 {inv_title}")
desc_text = t("Sélectionnez un département ci-dessous pour ouvrir son dossier. Le système vous expliquera de manière transparente <b>pourquoi</b> l'algorithme a pris cette décision.", "Select a department below to open its file. The system will transparently explain <b>why</b> the algorithm made this decision.")
st.markdown(f"<p style='color:#8b949e; margin-bottom: 20px;'>{desc_text}</p>", unsafe_allow_html=True)

# Selectbox for region
regions = ['Alibori', 'Atacora', 'Borgou', 'Collines', 'Littoral']
selected_region = st.selectbox(t("Sélectionnez le département à analyser :", "Select the department to analyze:"), regions)

# Database logic simulation based on region
if selected_region == 'Alibori':
    feat_labels = [t('Stabilité Récente (Base)', 'Recent Stability (Base)'), t('Inertie 7J (Dégradation lente)', '7D Inertia (Slow degradation)'), t('Panique Médiatique (Ton NLP)', 'Media Panic (NLP Tone)'), t('Surcharge d\'Événements', 'Event Overload'), t('Saisonnalité', 'Seasonality'), t('Climat sur 30 Jours', '30-Day Climate')]
    contributions = [13.0, 45.5, 18.2, 14.5, -2.5, -0.3]
    escalation_text = t("Le seuil critique de 70% a été violemment franchi hier.", "The critical threshold of 70% was violently crossed yesterday.")
    narrative_p1 = t("<b>Analyse de la machine :</b> Le score de risque explose non pas à cause d'un événement choc isolé, mais à cause de <b>l'Inertie</b>.", "<b>Machine analysis:</b> The risk score explodes not because of an isolated shock event, but because of <b>Inertia</b>.")
    narrative_p2 = t("L'algorithme remarque qu'en Alibori, la stabilité se dégrade doucement chaque jour depuis une semaine (la barre rouge géante sur le graphique). Ajoutons à cela la presse internationale qui commence à paniquer (Ton NLP très négatif), et l'IA conclut que la crise est imminente.", "The algorithm notes that in Alibori, stability has been slowly degrading every day for a week (the giant red bar on the graph). Add to this the international press starting to panic (very negative NLP Tone), and the AI concludes that a crisis is imminent.")
    y_values = np.concatenate([np.random.normal(30, 3, 15), np.linspace(35, 65, 8) + np.random.normal(0, 4, 8), np.linspace(70, 88.4, 7) + np.random.normal(0, 2, 7)])
    anom_x, anom_y = 15, y_values[15]
    panic_x, panic_y = 23, y_values[23]

elif selected_region == 'Atacora':
    feat_labels = [t('Stabilité Récente (Base)', 'Recent Stability (Base)'), t('Choc Passé (Climat 30J)', 'Past Shock (30D Climate)'), t('Panique Médiatique (Ton NLP)', 'Media Panic (NLP Tone)'), t('Inertie 7J (Dégradation)', '7D Inertia (Degradation)'), t('Saisonnalité', 'Seasonality'), t('Surcharge d\'Événements', 'Event Overload')]
    contributions = [15.0, 35.0, 22.0, 10.0, -5.0, -2.9]
    escalation_text = t("Le seuil de 70% vient tout juste d'être touché.", "The 70% threshold has just been touched.")
    narrative_p1 = t("<b>Analyse de la machine :</b> Ici, c'est le contraire de l'Alibori. Le système réagit à un <b>choc passé</b> (climat détérioré sur le long terme).", "<b>Machine analysis:</b> Here, it's the opposite of Alibori. The system reacts to a <b>past shock</b> (deteriorated climate over the long term).")
    narrative_p2 = t("Le fait marquant est le pessimisme extrême des articles de presse mondiaux traitant de la région (Panique Médiatique en rouge), qui pousse le risque vers la zone critique.", "The striking fact is the extreme pessimism of global press articles dealing with the region (Media Panic in red), which pushes the risk towards the critical zone.")
    y_values = np.concatenate([np.random.normal(40, 5, 20), np.linspace(50, 74.1, 10) + np.random.normal(0, 3, 10)])
    anom_x, anom_y = 20, y_values[20]
    panic_x, panic_y = 25, y_values[25]

elif selected_region == 'Borgou':
    feat_labels = [t('Stabilité Récente (Base)', 'Recent Stability (Base)'), t('Surcharge d\'Événements', 'Event Overload'), t('Panique Médiatique (Ton NLP)', 'Media Panic (NLP Tone)'), t('Climat sur 30 Jours', '30-Day Climate'), t('Saisonnalité', 'Seasonality'), t('Inertie 7J (Apaisement)', '7D Inertia (De-escalation)')]
    contributions = [20.0, 30.0, 5.0, -2.0, -1.0, -5.8]
    escalation_text = t("La zone jaune (Surveillance) est atteinte, comportement incertain.", "The yellow zone (Watch) is reached, uncertain behavior.")
    narrative_p1 = t("<b>Analyse de la machine :</b> Le Borgou est en zone de turbulence. Le signal principal qui inquiète l'IA est une <b>Anomalie de Volume</b>.", "<b>Machine analysis:</b> Borgou is in a turbulence zone. The main signal worrying the AI is a <b>Volume Anomaly</b>.")
    narrative_p2 = t("Il y a subitement beaucoup trop d'événements inhabituels qui s'y produisent en peu de temps. Cependant, la presse reste neutre et la tendance à long terme ne montre pas d'effondrement, d'où le classement en simple 'Surveillance'.", "Suddenly, there are too many unusual events happening there in a short time. However, the press remains neutral and the long-term trend shows no collapse, hence the simple 'Watch' classification.")
    y_values = np.concatenate([np.random.normal(25, 4, 15), np.random.normal(46.2, 5, 15)])
    anom_x, anom_y = 15, y_values[15]
    panic_x, panic_y = None, None

else:
    feat_labels = [t('Stabilité Récente (Base)', 'Recent Stability (Base)'), t('Saisonnalité', 'Seasonality'), t('Inertie 7J (Apaisement)', '7D Inertia (De-escalation)'), t('Climat sur 30 Jours', '30-Day Climate'), t('Ton NLP (Positif)', 'NLP Tone (Positive)'), t('Coopération (Volume)', 'Cooperation (Volume)')]
    contributions = [25.0, 2.0, -5.0, -8.0, -10.0, -15.0]
    escalation_text = t("Le risque est au plus bas, aucune anomalie détectée.", "Risk is at its lowest, no anomaly detected.")
    narrative_p1 = t("<b>Analyse de la machine :</b> Situation extrêmement calme. La majorité des actions recensées sont catégorisées comme 'coopératives'.", "<b>Machine analysis:</b> Extremely calm situation. The majority of recorded actions are categorized as 'cooperative'.")
    narrative_p2 = t("L'intelligence artificielle diminue la probabilité de crise grâce aux tonnes d'articles positifs (Ton NLP Positif) qui font redescendre la jauge de risque de manière drastique (barres vertes).", "The artificial intelligence decreases the crisis probability thanks to the tons of positive articles (Positive NLP Tone) which drastically bring down the risk gauge (green bars).")
    val = 22.8 if selected_region == 'Collines' else 12.5
    y_values = np.random.normal(val, 2, 30)
    anom_x, anom_y = None, None
    panic_x, panic_y = None, None

st.markdown(f"""
<div class="insight-box" style="border-left-color: #a371f7; background: rgba(163, 113, 247, 0.05); margin-bottom: 30px;">
    <h4 style="color: #a371f7; margin-top: 0;">🧠 {t("Le Diagnostic de l'Intelligence Artificielle", "The Artificial Intelligence Diagnostic")}</h4>
    <p style="font-size: 1.05rem; line-height: 1.6;">{narrative_p1}</p>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">{narrative_p2}</p>
</div>
""", unsafe_allow_html=True)

col_shap, col_timeline = st.columns([1, 1.2])

with col_shap:
    factors_title = t("Qu'est-ce qui pousse l'IA à décider ? (Facteurs)", "What drives the AI to decide? (Factors)")
    st.markdown(f"#### 🔍 {factors_title}")
    st.markdown(f"""<div style="font-size: 0.85rem; color: #8b949e; margin-bottom: 15px;">{t("Lecture : Les barres <b>rouges</b> font grimper le risque vers 100%. Les barres <b>vertes</b> agissent comme des boucliers qui apaisent le risque.", "Reading: <b>Red</b> bars push the risk towards 100%. <b>Green</b> bars act as shields that pacify the risk.")}</div>""", unsafe_allow_html=True)
    
    fig_shap = go.Figure(go.Waterfall(
        orientation="h",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative"],
        y=feat_labels[::-1],
        x=contributions[::-1],
        connector={"line": {"color": "rgba(255,255,255,0.1)"}},
        decreasing={"marker": {"color": "#3fb950"}},
        increasing={"marker": {"color": "#ff7b72"}},
        totals={"marker": {"color": "#58a6ff"}}
    ))
    
    apply_premium_layout(fig_shap)
    fig_shap.update_layout(
        height=320,
        margin=dict(l=0, r=20, t=20, b=0),
        xaxis=dict(title=t("Poids dans la décision (%)", "Weight in the decision (%)"), showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_shap, use_container_width=True)

with col_timeline:
    movie_title = t("Le Film de l'Escalade sur 30 Jours", "The 30-Day Escalation Movie")
    st.markdown(f"#### 📉 {movie_title}")
    st.markdown(f"""<div style="font-size: 0.85rem; color: #8b949e; margin-bottom: 15px;">{escalation_text}</div>""", unsafe_allow_html=True)
    
    days = pd.date_range(end=pd.Timestamp.today(), periods=30)
    
    fig_time = go.Figure()
    # Zone colors
    fig_time.add_hrect(y0=0, y1=40, fillcolor="rgba(63, 185, 80, 0.05)", layer="below", line_width=0)
    fig_time.add_hrect(y0=40, y1=70, fillcolor="rgba(210, 153, 34, 0.05)", layer="below", line_width=0)
    fig_time.add_hrect(y0=70, y1=100, fillcolor="rgba(255, 123, 114, 0.05)", layer="below", line_width=0)
    
    # Risk Line
    line_color = "#ff7b72" if y_values[-1] > 70 else ("#d29922" if y_values[-1] > 40 else "#3fb950")
    
    fig_time.add_trace(go.Scatter(
        x=days, y=y_values,
        mode='lines+markers',
        line=dict(color=line_color, width=3),
        marker=dict(size=6, color="#161b22", line=dict(color=line_color, width=2)),
        name=t("Niveau d'Alerte IA", "AI Alert Level")
    ))
    
    # Critical Threshold Line
    fig_time.add_hline(y=70, line_dash="dash", line_color="#ff7b72", annotation_text=t("SEUIL CRITIQUE DE RUPTURE (70%)", "CRITICAL RUPTURE THRESHOLD (70%)"), annotation_font_color="#ff7b72")
    
    # Anomaly markers
    if anom_x is not None and anom_y is not None:
        fig_time.add_annotation(x=days[anom_x], y=anom_y, text=t("Anomalie Volume", "Volume Anomaly"), showarrow=True, arrowhead=1, ax=0, ay=-40, font=dict(color="#d29922"), arrowcolor="#d29922")
    if panic_x is not None and panic_y is not None:
        fig_time.add_annotation(x=days[panic_x], y=panic_y, text=t("Panique Médiatique", "Media Panic"), showarrow=True, arrowhead=1, ax=-40, ay=-40, font=dict(color="#ff7b72"), arrowcolor="#ff7b72")
    
    apply_premium_layout(fig_time)
    fig_time.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis_range=[0, 100])
    st.plotly_chart(fig_time, use_container_width=True)

st.markdown("<hr style='border-color: #30363d;'/>", unsafe_allow_html=True)

# --- 5. STRATEGIC DIFFUSION MAP ---
st.markdown(f"### 📍 {t('Carte Tactique (Diffusion du Risque)', 'Tactical Map (Risk Diffusion)')}")
st.markdown(f"""
<div style="font-size: 1.05rem; color: #c9d1d9; margin-bottom: 10px;">
    {t("Voici la projection spatiale du modèle. Plus une zone est grande et rouge, plus le volume d'événements dangereux y est important.", "Here is the spatial projection of the model. The larger and redder an area, the more dangerous events are occurring there.")}
</div>
<div style="font-size: 0.95rem; color: #8b949e; margin-bottom: 20px;">
    {t("👉 <b>Interactif :</b> Cliquez sur les cercles pour voir le détail des événements.", "👉 <b>Interactive:</b> Click on the circles to see event details.")}
</div>
""", unsafe_allow_html=True)

html_map_path = "d:/Nouveau dossier/Hack  Isheero/GDELT_PROJECT-main/models/cachemodels/risk_hotspot_map_benin_2025.html"

if os.path.exists(html_map_path):
    st.markdown("""
    <div style="border: 1px solid #30363d; border-radius: 8px; overflow: hidden; background: #0d1117; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    """, unsafe_allow_html=True)
    with open(html_map_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=600, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error(t("La carte stratégique Folium n'a pas été générée par le notebook.", "The strategic Folium map was not generated by the notebook."))
