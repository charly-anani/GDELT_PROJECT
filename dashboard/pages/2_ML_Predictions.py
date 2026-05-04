
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import json
from pathlib import Path

# ─── Chemins des modèles ──────────────────────────────────────────────────────
# Adapter le chemin si ton repo a une structure différente
MODELS_DIR = Path(__file__).parent.parent / "models"

# ─── Chargement des modèles ───────────────────────────────────────────────────
@st.cache_resource
def load_models():
    """
    Charge les modèles sauvegardés par ml_model.ipynb.
    Retourne None pour chaque artefact manquant afin d'afficher
    un message d'erreur clair plutôt que de planter.
    """
    clf, kmeans, scaler, meta = None, None, None, {}

    try:
        clf = joblib.load(MODELS_DIR / "sentiment_classifier.pkl")
    except FileNotFoundError:
        pass

    try:
        kmeans = joblib.load(MODELS_DIR / "kmeans_events.pkl")
    except FileNotFoundError:
        pass

    try:
        scaler = joblib.load(MODELS_DIR / "scaler_cluster.pkl")
    except FileNotFoundError:
        pass

    try:
        meta = json.loads((MODELS_DIR / "model_metadata.json").read_text())
    except FileNotFoundError:
        pass

    return clf, kmeans, scaler, meta


clf, kmeans, scaler, meta = load_models()

# ─── En-tête ─────────────────────────────────────────────────────────────────
st.title("Machine Learning — Prédiction & Clustering")
st.caption("Analyse GDELT 2025 · iSHEERO x DataCamp Donates Hackathon 2026")

# Vérification que les modèles sont disponibles
models_ok = clf is not None and kmeans is not None and scaler is not None

if not models_ok:
    st.error(
        "Modèles introuvables dans `models/`. "
        "Lance d'abord `ml_model.ipynb` pour les générer, "
        "puis relance le dashboard."
    )
    st.stop()

# ─── KPIs modèle ─────────────────────────────────────────────────────────────
st.subheader("Performance du modèle")

k1, k2, k3, k4 = st.columns(4)

best_model_name = meta.get("best_model", "—")
f1_test         = meta.get("f1_macro_test", None)
cv_mean         = meta.get("cv_f1_macro_mean", None)
cv_std          = meta.get("cv_f1_macro_std", None)
n_clusters      = meta.get("n_clusters", "—")
sil             = meta.get("silhouette_score", None)

k1.metric("Meilleur modèle", best_model_name)
k2.metric(
    "F1-macro (test)",
    f"{f1_test:.3f}" if f1_test else "—",
    help="Score F1 macro sur 20% des données non vues pendant l'entraînement."
)
k3.metric(
    "F1-macro (CV 5-fold)",
    f"{cv_mean:.3f} ± {cv_std:.3f}" if cv_mean else "—",
    help="Validation croisée stratifiée sur l'ensemble du dataset."
)
k4.metric(
    "Silhouette clustering",
    f"{sil:.3f}" if sil else "—",
    help="Score de silhouette du K-Means. Plus proche de 1 = meilleure séparation."
)

# Interprétation automatique du F1
if f1_test:
    if f1_test >= 0.75:
        st.success(
            f"Le modèle {best_model_name} atteint un F1-macro de {f1_test:.3f} "
            f"— performance solide pour une classification à 3 classes sur données GDELT."
        )
    elif f1_test >= 0.60:
        st.warning(
            f"Le modèle {best_model_name} atteint un F1-macro de {f1_test:.3f} "
            f"— performance acceptable. La classe Neutre est souvent plus difficile à distinguer."
        )
    else:
        st.error(
            f"F1-macro de {f1_test:.3f} — le modèle a du mal à séparer les classes. "
            f"Vérifie l'équilibre des classes et les features utilisées."
        )

st.divider()

# ─── Section 1 : Prédiction interactive ──────────────────────────────────────
st.subheader("Prédire le sentiment d'un événement")
st.caption(
    "Renseigne les caractéristiques d'un événement hypothétique. "
    "Le modèle estime si la couverture médiatique sera Positive, Neutre ou Négative."
)

features_used = meta.get("features", [])

# On récupère les noms de colonnes réels utilisés à l'entraînement
# et on construit des widgets adaptés à chaque feature
col_left, col_right = st.columns(2)

with col_left:
    # Goldstein : -10 (très déstabilisant) à +10 (très stabilisant)
    goldstein_val = st.slider(
        "Score Goldstein",
        min_value=-10.0, max_value=10.0, value=0.0, step=0.5,
        help="Score de stabilité de l'événement. -10 = très déstabilisant, +10 = très stabilisant."
    )

    # QuadClass : 1 à 4
    quad_map = {
        "Coopération verbale (1)": 1,
        "Coopération matérielle (2)": 2,
        "Conflit verbal (3)": 3,
        "Conflit matériel (4)": 4,
    }
    quad_label = st.selectbox("Type d'événement (QuadClass)", list(quad_map.keys()))
    quad_val = quad_map[quad_label]

    is_conflict = 1 if quad_val >= 3 else 0

with col_right:
    mentions_val = st.number_input(
        "Nombre de mentions médiatiques",
        min_value=1, max_value=5000, value=10, step=5,
        help="Combien de fois cet événement est mentionné dans les médias."
    )

    sources_val = st.number_input(
        "Nombre de sources",
        min_value=1, max_value=500, value=5, step=1,
        help="Nombre de sources distinctes ayant couvert l'événement."
    )

    articles_val = st.number_input(
        "Nombre d'articles",
        min_value=1, max_value=1000, value=8, step=1,
        help="Nombre total d'articles publiés sur cet événement."
    )

# Mois et jour de la semaine
col_t1, col_t2 = st.columns(2)
with col_t1:
    month_names = {
        "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
        "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
        "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
    }
    month_label = st.selectbox("Mois de l'événement", list(month_names.keys()), index=0)
    month_val = month_names[month_label]

with col_t2:
    dow_names = {
        "Lundi": 0, "Mardi": 1, "Mercredi": 2, "Jeudi": 3,
        "Vendredi": 4, "Samedi": 5, "Dimanche": 6
    }
    dow_label = st.selectbox("Jour de la semaine", list(dow_names.keys()), index=0)
    dow_val = dow_names[dow_label]

# Cluster — déterminé automatiquement par le K-Means si la feature est utilisée
cluster_val = None
if "cluster" in features_used:
    cluster_feats_order = [
        c for c in [
            # ordre tel qu'utilisé dans ml_model.ipynb pour le scaler
            "goldstein", "quad_class", "mentions", "sources", "_month", "_is_conflict"
        ]
    ]
    # On reconstruit le vecteur de clustering dans le même ordre que lors de
    # l'entraînement. Les noms exacts dépendent du find_col() du notebook.
    # On utilise l'ordre implicite : Goldstein, QuadClass, Mentions, Sources, Month, IsConflict
    try:
        x_clust = np.array([[
            goldstein_val, quad_val, mentions_val, sources_val, month_val, is_conflict
        ]])
        x_clust_scaled = scaler.transform(x_clust)
        cluster_val = int(kmeans.predict(x_clust_scaled)[0])
    except Exception:
        cluster_val = 0

# Construire le vecteur de features dans l'ordre exact sauvegardé
# meta["features"] contient la liste dans l'ordre d'entraînement
feature_value_map = {
    # on mappe par mot-clé car find_col() peut produire des noms variés
}

def build_input_vector(features_list):
    """
    Reconstruit un vecteur de features dans l'ordre exact utilisé à l'entraînement,
    en faisant correspondre chaque nom de colonne à la valeur saisie.
    """
    row = {}
    for f in features_list:
        fl = f.lower()
        if "gold" in fl:
            row[f] = goldstein_val
        elif "quad" in fl or "category" in fl:
            row[f] = quad_val
        elif "mention" in fl:
            row[f] = mentions_val
        elif "source" in fl:
            row[f] = sources_val
        elif "article" in fl:
            row[f] = articles_val
        elif "month" in fl or fl == "_month":
            row[f] = month_val
        elif "dow" in fl or "day" in fl:
            row[f] = dow_val
        elif "conflict" in fl or "is_conf" in fl:
            row[f] = is_conflict
        elif "cluster" in fl:
            row[f] = cluster_val if cluster_val is not None else 0
        else:
            row[f] = 0  # fallback sécurisé
    return pd.DataFrame([row])


if st.button("Predire le sentiment", type="primary"):
    try:
        X_input = build_input_vector(features_used)
        prediction = clf.predict(X_input)[0]
        probas = clf.predict_proba(X_input)[0]
        classes = clf.classes_

        # Affichage du résultat
        sentiment_colors = {
            "Positif": "#00b894",
            "Neutre": "#636e72",
            "Negatif": "#e17055"
        }
        color = sentiment_colors.get(prediction, "#636e72")

        st.markdown(
            f"<h2 style='color:{color}; text-align:center;'>"
            f"Sentiment predit : {prediction}"
            f"</h2>",
            unsafe_allow_html=True
        )

        # Probabilités par classe
        proba_df = pd.DataFrame({
            "Sentiment": classes,
            "Probabilite": probas
        }).sort_values("Probabilite", ascending=True)

        fig_proba = px.bar(
            proba_df, x="Probabilite", y="Sentiment", orientation="h",
            title="Probabilites par classe",
            color="Sentiment",
            color_discrete_map=sentiment_colors,
            labels={"Probabilite": "Probabilite", "Sentiment": ""},
            text_auto=".2%",
            height=250
        )
        fig_proba.update_layout(showlegend=False, xaxis_range=[0, 1])
        st.plotly_chart(fig_proba, use_container_width=True)

        # Cluster correspondant
        if cluster_val is not None:
            cluster_names = meta.get("cluster_names", {})
            cluster_label = cluster_names.get(str(cluster_val), f"Cluster {cluster_val}")
            st.info(
                f"Cet événement appartient au profil : **{cluster_label}** "
                f"(Cluster {cluster_val})"
            )

    except Exception as e:
        st.error(
            f"Erreur lors de la prediction : {e}. "
            f"Vérifie que les features du modèle correspondent aux widgets."
        )

st.divider()

# ─── Section 2 : Importance des variables ────────────────────────────────────
st.subheader("Variables les plus influentes sur le sentiment")

try:
    importances = pd.DataFrame({
        "feature": features_used,
        "importance": clf.feature_importances_
    }).sort_values("importance", ascending=True)

    fig_imp = px.bar(
        importances,
        x="importance", y="feature", orientation="h",
        title="Importance des variables — Prédiction du sentiment médiatique",
        labels={"importance": "Importance relative", "feature": ""},
        color="importance", color_continuous_scale="Purples",
        height=max(300, len(features_used) * 45)
    )
    fig_imp.update_layout(showlegend=False)
    st.plotly_chart(fig_imp, use_container_width=True)

    top = importances.iloc[-1]
    st.caption(
        f"La variable la plus prédictive est **{top['feature']}** "
        f"(importance = {top['importance']:.3f})."
    )
except AttributeError:
    st.info("L'importance des variables n'est pas disponible pour ce type de modèle.")

st.divider()

# ─── Section 3 : Profils des clusters ────────────────────────────────────────
st.subheader("Profils des clusters d'événements (K-Means)")

cluster_names = meta.get("cluster_names", {})
n_clust = meta.get("n_clusters", None)

if cluster_names:
    st.caption(
        f"Le modèle K-Means a identifié **{n_clust} profils** distincts d'événements. "
        f"Score de silhouette : {sil:.3f}." if sil else ""
    )

    # Tableau des profils
    profiles_data = []
    for k, name in cluster_names.items():
        profiles_data.append({
            "Cluster": int(k),
            "Profil": name,
        })
    profiles_df = pd.DataFrame(profiles_data).sort_values("Cluster")
    st.dataframe(profiles_df, use_container_width=True, hide_index=True)

    st.caption(
        "Les noms de profils peuvent être personnalisés dans `ml_model.ipynb` "
        "(variable `CLUSTER_NAMES`) selon les caractéristiques réelles observées."
    )
else:
    st.info(
        "Les noms de clusters ne sont pas disponibles dans `model_metadata.json`. "
        "Relance `ml_model.ipynb` pour les générer."
    )

st.divider()

# ─── Section 4 : Note méthodologique ─────────────────────────────────────────
with st.expander("Note méthodologique — comprendre le modèle"):
    st.markdown("""
**Ce que le modèle prédit**

Le classifieur prédit si la couverture médiatique d'un événement GDELT sera
**Positive**, **Neutre** ou **Négative**, à partir de caractéristiques structurelles
de l'événement (type, stabilité, visibilité médiatique, moment de l'année).

**Ce que le modèle ne fait pas**

Le modèle n'analyse pas le contenu textuel des articles. Il s'appuie uniquement sur
les métadonnées GDELT. Une analyse de sentiment sur le texte des articles (via
HuggingFace Transformers par exemple) irait plus loin mais sort du périmètre GDELT pur.

**Limites à mentionner dans le rapport**

- La classe Neutre est souvent majoritaire dans GDELT, ce qui peut créer un
  déséquilibre de classes et pousser le modèle à sur-prédire Neutre.
- Le score de Goldstein est lui-même une métrique GDELT construite — le modèle
  prédit donc partiellement un signal corrélé à ses propres features.
- Les résultats sont valides pour des événements concernant le Bénin en 2025.
  La généralisation à d'autres pays ou périodes n'est pas garantie.

**Comment améliorer le modèle**

- Ajouter des features textuelles (TF-IDF sur les codes événements CAMEO).
- Tester XGBoost ou LightGBM pour de meilleures performances.
- Appliquer un rééquilibrage des classes (class_weight='balanced' ou SMOTE).
    """)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
c1, c2 = st.columns(2)
c1.caption("Source : GDELT v2 — Global Database of Events, Language and Tone")
c2.caption("iSHEERO x DataCamp Donates Hackathon 2026 · [isheero.com](https://isheero.com)")
