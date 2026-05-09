import os
import hashlib
from pathlib import Path

# Librairies data et visualisation
import pandas as pd
import numpy as np
import pandas_gbq
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")  # Désactive les warnings pour garder la sortie propre


# Identifiants du projet GCP / BigQuery
PROJECT_ID = "gdelt-494812"
DATASET_ID = "benin_2025"
KEY_PATH = "gdelt-494812-e7b391e14150.json"  # Fichier JSON de compte de service


# Création des répertoires de cache si besoin
os.makedirs("cache", exist_ok=True)
os.makedirs("cachemodels", exist_ok=True)


def get_credentials():
    """Charge les credentials GCP à partir du fichier de compte de service."""
    if os.path.exists(KEY_PATH):  # Vérifie que le fichier JSON existe
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(
            KEY_PATH,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]  # Accès complet GCP
        )
    return None  # Aucun credentials si le fichier est introuvable


# Initialise les credentials à partir du fichier local
credentials = get_credentials()


# Feedback utilisateur sur l'état des credentials
if credentials is not None:
    print("Service account credentials loaded")
    print(f"  Key file: {Path(KEY_PATH).resolve()}")  # Affiche le chemin absolu du fichier
else:
    print("JSON key file not found")
    print(f"  Expected path: {Path(KEY_PATH).resolve()}")  # Indique où le fichier est attendu
def charger_donnees(query, force_reload=False):
    """Exécute une requête BigQuery et met en cache le résultat en CSV."""
    # Clé courte de cache basée sur le hash MD5 de la requête
    query_hash = hashlib.md5(query.encode("utf-8")).hexdigest()[:8]
    cache_path = f"cache/cache_{query_hash}.csv"  # Chemin du fichier de cache


    # Si le cache existe et qu'on ne force pas le rechargement, on lit le CSV
    if os.path.exists(cache_path) and not force_reload:
        df = pd.read_csv(cache_path)
        print(f"Loaded from cache: {cache_path}")
    else:
        # Sinon, on exécute la requête sur BigQuery et on récupère un DataFrame
        df = pandas_gbq.read_gbq(
            query,
            project_id=PROJECT_ID,
            credentials=credentials,
            dialect="standard"  # SQL standard BigQuery
        )
        # Sauvegarde du résultat en CSV pour les appels suivants
        df.to_csv(cache_path, index=False)
        print(f"Loaded from BigQuery and cached: {cache_path}")


    return df  # Retourne toujours un DataFrame, du cache ou de BigQuery
# Requête pour récupérer le schéma de la table events_clean dans BigQuery
query_schema = f"""
SELECT
  column_name,
  data_type
FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'events_clean'
ORDER BY ordinal_position
"""


# Charge le schéma via BigQuery (pas de cache CSV réutilisé ici)
df_schema = charger_donnees(query_schema, force_reload=True)
df_schema  # Affiche le DataFrame contenant les colonnes et leurs types
# Requête pour extraire les variables utilisées en modélisation ML
query_ml = f"""
SELECT
  GLOBALEVENTID,
  date_clean,
  year_month_clean,
  EventRootCode,
  EventCode,
  QuadClass,
  QuadClass_Label,
  interaction_type,
  GoldsteinScale,
  goldstein_category,
  AvgTone,
  tone_category,
  NumMentions,
  Actor1Type1Code,
  Actor1Role,
  Actor2Type1Code,
  Actor2Role,
  ActionGeo_CountryCode,
  ActionGeo_ADM1Code,
  ActionGeo_Lat,
  ActionGeo_Long,
  has_international_actor,
  event_scope,
  is_significant
FROM `{PROJECT_ID}.{DATASET_ID}.events_clean`
ORDER BY date_clean DESC
"""


# Charge les données pour le jeu ML (avec cache via charger_donnees)
df_ml = charger_donnees(query_ml)
print(f"{len(df_ml):,} événements chargés pour ML")


df = df_ml.copy()  # Copie de travail pour ne pas modifier df_ml


# Conversion datetime + features calendaires
df['date'] = pd.to_datetime(df['date_clean'])  # Convertit la date en type datetime
df['month'] = df['date'].dt.month             # Mois numérique
df['dow'] = df['date'].dt.dayofweek           # Jour de la semaine (0=lundi)
df['week'] = df['date'].dt.isocalendar().week  # Semaine ISO [web:61][web:63][web:65]


# Typage strict des numériques
numeric_cols = ['GoldsteinScale', 'AvgTone', 'NumMentions', 'ActionGeo_Lat', 'ActionGeo_Long']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Force en float, non convertibles -> NaN [web:71]


# Risk Score descriptif (pour visualisations EDA seulement, PAS pour le modèle)
df['risk_raw'] = -df['GoldsteinScale']  # Inversion du signe: conflits forts -> score élevé
df['risk_level'] = pd.cut(
    df['risk_raw'],
    bins=[-np.inf, -5, -2, 2, 5, np.inf],
    labels=['Très positif', 'Positif', 'Neutre', 'Négatif', 'Très négatif']  # Catégorisation qualitative [web:67][web:70][web:73]
)


df['quadclass_name'] = df['QuadClass_Label']  # Alias plus explicite
df['is_conflict'] = (df['QuadClass'] >= 3).astype(int)  # Binaire: 1 si événement de conflit (EDA seulement)


# TARGET FUTURE — pas de leakage
# Pour chaque événement : y a-t-il un Goldstein ≤ -5 dans les 7 jours suivants ?
df = df.sort_values(['ActionGeo_ADM1Code', 'date']).reset_index(drop=True)  # Trie par région puis par date


df['goldstein_min_next_7d'] = (
    df.groupby('ActionGeo_ADM1Code')['GoldsteinScale']
      .shift(-1)                            # Décale vers le futur (événements suivants de la même région)
      .rolling(7, min_periods=1).min()      # Min sur les 7 lignes suivantes (7 jours) [web:69][web:72][web:75]
      .reset_index(level=0, drop=True)
)


df['target'] = (df['goldstein_min_next_7d'] <= -5).astype(int)  # 1 si conflit sévère dans les 7 jours futurs


# Géolocalisation — QC basique
df_geo = df[
    (df['ActionGeo_Lat'].notna()) &
    (df['ActionGeo_Long'].notna()) &
    (df['ActionGeo_Lat'] != 0) &
    (df['ActionGeo_Long'] != 0)
].copy()  # Sous-ensemble avec coordonnées valides pour les cartes


print(f'Nettoyage terminé')
print(f'  Lignes complètes        : {len(df):,}')
print(f'  Événements géolocalisés : {len(df_geo):,} ({100*len(df_geo)/len(df):.1f}%)')
print(f'  Risk Score range        : [{df["risk_raw"].min():.1f}, {df["risk_raw"].max():.1f}]')
print(f'  Target=1 (conflit J+7)  : {df["target"].sum():,} ({100*df["target"].mean():.1f}%)')

from sklearn.preprocessing import LabelEncoder


# Le tri a déjà été fait à la cellule précédente
# (par ActionGeo_ADM1Code, date)


# 1. Lag features Goldstein (passé)
df['goldstein_lag_7d']  = df.groupby('ActionGeo_ADM1Code')['GoldsteinScale'].shift(7)
df['goldstein_lag_14d'] = df.groupby('ActionGeo_ADM1Code')['GoldsteinScale'].shift(14)


# 2. Rolling means (tendance passée par région)
df['goldstein_roll_7d'] = (
    df.groupby('ActionGeo_ADM1Code')['GoldsteinScale']
      .rolling(7, min_periods=1).mean()
      .reset_index(level=0, drop=True)
)
df['goldstein_roll_30d'] = (
    df.groupby('ActionGeo_ADM1Code')['GoldsteinScale']
      .rolling(30, min_periods=1).mean()
      .reset_index(level=0, drop=True)
)


# 3. Volume d'événements sur 7 jours (par région)
df['event_count_7d'] = (
    df.groupby('ActionGeo_ADM1Code')['GLOBALEVENTID']
      .rolling(7, min_periods=1).count()
      .reset_index(level=0, drop=True)
)


# 4. Saisonnalité (encodage cyclique du mois)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)  # Composante sin du mois
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)  # Composante cos du mois


# 5. Encodage des acteurs (Label Encoding)
le_actor1 = LabelEncoder()
le_actor2 = LabelEncoder()
le_event  = LabelEncoder()

# On remplace les NaN par 'UNK' et on encode en entiers
df['Actor1Type1Code_enc'] = le_actor1.fit_transform(df['Actor1Type1Code'].fillna('UNK').astype(str))
df['Actor2Type1Code_enc'] = le_actor2.fit_transform(df['Actor2Type1Code'].fillna('UNK').astype(str))
df['EventRootCode_enc']   = le_event.fit_transform(df['EventRootCode'].fillna('UNK').astype(str))


# Vérification finale des nouvelles features
new_features = [
    'Actor1Type1Code_enc', 'Actor2Type1Code_enc',
    'goldstein_lag_7d', 'goldstein_lag_14d',
    'goldstein_roll_7d', 'goldstein_roll_30d',
    'month_sin', 'month_cos', 'event_count_7d'
]

missing = [f for f in new_features if f not in df.columns]
if missing:
    print(f"Manquant : {missing}")
else:
    print("Toutes les features sont créées :")
    for f in new_features:
        print(f"   - {f}")
    print("\nNaN par feature :")
    print(df[new_features].isna().sum())

# Features finales du modèle
features = [
    'Actor1Type1Code_enc',
    'Actor2Type1Code_enc',
    'AvgTone',
    'NumMentions',
    'goldstein_lag_7d',
    'goldstein_lag_14d',
    'goldstein_roll_7d',
    'goldstein_roll_30d',
    'month_sin',
    'month_cos',
    'event_count_7d'
]


# Filtrer les lignes complètes (toutes les features + target non nulles)
df_model = df.dropna(subset=features + ['target']).copy()


# Matrice de features (X) et variable cible (y)
X = df_model[features]
y = df_model['target']


# Split temporel (80% train, 20% test) basé sur la date
split_date = df_model['date'].quantile(0.8)   # Seuil de quantile sur la date
train_mask = df_model['date'] < split_date    # Tout ce qui est avant = train


X_train, y_train = X[train_mask], y[train_mask]
X_test,  y_test  = X[~train_mask], y[~train_mask]


# Diagnostic
events_lost = len(df) - len(df_model)         # Lignes perdues à cause des NaN
total_ml = len(X_train) + len(X_test)         # Total utilisé en ML


print(f"Données préparées pour ML")
print(f"  Total df : {len(df):,} événements")
print(f"  - Perdus (NaN features)  : {events_lost:,} ({100*events_lost/len(df):.1f}%)")
print(f"  - ML (complets)          : {len(df_model):,} → {total_ml:,} (train+test)")
print()
print(f"  Train : {len(X_train):,} ({df_model[train_mask]['date'].min().date()} → {df_model[train_mask]['date'].max().date()})")
print(f"  Test  : {len(X_test):,} ({df_model[~train_mask]['date'].min().date()} → {df_model[~train_mask]['date'].max().date()})")
print()
print(f"  Ratio target=1 (train) : {y_train.mean():.1%}")
print(f"  Ratio target=1 (test)  : {y_test.mean():.1%}")
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score
import joblib


# Entraînement du Random Forest
rf = RandomForestClassifier(
    n_estimators=100,        # Nombre d'arbres
    max_depth=10,           # Profondeur maximale des arbres
    min_samples_split=50,   # Min d'échantillons pour splitter un noeud
    random_state=42,        # Reproductibilité
    n_jobs=-1,              # Utilise tous les coeurs CPU
    class_weight='balanced' # Pondération automatique des classes (dataset déséquilibré) [web:77][web:79][web:80]
)

rf.fit(X_train, y_train)    # Apprentissage sur le set d'entraînement


# Prédictions
y_pred  = rf.predict(X_test)              # Prédiction binaire
y_proba = rf.predict_proba(X_test)[:, 1]  # Probabilité d'appartenir à la classe 1


# Baseline naïve : règle simple basée sur la moyenne mobile Goldstein 30j
baseline_pred = (X_test['goldstein_roll_30d'] <= -2).astype(int)


# Métriques de performance
f1_rf        = f1_score(y_test, y_pred)         # F1 du modèle [web:90][web:84]
f1_base      = f1_score(y_test, baseline_pred)  # F1 de la baseline
auc_rf       = roc_auc_score(y_test, y_proba)   # Aire sous la courbe ROC
precision_rf = precision_score(y_test, y_pred)  # Précision (qualité des alertes)
recall_rf    = recall_score(y_test, y_pred)     # Rappel (taux de détection des conflits) [web:84][web:81]


print("=" * 60)
print("  EVALUATION — prédiction conflit grave J+1 à J+7")
print("=" * 60)
print(f"  F1 modèle     : {f1_rf:.3f}")
print(f"  F1 baseline   : {f1_base:.3f}")
print(f"  Lift modèle   : +{(f1_rf - f1_base)*100:.1f} pts vs baseline")
print()
print(f"  ROC-AUC       : {auc_rf:.3f}")
print(f"  Precision     : {precision_rf:.3f}  (sur les alertes émises, % de vraies)")
print(f"  Recall        : {recall_rf:.3f}  (sur les vrais conflits, % détectés)")
print("=" * 60)


# Sauvegarde du modèle et des objets nécessaires à l'inférence
joblib.dump(rf,       'cachemodels/risk_model.pkl')   # Modèle entraîné [web:82][web:85]
joblib.dump(features, 'cachemodels/features.pkl')     # Liste des features
joblib.dump(le_event, 'cachemodels/le_event.pkl')     # Encoders pour reproduire le prétraitement
joblib.dump(le_actor1,'cachemodels/le_actor1.pkl')
joblib.dump(le_actor2,'cachemodels/le_actor2.pkl')

print("\nModele entraîne et sauvegardé")
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay


print("=" * 60)
print("EVALUATION DU MODELE — Conflit grave J+1 a J+7")
print("=" * 60)
print(classification_report(
    y_test, y_pred,
    target_names=["Pas de conflit grave", "Conflit grave attendu"]  # Noms lisibles des classes [web:93][web:96]
))


# Matrice de confusion brute
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Pas de conflit", "Conflit J+7"]  # Labels affiches sur les axes [web:94][web:104]
)


# Affichage graphique de la matrice de confusion
fig, ax = plt.subplots(figsize=(6, 5))
disp.plot(ax=ax, cmap="Reds", colorbar=False)  # Heatmap avec colormap rouge [web:95][web:101]
ax.set_title("Matrice de confusion — Prediction conflit grave a 7 jours")
plt.tight_layout()
plt.show()


# Lecture business a partir de la matrice de confusion
tn, fp, fn, tp = cm.ravel()  # Decompose la matrice 2x2 en TN, FP, FN, TP [web:97][web:103]
total_alertes = tp + fp
total_vrais   = tp + fn


print("\n" + "=" * 60)
print("  LECTURE BUSINESS — comme un prefet le verrait")
print("=" * 60)
print(f"  Vrais positifs (alertes justes)     : {tp:4d}")
print(f"  Faux positifs (fausses alertes)     : {fp:4d}")
print(f"  Faux negatifs (conflits rates)      : {fn:4d}")
print(f"  Vrais negatifs (calme bien predit)  : {tn:4d}")
print()
if total_alertes > 0:
    print(f"  -> Sur 100 alertes emises, {100*tp/total_alertes:.0f} sont des vrais conflits")
if total_vrais > 0:
    print(f"  -> Sur 100 vrais conflits, {100*tp/total_vrais:.0f} sont detectes a l'avance")
print("=" * 60)

feat_imp = pd.DataFrame({
    'feature': features,
    'importance': rf.feature_importances_  # Importances Gini des features du Random Forest
}).sort_values('importance', ascending=False)


# Renommage lisible pour lecture métier
feature_labels = {
    'Actor1Type1Code_enc': 'Type acteur 1',
    'Actor2Type1Code_enc': 'Type acteur 2',
    'AvgTone': 'Tonalite presse',
    'NumMentions': 'Nb mentions presse',
    'goldstein_lag_7d': 'Goldstein J-7',
    'goldstein_lag_14d': 'Goldstein J-14',
    'goldstein_roll_7d': 'Moyenne Goldstein 7j',
    'goldstein_roll_30d': 'Moyenne Goldstein 30j',
    'month_sin': 'Saisonnalite (sin)',
    'month_cos': 'Saisonnalite (cos)',
    'event_count_7d': 'Volume evenements 7j',
}
feat_imp['feature_label'] = feat_imp['feature'].map(feature_labels).fillna(feat_imp['feature'])


# Barplot horizontal des importances
fig_imp = px.bar(
    feat_imp,
    x='importance',
    y='feature_label',
    orientation='h',
    title='<b>Quels signaux predisent un conflit grave a 7 jours ?</b>',
    height=480,
    color='importance',
    color_continuous_scale='Reds',
    text=feat_imp['importance'].apply(lambda x: f'{x*100:.1f}%')
)
fig_imp.update_layout(
    yaxis={'categoryorder': 'total ascending', 'title': ''},
    xaxis={'title': 'Importance relative'},
    showlegend=False,
    coloraxis_showscale=False,
    template='plotly_white',
)
fig_imp.update_traces(textposition='outside')
fig_imp.show()


# Insight pour le pitch
top1 = feat_imp.iloc[0]                            # Feature la plus importante
top3 = feat_imp.head(3)['feature_label'].tolist()  # Top 3 pour le discours


print("\n" + "=" * 60)
print("  TOP FEATURES — l'histoire que raconte le modele")
print("=" * 60)
print(feat_imp[['feature_label', 'importance']].head(10).to_string(index=False))
print("=" * 60)
print(f"\n-> Signal #1 : {top1['feature_label']} ({top1['importance']*100:.1f}%)")
print(f"-> Top 3     : {', '.join(top3)}")
# Installation Folium (commenter si déjà installe)
# !pip install folium --quiet


import folium
from folium.plugins import HeatMap


# 1. Preparation des hotspots (test set + predictions)
df_test_pred = df_model.loc[~train_mask].copy()
df_test_pred["risk_proba"] = y_proba   # Probabilite predite de conflit grave
df_test_pred["y_pred"]     = y_pred    # Prediction binaire du modele


# Harmonisation du code departement (fusion BN generique avec BN00)
df_test_pred["ActionGeo_ADM1Code"] = df_test_pred["ActionGeo_ADM1Code"].replace({"BN": "BN00"})


# Aggregation par departement (score moyen + volume + coordonnees)
hotspots = (
    df_test_pred
    .dropna(subset=["ActionGeo_ADM1Code", "ActionGeo_Lat", "ActionGeo_Long"])
    .groupby("ActionGeo_ADM1Code", as_index=False)
    .agg(
        risk_score=("risk_proba", "mean"),
        event_count=("GLOBALEVENTID", "count"),
        lat=("ActionGeo_Lat", "median"),
        lon=("ActionGeo_Long", "median")
    )
)


# Categorisation du risque (Low / Medium / High)
hotspots["risk_category"] = pd.cut(
    hotspots["risk_score"],
    bins=[0, 0.33, 0.66, 1.0],
    labels=["Low", "Medium", "High"],
    include_lowest=True
)


print(f"Hotspots crees : {len(hotspots)} regions")


# 2. Filtrer Benin + nommer les departements
hotspots_benin = hotspots[hotspots["ActionGeo_ADM1Code"].str.startswith("BN", na=False)].copy()
df_map = hotspots_benin[hotspots_benin["ActionGeo_ADM1Code"] != "BN00"].copy()


dept_names = {
    "BN07": "Alibori", "BN08": "Atakora", "BN09": "Atlantique",
    "BN10": "Borgou", "BN11": "Collines", "BN12": "Kouffo",
    "BN13": "Donga", "BN14": "Littoral (Cotonou)", "BN15": "Mono",
    "BN16": "Oueme (Porto-Novo)", "BN17": "Plateau", "BN18": "Zou",
    "BN00": "Benin (non localise)"
}
df_map["dept_name"] = df_map["ActionGeo_ADM1Code"].map(dept_names).fillna(df_map["ActionGeo_ADM1Code"])


# Palette de couleurs par niveau de risque
COLOR_LOW, COLOR_MED, COLOR_HIGH = "#27ae60", "#f39c12", "#e74c3c"
df_map["risk_category_str"] = df_map["risk_category"].astype(str)
df_map["color"] = df_map["risk_category_str"].map({
    "Low": COLOR_LOW, "Medium": COLOR_MED, "High": COLOR_HIGH
}).fillna("#888888")


# 3. Carte Folium
center_lat = df_map["lat"].median()
center_lon = df_map["lon"].median()


m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=7,
    tiles="OpenStreetMap",
    prefer_canvas=True,
)


# Heatmap des probabilites de risque
heat_data = [[row["lat"], row["lon"], row["risk_score"]] for _, row in df_map.iterrows()]
HeatMap(
    heat_data,
    radius=20, blur=18, min_opacity=0.3,
    gradient={"0.0": "#27ae60", "0.33": "#f39c12", "0.66": "#e74c3c", "1.0": "#c0392b"},
).add_to(m)


# Marqueurs circulaires avec popup HTML riche
for _, row in df_map.iterrows():
    radius = max(6, min(row["event_count"] * 0.8, 40))  # Taille ~ volume d'evenements
    risk_label = row["risk_category_str"]

    popup_html = f"""
    <div style="font-family:Inter,sans-serif;min-width:220px;">
        <b style="font-size:15px;color:#1f2937;">{row['dept_name']}</b><br>
        <span style="font-size:10px;color:#9ca3af;">{row['ActionGeo_ADM1Code']}</span>
        <hr style="margin:6px 0;border-color:#e5e7eb;">
        <b style="color:{row['color']};font-size:13px;">Risque {risk_label}</b><br>
        <div style="margin-top:6px;color:#6b7280;font-size:12px;">
            <b>{int(row['event_count'])}</b> evenements analyses<br>
            Probabilite conflit J+7 : <b style="color:{row['color']};">{row['risk_score']:.1%}</b>
        </div>
    </div>
    """

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color="white", weight=1.5,
        fill=True, fill_color=row["color"], fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=260),
        tooltip=f"{row['dept_name']} — Risque J+7 : {row['risk_score']:.1%}",
    ).add_to(m)


# 4. Legende (resume analytique dans un panneau fixe)
stats_by_risk = df_map.groupby("risk_category", observed=False).agg({
    "ActionGeo_ADM1Code": "count",
    "risk_score": "mean",
    "event_count": "sum"
}).reset_index()


# Cas des evenements non localises (BN00)
bn00_data = hotspots_benin[hotspots_benin["ActionGeo_ADM1Code"] == "BN00"]
if len(bn00_data) > 0:
    bn00_row = bn00_data.iloc[0]
    bn00_events = int(bn00_row["event_count"])
    bn00_risk = bn00_row["risk_score"]
    bn00_category = str(bn00_row["risk_category"])
else:
    bn00_events, bn00_risk, bn00_category = 0, 0, "N/A"


# Lignes HTML pour la table de stats par niveau de risque
stats_rows_html = ""
for risk_level in ["High", "Medium", "Low"]:
    matching = stats_by_risk[stats_by_risk["risk_category"].astype(str) == risk_level]
    if len(matching) > 0:
        r = matching.iloc[0]
        nb_regions = int(r["ActionGeo_ADM1Code"])
        avg_risk = r["risk_score"]
        total_events = int(r["event_count"])
        color = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"}[risk_level]
        stats_rows_html += f"""
        <tr>
            <td style="padding:4px 8px;font-size:11px;font-weight:600;color:{color};">{risk_level}</td>
            <td style="padding:4px 8px;font-size:11px;text-align:center;">{nb_regions}</td>
            <td style="padding:4px 8px;font-size:11px;text-align:center;color:{color};font-weight:700;">{avg_risk:.1%}</td>
            <td style="padding:4px 8px;font-size:11px;text-align:center;">{total_events}</td>
        </tr>"""


# Ligne supplementaire pour BN00 si present
if bn00_events > 0:
    stats_rows_html += f"""
        <tr style="background:#f9fafb;border-top:1px dashed #d1d5db;">
            <td colspan="4" style="padding:4px 8px;font-size:10px;color:#6b7280;font-style:italic;">
                + Evenements non localises : <b>{bn00_events}</b> evts ({bn00_risk:.1%} risk)
            </td>
        </tr>"""


# Top 3 regions a risque eleve pour mise en avant
top_regions = df_map.sort_values("risk_score", ascending=False).head(3)
top_regions_html = ""
for _, row in top_regions.iterrows():
    color_display = row["color"]
    top_regions_html += f"""
    <tr style="background:#fff5f5;">
        <td style="padding:4px 8px;font-size:11px;font-weight:600;color:{color_display};">{row['dept_name']}</td>
        <td style="padding:4px 8px;font-size:11px;text-align:center;color:{color_display};font-weight:700;">{row['risk_score']:.1%}</td>
        <td style="padding:4px 8px;font-size:11px;text-align:center;">{int(row['event_count'])}</td>
    </tr>"""


# Bloc HTML de legende/panneau d'information
legend_html = f"""
<div style="position:fixed; bottom:30px; left:30px; z-index:9999;
    background:rgba(255,255,255,0.97); color:#1f2937;
    padding:16px 20px; border-radius:12px;
    font-family:Inter,sans-serif; font-size:13px;
    border:1px solid #e5e7eb; box-shadow:0 4px 20px rgba(0,0,0,0.15);
    max-width:320px;">
    <b style="font-size:15px;display:block;margin-bottom:10px;">
        Risque predit J+7 — Benin 2025
    </b>
    <span style="color:#27ae60;font-size:18px;">●</span>&nbsp;Low Risk<br>
    <span style="color:#f39c12;font-size:18px;">●</span>&nbsp;Medium Risk<br>
    <span style="color:#e74c3c;font-size:18px;">●</span>&nbsp;High Risk<br>
    <div style="margin-top:10px;padding-top:10px;border-top:1px solid #e5e7eb;
                color:#6b7280;font-size:11px;line-height:1.5;">
        <b>Modele ML :</b> Random Forest (forecasting 7j)<br>
        Probabilite d'un evenement grave dans les 7 prochains jours<br>
        Taille = volume d'evenements observes<br>
        Cliquer sur un point pour les details
    </div>
    <div style="margin-top:12px;padding-top:10px;border-top:1px solid #e5e7eb;">
        <b style="font-size:12px;color:#374151;">Repartition par niveau de risque</b>
        <table style="width:100%;margin-top:8px;border-collapse:collapse;">
            <thead><tr style="background:#f9fafb;">
                <th style="padding:4px 8px;font-size:10px;text-align:left;color:#6b7280;">Niveau</th>
                <th style="padding:4px 8px;font-size:10px;text-align:center;color:#6b7280;">Dep.</th>
                <th style="padding:4px 8px;font-size:10px;text-align:center;color:#6b7280;">Risque</th>
                <th style="padding:4px 8px;font-size:10px;text-align:center;color:#6b7280;">Evts</th>
            </tr></thead>
            <tbody>{stats_rows_html}</tbody>
        </table>
    </div>
    <div style="margin-top:12px;padding-top:10px;border-top:1px solid #e5e7eb;">
        <b style="font-size:12px;color:#e74c3c;">Top 3 departements sensibles</b>
        <table style="width:100%;margin-top:8px;border-collapse:collapse;">
            <thead><tr style="background:#fff5f5;">
                <th style="padding:4px 8px;font-size:10px;text-align:left;color:#e74c3c;">Departement</th>
                <th style="padding:4px 8px;font-size:10px;text-align:center;color:#e74c3c;">Risk</th>
                <th style="padding:4px 8px;font-size:10px;text-align:center;color:#e74c3c;">Evts</th>
            </tr></thead>
            <tbody>{top_regions_html}</tbody>
        </table>
    </div>
    <div style="margin-top:10px;font-size:9px;color:#9ca3af;font-style:italic;text-align:center;">
        Early Warning System — ML Prediction<br>
        {len(df_map)} departements analyses
    </div>
</div>
"""


m.get_root().html.add_child(folium.Element(legend_html))


# Export de la carte
m.save("cachemodels/risk_hotspot_map_benin_2025.html")
print("Carte exportee : cachemodels/risk_hotspot_map_benin_2025.html")
print(f"   {len(df_map)} departements visibles")
print(f"   {bn00_events} evenements non localises (en legende)")


# Top regions a surveiller (resume texte)
print("\nREGIONS A SURVEILLER CETTE SEMAINE :")
for i, (_, row) in enumerate(top_regions.iterrows(), 1):
    print(f"   {i}. {row['dept_name']:25s} -> {row['risk_score']:.1%} de risque ({int(row['event_count'])} evts)")
feat_imp.to_csv('cachemodels/feature_importance.csv', index=False)
hotspots.to_csv('cachemodels/hotspots.csv', index=False)
df_test_pred[['date', 'ActionGeo_ADM1Code', 'risk_proba', 'y_pred']].to_csv(
    'cachemodels/test_predictions.csv', index=False
)


print("Artifacts sauvegardes dans cachemodels/")
print("  - risk_model.pkl")
print("  - features.pkl")
print("  - le_event.pkl, le_actor1.pkl, le_actor2.pkl")
print("  - feature_importance.csv")
print("  - hotspots.csv")
print("  - test_predictions.csv")
print("  - risk_hotspot_map_benin_2025.html")