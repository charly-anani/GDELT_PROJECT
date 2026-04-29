# GDELT Project

Projet GDELT organisé autour d'une source unique de vérité dans Google BigQuery. Tous les traitements de préparation sont portés par SQL dans BigQuery, sans pipeline Python local d'extraction, de nettoyage ou d'enrichissement.

## Contexte BigQuery

- Projet BigQuery : `gdelt-494812`
- Dataset principal : `benin_2025`
- Les requêtes d'extraction et de transformation sont versionnées dans `sql/`.
- La documentation de connexion BigQuery est centralisée dans `config/bigquery.md`.

## Architecture

```text
GDELT Project/
├── .gitignore
├── README.md
├── requirements.txt
├── config/
│   └── bigquery.md
├── dashboard/
│   └── app.py
├── data/
│   └── data_dictionary.md
├── models/
├── notebooks/
│   └── exploration.ipynb
└── sql/
    ├── 01_extract_events.sql
    ├── 02_extract_gkg.sql
    ├── 03_extract_mentions.sql
    ├── 04_clean_enrich_events.sql
    ├── 05_clean_enrich_mentions.sql
    └── 06_clean_enrich_gkg.sql
```

## Organisation Du Flux

1. Les requêtes `01_extract_*.sql` extraient les données brutes depuis BigQuery.
2. Les requêtes `04_clean_enrich_*.sql` matérialisent le nettoyage et l'enrichissement directement dans BigQuery.
3. `notebooks/exploration.ipynb` sert à l'exploration analytique.
4. `dashboard/app.py` reste l'interface de visualisation du projet.
5. `data/data_dictionary.md` documente les colonnes et les règles métier.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Conventions

- Aucun répertoire local de données brutes, nettoyées ou enrichies n'est conservé dans le projet.
- Les fichiers SQL suivent un préfixe numérique pour garder l'ordre d'exécution clair.
- Les informations sensibles BigQuery ne doivent jamais être commitées.

## Prochaines étapes

- compléter `config/bigquery.md` avec le mode d'authentification retenu,
- écrire les requêtes de nettoyage et d'enrichissement SQL,
- documenter les colonnes finales dans le dictionnaire de données.
