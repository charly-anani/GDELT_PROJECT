import streamlit as st
import pydeck as pdk
import pandas as pd
import math

def inject_custom_css():
    try:
        with open("dashboard/assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
        
    # Additional CSS to hide default sidebar and add flag animations
    st.markdown("""
    <style>
    [data-testid="stSidebarNavItems"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    .benin-flag-glow {
        font-size: 3.5rem;
        display: inline-block;
        animation: flag-pulse 2.5s infinite alternate;
        margin-bottom: 5px;
    }
    @keyframes flag-pulse {
        0% { filter: drop-shadow(0 0 5px rgba(0, 166, 81, 0.4)) drop-shadow(0 0 10px rgba(252, 209, 22, 0.4)); transform: scale(1); }
        100% { filter: drop-shadow(0 0 15px rgba(0, 166, 81, 0.8)) drop-shadow(0 0 20px rgba(235, 17, 36, 0.8)); transform: scale(1.05); }
    }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    if 'lang' not in st.session_state:
        st.session_state['lang'] = 'fr'

def main():
    st.set_page_config(
        page_title="Dashboard OSINT | Benin",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    inject_custom_css()
    init_session_state()
    
    lang = st.session_state['lang']
    def t(fr, en): return fr if lang == 'fr' else en
    
    # --- SIDEBAR & NAVIGATION ---
    st.sidebar.markdown(f"### 🌐 {t('Langue', 'Language')}")
    lang_col1, lang_col2 = st.sidebar.columns(2)
    if lang_col1.button("🇫🇷 FR", use_container_width=True):
        st.session_state['lang'] = 'fr'
        st.rerun()
    if lang_col2.button("🇬🇧 EN", use_container_width=True):
        st.session_state['lang'] = 'en'
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div class='benin-flag-glow'>🇧🇯</div>", unsafe_allow_html=True)
    st.sidebar.title(t("Intelligence Stratégique", "Strategic Intelligence"))
    st.sidebar.markdown(f"<span style='color: #8b949e; font-size: 0.9rem;'>{t('Équipe 1 - Hackathon iSheero', 'Team 1 - iSheero Hackathon')}</span>", unsafe_allow_html=True)
    
    # Custom Navigation Links
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown(f"**{t('NAVIGATION', 'NAVIGATION')}**")
    
    try:
        st.sidebar.page_link("app.py", label=t("Accueil (Global Network)", "Home (Global Network)"), icon="🌍")
        st.sidebar.page_link("pages/1_Executive_Overview.py", label=t("Briefing National", "National Briefing"), icon="📊")
        st.sidebar.page_link("pages/2_Media_Perception.py", label=t("Perception Médiatique", "Media Perception"), icon="📰")
        st.sidebar.page_link("pages/3_Geographic_Intelligence.py", label=t("Fracture Spatiale", "Spatial Divide"), icon="🗺️")
        st.sidebar.page_link("pages/4_Event_Dynamics.py", label=t("Dynamiques d'Événements", "Event Dynamics"), icon="⚡")
        st.sidebar.page_link("pages/5_Machine_Learning_Risk.py", label=t("Investigation IA", "AI Investigation"), icon="🎯")
        st.sidebar.page_link("pages/6_Strategic_Insights.py", label=t("Insights Stratégiques", "Strategic Insights"), icon="💡")
    except Exception as e:
        st.sidebar.warning(f"Navigation error: {str(e)}")

    st.sidebar.markdown("---")
    st.sidebar.info(
        t(
            "**Mission**\n\nAnalyser l'asymétrie entre la réalité factuelle et la perception médiatique internationale (projet GDELT 2025).",
            "**Mission**\n\nAnalyze the asymmetry between factual reality and international media perception (GDELT 2025 project)."
        )
    )
    
    # --- LANDING PAGE HERO SECTION ---
    title_text = t("Centre de Commandement Géopolitique", "Geopolitical Command Center")
    subtitle_text = t("Dashboard de Renseignement Systémique analysant en temps réel les bases de données GDELT pour révéler les paradoxes médiatiques et anticiper les risques sécuritaires au Bénin.", "Systemic Intelligence Dashboard analyzing GDELT databases in real time to reveal media paradoxes and anticipate security risks in Benin.")
    
    st.markdown(f"""
    <div class="hero-container">
        <div style="font-size: 4rem; margin-bottom: 10px;"><span style="-webkit-text-fill-color: initial;">🌍</span></div>
        <div class="hero-title">{title_text}</div>
        <div class="hero-subtitle">
            {subtitle_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- GLOBAL MAP VISUAL EFFECT ---
    map_title = t("Réseau d'Acquisition OSINT (Simulation)", "OSINT Acquisition Network (Simulation)")
    st.markdown(f"#### 📡 {map_title}")
    
    # Coordinates
    benin = [2.3158, 9.3077]
    cities = [
        {"name": "New York", "coords": [-74.006, 40.7128]},
        {"name": "Paris", "coords": [2.3522, 48.8566]},
        {"name": "London", "coords": [-0.1276, 51.5074]},
        {"name": "Beijing", "coords": [116.4074, 39.9042]},
        {"name": "Moscow", "coords": [37.6173, 55.7558]},
        {"name": "Pretoria", "coords": [28.1881, -25.7461]}
    ]
    
    # Generate arcs
    df_arcs = pd.DataFrame([
        {"source": c["coords"], "target": benin, "value": 100} for c in cities
    ])
    
    # Generate points (Cities + Benin)
    points = [{"lon": c["coords"][0], "lat": c["coords"][1], "color": [88, 166, 255, 200], "radius": 80000} for c in cities]
    points.append({"lon": benin[0], "lat": benin[1], "color": [163, 113, 247, 255], "radius": 150000})
    df_points = pd.DataFrame(points)
    
    # Layers
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=df_arcs,
        get_source_position="source",
        get_target_position="target",
        get_source_color=[88, 166, 255, 120], # Blue transparent
        get_target_color=[163, 113, 247, 255], # Purple solid
        get_width="3",
        tilt=15,
        pickable=False
    )
    
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_points,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="radius",
        pickable=False
    )
    
    view_state = pdk.ViewState(latitude=20, longitude=10, zoom=1.5, pitch=45)
    
    # Use CARTO_DARK for a beautiful background without API key
    r = pdk.Deck(
        layers=[arc_layer, scatter_layer], 
        initial_view_state=view_state, 
        map_provider="carto",
        map_style=pdk.map_styles.CARTO_DARK, 
        height=500
    )
    st.pydeck_chart(r)
    
    # Instructions
    st.markdown(f"""
    <div class="edu-box" style="margin-top: 40px; text-align: center;">
        <h5>{t("Initialisation Terminée", "Initialization Complete")}</h5>
        <p>{t("Veuillez utiliser le panneau latéral de navigation pour accéder aux différents modules analytiques du système.", "Please use the side navigation panel to access the different analytical modules of the system.")}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
