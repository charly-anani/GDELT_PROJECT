!pip install pandas-gbq google-auth --quiet

import os
import hashlib
import pandas as pd
import pandas_gbq
import plotly.express as px
import plotly.io as pio
pio.templates.default = "plotly_dark"

PROJECT_ID = "gdelt-494812"
DATASET_ID = "benin_2025"
KEY_PATH = "gdelt-494812-e7b391e14150.json"
def get_credentials():
    if os.path.exists(KEY_PATH):
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(KEY_PATH)
    return None

credentials = get_credentials()
os.makedirs("cache/", exist_ok=True)

def charger_donnees(query, force_reload=False):
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
    cache_path = f"cache/cache_{query_hash}.csv"
    if os.path.exists(cache_path) and not force_reload:
        df = pd.read_csv(cache_path)
    else:
        df = pandas_gbq.read_gbq(query, project_id=PROJECT_ID, credentials=credentials)
        df.to_csv(cache_path, index=False)
    return df
query_events_head = f"""
SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.events_clean`
LIMIT 5
"""

df_events = charger_donnees(query_events_head)
df_events.head()
query_gkg_head = f"""
SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.gkg_clean`
LIMIT 5
"""

df_gkg = charger_donnees(query_gkg_head)
df_gkg.head()
query_mentions_head = f"""
SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.mentions_clean`
LIMIT 5
"""

df_mentions = charger_donnees(query_mentions_head)
df_mentions.head()


# Récupère le nombre total d'événements par mois depuis la table events_clean
query_volume_evenements = f"""
SELECT
    MonthYear AS year_month,
    COUNT(*) AS volume_events
FROM `{PROJECT_ID}.{DATASET_ID}.events_clean`
WHERE MonthYear IS NOT NULL
GROUP BY year_month
ORDER BY year_month
"""
# Exécute la requête SQL et charge les résultats dans un DataFrame pandas
df_events_volume = charger_donnees(query_volume_evenements).copy()
# Convertit la colonne mensuelle au format date puis trie les données chronologiquement
df_events_volume["year_month"] = pd.to_datetime(
    df_events_volume["year_month"].astype(str),
    format="%Y%m"
)
df_events_volume = df_events_volume.sort_values("year_month").reset_index(drop=True)
df_events_volume["label_month"] = df_events_volume["year_month"].dt.strftime("%b %Y")
# Identifie le mois le plus actif, le mois le plus calme et la moyenne mensuelle
idx_max = df_events_volume["volume_events"].idxmax()
idx_min = df_events_volume["volume_events"].idxmin()

mois_max = df_events_volume.loc[idx_max, "label_month"]
val_max  = int(df_events_volume.loc[idx_max, "volume_events"])

mois_min = df_events_volume.loc[idx_min, "label_month"]
val_min  = int(df_events_volume.loc[idx_min, "volume_events"])
# Crée une courbe temporelle pour visualiser l'évolution mensuelle du volume d'événements
fig_events = px.line(
    df_events_volume,
    x="year_month",
    y="volume_events",
    markers=True,
    title="Évolution mensuelle du volume d'événements sur le Bénin"
)
# Personnalise la ligne principale, les points, la zone remplie et le survol
fig_events.update_traces(
    line=dict(color="#2F6BFF", width=3),
    marker=dict(size=8, color="#2F6BFF"),
    fill="tozeroy",
    fillcolor="rgba(47,107,255,0.08)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Événements : %{y:,}<extra></extra>"
)
# Réinitialisons les annotations pour éviter les doublons à chaque ré-exécution
fig_events.layout.annotations = []

# Ajoutons les annotations pour le mois le plus actif et le mois le plus calme
fig_events.add_annotation(
    x=df_events_volume.loc[idx_max, "year_month"],
    y=val_max,
    text=f"Mois le plus actif<br><b>{mois_max}</b><br>{val_max:,} événements",
    showarrow=True, arrowhead=2, ax=0, ay=-85,
    bgcolor="rgba(228,87,86,0.12)", bordercolor="#E45756", borderwidth=1,
    font=dict(size=11)
)

fig_events.add_annotation(
    x=df_events_volume.loc[idx_min, "year_month"],
    y=val_min,
    text=f"Mois le plus calme<br><b>{mois_min}</b><br>{val_min:,} événements",
    showarrow=True, arrowhead=2, ax=0, ay=-85,
    bgcolor="rgba(44,177,161,0.12)", bordercolor="#2CB1A1", borderwidth=1,
    font=dict(size=11)
)

# Affichons le total global comme sous-titre intégré dans le graphique
fig_events.add_annotation(
    text=f"Total annuel : <b>{df_events_volume['volume_events'].sum():,} événements</b>",
    xref="paper", yref="paper",
    x=1.0, y=1.08, xanchor="right", showarrow=False,
    font=dict(size=13, color="#6B7280"),
    bgcolor="rgba(0,0,0,0.04)", bordercolor="rgba(0,0,0,0.08)", borderwidth=1
)

fig_events.show()



# ── Palette centralisée ─────────────────────────────────────────────
# ── Palette centralisée — Jaune (Coopération) & Rouge (Conflit) ─────
COLOR_COOP_DARK  = "#F5A800"   # Jaune ambré foncé  — Verbal Cooperation
COLOR_COOP_LIGHT = "#FFD166"   # Jaune doux clair   — Material Cooperation
COLOR_CONF_DARK  = "#E45756"   # Rouge vif foncé    — Verbal Conflict
COLOR_CONF_LIGHT = "#FF9E9E"   # Rouge rosé clair   — Material Conflict

# ── Query ───────────────────────────────────────────────────────────
query_donut = f"""
SELECT
    QuadClass_Label,
    interaction_type,
    COUNT(*) AS nb_events
FROM `{PROJECT_ID}.{DATASET_ID}.events_clean`
WHERE QuadClass_Label IS NOT NULL
GROUP BY QuadClass_Label, interaction_type
ORDER BY nb_events DESC
"""
df_donut = charger_donnees(query_donut)

# ── Palette fixe sur les 4 labels GDELT ─────────────────────────────
color_map_donut = {
    "Verbal Cooperation":   COLOR_COOP_DARK,
    "Material Cooperation": COLOR_COOP_LIGHT,
    "Verbal Conflict":      COLOR_CONF_DARK,
    "Material Conflict":    COLOR_CONF_LIGHT
}

# ── KPIs ─────────────────────────────────────────────────────────────
total = df_donut["nb_events"].sum()

# ── Figure ───────────────────────────────────────────────────────────
fig_donut = px.pie(
    df_donut,
    names="QuadClass_Label",
    values="nb_events",
    hole=0.45,
    title="Bénin 2025 : Répartition des types d'événements (Coopération vs Conflit)",
    color="QuadClass_Label",
    color_discrete_map=color_map_donut
)

fig_donut.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Événements : %{value:,}<br>"
        "Part : %{percent:.1%}"
        "<extra></extra>"
    )
)

fig_donut.update_layout(
    template="plotly_dark",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    annotations=[dict(
        text=f"<b>{total:,}</b><br>événements",
        x=0.5, y=0.5,
        font=dict(size=13, color="white"),
        showarrow=False
    )],
    title=dict(font=dict(size=16)),
    margin=dict(t=60, b=80, l=20, r=20)
)

fig_donut.show()

# Question : évolution coopération vs conflit dans le temps
query_coop_vs_conflit = f"""
SELECT
    MonthYear AS year_month,
    interaction_type,
    COUNT(*) AS nb_events,
    AVG(GoldsteinScale) AS score_goldstein_moyen
FROM `{PROJECT_ID}.{DATASET_ID}.events_clean`
WHERE MonthYear IS NOT NULL
GROUP BY year_month, interaction_type
ORDER BY year_month
"""
df_coop = charger_donnees(query_coop_vs_conflit)
df_coop["year_month"] = pd.to_datetime(df_coop["year_month"].astype(str), format="%Y%m")

fig_coop = px.line(
    df_coop,
    x="year_month",
    y="nb_events",
    color="interaction_type",
    markers=True,
    title="Coopération vs Conflit au Bénin — Évolution 2025",
    color_discrete_map={
        "Cooperation": "#2F6BFF",   # bleu
        "Conflict":    "#E45756"    # rouge
    }
)
fig_coop.update_traces(line=dict(width=2.5), marker=dict(size=7))
fig_coop.update_layout(
    template="plotly_dark",
    legend_title_text="Type d'interaction",
    xaxis_title="Mois",
    yaxis_title="Nombre d'événements",
    hovermode="x unified"
)
fig_coop.show()



# — Ton médiatique mensuel depuis gkg_clean
query_tone = f"""
SELECT
  DATE_TRUNC(PARSE_DATE('%Y%m%d', SUBSTR(CAST(DATE AS STRING), 1, 8)), MONTH) AS year_month,
  AVG(CAST(SPLIT(V2Tone, ',')[OFFSET(0)] AS FLOAT64)) AS tone_moyen,
  COUNT(*) AS nb_articles
FROM `{PROJECT_ID}.{DATASET_ID}.gkg_clean`
WHERE V2Tone IS NOT NULL
  AND DATE IS NOT NULL
GROUP BY year_month
ORDER BY year_month
"""

df_tone = charger_donnees(query_tone).copy()
df_tone['year_month'] = pd.to_datetime(df_tone['year_month'])
df_tone = df_tone.sort_values('year_month').reset_index(drop=True)
df_tone['label_month'] = df_tone['year_month'].dt.strftime('%b %Y')

# Identifier les extremes
idx_min = df_tone['tone_moyen'].idxmin()
idx_max = df_tone['tone_moyen'].idxmax()

mois_negatif = df_tone.loc[idx_min, 'label_month']
val_negatif = round(df_tone.loc[idx_min, 'tone_moyen'], 2)

mois_positif = df_tone.loc[idx_max, 'label_month']
val_positif = round(df_tone.loc[idx_max, 'tone_moyen'], 2)

tone_moyen_global = round(df_tone['tone_moyen'].mean(), 2)
COLOR_NEG = '#E45756'
COLOR_POS = '#2CB1A1'
COLOR_LINE = '#2F6BFF'

fig_tone = px.line(
    df_tone,
    x='year_month',
    y='tone_moyen',
    markers=True,
    title='Évolution mensuelle du ton médiatique autour du Bénin — 2025'
)

fig_tone.update_traces(
    line=dict(color=COLOR_LINE, width=3),
    marker=dict(size=8, color=COLOR_LINE),
    hovertemplate='<b>%{x|%b %Y}</b><br>Ton moyen : %{y:.2f}<extra></extra>'
)

# Ligne de référence à 0 (neutre)
fig_tone.add_hline(
    y=0,
    line_dash='dash',
    line_color='rgba(255,255,255,0.3)',
    annotation_text='Ton neutre (0)',
    annotation_position='bottom right',
    annotation_font_size=11
)

# Annotation mois le plus négatif
fig_tone.add_annotation(
    x=df_tone.loc[idx_min, 'year_month'],
    y=val_negatif,
    text=f'Mois le plus négatif<br><b>{mois_negatif}</b><br>{val_negatif}',
    showarrow=True, arrowhead=2, ax=0, ay=-70,
    bgcolor='rgba(228,87,86,0.12)', bordercolor=COLOR_NEG,
    borderwidth=1, font=dict(size=11)
)

# Annotation mois le plus positif
fig_tone.add_annotation(
    x=df_tone.loc[idx_max, 'year_month'],
    y=val_positif,
    text=f'Mois le plus positif<br><b>{mois_positif}</b><br>{val_positif}',
    showarrow=True, arrowhead=2, ax=0, ay=-70,
    bgcolor='rgba(44,177,161,0.12)', bordercolor=COLOR_POS,
    borderwidth=1, font=dict(size=11)
)

# Moyenne globale en sous-titre
fig_tone.add_annotation(
    text=f'Ton moyen global 2025 : <b>{tone_moyen_global}</b>',
    xref='paper', yref='paper',
    x=1.0, y=1.08, xanchor='right',
    showarrow=False,
    font=dict(size=13, color='#6B7280'),
    bgcolor='rgba(0,0,0,0.04)', bordercolor='rgba(0,0,0,0.08)', borderwidth=1
)

fig_tone.update_layout(
    template='plotly_dark',
    xaxis_title='Mois',
    yaxis_title='Ton moyen (V2Tone)',
    legend=dict(tracegroupgap=0)
)

fig_tone.show()

# ── Palette pour le ton ─────────────────────────────────────────
COLOR_VERY_NEG = "#8B0000"    
COLOR_NEG      = "#E45756"    
COLOR_NEUTRAL  = "#A6ACAF"    
COLOR_POS      = "#2CB1A1"     
COLOR_VERY_POS = "#00C853"  

# ── Query — Distribution des sentiments (donut) ──────────────────
query_tone_distrib = f"""
SELECT
    tone_category,
    COUNT(*) AS nb_articles
FROM `{PROJECT_ID}.{DATASET_ID}.gkg_clean`
WHERE tone_category IS NOT NULL
GROUP BY tone_category
ORDER BY nb_articles DESC
"""
df_tone_distrib = charger_donnees(query_tone_distrib)

# ── Palette fixe sur les 5 catégories de ton ────────────────────
color_map_tone = {
    "Very Negative": COLOR_VERY_NEG,
    "Negative":      COLOR_NEG,
    "Neutral":       COLOR_NEUTRAL,
    "Positive":      COLOR_POS,
    "Very Positive": COLOR_VERY_POS
}

# ── KPIs ──────────────────────────────────────────────────────────
total_articles = df_tone_distrib["nb_articles"].sum()

# ── Figure ────────────────────────────────────────────────────────
fig_tone = px.pie(
    df_tone_distrib,
    names="tone_category",
    values="nb_articles",
    hole=0.45,
    title="Bénin 2025 : Distribution du ton médiatique (V2Tone)",
    color="tone_category",
    color_discrete_map=color_map_tone,
    category_orders={"tone_category": ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"]}
)

fig_tone.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Articles : %{value:,}<br>"
        "Part : %{percent:.1%}"
        "<extra></extra>"
    )
)

fig_tone.update_layout(
    template="plotly_dark",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    annotations=[dict(
        text=f"<b>{total_articles:,}</b><br>articles",
        x=0.5, y=0.5,
        font=dict(size=13, color="white"),
        showarrow=False
    )],
    title=dict(font=dict(size=16)),
    margin=dict(t=60, b=80, l=20, r=20)
)

fig_tone.show()


# VIZ 4 — Cartographie des événements GDELT au Bénin 2025
query_carte = f"""
SELECT
  ActionGeo_FullName    AS lieu,
  ActionGeo_Lat         AS lat,
  ActionGeo_Long        AS lon,
  interaction_type,
  COUNT(*)              AS nb_events,
  AVG(GoldsteinScale)   AS goldstein_moyen
FROM `{PROJECT_ID}.{DATASET_ID}.events_clean`
WHERE
  ActionGeo_CountryCode = 'BN'
  AND ActionGeo_Lat  IS NOT NULL
  AND ActionGeo_Long IS NOT NULL
  AND CAST(Year AS INT64) = 2025
GROUP BY lieu, lat, lon, interaction_type
ORDER BY nb_events DESC
"""

df_carte = charger_donnees(query_carte).copy()
# Installation de la bibliothèque Folium pour la cartographie interactive
!pip install folium --quiet

import folium
from folium.plugins import HeatMap
import pandas as pd

# PRÉPARATION DES DONNÉES

# Agrégation des données par lieu géographique
df_map = (
    df_carte
    .groupby(["lieu", "lat", "lon"])
    .agg(
        nb_events        = ("nb_events",        "sum"),
        interaction_type = ("interaction_type", lambda x: x.mode()[0]),
        goldstein_moyen  = ("goldstein_moyen",  "mean"),
    )
    .reset_index()
    .sort_values("nb_events", ascending=False)
)

# Définition des couleurs selon le type d'interaction
COLOR_COOP = "#F5A800"  # Jaune pour la coopération
COLOR_CONF = "#E45756"  # Rouge pour le conflit

df_map["color"] = df_map["interaction_type"].map(
    {"Cooperation": COLOR_COOP, "Conflict": COLOR_CONF}
).fillna("#888888")

# CRÉATION DE LA CARTE DE BASE

# Carte centrée sur le Bénin avec zoom initial
m = folium.Map(
    location=[9.3, 2.3],
    zoom_start=8,
    tiles="OpenStreetMap",
    prefer_canvas=True,
    zoom_control=True,
    scrollWheelZoom=True,
)

# HEATMAP : DENSITÉ SPATIALE DES ÉVÉNEMENTS

# Préparation des données pour la heatmap
heat_data = [
    [row["lat"], row["lon"], row["nb_events"]]
    for _, row in df_map.iterrows()
]

# Ajout de la couche heatmap avec gradient de couleur
HeatMap(
    heat_data,
    radius=18,
    blur=15,
    min_opacity=0.3,
    max_zoom=10,
    gradient={"0.3": "#F5A800", "0.6": "#ff6b35", "1.0": "#E45756"},
).add_to(m)

# MARQUEURS CIRCULAIRES : POINTS INDIVIDUELS

for _, row in df_map.iterrows():
    # Taille du cercle proportionnelle au nombre d'événements
    radius = max(5, min(row["nb_events"] * 0.5, 35))
    
    # Symbole selon le type d'interaction
    symbol = "Cooperation" if row["interaction_type"] == "Cooperation" else "Conflict"
    
    # Contenu du popup
    popup_html = f"""
    <div style="font-family:Inter,sans-serif;min-width:180px;">
        <b style="font-size:14px;">{row['lieu'].split(',')[0]}</b><br>
        <hr style="margin:4px 0;border-color:#eee;">
        <b>{row['interaction_type']}</b><br>
        <b>{int(row['nb_events'])}</b> événements<br>
        Goldstein : <b>{round(row['goldstein_moyen'], 2)}</b>
    </div>
    """
    
    # Ajout du marqueur circulaire
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color="white",
        weight=1.2,
        fill=True,
        fill_color=row["color"],
        fill_opacity=0.82,
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"{row['lieu'].split(',')[0]} - {int(row['nb_events'])} évts",
    ).add_to(m)

# LÉGENDE ET TABLEAU STATISTIQUE PAR RÉGION

# Séparation des données : centroïde national vs villes réelles
CENTROID_LAT, CENTROID_LON = 9.5, 2.25

df_centroid = df_carte[
    (df_carte["lat"] == CENTROID_LAT) & (df_carte["lon"] == CENTROID_LON)
]
df_villes = df_carte[
    ~((df_carte["lat"] == CENTROID_LAT) & (df_carte["lon"] == CENTROID_LON))
]

# Statistiques pour le centroïde national
centroid_total = int(df_centroid["nb_events"].sum())
centroid_conf  = int(df_centroid[df_centroid["interaction_type"] == "Conflict"]["nb_events"].sum())
centroid_coop  = int(df_centroid[df_centroid["interaction_type"] == "Cooperation"]["nb_events"].sum())
centroid_pct_c = round(centroid_conf / centroid_total * 100, 1) if centroid_total > 0 else 0
centroid_pct_k = round(centroid_coop / centroid_total * 100, 1) if centroid_total > 0 else 0

# Classification par région géographique
df_region = df_villes.copy()
df_region["region"] = df_region["lat"].apply(
    lambda x: "Nord (>9°N)" if x > 9 else ("Centre (7–9°N)" if x >= 7 else "Sud (<7°N)")
)

# Tableau croisé par région et type d'interaction
region_pivot = df_region.pivot_table(
    index="region", columns="interaction_type",
    values="nb_events", aggfunc="sum"
).fillna(0)

region_pivot["total"]    = region_pivot.sum(axis=1)
region_pivot["pct_conf"] = (region_pivot.get("Conflict", 0) / region_pivot["total"] * 100).round(1)
region_pivot["pct_coop"] = (region_pivot.get("Cooperation", 0) / region_pivot["total"] * 100).round(1)

# Génération des lignes HTML pour le tableau
region_rows_html = ""
for region in ["Nord (>9°N)", "Centre (7–9°N)", "Sud (<7°N)"]:
    if region in region_pivot.index:
        r = region_pivot.loc[region]
        total = int(r["total"])
        pct_c = r["pct_conf"]
        pct_k = r["pct_coop"]
        bar_color = "#E45756" if pct_c > 40 else ("#ff6b35" if pct_c > 20 else "#F5A800")
        region_rows_html += f"""
        <tr>
            <td style="padding:4px 6px;font-size:11px;font-weight:600;">{region}</td>
            <td style="padding:4px 6px;font-size:11px;text-align:center;">{total}</td>
            <td style="padding:4px 6px;font-size:11px;text-align:center;color:{bar_color};font-weight:700;">{pct_c}%</td>
            <td style="padding:4px 6px;font-size:11px;text-align:center;color:#F5A800;font-weight:700;">{pct_k}%</td>
        </tr>"""

# Ligne pour le centroïde national
region_rows_html += f"""
        <tr style="background:#f9fafb;border-top:1px dashed #d1d5db;">
            <td style="padding:4px 6px;font-size:11px;font-style:italic;color:#6b7280;">Bénin générique</td>
            <td style="padding:4px 6px;font-size:11px;text-align:center;color:#6b7280;">{centroid_total}</td>
            <td style="padding:4px 6px;font-size:11px;text-align:center;color:#9ca3af;">{centroid_pct_c}%</td>
            <td style="padding:4px 6px;font-size:11px;text-align:center;color:#9ca3af;">{centroid_pct_k}%</td>
        </tr>"""

# HTML de la légende complète
legend_html = f"""
<div style="
    position:fixed; bottom:30px; left:30px; z-index:9999;
    background:rgba(255,255,255,0.97); color:#1f2937;
    padding:14px 18px; border-radius:12px;
    font-family:Inter,sans-serif; font-size:13px;
    border:1px solid #e5e7eb; box-shadow:0 4px 20px rgba(0,0,0,0.15);
    max-width:280px;
">
    <b style="font-size:14px;display:block;margin-bottom:8px;">
        Bénin - Événements 2025
    </b>

    <span style="color:#F5A800;font-size:18px;">●</span>&nbsp;Coopération<br>
    <span style="color:#E45756;font-size:18px;">●</span>&nbsp;Conflit<br>

    <div style="margin-top:8px;padding-top:8px;border-top:1px solid #e5e7eb;
                color:#6b7280;font-size:11px;line-height:1.5;">
        Taille du cercle = volume d'événements<br>
        Zone colorée = densité (heatmap)<br>
        Cliquer sur un point pour les détails
    </div>

    <div style="margin-top:10px;padding-top:10px;border-top:1px solid #e5e7eb;">
        <b style="font-size:11px;color:#374151;">Répartition par zone géographique</b>
        <table style="width:100%;margin-top:6px;border-collapse:collapse;">
            <thead>
                <tr style="background:#f9fafb;">
                    <th style="padding:4px 6px;font-size:10px;text-align:left;color:#6b7280;">Région</th>
                    <th style="padding:4px 6px;font-size:10px;text-align:center;color:#6b7280;">Évts</th>
                    <th style="padding:4px 6px;font-size:10px;text-align:center;color:#E45756;">Conflit</th>
                    <th style="padding:4px 6px;font-size:10px;text-align:center;color:#F5A800;">Coop.</th>
                </tr>
            </thead>
            <tbody>
                {region_rows_html}
            </tbody>
        </table>
        <div style="margin-top:5px;font-size:9px;color:#9ca3af;font-style:italic;">
            Note : Bénin générique = articles sans ville précise,<br>
            géolocalisés au centroïde national (9.5°N, 2.25°E)
        </div>
    </div>
</div>
"""

# Ajout de la légende à la carte
m.get_root().html.add_child(folium.Element(legend_html))

# EXPORT DE LA CARTE

m.save("viz4_carte_benin_2025.html")
print("Carte exportée avec succès : viz4_carte_benin_2025.html")


# Évolution mensuelle des mentions GDELT au Bénin en 2025
query_mentions_mois = f"""
SELECT
  m.mention_year_month AS mois,
  COUNT(*)             AS nb_mentions
FROM `{PROJECT_ID}.{DATASET_ID}.mentions_clean` AS m
JOIN `{PROJECT_ID}.{DATASET_ID}.events_clean`   AS e
  ON m.GLOBALEVENTID = e.GLOBALEVENTID
WHERE
  e.ActionGeo_CountryCode = 'BN'
  AND CAST(e.Year AS INT64) = 2025
  AND m.mention_year_month IS NOT NULL
GROUP BY mois
ORDER BY mois ASC
"""

df_mentions_mois = charger_donnees(query_mentions_mois).copy()
import plotly.graph_objects as go

mapping_mois = {
    "2025-01": "Jan", "2025-02": "Fév", "2025-03": "Mar", "2025-04": "Avr",
    "2025-05": "Mai", "2025-06": "Jun", "2025-07": "Jul", "2025-08": "Aoû",
    "2025-09": "Sep", "2025-10": "Oct", "2025-11": "Nov", "2025-12": "Déc"
}

df_mentions_mois["mois_label"] = df_mentions_mois["mois"].map(mapping_mois)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_mentions_mois["mois_label"],
    y=df_mentions_mois["nb_mentions"],
    mode="lines+markers",
    line=dict(
        color="#4f98a3",
        width=3,
        shape="spline",
        smoothing=0.9
    ),
    marker=dict(size=8, color="#4f98a3"),
    fill="tozeroy",
    fillcolor="rgba(79,152,163,0.12)",
    hovertemplate="%{x} : <b>%{y:,}</b> mentions<extra></extra>"
))

fig.update_layout(
    title=dict(
        text="Évolution mensuelle des mentions GDELT (Nombre de mentions GDELT par mois · Bénin 2025)",
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=18, color="#b8c0c8")
    ),
    template="plotly_dark",
    showlegend=False,
    xaxis_title="",
    yaxis_title="Nombre de mentions",
    margin=dict(t=110, l=70, r=40, b=70)
)

fig.add_annotation(
    text="<b>Série temporelle</b>",
    xref="paper", yref="paper",
    x=0.98, y=1.08,
    showarrow=False,
    xanchor="right",
    yanchor="middle",
    font=dict(size=12, color="#4f98a3"),
    bgcolor="rgba(79,152,163,0.12)",
    bordercolor="#4f98a3",
    borderwidth=1,
    borderpad=6
)

fig.show()

#  Langue des sources des mentions GDELT au Bénin en 2025
query_langues = f"""
SELECT
  m.source_language AS langue,
  COUNT(*)          AS nb_mentions
FROM `{PROJECT_ID}.{DATASET_ID}.mentions_clean` AS m
JOIN `{PROJECT_ID}.{DATASET_ID}.events_clean`   AS e
  ON m.GLOBALEVENTID = e.GLOBALEVENTID
WHERE
  e.ActionGeo_CountryCode = 'BN'
  AND CAST(e.Year AS INT64) = 2025
  AND m.source_language IS NOT NULL
GROUP BY langue
ORDER BY nb_mentions DESC
LIMIT 5
"""

df_langues = charger_donnees(query_langues).copy()
import plotly.graph_objects as go

# Calcul des pourcentages
df_langues["pct"] = (
    df_langues["nb_mentions"] / df_langues["nb_mentions"].sum() * 100
).round(1)

# Ordre décroissant
df_langues = df_langues.sort_values("pct", ascending=False)

# Une couleur différente par barre
bar_colors = ["#4f98a3", "#e8af34", "#6daa45", "#fdab43", "#a86fdf"]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_langues["langue"],
    y=df_langues["pct"],
    marker_color=bar_colors[:len(df_langues)],
    marker_line_color="rgba(255,255,255,0.10)",
    marker_line_width=1,
    text=df_langues["pct"].astype(str) + "%",
    textposition="outside",
    hovertemplate="%{x} : <b>%{y}%</b><extra></extra>"
))

fig.update_layout(
    title=dict(
        text="Langue des sources (source_language — top 5 langues)",
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=18, color="#b8c0c8")
    ),
    template="plotly_dark",
    showlegend=False,
    xaxis_title="",
    yaxis_title="% des mentions",
    margin=dict(t=110, l=70, r=40, b=70),
    width=1100,
    height=520,
    bargap=0.22,
    barcornerradius=12
)

fig.add_annotation(
    text="<b>Bar chart</b>",
    xref="paper", yref="paper",
    x=0.98, y=1.08,
    showarrow=False,
    xanchor="right",
    yanchor="middle",
    font=dict(size=12, color="#4f98a3"),
    bgcolor="rgba(79,152,163,0.12)",
    bordercolor="#4f98a3",
    borderwidth=1,
    borderpad=6
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="rgba(255,255,255,0.08)",
    zeroline=False
)

fig.update_xaxes(showgrid=False)

fig.show()



#  Niveau de confiance des mentions GDELT au Bénin en 2025
query_confidence = f"""
SELECT
  m.confidence_level AS confidence_cat,
  COUNT(*)           AS nb_mentions
FROM `{PROJECT_ID}.{DATASET_ID}.mentions_clean` AS m
JOIN `{PROJECT_ID}.{DATASET_ID}.events_clean`   AS e
  ON m.GLOBALEVENTID = e.GLOBALEVENTID
WHERE
  e.ActionGeo_CountryCode = 'BN'
  AND CAST(e.Year AS INT64) = 2025
  AND m.confidence_level IS NOT NULL
GROUP BY confidence_cat
ORDER BY nb_mentions DESC
"""

df_confidence = charger_donnees(query_confidence).copy()
import plotly.graph_objects as go

# Calcul des pourcentages
df_confidence["pct"] = (
    df_confidence["nb_mentions"] / df_confidence["nb_mentions"].sum() * 100
).round(1)

# Harmoniser les labels si besoin
df_confidence["confidence_cat"] = df_confidence["confidence_cat"].str.title()

# Couleurs : vert (High), jaune (Medium), rouge (Low)
colors_confidence = {
    "High": "rgba(109,170,69,1.0)",    # vert
    "Medium": "rgba(232,175,52,1.0)",  # jaune
    "Low": "rgba(209,99,99,1.0)"       # rouge
}

# Trier par pct décroissant
df_confidence = df_confidence.sort_values("pct", ascending=False)

# Appliquer les couleurs dans l'ordre trié
bar_colors = [colors_confidence.get(c, "#b8c0c8") for c in df_confidence["confidence_cat"]]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_confidence["confidence_cat"],
    y=df_confidence["pct"],
    marker_color=bar_colors,
    marker_line_color="rgba(255,255,255,0.10)",
    marker_line_width=1,
    text=df_confidence["pct"].astype(str) + "%",
    textposition="outside",
    hovertemplate="%{x} : <b>%{y}%</b><extra></extra>"
))

fig.update_layout(
    title=dict(
        text="Niveau de confiance (confidence_level par catégorie)",
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=18, color="#b8c0c8")
    ),
    template="plotly_dark",
    showlegend=False,
    xaxis_title="",
    yaxis_title="% des mentions",
    margin=dict(t=110, l=70, r=40, b=70),
    width=1100,
    height=520,
    bargap=0.22,
    barcornerradius=12
)

fig.add_annotation(
    text="<b>Bar chart</b>",
    xref="paper", yref="paper",
    x=0.98, y=1.08,
    showarrow=False,
    xanchor="right",
    yanchor="middle",
    font=dict(size=12, color="#4f98a3"),
    bgcolor="rgba(79,152,163,0.12)",
    bordercolor="#4f98a3",
    borderwidth=1,
    borderpad=6
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="rgba(255,255,255,0.08)",
    zeroline=False,
    range=[0, df_confidence["pct"].max() * 1.2]
)

fig.update_xaxes(showgrid=False)

fig.show()



# Ton éditorial des mentions GDELT au Bénin en 2025
query_tone = f"""
SELECT
  m.tone_category AS tone_cat,
  COUNT(*)        AS nb_mentions
FROM `{PROJECT_ID}.{DATASET_ID}.mentions_clean` AS m
JOIN `{PROJECT_ID}.{DATASET_ID}.events_clean`   AS e
  ON m.GLOBALEVENTID = e.GLOBALEVENTID
WHERE
  e.ActionGeo_CountryCode = 'BN'
  AND CAST(e.Year AS INT64) = 2025
  AND m.tone_category IS NOT NULL
GROUP BY tone_cat
ORDER BY nb_mentions DESC
"""

df_tone = charger_donnees(query_tone).copy()
import plotly.graph_objects as go

# Calcul des pourcentages
df_tone["pct"] = (
    df_tone["nb_mentions"] / df_tone["nb_mentions"].sum() * 100
).round(1)

# Harmoniser les libellés si besoin
df_tone["tone_cat"] = df_tone["tone_cat"].astype(str).str.strip().str.title()

# Tri décroissant par proportion
df_tone = df_tone.sort_values("pct", ascending=False)

# Couleurs selon le ton
colors_tone = {
    "Very Positive": "#3fa34d",
    "Positive": "#6daa45",
    "Neutral": "#e8af34",
    "Negative": "#d16363",
    "Very Negative": "#b23a48"
}

bar_colors = [colors_tone.get(c, "#b8c0c8") for c in df_tone["tone_cat"]]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_tone["tone_cat"],
    y=df_tone["pct"],
    marker_color=bar_colors,
    marker_line_color="rgba(255,255,255,0.10)",
    marker_line_width=1,
    text=df_tone["pct"].astype(str) + "%",
    textposition="outside",
    hovertemplate="%{x} : <b>%{y}%</b><extra></extra>"
))

fig.update_layout(
    title=dict(
        text="Ton éditorial des mentions (tone_category — MentionDocTone)",
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=18, color="#b8c0c8")
    ),
    template="plotly_dark",
    showlegend=False,
    xaxis_title="",
    yaxis_title="% des mentions",
    margin=dict(t=110, l=70, r=40, b=70),
    width=1100,
    height=520,
    bargap=0.22,
    barcornerradius=12
)

fig.add_annotation(
    text="<b>Bar chart</b>",
    xref="paper", yref="paper",
    x=0.98, y=1.08,
    showarrow=False,
    xanchor="right",
    yanchor="middle",
    font=dict(size=12, color="#4f98a3"),
    bgcolor="rgba(79,152,163,0.12)",
    bordercolor="#4f98a3",
    borderwidth=1,
    borderpad=6
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="rgba(255,255,255,0.08)",
    zeroline=False,
    range=[0, df_tone["pct"].max() * 1.2]
)

fig.update_xaxes(showgrid=False)

fig.show()


#  Part des mentions traduites vs non traduites · Bénin 2025
query_translated = f"""
SELECT
  m.is_translated AS is_translated,
  COUNT(*)        AS nb_mentions
FROM `{PROJECT_ID}.{DATASET_ID}.mentions_clean` AS m
JOIN `{PROJECT_ID}.{DATASET_ID}.events_clean`   AS e
  ON m.GLOBALEVENTID = e.GLOBALEVENTID
WHERE
  e.ActionGeo_CountryCode = 'BN'
  AND CAST(e.Year AS INT64) = 2025
  AND m.is_translated IS NOT NULL
GROUP BY is_translated
ORDER BY nb_mentions DESC
"""

df_translated = charger_donnees(query_translated).copy()
import plotly.graph_objects as go

# Remapper True/False en labels lisibles
df_translated["translated_label"] = df_translated["is_translated"].map({
    True: "Traduit (Translingual)",
    False: "Non traduit"
})

# Calcul des pourcentages
df_translated["pct"] = (
    df_translated["nb_mentions"] / df_translated["nb_mentions"].sum() * 100
).round(1)

# Tri décroissant
df_translated = df_translated.sort_values("pct", ascending=False)

# Couleurs : bleu pour traduit, gris pour non traduit
bar_colors = []
for v in df_translated["is_translated"]:
    if v:
        bar_colors.append("#4f98a3")  # traduit
    else:
        bar_colors.append("#7f8c8d")  # non traduit

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_translated["translated_label"],
    y=df_translated["pct"],
    marker_color=bar_colors,
    marker_line_color="rgba(255,255,255,0.10)",
    marker_line_width=1,
    text=df_translated["pct"].astype(str) + "%",
    textposition="outside",
    hovertemplate="%{x} : <b>%{y}%</b><extra></extra>"
))

fig.update_layout(
    title=dict(
        text="Part des mentions traduites (is_translated)",
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=18, color="#b8c0c8")
    ),
    template="plotly_dark",
    showlegend=False,
    xaxis_title="",
    yaxis_title="% des mentions",
    margin=dict(t=110, l=70, r=40, b=70),
    width=900,
    height=480,
    bargap=0.35,
    barcornerradius=12
)

fig.add_annotation(
    text="<b>Bar chart</b>",
    xref="paper", yref="paper",
    x=0.98, y=1.08,
    showarrow=False,
    xanchor="right",
    yanchor="middle",
    font=dict(size=12, color="#4f98a3"),
    bgcolor="rgba(79,152,163,0.12)",
    bordercolor="#4f98a3",
    borderwidth=1,
    borderpad=6
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="rgba(255,255,255,0.08)",
    zeroline=False,
    range=[0, df_translated["pct"].max() * 1.3]
)

fig.update_xaxes(showgrid=False)

fig.show()


# Top 19 EventCategory · Bénin 2025

query_eventcategory = f"""
SELECT
  EventCategory,
  COUNT(*) AS nb_occurrences
FROM `{PROJECT_ID}.{DATASET_ID}.events_clean`
WHERE
  EventCategory IS NOT NULL
GROUP BY
  EventCategory
ORDER BY
  nb_occurrences DESC
"""

df_eventcategory = charger_donnees(query_eventcategory).copy()
df_eventcategory.to_csv("eventcategory_benin_2025.csv", index=False, encoding="utf-8")

# Afficher le top
df_eventcategory
import plotly.express as px


# Bar chart horizontal trié croissant pour lecture naturelle
fig_eventcat = px.bar(
    df_eventcategory.sort_values("nb_occurrences", ascending=True),
    x="nb_occurrences",
    y="EventCategory",
    orientation="h",
    text="nb_occurrences",
    title="Catégories d'événements GDELT au Bénin en 2025",
    labels={
        "nb_occurrences": "Nombre d'événements",
        "EventCategory": "Catégorie"
    },
    color="nb_occurrences",
    color_continuous_scale="RdYlGn"  # Rouge (conflit) → Jaune → Vert (coopération)
)


fig_eventcat.update_traces(
    textposition="outside",
    textfont=dict(size=13),
    hovertemplate="<b>%{y}</b><br>Événements : %{x:,}<extra></extra>"
)


fig_eventcat.update_layout(
    template="plotly_dark",
    height=900,
    width=1500,
    showlegend=False,
    coloraxis_showscale=False,
    title_x=0.02,
    title_font_size=20,
    margin=dict(l=20, r=140, t=80, b=50),
    font=dict(size=14, family="Inter, Arial, sans-serif")
)


fig_eventcat.update_xaxes(
    showgrid=True,
    gridcolor="rgba(255,255,255,0.12)",
    title_font_size=14
)


fig_eventcat.update_yaxes(
    showgrid=False,
    title_font_size=14
)

# Enregistrement de la visualisation en fichier HTML interactif
fig_eventcat.write_html("categories_evenements_gdelt_benin_2025.html")

fig_eventcat.show()
