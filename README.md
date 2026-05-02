# GDELT Project

Analyse des événements médiatisés au Bénin via GDELT v2.0 dans Google BigQuery.

**Statut** : Work in Progress. Architecture et flux en place ; documentation et contenu détaillé à suivre.

## À propos du projet

- **Données** : GDELT Event Database v2.0 (mise à jour tous les 15 minutes)
- **Couverture** : 12 derniers mois, focus Bénin
- **Source unique de vérité** : Google BigQuery (pas de pipeline local d'extraction)
- **Référence** : GDELT Event Database Data Format Codebook v2.0 (février 2015)

## Contexte BigQuery

- **Projet BigQuery** : `gdelt-494812`
- **Dataset** : `benin_2025`
- **Tables** : `events`, `eventmentions`, `gkg`
- Documentation BigQuery : [config/bigquery.md](config/bigquery.md)
- Dictionnaire de données : [data/data_dictionary.md](data/data_dictionary.md)

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

## Flux de traitement

1. **Extraction** (`01_extract_*.sql`) : données brutes depuis BigQuery
2. **Nettoyage & Enrichissement** (`04_clean_enrich_*.sql`) : transformation in-place BigQuery
3. **Exploration** (`notebooks/`) : analyse analytique interactif
4. **Visualisation** (`dashboard/`) : interface utilisateur
5. **Documentation** (`data/data_dictionary.md`) : référence colonnes et taxonomies

## Authentification BigQuery

Les données sont stockées dans BigQuery projet `gdelt-494812`, dataset `benin_2025`.

**Sur Kaggle** : l'authentification est automatique dès lors que le compte Google propriétaire du projet est lié via **Add-ons → Google Cloud Services**. Le notebook s'exécute directement avec **Run All**.

**En local** (VSCode / Jupyter) : l'authentification repose sur un Service Account JSON obtenu via [console.cloud.google.com](https://console.cloud.google.com) :
- Accès au projet `gdelt-494812` → **IAM & Admin → Comptes de service**
- Création d'un compte avec rôles : `Lecteur de données BigQuery` + `Utilisateur de job BigQuery`
- Génération d'une clé JSON (**Clés → Créer → JSON**)
- Le fichier téléchargé est déposé à la racine sous `gdelt-494812-54aad2c4e931.json` (exclu git via `.gitignore`)

Les requêtes exécutées dans les notebooks pointent directement vers l'ensemble de données nettoyé et enrichi dans BigQuery.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```


