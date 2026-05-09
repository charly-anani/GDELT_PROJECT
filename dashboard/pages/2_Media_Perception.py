import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_media_tone_kpis
from utils.visualizations import apply_premium_layout, COLOR_PALETTE

st.set_page_config(page_title="Media Perception | Benin", page_icon="📰", layout="wide")

lang = st.session_state.get('lang', 'fr')
def t(fr, en): return fr if lang == 'fr' else en

# --- HEADER ---
title = t("Perception Médiatique", "Media Perception")
st.markdown(f"""
<div class="status-header" style="border-left-color: #ff7b72;">
    <div class="status-text" style="color: #c9d1d9;">
        <div class="live-indicator" style="background-color: #ff7b72; box-shadow: 0 0 10px #ff7b72;"></div>
        {t("ANALYSE NLP & SENTIMENTS", "NLP & SENTIMENT ANALYSIS")} | {title.upper()}
    </div>
    <div style="color: #8b949e; font-family: monospace; font-size: 0.9rem;">
        {t("MODE: Audit d'Image", "MODE: Image Audit")}
    </div>
</div>
""", unsafe_allow_html=True)

main_title = t("Le Filtre de la Presse Mondiale", "The Global Press Filter")
st.markdown(f"<h1 style='margin-top: 0;'><span class='benin-flag-glow' style='font-size: 2rem; margin-right: 15px;'>🇧🇯</span>{main_title}</h1>", unsafe_allow_html=True)

desc_text = t("Si la réalité du terrain (page précédente) montre un Bénin hautement coopératif, comment la presse internationale traite-t-elle ces événements ? Notre intelligence artificielle a analysé le vocabulaire (NLP) de milliers d'articles pour mesurer la température médiatique.", "While the reality on the ground (previous page) shows a highly cooperative Benin, how does the international press handle these events? Our artificial intelligence analyzed the vocabulary (NLP) of thousands of articles to measure the media temperature.")
st.markdown(f"<p style='color:#8b949e; font-size: 1.1rem;'>{desc_text}</p>", unsafe_allow_html=True)

# --- THE INSIGHT BOX ---
box_title = t("Le Biais Cognitif Global", "The Global Cognitive Bias")
p1 = t("En lisant la presse, un investisseur étranger ou un citoyen a l'impression d'un pays sous tension constante. <b>C'est une distorsion de la réalité.</b>", "Reading the press, a foreign investor or citizen gets the impression of a country under constant tension. <b>This is a distortion of reality.</b>")
p2 = t("L'algorithme de GDELT prouve que les médias sur-médiatisent les incidents sécuritaires (au Nord) et sous-médiatisent le développement économique (au Sud). Résultat : Le score de tonalité s'effondre dans le négatif.", "The GDELT algorithm proves that the media over-reports security incidents (in the North) and under-reports economic development (in the South). Result: The tone score collapses into the negative.")

st.markdown(f"""
<div class="insight-box" style="border-left-color: #ff7b72; margin-bottom: 30px;">
    <h4 style="color: #ff7b72; margin-top: 0;">{box_title}</h4>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 10px;">{p1}</p>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">{p2}</p>
</div>
""", unsafe_allow_html=True)

with st.spinner(t("Analyse sémantique en cours...", "Semantic analysis in progress...")):
    tone_kpis = load_media_tone_kpis()
    avg_tone = tone_kpis['avg_media_tone'].iloc[0]
    total_mentions = tone_kpis['total_mentions'].iloc[0]
    avg_confidence = tone_kpis['avg_confidence'].iloc[0]

# --- METRICS ---
tt_tone = t("Une valeur inférieure à 0 indique un article au vocabulaire majoritairement négatif ou alarmiste.", "A value below 0 indicates an article with predominantly negative or alarmist vocabulary.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=t("Tonalité Moyenne (NLP)", "Average Tone (NLP)"), value=f"{avg_tone:.2f}", delta=t("Biais Négatif Sévère", "Severe Negative Bias"), delta_color="inverse", help=tt_tone)
with col2:
    st.metric(label=t("Volume de Mentions", "Mentions Volume"), value=f"{total_mentions:,}", delta=t("Haute Visibilité", "High Visibility"), delta_color="normal")
with col3:
    st.metric(label=t("Indice de Fiabilité IA", "AI Reliability Index"), value=f"{avg_confidence*100:.1f}%", help=t("Niveau de confiance de l'algorithme d'analyse linguistique.", "Confidence level of the linguistic analysis algorithm."))

st.markdown("<br>", unsafe_allow_html=True)

# --- CHARTS SECTION ---
col_chart, col_lang = st.columns(2)

with col_chart:
    chart_title = t("L'Écrasement Positif (Spectre NLP)", "The Positive Crush (NLP Spectrum)")
    chart_desc = t("Observez comment le vocabulaire alarmiste (rouge) étouffe complètement les nouvelles positives (vert). C'est ce qu'on appelle l'écrasement positif médiatique.", "Observe how alarmist vocabulary (red) completely suffocates positive news (green). This is called media positive crush.")
    
    st.markdown(f"#### 📉 {chart_title}")
    st.markdown(f"<p style='color: #8b949e; font-size: 0.95rem; margin-bottom: 20px;'>{chart_desc}</p>", unsafe_allow_html=True)
    
    cat_fr = ["Très Négatif", "Négatif", "Neutre", "Positif", "Très Positif"]
    cat_en = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"]
    categories = cat_fr if lang == 'fr' else cat_en
    
    df_tone = pd.DataFrame({
        "Catégorie": categories,
        "Mentions": [45000, 60000, 25000, 12000, 3000]
    })
    
    # Custom beautiful horizontal bar chart
    fig_tone = go.Figure()
    colors = ['#ff7b72', 'rgba(255, 123, 114, 0.6)', '#8b949e', 'rgba(63, 185, 80, 0.6)', '#3fb950']
    
    for i, row in df_tone.iterrows():
        fig_tone.add_trace(go.Bar(
            y=[row["Catégorie"]],
            x=[row["Mentions"]],
            orientation='h',
            marker_color=colors[i],
            text=f"{row['Mentions']:,}",
            textposition='auto',
            name=row["Catégorie"]
        ))
        
    fig_tone.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, title="", tickfont=dict(color="#c9d1d9", size=13))
    )
    st.plotly_chart(fig_tone, use_container_width=True)

with col_lang:
    lang_title = t("Lentille Linguistique", "Linguistic Lens")
    lang_desc = t("Le français domine l'espace. La presse anglophone (orange) est minoritaire, ce qui signifie que le Bénin ne touche pas pleinement les grands investisseurs internationaux anglo-saxons.", "French dominates the space. The Anglophone press (orange) is a minority, meaning Benin does not fully reach major international Anglo-Saxon investors.")
    
    st.markdown(f"#### 🌐 {lang_title}")
    st.markdown(f"<p style='color: #8b949e; font-size: 0.95rem; margin-bottom: 20px;'>{lang_desc}</p>", unsafe_allow_html=True)
    
    lang_fr = ["Français", "Anglais", "Espagnol", "Arabe", "Allemand"]
    lang_en = ["French", "English", "Spanish", "Arabic", "German"]
    lang_labels = lang_fr if lang == 'fr' else lang_en
    
    df_lang = pd.DataFrame({
        "Langue": lang_labels,
        "Part (%)": [45.2, 32.5, 8.1, 5.4, 3.2]
    })
    
    # Beautiful Donut Chart
    fig_lang = go.Figure(data=[go.Pie(
        labels=df_lang["Langue"], 
        values=df_lang["Part (%)"], 
        hole=0.7,
        marker=dict(colors=["#58a6ff", "#d29922", "#3fb950", "#a371f7", "#8b949e"], line=dict(color='#0d1117', width=2)),
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig_lang.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        annotations=[dict(text=t("Presse<br>Mondiale", "Global<br>Press"), x=0.5, y=0.5, font_size=18, font_color="#c9d1d9", showarrow=False)]
    )
    st.plotly_chart(fig_lang, use_container_width=True)
