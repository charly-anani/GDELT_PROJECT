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



## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


