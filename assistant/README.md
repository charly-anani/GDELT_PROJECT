# GDELT Assistant — Documentation Complète

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Installation](#installation)
3. [Démarrage rapide](#démarrage-rapide)
4. [Architecture](#architecture)
5. [Mode Console Testing](#mode-console-testing)
6. [API & Intégration](#api--intégration)
7. [Logs & Monitoring](#logs--monitoring)
8. [Dépannage](#dépannage)

---

## Vue d'ensemble

**GDELT Assistant** transforme des questions en langage naturel en requêtes SQL/BigQuery pour analyser les données GDELT du Bénin (2025).

**Flux:**
```
Question utilisateur
    ↓
Génération SQL via Groq LLM
    ↓
Validation & Auto-correction SQL
    ↓
Exécution BigQuery
    ↓
Construction de la réponse JSON
    ↓
Réponse structurée (données + métadonnées)
```

---

## Installation

### Prérequis
- Python 3.10+
- Virtual env activé
- Google Cloud SDK (pour BigQuery)

### Étapes

```bash
# 1. Activer l'environnement
source ../.venv/bin/activate

# 2. Installer dépendances
pip install -r ../requirements.txt

# 3. Configuration Google Cloud
gcloud auth application-default login
```

### Clé API Groq (OBLIGATOIRE)

L'assistant utilise **Groq** comme LLM. Sans clé API, **rien ne fonctionnera**.

1. Aller sur https://console.groq.com/keys
2. Créer un compte gratuit (ou se connecter)
3. Cliquer sur **"Create API Key"**
4. Copier la clé générée

> **Limite gratuite** : 10 000 tokens par jour. Au-delà, les requêtes seront rejetées jusqu'au lendemain.

### Créer le fichier `.env`

Coller votre clé à la place de `coller_votre_clé_ici` :

```bash
cat > ../.env << 'EOF'
GROQ_API_KEY=coller_votre_clé_ici
GROQ_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3
GROQ_MAX_TOKENS=700
GROQ_TOP_P=0.9
EOF
```

**Vérification** : ouvrir le fichier `.env` et s'assurer que la ligne `GROQ_API_KEY=gsk_...` contient bien votre clé (elle commence généralement par `gsk_`).

---

## Démarrage rapide

### Mode 1: Interface Web HTML + API
```bash
# Terminal 1 - Lancer l'API (OBLIGATOIRE)
cd ..
uvicorn api:app --reload
```
Ouvrira API sur http://localhost:8000

```bash
# Terminal 2 - Ouvrir l'interface dans le navigateur
open http://localhost:8000
# (L'API sert automatiquement le HTML - ne pas ouvrir le fichier directement !)
```

### Mode 2: API REST uniquement (pour développeurs)
```bash
cd ..
uvicorn api:app --reload
```
Documentation interactive: http://localhost:8000/docs

### Mode 3: Mode Ligne de Commande
```bash
cd ..
python -c "from assistant.core.nl2sql import process_user_question; import json; response = process_user_question('Combien d\'événements en 2025 ?'); print(json.dumps(response, indent=2, default=str))"
```

---

## Architecture

### Structure du dossier
```
assistant/
├── core/                   # Moteur principal
│   ├── nl2sql.py           # Orchestration (NL→SQL)
│   ├── llm_client.py       # Client Groq
│   ├── sql_validator.py    # Validation & auto-correction
│   ├── bigquery_runner.py  # Exécution BigQuery
│   ├── response_builder.py # Construction réponses
│   ├── explainer.py        # Explication des résultats
│   ├── logger.py           # Enregistrement interactions (optionnel)
│   └── config.py           # Configuration
├── metadata/
│   ├── column_dictionary.py    # Schéma (500+ colonnes)
│   └── schema_retriever.py     # Extraction contexte
├── prompts/
│   └── system_prompt.py    # Instructions LLM
├── ui/
│   └── gdelt-assistant_v2.html # Interface Web HTML/JavaScript
└── README.md               # Ce fichier
```

### Flux d'exécution détaillé

```
1. Entrée utilisateur
   ↓
2. Validation & détection ambiguïté (clarifier.py)
   ↓
3. Extraction schéma pertinent (schema_retriever.py)
   ↓
4. Construction prompt LLM (system_prompt.py)
   ↓
5. Génération SQL via Groq (llm_client.py)
   ↓
6. Validation & auto-correction SQL (sql_validator.py)
   ↓
7. Exécution BigQuery (bigquery_runner.py)
   ↓
8. Construction réponse (response_builder.py)
   ↓
9. Explication LLM des insights (explainer.py)
   ↓
10. Enregistrement logs (logger.py)
    ↓
11. Affichage utilisateur (tableau + insight)
```

---

## Mode Ligne de Commande

Testez directement sans UI avec Python:

### Exemple simple
```bash
time python -c "
from assistant.core.nl2sql import process_user_question
print(process_user_question(\"Quels événements ont reçu le plus de couverture médiatique au Bénin en 2025 ?\"))
"
```

### Questions à essayer
- "Combien d'événements en 2025 ?"
- "Quels sont les top 10 médias ?"
- "Quelle est l'évolution mensuelle de la tonalité ?"
- "Quels sont les types d'événements les plus fréquents au Bénin en 2025 ?"


---

## API & Intégration

Fichier: `../api.py`

### Routes disponibles

#### GET /
Retourne l'interface HTML v2

#### POST /api/question
Traite une question en langage naturel

**Request:**
```json
{
  "question": "Combien d'événements en 2025 ?"
}
```

**Response:**
```json
{
  "status": "success",
  "user_message": "31,504 événements",
  "data": [
    {"total": 31504}
  ],
  "sql": "SELECT COUNT(DISTINCT GLOBALEVENTID) AS total FROM events_clean WHERE Year = 2025",
  "metadata": {
    "time_seconds": 2.3,
    "row_count": 1,
    "job_id": "project.us.job_xyz"
  }
}
```

#### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "version": "2.0"
}
```

---


---



---

## Intelligence LLM

**Modèle:** Groq `llama-3.3-70b-versatile`

**Paramètres:**
- Température: 0.3 (déterministe)
- Max tokens: 700
- Top-P: 0.9

**Clé API:** Gratuite sur https://console.groq.com/keys — limite 10 000 tokens/jour

**Prompt système inclut:**
- Noms colonnes exacts (snake_case vs CamelCase)
- Descriptions métier (500+ colonnes)
- Patterns de requêtes courantes
- Règles de sécurité SQL

---

## Types de Réponses

### KPI (Nombre simple)
```json
{
  "status": "success",
  "user_message": "31,504 événements",
  "data": [{"total": 31504}]
}
```

### Table (Données tabulaires)
```json
{
  "status": "success",
  "user_message": "Top 5 médias",
  "data": [
    {"source": "punchng.com", "count": 2037},
    {"source": "dailypost.ng", "count": 1952}
  ]
}
```

---

## Dépannage

### Erreur: "No module named 'groq'"
```bash
pip install groq
```

### Erreur: "BigQuery Authentication failed"
```bash
gcloud auth application-default login
```


### Erreur: Groq clé invalide ou requêtes rejetées
- Vérifier que la clé est bien présente dans `.env`
- En obtenir une nouvelle sur https://console.groq.com/keys
- Si limite atteinte (10 000 tokens/jour) -> réessayer demain

### Erreur: API ne démarre pas
```bash
# Vérifier que le port 8000 est libre
lsof -i :8000
# Si occupé, tuer le processus ou utiliser un port différent
uvicorn api:app --reload --port 8001
```

### Erreur: "Table mentions_clean not found"
Vérifier que les données BigQuery existent :
```bash
cd ..
python -c "
from assistant.core.config import BQ_PROJECT, BQ_DATASET, BQ_TABLES
print(f'Project: {BQ_PROJECT}')
print(f'Dataset: {BQ_DATASET}')
print(f'Tables: {BQ_TABLES}')
"
```

---

## Fichiers Clés

| Fichier | Rôle | Ligne d'entrée |
|---------|------|---|
| **core/nl2sql.py** | Orchestration principale | `process_user_question()` |
| **core/llm_client.py** | Appels Groq | `llm_chat(system, user)` |
| **core/sql_validator.py** | Validation SQL | `validate_sql(sql)` |
| **core/bigquery_runner.py** | Exécution BQ | `run_query(sql)` |
| **metadata/column_dictionary.py** | Schéma complet (500+ colonnes) | `COLUMN_METADATA` |
| **prompts/system_prompt.py** | Instructions LLM | `get_system_prompt()` |
| **core/response_builder.py** | Construction réponses | `build_success_response()` |

---

## Checklist Démarrage

- [ ] Virtual env activé
- [ ] requirements.txt installé
- [ ] Clé API Groq obtenue sur https://console.groq.com/keys
- [ ] .env configuré (GROQ_API_KEY=gsk_...)
- [ ] `gcloud auth application-default login`
- [ ] Tester: `time python -c "
from assistant.core.nl2sql import process_user_question
print(process_user_question(\"Quels événements ont reçu le plus de couverture médiatique au Bénin en 2025 ?\"))
"`
- [ ] API: `uvicorn ../api:app --reload`    et aller sur le lien generalement http://localhost:8000/ sauf si port precis

---

## Points d'entrée

| Mode | Port | Commande |
|------|------|----------|
| Web UI (HTML) | 8000 | `uvicorn ../api:app --reload` |
| API REST | 8000 | `uvicorn ../api:app --reload` |
| Ligne de commande | - | `time python -c "
from assistant.core.nl2sql import process_user_question
print(process_user_question(\"Quels événements ont reçu le plus de couverture médiatique au Bénin en 2025 ?\"))
"` |

---

