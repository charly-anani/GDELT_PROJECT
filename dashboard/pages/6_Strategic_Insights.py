import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.visualizations import apply_premium_layout

st.set_page_config(page_title="Strategic Insights | Benin", page_icon="🎯", layout="wide")

lang = st.session_state.get('lang', 'fr')
def t(fr, en): return fr if lang == 'fr' else en

# --- HEADER ---
title_text = t("Salle de Décision Stratégique", "Strategic Decision Room")
st.markdown(f"""
<div class="status-header" style="border-left-color: #ff7b72;">
    <div class="status-text" style="color: #c9d1d9;">
        <div class="live-indicator" style="background-color: #ff7b72; box-shadow: 0 0 10px #ff7b72;"></div>
        {t("RECOMMANDATIONS OPÉRATIONNELLES", "OPERATIONAL RECOMMENDATIONS")} | {title_text.upper()}
    </div>
    <div style="color: #8b949e; font-family: monospace; font-size: 0.9rem;">
        {t("MODE: Orienté Action", "MODE: Action-Oriented")}
    </div>
</div>
""", unsafe_allow_html=True)

main_title = t("Le Bilan du Hackathon", "The Hackathon Conclusion")
st.markdown(f"<h1 style='margin-top: 0;'><span class='benin-flag-glow' style='font-size: 2rem; margin-right: 15px;'>🇧🇯</span>{main_title}</h1>", unsafe_allow_html=True)

intro_desc = t("La véritable menace pour le Bénin n'est pas factuelle, elle est <b>narrative</b>. Après avoir analysé les données brutes, la cartographie spatiale et les prédictions de l'IA, voici notre diagnostic final. Choisissez votre profil pour découvrir le plan d'action qui vous correspond.", "The real threat to Benin is not factual, it is <b>narrative</b>. After analyzing raw data, spatial mapping, and AI predictions, here is our final diagnostic. Choose your profile to discover your corresponding action plan.")
st.markdown(f"<p style='color:#8b949e; font-size: 1.1rem;'>{intro_desc}</p>", unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# --- INTERACTIVE PROFILE SELECTOR ---
profile_label = t("Quel est votre rôle ?", "What is your role?")
st.markdown(f"<h3 style='color: #c9d1d9; text-align: center; margin-bottom: 20px;'>{profile_label}</h3>", unsafe_allow_html=True)

# Styling radio buttons to look nicer
st.markdown("""
<style>
div.row-widget.stRadio > div { flex-direction:row; justify-content: center; gap: 20px; }
div.row-widget.stRadio > div > label { 
    background-color: rgba(13, 17, 23, 0.8); 
    padding: 10px 25px; 
    border-radius: 8px; 
    border: 1px solid #30363d;
    cursor: pointer;
    transition: all 0.3s;
}
div.row-widget.stRadio > div > label:hover { border-color: #58a6ff; }
</style>
""", unsafe_allow_html=True)

options = [
    "🏛️ " + t("Décideur Public", "Public Decision Maker"),
    "📰 " + t("Journaliste", "Journalist"),
    "🔬 " + t("Chercheur / Analyste", "Researcher / Analyst")
]

selected_profile = st.radio("", options, horizontal=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- DYNAMIC CONTENT BASED ON PROFILE ---

if "Décideur Public" in selected_profile or "Public Decision Maker" in selected_profile:
    # ---------------- DECISION MAKER ----------------
    col_text, col_viz = st.columns([1, 1.2])
    
    with col_text:
        h2_dec = t("Plan d'Action Gouvernemental", "Governmental Action Plan")
        obj_dec = t("L'objectif : Protéger les investissements et anticiper les crises.", "The objective: Protect investments and anticipate crises.")
        st.markdown(f"<h2 style='color: #ff7b72; margin-top: 0;'>{h2_dec}</h2>", unsafe_allow_html=True)
        st.markdown(f"**{obj_dec}**")
        
        st.markdown(f"""
        <div style="background: rgba(255, 123, 114, 0.05); border-left: 4px solid #ff7b72; padding: 15px; margin-top: 20px; border-radius: 0 8px 8px 0;">
            <h4 style="color: #ff7b72; margin-top: 0;">1. Alerte Préventive au Nord</h4>
            <p>{t("La carte 3D a montré que l'Alibori génère de l'instabilité malgré un faible volume. Utilisez notre IA prédictive J+7 pour envoyer des renforts tactiques ou sociaux avant que la situation ne s'envenime.", "The 3D map showed that Alibori generates instability despite low volume. Use our D+7 predictive AI to send tactical or social reinforcements before the situation escalates.")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(63, 185, 80, 0.05); border-left: 4px solid #3fb950; padding: 15px; margin-top: 15px; border-radius: 0 8px 8px 0;">
            <h4 style="color: #3fb950; margin-top: 0;">2. Rassurer les Investisseurs (Sud)</h4>
            <p>{t("La barre de dominance a prouvé que 66% des actions sont diplomatiques. Brandissez ces chiffres pour rassurer les Investisseurs Étrangers (IDE) sur l'hyper-stabilité économique du Sud (Littoral/Atlantique).", "The dominance bar proved that 66% of actions are diplomatic. Wield these figures to reassure Foreign Investors (FDI) about the economic hyper-stability of the South (Littoral/Atlantique).")}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_viz:
        # Gauge Chart for Decision Makers
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = 66,
            title = {'text': t("Indice de Confiance National", "National Confidence Index"), 'font': {'color': '#c9d1d9'}},
            delta = {'reference': 50, 'increasing': {'color': "#3fb950"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#8b949e"},
                'bar': {'color': "#58a6ff"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#30363d",
                'steps': [
                    {'range': [0, 34], 'color': "rgba(255, 123, 114, 0.3)"},
                    {'range': [34, 100], 'color': "rgba(63, 185, 80, 0.2)"}],
                'threshold': {
                    'line': {'color': "#ff7b72", 'width': 4},
                    'thickness': 0.75,
                    'value': 85}
            }))
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': '#c9d1d9'})
        st.plotly_chart(fig, use_container_width=True)

elif "Journaliste" in selected_profile:
    # ---------------- JOURNALIST ----------------
    col_text, col_viz = st.columns([1, 1.2])
    
    with col_text:
        h2_jour = t("Nouvel Angle Éditorial", "New Editorial Angle")
        obj_jour = t("L'objectif : Corriger le biais cognitif mondial et enquêter là où ça compte.", "The objective: Correct the global cognitive bias and investigate where it matters.")
        st.markdown(f"<h2 style='color: #58a6ff; margin-top: 0;'>{h2_jour}</h2>", unsafe_allow_html=True)
        st.markdown(f"**{obj_jour}**")
        
        st.markdown(f"""
        <div style="background: rgba(88, 166, 255, 0.05); border-left: 4px solid #58a6ff; padding: 15px; margin-top: 20px; border-radius: 0 8px 8px 0;">
            <h4 style="color: #58a6ff; margin-top: 0;">1. Raconter la Vraie Histoire</h4>
            <p>{t("Vos confrères rédigent 72% d'articles alarmistes alors que la réalité n'affiche que 34% de tensions. Démarquez-vous : l'histoire du Bénin est celle d'un boom de coopération économique.", "Your peers write 72% alarmist articles while reality shows only 34% tension. Stand out: Benin's story is one of an economic cooperation boom.")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(210, 153, 34, 0.05); border-left: 4px solid #d29922; padding: 15px; margin-top: 15px; border-radius: 0 8px 8px 0;">
            <h4 style="color: #d29922; margin-top: 0;">2. Journalisme d'Anticipation (OSINT)</h4>
            <p>{t("Servez-vous de notre IA comme d'un radar. Lorsqu'une probabilité de crise clignote au Nord, envoyez vos équipes sur le terrain avant que l'événement ne devienne viral.", "Use our AI as a radar. When a crisis probability flashes in the North, send your teams into the field before the event goes viral.")}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_viz:
        # Radar Chart for Journalists comparing Media vs Reality
        categories = [t('Coopération', 'Cooperation'), t('Conflit Spatial', 'Spatial Conflict'), t('Économie', 'Economy'), t('Diplomatie', 'Diplomacy'), t('Stabilité', 'Stability')]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
              r=[20, 80, 10, 30, 20],
              theta=categories,
              fill='toself',
              name=t('Ce que dit la Presse (Biais)', 'What the Press Says (Bias)'),
              line_color='#ff7b72',
              fillcolor='rgba(255, 123, 114, 0.3)'
        ))
        fig.add_trace(go.Scatterpolar(
              r=[70, 20, 85, 66, 90],
              theta=categories,
              fill='toself',
              name=t('La Réalité des Données', 'Data Reality'),
              line_color='#3fb950',
              fillcolor='rgba(63, 185, 80, 0.3)'
        ))
        fig.update_layout(
          polar=dict(
            radialaxis=dict(visible=False, range=[0, 100]),
            bgcolor='rgba(0,0,0,0)'
          ),
          showlegend=True,
          legend=dict(yanchor="top", y=-0.1, xanchor="center", x=0.5, orientation="h"),
          paper_bgcolor='rgba(0,0,0,0)',
          font={'color': '#c9d1d9'}
        )
        st.plotly_chart(fig, use_container_width=True)

elif "Chercheur" in selected_profile or "Researcher" in selected_profile:
    # ---------------- RESEARCHER ----------------
    col_text, col_viz = st.columns([1, 1.2])
    
    with col_text:
        h2_res = t("Pistes de Recherche Futures", "Future Research Avenues")
        obj_res = t("L'objectif : Comprendre l'asymétrie structurelle et améliorer les modèles d'IA.", "The objective: Understand structural asymmetry and improve AI models.")
        st.markdown(f"<h2 style='color: #a371f7; margin-top: 0;'>{h2_res}</h2>", unsafe_allow_html=True)
        st.markdown(f"**{obj_res}**")
        
        st.markdown(f"""
        <div style="background: rgba(163, 113, 247, 0.05); border-left: 4px solid #a371f7; padding: 15px; margin-top: 20px; border-radius: 0 8px 8px 0;">
            <h4 style="color: #a371f7; margin-top: 0;">1. L'Inertie du Risque Géospatial</h4>
            <p>{t("La carte thermique a révélé des modèles récurrents (hotspots). Sujet de thèse potentiel : Pourquoi la dégradation des événements sur 7 jours (Goldstein Roll 7D) est-elle la métrique prédictive la plus puissante dans notre Random Forest ?", "The heatmap revealed recurring patterns (hotspots). Potential thesis topic: Why is the degradation of events over 7 days (Goldstein Roll 7D) the most powerful predictive metric in our Random Forest?")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(88, 166, 255, 0.05); border-left: 4px solid #58a6ff; padding: 15px; margin-top: 15px; border-radius: 0 8px 8px 0;">
            <h4 style="color: #58a6ff; margin-top: 0;">2. Étude de l'Écho Sémantique</h4>
            <p>{t("Investiguez le 'Gouffre Sémantique' : analysez la corrélation temporelle entre un incident mineur et la propagation virale du vocabulaire négatif (NLP) dans les médias anglophones.", "Investigate the 'Semantic Chasm': analyze the temporal correlation between a minor incident and the viral spread of negative vocabulary (NLP) in Anglophone media.")}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_viz:
        # Funnel Chart for Researchers
        fig = go.Figure(go.Funnelarea(
            text=[t("Événements Réels (GDELT)", "Real Events (GDELT)"), t("Traitement NLP Brut", "Raw NLP Processing"), t("Filtre Biais Médias", "Media Bias Filter"), t("Perception du Lecteur", "Reader Perception")],
            values=[100000, 60000, 20000, 5000],
            marker={"colors": ["#3fb950", "#58a6ff", "#d29922", "#ff7b72"]}
        ))
        fig.update_layout(
            title={'text': t("L'entonnoir de la désinformation", "The Disinformation Funnel"), 'font': {'color': '#c9d1d9'}},
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#c9d1d9'}
        )
        st.plotly_chart(fig, use_container_width=True)
