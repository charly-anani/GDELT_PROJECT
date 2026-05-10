# assistant/core/chart_router.py

from typing import Any, Dict, Optional

import folium
import pandas as pd
import plotly.express as px
from folium.plugins import HeatMap

from assistant.core.chart_style import (
    PALETTE,
    apply_plotly_style,
    normalize_date_column,
)

COLOR_COOP = PALETTE["secondary"]
COLOR_CONF = PALETTE["primary"]
COLOR_NEUTRAL = PALETTE["neutral"]

BENIN_CENTER = [9.3, 2.3]
BENIN_CENTROID_LAT = 9.5
BENIN_CENTROID_LON = 2.25


def choose_chart(
    df: pd.DataFrame,
    question: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = metadata or {}
    question_lower = question.lower()

    if df.empty:
        return {"chart_type": "table"}

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    object_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    date_like_cols = [
        c for c in df.columns
        if any(tok in c.lower() for tok in ["date", "day", "month", "year"])
    ]

    lat_cols = [c for c in df.columns if "lat" in c.lower()]
    lon_cols = [
        c for c in df.columns
        if "long" in c.lower() or "lon" in c.lower() or "lng" in c.lower()
    ]

    # 1. KPI
    if df.shape == (1, 1):
        return {
            "chart_type": "kpi",
            "value": df.columns[0],
            "title": metadata.get("title") if metadata else None,
        }

    # 2. Carte
    if lat_cols and lon_cols:
        return {
            "chart_type": "map",
            "lat": lat_cols[0],
            "lon": lon_cols[0],
            "title": metadata.get("title") if metadata else "Carte des événements géographiques",
        }

    # 3. Série temporelle
    if date_like_cols and numeric_cols:
        return {
            "chart_type": "line",
            "x": date_like_cols[0],
            "y": numeric_cols[0],
            "title": metadata.get("title") if metadata else None,
        }

    # 4. Répartition / parts de total
    if any(
        kw in question_lower
        for kw in ["répartition", "repartition", "part", "proportion", "pourcentage"]
    ):
        if object_cols and numeric_cols:
            return {
                "chart_type": "pie",
                "category": object_cols[0],
                "value": numeric_cols[0],
                "title": metadata.get("title") if metadata else None,
            }

    # 5. Catégorie + mesure
    if object_cols and numeric_cols:
        return {
            "chart_type": "bar",
            "x": object_cols[0],
            "y": numeric_cols[0],
            "title": metadata.get("title") if metadata else None,
        }

    # 6. Tableau détaillé
    return {"chart_type": "table", "title": metadata.get("title") if metadata else None}


def _pick_first_existing(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _normalize_interaction(value: Any) -> str:
    """
    Normalise les types d'interaction pour la carte.
    Gère par exemple : 'Verbal Cooperation', 'Material Conflict', etc.
    """
    val = str(value).lower()
    if "coop" in val:
        return "Cooperation"
    if "conflict" in val or "conflit" in val:
        return "Conflict"
    return "Unknown"


def _build_folium_map(
    df: pd.DataFrame,
    chart_plan: Dict[str, Any],
) -> Optional[folium.Map]:
    if df.empty:
        return None

    lat_col = chart_plan.get("lat") or _pick_first_existing(df, ["lat", "ActionGeoLat"])
    lon_col = chart_plan.get("lon") or _pick_first_existing(df, ["lon", "ActionGeoLong"])
    place_col = _pick_first_existing(df, ["lieu", "ActionGeoFullName", "location"])
    events_col = _pick_first_existing(df, ["nb_events", "event_count", "count", "NumMentions"])
    interaction_col = _pick_first_existing(df, ["interaction_type", "QuadClassLabel", "interaction"])
    goldstein_col = _pick_first_existing(df, ["goldstein_moyen", "GoldsteinScale", "goldstein"])

    if not lat_col or not lon_col:
        return None

    df_map = df.copy()

    if place_col is None:
        place_col = "__place__"
        df_map[place_col] = "Lieu inconnu"

    if events_col is None:
        events_col = "__events__"
        df_map[events_col] = 1

    if interaction_col is None:
        interaction_col = "__interaction__"
        df_map[interaction_col] = "Unknown"

    if goldstein_col is None:
        goldstein_col = "__goldstein__"
        df_map[goldstein_col] = 0.0

    df_map = df_map.dropna(subset=[lat_col, lon_col]).copy()

    if df_map.empty:
        return None

    def safe_mode(series: pd.Series):
        mode = series.mode()
        if len(mode) > 0:
            return mode.iloc[0]
        return "Unknown"

    grouped = (
        df_map
        .groupby([place_col, lat_col, lon_col], dropna=False)
        .agg(
            nb_events=(events_col, "sum"),
            interaction_type=(interaction_col, safe_mode),
            goldstein_moyen=(goldstein_col, "mean"),
        )
        .reset_index()
        .sort_values("nb_events", ascending=False)
    )

    # Normalisation des types d'interaction
    grouped["interaction_type"] = grouped["interaction_type"].apply(_normalize_interaction)

    grouped["color"] = grouped["interaction_type"].map(
        {"Cooperation": COLOR_COOP, "Conflict": COLOR_CONF}
    ).fillna(COLOR_NEUTRAL)

    m = folium.Map(
        location=BENIN_CENTER,
        zoom_start=8,
        tiles="OpenStreetMap",
        prefer_canvas=True,
        zoom_control=True,
        scrollWheelZoom=True,
    )

    heat_data = [
        [row[lat_col], row[lon_col], row["nb_events"]]
        for _, row in grouped.iterrows()
    ]

    if heat_data:
        HeatMap(
            heat_data,
            radius=18,
            blur=15,
            min_opacity=0.3,
            max_zoom=10,
            gradient={"0.3": COLOR_COOP, "0.6": "#ff6b35", "1.0": COLOR_CONF},
        ).add_to(m)

    for _, row in grouped.iterrows():
        radius = max(5, min(float(row["nb_events"]) * 0.5, 35))
        place_name = str(row[place_col]).split(",")[0]

        popup_html = f"""
        <div style="font-family:Inter,sans-serif;min-width:180px;">
            <b style="font-size:14px;">{place_name}</b><br>
            <hr style="margin:4px 0;border-color:#eee;">
            <b>{row['interaction_type']}</b><br>
            <b>{int(row['nb_events'])}</b> événements<br>
            Goldstein : <b>{round(float(row['goldstein_moyen']), 2)}</b>
        </div>
        """

        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=radius,
            color="white",
            weight=1.2,
            fill=True,
            fill_color=row["color"],
            fill_opacity=0.82,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{place_name} - {int(row['nb_events'])} évts",
        ).add_to(m)

    df_centroid = grouped[
        (grouped[lat_col] == BENIN_CENTROID_LAT)
        & (grouped[lon_col] == BENIN_CENTROID_LON)
    ]

    df_villes = grouped[
        ~(
            (grouped[lat_col] == BENIN_CENTROID_LAT)
            & (grouped[lon_col] == BENIN_CENTROID_LON)
        )
    ].copy()

    centroid_total = int(df_centroid["nb_events"].sum()) if not df_centroid.empty else 0
    centroid_conf = int(
        df_centroid[df_centroid["interaction_type"] == "Conflict"]["nb_events"].sum()
    ) if not df_centroid.empty else 0
    centroid_coop = int(
        df_centroid[df_centroid["interaction_type"] == "Cooperation"]["nb_events"].sum()
    ) if not df_centroid.empty else 0

    centroid_pct_c = round((centroid_conf / centroid_total) * 100, 1) if centroid_total > 0 else 0
    centroid_pct_k = round((centroid_coop / centroid_total) * 100, 1) if centroid_total > 0 else 0

    if not df_villes.empty:
        df_villes["region"] = df_villes[lat_col].apply(
            lambda x: "Nord (>9°N)" if x > 9 else ("Centre (7–9°N)" if x >= 7 else "Sud (<7°N)")
        )

        region_pivot = df_villes.pivot_table(
            index="region",
            columns="interaction_type",
            values="nb_events",
            aggfunc="sum",
        ).fillna(0)

        region_pivot["total"] = region_pivot.sum(axis=1)
        region_pivot["pct_conf"] = (
            region_pivot.get("Conflict", 0) / region_pivot["total"] * 100
        ).round(1)
        region_pivot["pct_coop"] = (
            region_pivot.get("Cooperation", 0) / region_pivot["total"] * 100
        ).round(1)
    else:
        region_pivot = pd.DataFrame()

    region_rows_html = ""
    for region in ["Nord (>9°N)", "Centre (7–9°N)", "Sud (<7°N)"]:
        if region in region_pivot.index:
            r = region_pivot.loc[region]
            total = int(r["total"])
            pct_c = r["pct_conf"]
            pct_k = r["pct_coop"]
            bar_color = COLOR_CONF if pct_c > 40 else ("#ff6b35" if pct_c > 20 else COLOR_COOP)

            region_rows_html += f"""
            <tr>
                <td style="padding:4px 6px;font-size:11px;font-weight:600;">{region}</td>
                <td style="padding:4px 6px;font-size:11px;text-align:center;">{total}</td>
                <td style="padding:4px 6px;font-size:11px;text-align:center;color:{bar_color};font-weight:700;">{pct_c}%</td>
                <td style="padding:4px 6px;font-size:11px;text-align:center;color:{COLOR_COOP};font-weight:700;">{pct_k}%</td>
            </tr>
            """

    region_rows_html += f"""
    <tr style="background:#f9fafb;border-top:1px dashed #d1d5db;">
        <td style="padding:4px 6px;font-size:11px;font-style:italic;color:#6b7280;">Bénin générique</td>
        <td style="padding:4px 6px;font-size:11px;text-align:center;color:#6b7280;">{centroid_total}</td>
        <td style="padding:4px 6px;font-size:11px;text-align:center;color:#9ca3af;">{centroid_pct_c}%</td>
        <td style="padding:4px 6px;font-size:11px;text-align:center;color:#9ca3af;">{centroid_pct_k}%</td>
    </tr>
    """

    legend_html = f"""
    <div style="
        position:fixed; bottom:30px; left:30px; z-index:9999;
        background:rgba(255,255,255,0.97); color:#1f2937;
        padding:14px 18px; border-radius:12px;
        font-family:Inter,sans-serif; font-size:13px;
        border:1px solid #e5e7eb; box-shadow:0 4px 20px rgba(0,0,0,0.15);
        max-width:280px;
    ">
        <b style="font-size:14px;display:block;margin-bottom:8px;">Bénin - Événements</b>

        <span style="color:{COLOR_COOP};font-size:18px;">●</span>&nbsp;Coopération<br>
        <span style="color:{COLOR_CONF};font-size:18px;">●</span>&nbsp;Conflit<br>

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
                        <th style="padding:4px 6px;font-size:10px;text-align:center;color:{COLOR_CONF};">Conflit</th>
                        <th style="padding:4px 6px;font-size:10px;text-align:center;color:{COLOR_COOP};">Coop.</th>
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

    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def build_chart(df: pd.DataFrame, chart_plan: Dict[str, Any]) -> Any:
    chart_type = chart_plan.get("chart_type")
    title = chart_plan.get("title")

    if df.empty:
        return None

    if chart_type == "kpi":
        return None

    if chart_type == "bar":
        x = chart_plan.get("x")
        y = chart_plan.get("y")
        if x and y and x in df.columns and y in df.columns:
            fig = px.bar(
                df,
                x=x,
                y=y,
                color_discrete_sequence=[PALETTE["primary"]],
            )
            return apply_plotly_style(fig, title=title or f"{y} par {x}")
        return None

    if chart_type == "line":
        x = chart_plan.get("x")
        y = chart_plan.get("y")
        if x and y and x in df.columns and y in df.columns:
            df_plot = df.copy()
            df_plot[x] = normalize_date_column(df_plot, x)
            df_plot = df_plot.sort_values(x)

            fig = px.line(
                df_plot,
                x=x,
                y=y,
                markers=True,
                color_discrete_sequence=[PALETTE["primary"]],
            )
            return apply_plotly_style(fig, title=title or f"{y} selon {x}")
        return None

    if chart_type == "pie":
        category = chart_plan.get("category")
        value = chart_plan.get("value")
        if category and value and category in df.columns and value in df.columns:
            fig = px.pie(
                df,
                names=category,
                values=value,
                hole=0.4,
                color_discrete_sequence=[
                    PALETTE["primary"],
                    PALETTE["secondary"],
                    PALETTE["neutral"],
                    "#ff6b35",
                    "#6b7280",
                ],
            )
            return apply_plotly_style(
                fig,
                title=title or f"Répartition de {value} par {category}",
            )
        return None

    if chart_type == "map":
        return _build_folium_map(df, chart_plan)

    if chart_type == "table":
        return None  # Les tables sont gérées par Streamlit directement

    return None