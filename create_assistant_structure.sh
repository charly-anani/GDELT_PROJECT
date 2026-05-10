#!/bin/bash

mkdir -p assistant/core
mkdir -p assistant/prompts
mkdir -p assistant/ui
mkdir -p assistant/tests
mkdir -p assistant/logs

echo "# Point d'entrée de l'assistant : lance l'app avec 'streamlit run assistant/app.py'" > assistant/app.py
echo "# Dépendances Python spécifiques à l'assistant (streamlit, google-cloud-bigquery, plotly...)" > assistant/requirements_assistant.txt
echo "# Documentation de l'assistant : installation, usage, architecture et exemples de questions" > assistant/README.md

echo "# Projet BigQuery, noms des tables, colonnes whitelistées et paramètres globaux" > assistant/core/config.py
echo "# Convertit une question en langage naturel en requête SQL BigQuery via Gemini" > assistant/core/nl2sql.py
echo "# Valide et bloque les requêtes dangereuses (INSERT, DROP, sans filtre pays/date)" > assistant/core/sql_validator.py
echo "# Exécute la requête SQL sur BigQuery, mesure le temps de réponse et logue les erreurs" > assistant/core/bigquery_runner.py
echo "# Choisit automatiquement le bon type de graphique Plotly (bar, line, pie, map, kpi)" > assistant/core/chart_router.py
echo "# Génère une explication en français simple des résultats retournés par BigQuery" > assistant/core/explainer.py
echo "# Enregistre chaque requête dans un fichier CSV d'audit (question, SQL, durée, statut)" > assistant/core/logger.py

echo "# Prompt système complet envoyé à Gemini : rôle, règles, glossaire métier GDELT Bénin" > assistant/prompts/system_prompt.py
echo "# 10 exemples few-shot (question → SQL) pour guider Gemini vers des requêtes correctes" > assistant/prompts/examples.py
echo "# Prompt d'interprétation journalistique : transforme des chiffres bruts en analyse lisible" > assistant/prompts/explainer_prompt.py

echo "# Interface Streamlit complète : chat, exemples cliquables, affichage graphiques et tableau" > assistant/ui/chat_interface.py

echo "# Tests unitaires pytest pour le validateur SQL (injections, requêtes interdites, cas limites)" > assistant/tests/test_sql_validator.py

echo "✅ Structure assistant/ créée avec succès !"
tree assistant/
