import streamlit as st
import pandas as pd
import pydeck as pdk
import os
from utils.data_loader import load_geographic_hotspots
from utils.visualizations import COLOR_PALETTE

st.set_page_config(page_title="Geographic Intelligence | Benin", page_icon="🗺️", layout="wide")

lang = st.session_state.get('lang', 'fr')
def t(fr, en): return fr if lang == 'fr' else en

# --- 1. HEADER & AMBIANCE ---
title_text = t("La Fracture Spatiale", "The Spatial Divide")
st.markdown(f"""
<div class="status-header" style="border-left-color: #58a6ff;">
    <div class="status-text" style="color: #c9d1d9;">
        <div class="live-indicator" style="background-color: #58a6ff; box-shadow: 0 0 10px #58a6ff;"></div>
        {t("ANALYSE TERRITORIALE", "TERRITORIAL ANALYSIS")} | {title_text.upper()}
    </div>
    <div style="color: #8b949e; font-family: monospace; font-size: 0.9rem;">
        {t("MODE: Visualisation 3D Interactive", "MODE: Interactive 3D Visualization")}
    </div>
</div>
""", unsafe_allow_html=True)

title_text2 = t("Où se concentrent les véritables enjeux ?", "Where are the real stakes concentrated?")
st.markdown(f"<h1 style='margin-top: 0;'><span class='benin-flag-glow' style='font-size: 2rem; margin-right: 15px;'>🇧🇯</span>{title_text2}</h1>", unsafe_allow_html=True)
subtitle_desc = t("Une vue aérienne des dynamiques du pays. Naviguez sur la carte pour explorer les zones d'activité et d'alerte.", "An aerial view of the country's dynamics. Navigate the map to explore activity and alert zones.")
st.markdown(f"<p style='color:#8b949e; font-size: 1.1rem;'>{subtitle_desc}</p>", unsafe_allow_html=True)

# Explication simplifiée pour non-codeurs
p1 = t("Sur cette carte interactive, il y a des 'piliers' sur chaque département.", "On this interactive map, there are 'pillars' on each department.")
p2 = t("Plus le pilier est <b>haut</b>, plus il se passe de choses (volume d'événements). Plus le pilier tire vers le <b>rouge</b>, plus l'actualité y est tendue. Les piliers <b>bleus/verts</b> signalent au contraire des zones stables et dynamiques.", "The <b>higher</b> the pillar, the more things are happening (event volume). The more the pillar tends towards <b>red</b>, the more tense the news is there. The <b>blue/green</b> pillars, on the other hand, indicate stable and dynamic areas.")

st.markdown(f"""
<div class="insight-box" style="border-left-color: #58a6ff; margin-bottom: 30px;">
    <h4 style="color: #58a6ff; margin-top: 0;">{t("Comment lire cette carte 3D ?", "How to read this 3D map?")}</h4>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 10px;">{p1}</p>
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">{p2}</p>
</div>
""", unsafe_allow_html=True)

geo_data = load_geographic_hotspots()
geo_data = geo_data.dropna(subset=['lat', 'lon', 'event_count'])

# Couleurs plus éclatantes (Neon Cyber)
geo_data['color_r'] = geo_data['mean_goldstein'].apply(lambda x: 255 if x < 0 else 88)
geo_data['color_g'] = geo_data['mean_goldstein'].apply(lambda x: 80 if x < 0 else 166)
geo_data['color_b'] = geo_data['mean_goldstein'].apply(lambda x: 80 if x < 0 else 255)
geo_data['color'] = geo_data.apply(lambda row: [row['color_r'], row['color_g'], row['color_b'], 200], axis=1)

tab_name1 = t("Radar Géospatial (Vue 3D)", "Geospatial Radar (3D View)")
tab_name2 = t("Carte de Chaleur (Densité)", "Heatmap (Density)")

tab1, tab2 = st.tabs([tab_name1, tab_name2])

with tab1:
    col_title = t("Explorateur Interactif", "Interactive Explorer")
    col_desc = t("👉 <b>Astuce :</b> Utilisez le bouton droit de votre souris (ou maintenez CTRL + Clic) pour faire pivoter la carte en 3D.", "👉 <b>Tip:</b> Use your right mouse button (or hold CTRL + Click) to rotate the map in 3D.")
    
    st.markdown(f"#### {col_title}")
    st.markdown(f"<p style='color: #8b949e; font-size: 0.95rem; margin-bottom: 1rem;'>{col_desc}</p>", unsafe_allow_html=True)
    
    # Couche 1: Piliers 3D (ColumnLayer)
    layer_col = pdk.Layer(
        "ColumnLayer",
        data=geo_data,
        get_position=["lon", "lat"],
        get_elevation="event_count",
        elevation_scale=50,
        radius=15000,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )
    
    # Couche 2: Halo lumineux autour des zones de tension (Scatterplot)
    hotspots = geo_data[geo_data['mean_goldstein'] < -2]
    layer_glow = pdk.Layer(
        "ScatterplotLayer",
        data=hotspots,
        get_position=["lon", "lat"],
        get_color=[255, 75, 75, 50], # Rouge transparent
        get_radius=40000, # Large halo
        pickable=False,
    )
    
    # Couche 3: Halo autour des zones stables
    stable = geo_data[geo_data['mean_goldstein'] > 2]
    layer_glow_stable = pdk.Layer(
        "ScatterplotLayer",
        data=stable,
        get_position=["lon", "lat"],
        get_color=[88, 166, 255, 50], # Bleu transparent
        get_radius=40000,
        pickable=False,
    )

    view_state = pdk.ViewState(
        longitude=2.3158,
        latitude=9.3077,
        zoom=6.2,
        pitch=45,
        bearing=15
    )
    
    # IMPORTANT: On utilise CARTO_DARK pour forcer l'affichage de la carte de fond sans clé API Mapbox
    r = pdk.Deck(
        layers=[layer_glow, layer_glow_stable, layer_col],
        initial_view_state=view_state,
        tooltip={"html": "<div style='font-family: Arial; padding: 5px;'><b style='font-size: 1.2em;'>{region_name}</b><br/><br/><b>Volume d'Activité :</b> {event_count} événements<br/><b>Indice de Tension :</b> {mean_goldstein}</div>"},
        map_provider="carto",
        map_style=pdk.map_styles.CARTO_DARK,
        height=600
    )
    st.pydeck_chart(r)

with tab2:
    hm_title = t("Analyse de Densité Historique", "Historical Density Analysis")
    st.markdown(f"#### {hm_title}")
    hm_desc = t("Cette carte affiche la répartition de tous les événements au fil du temps.", "This map shows the distribution of all events over time.")
    st.markdown(f"<p style='color: #8b949e; font-size: 0.95rem; margin-bottom: 1rem;'>{hm_desc}</p>", unsafe_allow_html=True)
    
    html_map_path = "d:/Nouveau dossier/Hack  Isheero/GDELT_PROJECT-main/notebooks/viz4_carte_benin_2025.html"
    
    if os.path.exists(html_map_path):
        with st.container():
            st.markdown("""
            <div style="border: 1px solid #30363d; border-radius: 8px; overflow: hidden; background: #0d1117; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            """, unsafe_allow_html=True)
            with open(html_map_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=650, scrolling=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        err_msg = t(
            f"La carte de chaleur n'a pas pu être chargée.", 
            f"The heatmap could not be loaded."
        )
        st.info(err_msg)
