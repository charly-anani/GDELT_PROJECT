# GDELT Project — Analyse des événements médiatisés au Bénin via GDELT v2.0 dans Google BigQuery

Projet d'analyse exploratoire et de prévision du risque d'événements graves au Bénin à partir de la base **GDELT v2.0**, avec **Google BigQuery** comme source unique de vérité, une phase d'**exploration analytique** dans notebook, puis une phase de **modélisation prédictive** orientée early warning.

Le projet suit une logique simple : **extraire, nettoyer, enrichir, explorer, modéliser, restituer**. Les données sont centralisées dans BigQuery, les notebooks consomment directement les tables préparées, et les sorties finales incluent des visualisations, des métriques ML et une carte de hotspots de risque par département.

---

## À propos du projet

- **Données** : GDELT Event Database v2.0 (mise à jour tous les 15 minutes)
- **Couverture** : 12 derniers mois, focus Bénin
- **Source unique de vérité** : Google BigQuery (pas de pipeline local d'extraction)
- **Référence** : GDELT Event Database Data Format Codebook v2.0 (février 2015)

---

## Contexte BigQuery

- **Projet BigQuery** : `gdelt-494812`
- **Dataset** : `benin_2025`
- **Tables** : `events_clean`, `mentions_clean`, `gkg_clean`
- Documentation BigQuery : [config/bigquery.md](config/bigquery.md)
- Dictionnaire de données : [data/data_dictionary.md](data/data_dictionary.md)

---

## Architecture

```text
GDELT Project/
├── README.md
├── requirements.txt
├── config/
│   └── bigquery.md                (connexion et paramètres)
├── dashboard/
│   └── app.py                     (interface visualisation)
├── data/
│   └── data_dictionary.md         (documentation colonnes v2.0)
├── models/                        (à compléter)
├── notebooks/
│   └── exploration.ipynb          (analyse exploratoire)
└── sql/
    ├── 01_extract_events.sql      (requêtes extraction)
    ├── 02_extract_gkg.sql
    ├── 03_extract_mentions.sql
    ├── 04_clean_enrich_events.sql (transformations BigQuery)
    ├── 05_clean_enrich_mentions.sql
    └── 06_clean_enrich_gkg.sql
```

---

## Flux de traitement

1. **Extraction** (`01_extract_*.sql`) : données brutes depuis BigQuery
2. **Nettoyage & Enrichissement** (`04_clean_enrich_*.sql`) : transformation in-place BigQuery
3. **Exploration** (`notebooks/`) : analyse analytique interactive
4. **Visualisation** (`dashboard/`) : interface utilisateur
5. **Documentation** (`data/data_dictionary.md`) : référence colonnes et taxonomies

---

## Authentification BigQuery

L’accès BigQuery est accordé uniquement aux comptes Google autorisés au préalable.

Pour permettre l’exécution locale du notebook, les accès suivants doivent être attribués sur l’adresse e-mail Google de l’évaluateur :

- Au niveau du **projet** `gdelt-494812` : rôle `Utilisateur de job BigQuery` (`BigQuery Job User`) pour permettre l’exécution des requêtes.  
- Au niveau du **dataset** `benin_2025` : rôle `Lecteur de données BigQuery` (`BigQuery Data Viewer`) pour permettre la lecture des tables. 


Concrètement, pour qu’un évaluateur puisse exécuter le notebook, son compte Google doit obligatoirement faire partie de la liste d’e‑mails autorisés ci‑dessous.

### Liste des e-mails autorisés

- [email 1]
- [email 2]
- [email 3]

### Sur Kaggle

1. **Add-ons → Google Cloud Services** → lier son compte Google
2. Activer **BigQuery**
3. **Run All** — aucune configuration supplémentaire, sous réserve que le compte utilisé fasse partie des e-mails autorisés

### En local (VSCode / Jupyter)

Prérequis : avoir [gcloud CLI](https://cloud.google.com/sdk/docs/install) installé. [web:666]

**Windows** : télécharger et exécuter l’installeur  
[GoogleCloudSDKInstaller.exe](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe)  
— suivre les étapes de l’installeur, il configure tout automatiquement.

**macOS :**
```bash
brew install --cask google-cloud-sdk
```

**Linux (Debian/Ubuntu) :**
```bash
sudo apt-get install google-cloud-cli
```

Ensuite :

```bash
# 1. Installer les dépendances
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. S'authentifier avec son compte Google (à faire une seule fois)
gcloud auth application-default login

# 3. Exécuter le notebook depuis la racine du projet
jupyter notebook notebooks/exploration.ipynb
```

L’étape `gcloud auth application-default login` ouvre le navigateur pour une connexion Google standard et crée les credentials locaux utilisés automatiquement par les bibliothèques BigQuery. 

---

---

## Notebook 1 — Exploration analytique

Le notebook `exploration.ipynb` constitue la première phase du projet. Il se connecte au dataset BigQuery, met en cache les requêtes localement, puis inspecte les trois tables nettoyées pour comprendre la structure, la granularité et le potentiel analytique des données.

### Connexion et cache local

Le notebook installe les bibliothèques nécessaires, définit `PROJECT_ID`, `DATASET_ID` et un éventuel `KEY_PATH`, puis crée un dossier `cache/` pour stocker les résultats des requêtes sous forme de CSV hashés.

Cette stratégie de cache remplit deux fonctions :
- réduire le nombre d'appels BigQuery répétés ;
- améliorer la reproductibilité et le temps d'itération pendant l'exploration.

### Inspection des tables

Le notebook récupère des échantillons des tables `events_clean`, `gkg_clean` et `mentions_clean`, ce qui permet de vérifier les colonnes disponibles et d'identifier les principales dimensions d'analyse.

### Questions analytiques adressées

Cette phase sert à répondre à des questions de type :
- Comment évolue le volume d'événements médiatisés au Bénin ?
- Quelles catégories dominent selon les périodes ?
- Quelle est la tonalité globale des articles et événements ?
- Quels départements ou zones concentrent les événements les plus sensibles ?
- Quelles variables semblent intéressantes pour la suite de la modélisation ?

---

## Notebook 2 — Modélisation prédictive

Le notebook `models.ipynb` formalise la deuxième étape du projet : construire un **modèle de prédiction du risque** à partir des événements GDELT.

L'objectif affiché est explicite : **prédire, à 7 jours et par département, la probabilité d'un événement grave**, défini ici par un seuil sur la `GoldsteinScale`.

### Problème métier posé

Le notebook ne cherche pas simplement à reclasser des événements déjà observés. Il adopte une vraie logique **forecasting / early warning** : les variables explicatives regardent le passé, tandis que la cible regarde les 7 jours suivants.

C'est le point méthodologique central du projet : éviter le **data leakage** afin que le modèle reste pertinent en conditions réelles.

### Préparation des données

Le notebook charge les colonnes utiles depuis `events_clean`, puis effectue un nettoyage structuré : conversion des dates, typage numérique, contrôle de la géolocalisation et construction de variables descriptives complémentaires.

**31 504 événements** sont chargés pour la partie ML, avec **31 464 événements géolocalisés** (99,9% de couverture géographique exploitable).

### Définition de la target

La variable cible `target` est construite de manière prospective : **y aura-t-il, dans les 7 jours suivants et dans le même département, un événement avec `GoldsteinScale <= -5` ?**

La cible est donc une variable binaire :
- `1` = conflit grave attendu dans les 7 prochains jours
- `0` = pas de conflit grave attendu à cet horizon

Cette construction est **anti-leakage**, car les features regardent uniquement le passé tandis que la target regarde le futur.

### Feature engineering

Le projet construit des variables temporelles et agrégées : lags et moyennes glissantes de `GoldsteinScale`, saisonnalité cyclique, encodage des types d'acteurs, nombre d'événements récents.

### Split temporel

Le découpage train/test suit une logique chronologique :
- **Train** : ~23 191 événements (2025-01-01 à 2025-11-26)
- **Test** : ~5 831 événements (2025-11-27 à 2025-12-31)

### Modèle entraîné

Le modèle principal est un **RandomForestClassifier** avec `n_estimators = 100`, `max_depth = 10`, `min_samples_split = 50`.

### Résultats du modèle

- **F1 modèle** : ~0,82
- **F1 baseline** : ~0,13
- **Lift** : +69 points
- **ROC-AUC** : ~0,83
- **Précision** : ~0,85
- **Recall** : ~0,79

**Interprétation business** :
- Sur 100 alertes émises, ~85 correspondent à de vrais conflits
- Sur 100 vrais conflits, ~79 sont détectés à l'avance

### Importance des variables

Les signaux les plus déterminants :
1. **Moyenne Goldstein 7j** : ~65%
2. **Moyenne Goldstein 30j** : ~18%
3. **Tonalité presse** : ~7%
4. **Goldstein J-7** : ~3%
5. **Goldstein J-14** : ~2%

Le modèle apprend une logique d'**inertie du risque** : la sévérité récente et la tendance courte/moyenne expliquent l'essentiel de la probabilité d'un conflit grave futur.

### Restitution cartographique

Le projet produit une **carte interactive Folium** des hotspots prédits pour le Bénin, agrégée par département avec score de risque moyen, volume d'événements et catégorie de risque (`Low`, `Medium`, `High`).

### Artefacts générés

- Modèle Random Forest sérialisé
- Encodeurs des variables catégoriques
- Importance des variables (CSV)
- Agrégation spatiale des risques (hotspots.csv)
- Prédictions sur le jeu de test
- Carte interactive exportée (HTML)

### À quoi sert le modèle en pratique

Une fois entraîné, le modèle peut servir de composant d'un **système d'alerte précoce** :
1. De nouveaux événements GDELT sont ingérés dans BigQuery
2. Les mêmes transformations et features sont recalculées
3. Le modèle attribue une probabilité de conflit grave à horizon 7 jours
4. Les scores sont agrégés par département
5. Un tableau de bord ou une carte priorise les zones à surveiller

Cela peut appuyer une cellule de veille territoriale, orienter un reporting hebdomadaire, déclencher une analyse humaine ciblée, ou prioriser l'attention sur les départements où le risque est en hausse.

---

## Forces du projet

- **Source unique de vérité BigQuery** → limite les écarts entre extraction, analyse et production
- **Séparation claire** entre nettoyage SQL, exploration analytique et modélisation
- **Construction anti-leakage de la target** → essentielle pour un vrai cas de forecasting
- **Split temporel** → plus réaliste qu'un split aléatoire pour des données chronologiques
- **Lecture business des métriques** → utile pour un jury, un recruteur ou un décideur
- **Sortie cartographique** → transforme le modèle en outil d'aide à la décision

## Limites actuelles et pistes d'amélioration

- Enrichir le README avec les **requêtes SQL clés** de préparation
- Documenter plus explicitement le **schéma des tables nettoyées**
- Ajouter une **validation temporelle glissante** plutôt qu'un seul split
- Comparer Random Forest à d'autres modèles comme XGBoost ou LightGBM
- Intégrer davantage les tables `gkg_clean` et `mentions_clean` dans les features de prédiction
- Industrialiser la phase de scoring via un job planifié ou un dashboard de monitoring

---

## Résumé méthodologique

Le projet peut se résumer en une chaîne analytique complète :

**GDELT brut → BigQuery nettoyé/enrichi → exploration descriptive → feature engineering temporel → target future anti-leakage → Random Forest → métriques business → carte des hotspots de risque.**

Cette logique montre bien que le projet ne se limite pas à une visualisation exploratoire : il met en place une vraie **chaîne data analytique et prédictive** appliquée au suivi des événements médiatisés au Bénin.