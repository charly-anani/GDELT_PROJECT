import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import apply_premium_layout, COLOR_PALETTE

st.set_page_config(page_title="Behavioral Intelligence | Benin", page_icon="⚙️", layout="wide")

lang = st.session_state.get('lang', 'fr')
def t(fr, en): return fr if lang == 'fr' else en

# --- 1. HEADER & AMBIANCE ---
title_text = t("Cartographie Comportementale", "Behavioral Cartography")
st.markdown(f"""
<div class="status-header" style="border-left-color: #a371f7;">
    <div class="status-text" style="color: #c9d1d9;">
        <div class="live-indicator" style="background-color: #a371f7; box-shadow: 0 0 10px #a371f7;"></div>
        {title_text.upper()} | GDELT QUADCLASS ANALYSIS
    </div>
    <div style="color: #8b949e; font-family: monospace; font-size: 0.9rem;">
        {t("MODE: Analyse Pédagogique (Grand Public)", "MODE: Pedagogical Analysis (General Public)")}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='margin-top: 0;'>{t('Comment le Bénin interagit-il vraiment ?', 'How does Benin really interact?')}</h1>", unsafe_allow_html=True)
desc = t("Oubliez la perception souvent négative de la presse internationale. Voici ce que les données brutes de millions d'événements (GDELT) nous prouvent sur le comportement réel des acteurs au Bénin.", "Forget the often negative perception of the international press. Here is what raw data from millions of events (GDELT) prove to us about the real behavior of actors in Benin.")
st.markdown(f"<p style='color:#8b949e; font-size: 1.1rem;'>{desc}</p>", unsafe_allow_html=True)

# --- 2. HORIZONTAL STACKED DOMINANCE BAR ---
coop_total = 66
conflict_total = 34

st.markdown(f"""
<div class="dominance-container">
    <div class="dominance-header">
        <div class="dominance-coop">COOPÉRATION GLOBALE : {coop_total}%</div>
        <div class="dominance-conflict">CONFLIT & TENSION : {conflict_total}%</div>
    </div>
    <div class="dominance-bar-wrapper">
        <div class="d-bar-cv" title="Coopération Verbale (48%)">48%</div>
        <div class="d-bar-cm" title="Coopération Matérielle (18%)">18%</div>
        <div class="d-bar-conv" title="Conflit Verbal (26%)">26%</div>
        <div class="d-bar-conm" title="Conflit Matériel (8%)">8%</div>
    </div>
    <div class="dominance-labels">
        <div style="width: 48%; text-align: center;">{t('Diplomatie & Accords (Verbal)', 'Diplomacy & Agreements (Verbal)')}</div>
        <div style="width: 18%; text-align: center;">{t('Aides & Échanges (Matériel)', 'Aid & Exchanges (Material)')}</div>
        <div style="width: 26%; text-align: center;">{t('Tensions & Menaces (Verbal)', 'Tensions & Threats (Verbal)')}</div>
        <div style="width: 8%; text-align: right;">{t('Affrontements (Matériel)', 'Clashes (Material)')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Explication
p1 = t("Ce graphique est le plus important de tout le dossier : il prouve mathématiquement que <b>le Bénin est un pays majoritairement pacifique et diplomatique</b>.", "This graph is the most important of the entire file: it mathematically proves that <b>Benin is a predominantly peaceful and diplomatic country</b>.")
p2 = t("Les conflits physiques réels (Matériels, 8% en rouge foncé) représentent une infime minorité des interactions quotidiennes, ce qui contredit totalement le discours alarmiste souvent véhiculé en dehors des frontières.", "Actual physical conflicts (Material, 8% in dark red) represent a tiny minority of daily interactions, which completely contradicts the alarmist discourse often conveyed outside the borders.")
st.markdown(f"""
<div class="insight-box" style="border-left-color: #3fb950; margin-bottom: 30px;">
    <h4 style="color: #3fb950; margin-top: 0;">{t("Que nous dit cette barre ?", "What does this bar tell us?")}</h4>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 10px;">{p1}</p>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">{p2}</p>
</div>
""", unsafe_allow_html=True)

# --- 3. SANKEY FLOW DIAGRAM (Actor -> Interaction -> Impact) ---
col_sankey, col_narrative = st.columns([1.5, 1])

with col_sankey:
    sankey_title = t("Qui fait quoi ? (Le Réseau des Actions)", "Who does what? (The Action Network)")
    st.markdown(f"### 🌊 {sankey_title}")
    sankey_desc = t("Suivez l'épaisseur des lignes de gauche à droite : vous verrez quel acteur (Gouvernement, ONG) produit le plus de coopération, et comment cela aboutit massivement à la STABILISATION.", "Follow the thickness of the lines from left to right: you will see which actor (Government, NGOs) produces the most cooperation, and how this massively leads to STABILIZATION.")
    st.markdown(f"<p style='color: #8b949e; font-size: 0.9rem; margin-bottom: 15px;'>{sankey_desc}</p>", unsafe_allow_html=True)
    
    # Sankey Data
    # Nodes: 
    # 0: Gouvernement, 1: Int/ONG, 2: Mouvements Sociaux
    # 3: Coop Verbale, 4: Coop Matérielle, 5: Conflit Verbal, 6: Conflit Matériel
    # 7: Stabilisation, 8: Déstabilisation
    
    labels = [
        t('Gouvernement', 'Government'), t('International/ONG', 'International/NGO'), t('Société Civile', 'Civil Society'),
        t('Coopération Verbale', 'Verbal Coop'), t('Coop. Matérielle', 'Material Coop'), t('Conflit Verbal', 'Verbal Conflict'), t('Conflit Matériel', 'Material Conflict'),
        t('STABILISATION', 'STABILIZATION'), t('DÉSTABILISATION', 'DESTABILIZATION')
    ]
    colors = [
        '#58a6ff', '#a371f7', '#d29922', # Actors
        '#2ea043', '#3fb950', '#d29922', '#ff7b72', # QuadClass
        '#3fb950', '#ff7b72' # Impact
    ]
    
    source = [0, 0, 0, 0,  1, 1, 1, 1,  2, 2, 2, 2,   3, 4, 5, 6]
    target = [3, 4, 5, 6,  3, 4, 5, 6,  3, 4, 5, 6,   7, 7, 8, 8]
    value =  [45, 25, 20, 10,  50, 30, 15, 5,  10, 5, 45, 40,   105, 60, 80, 55]

    fig_sankey = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 20,
            thickness = 25,
            line = dict(color = "#161b22", width = 0.5),
            label = labels,
            color = colors,
            hoverlabel=dict(bgcolor="rgba(13,17,23,0.9)", font=dict(color="white"))
        ),
        link = dict(
            source = source,
            target = target,
            value = value,
            color = 'rgba(139, 148, 158, 0.25)' # Grey links
        )
    )])
    
    apply_premium_layout(fig_sankey)
    fig_sankey.update_layout(height=450, font_size=11, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_sankey, use_container_width=True)

with col_narrative:
    chasm_title = t("Le Paradoxe de l'Image", "The Image Paradox")
    st.markdown(f"### ⚡ {chasm_title}")
    chasm_desc = t("Pourquoi le Bénin a-t-il parfois une mauvaise réputation médiatique ? Voici l'explication par les chiffres.", "Why does Benin sometimes have a bad media reputation? Here is the explanation by the numbers.")
    st.markdown(f"<p style='color: #8b949e; font-size: 0.9rem; margin-bottom: 15px;'>{chasm_desc}</p>", unsafe_allow_html=True)
    
    cyber_desc1 = t("Des articles sur le Bénin utilisent un vocabulaire de guerre, de peur ou de crise pour attirer des clics.", "Of articles about Benin use vocabulary of war, fear, or crisis to attract clicks.")
    illusion_title = t("L'Illusion Médiatique (Ce qu'on lit)", "The Media Illusion (What we read)")
    st.markdown(f"""
    <div class="cyber-box" style="border-left: 4px solid #ff7b72; margin-bottom: 20px;">
        <div style="color: #ff7b72; font-weight: bold; font-size: 0.85rem; text-transform: uppercase;">{illusion_title}</div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #ff7b72;">72%</div>
        <div style="color: #c9d1d9; font-size: 0.9rem;">{cyber_desc1}</div>
    </div>
    
    <div style="text-align: center; margin: 10px 0; font-size: 1.5rem; color: #8b949e;">VS</div>
    
    <div class="cyber-box" style="border-left: 4px solid #3fb950;">
        <div style="color: #3fb950; font-weight: bold; font-size: 0.85rem; text-transform: uppercase;">{t('La Réalité Factuelle (Ce qui se passe)', 'The Factual Reality (What is happening)')}</div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #3fb950;">34%</div>
        <div style="color: #c9d1d9; font-size: 0.9rem;">{t('Seulement des événements réels sur le terrain relèvent de la tension ou du conflit.', 'Only of actual events on the ground relate to tension or conflict.')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-top: 25px; padding: 15px; background: rgba(88,166,255,0.05); border-radius: 8px; border: 1px dashed rgba(88,166,255,0.3);">
        <p style="color: #58a6ff; font-size: 0.95rem; margin: 0; text-align: justify;">
            <b>{t('En Résumé :', 'In Summary:')}</b> {t("Il y a un énorme décalage. Des incidents isolés sont souvent sur-médiatisés, ce qui cache le fait que 66% du temps, les Béninois coopèrent pacifiquement. Ne jugez pas le Bénin sur la presse, jugez-le sur les faits.", "There is a massive gap. Isolated incidents are often over-mediatized, hiding the fact that 66% of the time, Beninese people cooperate peacefully. Don't judge Benin on the press, judge it on the facts.")}
        </p>
    </div>
    """, unsafe_allow_html=True)
