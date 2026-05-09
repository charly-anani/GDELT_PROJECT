#  Architecture GDELT Assistant

## Démarrage - Ordre Important

```bash
# TERMINAL 1 - Lancer l'API (OBLIGATOIRE EN PREMIER)
cd /chemin/vers/GDELT\ Project
source .venv/bin/activate
uvicorn api:app --reload
```
Attend: "Application startup complete on 0.0.0.0:8000"

```bash
# TERMINAL 2 - Ouvrir l'interface dans le navigateur
open http://localhost:8000
# L'API sert automatiquement le HTML - ne pas ouvrir le fichier directement !
```

---

## Important: Pourquoi http://localhost:8000 et pas le fichier directement ?

**Problème si vous ouvrez le fichier HTML directement** (file://):
```
file:///chemin/vers/assistant/ui/gdelt-assistant_v2.html

→ Le HTML essaie: fetch('http://localhost:8000/ask', ...)
→ Erreur: CORS bloqué (fichier local ≠ serveur HTTP)
→ ⚠️ HTTP 405 - Erreur de connexion
```

**Solution: L'API FastAPI sert le HTML**:
```python
# api.py
@app.get("/")
def serve_root():
    html_path = Path(...) / "assistant" / "ui" / "gdelt-assistant_v2.html"
    return FileResponse(html_path)
```

Donc:
1. Lancez l'API: `uvicorn api:app --reload`
2. Accédez via l'API: `http://localhost:8000`
3. L'API sert le HTML (et la fetch() vers /ask fonctionne)

---

## Vue d'ensemble complète

```
    UTILISATEUR
  (HTML Interface)

          ↓

  assistant/ui/gdelt-assistant_v2.html
  (Interface Web HTML/JavaScript)

          ↓

  HTTP POST /ask
  (api.py - FastAPI sur port 8000)

          ↓

    core/nl2sql.py
    (ORCHESTRATION - Points d'entrée)

    process_user_question(question)
    → response = {...}

  ↓     ↓             ↓            ↓
 [1]   [2]           [3]          [4]
Input Ambig.     Schema    LLM Prompt
Valid  Detec.   Extract   Building

          ↓

    [5] LLM_CLIENT
    groq.Groq API
    → SQL generated

            ↓

    [6] SQL_VALIDATOR
    - Validation
    - Auto-correction
    - Security checks

            ↓

    [7] BIGQUERY_RUNNER
    execute SQL
    → DataFrame results

            ↓

    [8] RESPONSE_BUILDER
    - Format data
    - Build JSON

            ↓

    [9] EXPLAINER
    - Generate insights

            ↓

    [10] LOGGER
    - Log to CSV

            ↓

      RESPONSE JSON
      {status, data,
       insight, sql, ...}

             ↓

    HTTP 200 Response
    (JSON au frontend)

             ↓

      AFFICHAGE HTML
      (Tableaux + Insight)

```

---

## Communication HTML ↔ API

### Côté HTML (gdelt-assistant_v2.html)
```javascript
const response = await fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "Combien d'événements ?"
  })
});

const data = await response.json();
// data = {
//   status: "success",
//   user_message: "31504 événements",
//   data: [...],
//   chart_type: "kpi",
//   sql: "SELECT COUNT(...)"
// }
```

### Côté API (api.py)
```python
@app.post("/ask")
def ask(request: AskRequest):
    response = process_user_question(request.question)
    return response
```

---

## Modules Détaillés

### **core/** — Moteur Principal

#### `nl2sql.py` — ORCHESTRATION (1000+ lignes)
```python
def process_user_question(question: str) -> dict:
    """
    Flux complet: question → SQL → résultats → réponse

    Étapes:
    1. validate_input() → Vérifie la question
    2. detect_ambiguity() → Demande clarification si besoin
    3. get_relevant_column_descriptions() → Extrait contexte schéma
    4. get_system_prompt() → Crée prompt LLM
    5. llm_chat() → Génère SQL via Groq
    6. validate_sql() → Valide et corrige SQL
    7. bq_runner.run_query() → Exécute BigQuery
    8. build_response() → Construit JSON
    9. log_interaction() → Enregistre en CSV
    10. return response
    """
```

#### `llm_client.py` — Groq LLM
```python
def llm_chat(system: str, user: str) -> str:
    """Appel à Groq Cloud API"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[...],
        temperature=0.3,
        max_tokens=700
    )
    return response.choices[0].message.content
```

#### `sql_validator.py` — Validation & Auto-correction
- Vérifie colonnes valides
- Valide tables existantes
- Joins autorisés (GLOBALEVENTID)
- Bloque injection SQL
- Auto-correction: syntaxe, colonnes, alias

#### `bigquery_runner.py` — Exécution BigQuery
```python
def run_query(sql: str) -> Tuple[pd.DataFrame, dict]:
    """Exécute SQL sur BigQuery, retourne DataFrame + métadonnées"""
```

#### `response_builder.py` — Construction Réponses
```python
build_success_response(df, sql, ...)
build_error_response(message, details)
build_clarification_response(message, options)
build_kpi_response(label, value)
```

#### `explainer.py` — Explications & Insights
```python
PALETTE = {
    "primary": "#E45756",      # Conflit (rouge)
    "secondary": "#F5A800",    # Coopération (orange)
    "neutral": "#888888"
}

#### `explainer.py` — Explications & Insights
```python
def get_explanation(question: str, sql: str, hint: str) -> str:
    """Génère explication simple et lisible de la requête"""
```

#### `logger.py` — Logging (optionnel)
```python
def log_interaction(question, sql, status, row_count, time_seconds, error):
    """Enregistre interactions dans assistant/logs/"""
```

#### `config.py` — Configuration Centrale
```python
BQ_PROJECT = "gdelt-494812"
BQ_DATASET = "benin_2025"
BQ_TABLES = {
    "events": "events_clean",
    "mentions": "mentions_clean",
    "gkg": "gkg_clean"
}
LLM_TEMPERATURE = 0.3
ALLOWED_INTENTS = ["COUNT", "TOP", "EVOLUTION", "SUMMARY", ...]
```

---

### **metadata/** — Schéma et Contexte

#### `column_dictionary.py` — Dictionnaire Complet (5000+ lignes)
```python
COLUMN_METADATA = {
    "events_clean": {
        "GLOBALEVENTID": {
            "business_name": "ID événement unique",
            "definition": "Identifiant global pour chaque événement GDELT",
            "use_for": ["Groupement", "Agrégation", "Jointures"],
            "avoid_for": ["Affichage direct"],
            "data_type": "integer",
            "example_values": [123456789, 987654321],
            "synonyms": ["event_id", "id"]
        },
        # ... 150+ colonnes
    },
    "mentions_clean": { ... },
    "gkg_clean": { ... }
}
```

#### `schema_retriever.py` — Extraction Contexte
```python
def get_relevant_column_descriptions(question: str) -> dict:
    """
    Cherche colonnes pertinentes pour la question
    Scoring: mots-clés + contexte + poids
    Retourne: {table: {colonne: description}}
    """
```

---

### **prompts/** — Prompts LLM

#### `system_prompt.py` — Instructions Groq
```python
def get_system_prompt() -> str:
    """
    Retourne prompt complet (3000+ tokens):

    1. Rôle: "Tu es un expert SQL pour GDELT..."
    2. Tables: Descriptions détaillées des 3 tables
    3. Colonnes: Noms exacts + descriptions (via column_dictionary)
    4. Patterns: COUNT, TOP, EVOLUTION, HEATMAP, MAP...
    5. Sécurité: "Jamais d'injections SQL", "Utilise GLOBALEVENTID"
    6. Exemples: Few-shot learning (4-5 exemples)
    7. Contexte: Business rules, constraints
    """
```

---

### **ui/** — Interface Utilisateur (Réutilisable)


## Structure du Projet

```
GDELT Project/
├── api.py                    ← FastAPI entry point (port 8000)
├── requirements.txt          ← Dépendances Python
├── .env                      ← Config (GROQ_API_KEY, etc.)
│
└── assistant/
    ├── README.md             ← Documentation principale
    ├── QUICKSTART.md         ← Démarrage rapide
    ├── ARCHITECTURE.md       ← Ce fichier
    │
    ├── core/                 ← Moteur (11 modules)
    │   ├── nl2sql.py
    │   ├── llm_client.py
    │   ├── sql_validator.py
    │   ├── bigquery_runner.py
    │   ├── response_builder.py
    │   ├── explainer.py
    │   ├── logger.py
    │   └── config.py
    │
    ├── metadata/             ← Schéma (500+ colonnes)
    │   ├── column_dictionary.py
    │   └── schema_retriever.py
    │
    ├── prompts/              ← Instructions LLM
    │   ├── system_prompt.py
    │   ├── examples.py
    │   └── __init__.py
    │
    └── ui/                   ← Interface utilisateur
        └── gdelt-assistant_v2.html   ← Interface Web HTML/JavaScript

```

```

---

## Flux d'Exécution Détaillé

### Étape 1: Utilisateur pose une question
```
Frontend: input "Combien d'événements dangereux ?"
          ↓
          POST /ask
```

### Étape 2: Input Validation
```
Vérification:
  • Longueur > 0
  • Pas d'injections
  ✓ Valide
```

### Étape 3: Ambiguity Detection
```
"dangereux" est ambigu
  → GoldsteinScale < -5 ?
  → QuadClass 3 ou 4 ?

Réponse: Clarification demandée
```

### Étape 4: Schema Extraction
```
Cherche dans column_dictionary:
  • GoldsteinScale
  • QuadClass
  • GLOBALEVENTID (pour COUNT)

Injecte contexte dans prompt
```

### Étape 5: LLM Prompt Building
```
[SYSTEM]
Tu es un expert SQL pour GDELT...
Tables: events_clean, mentions_clean, gkg_clean
Colonnes: GLOBALEVENTID, GoldsteinScale, QuadClass, ...
Patterns: COUNT(*), TOP 10, JOIN on GLOBALEVENTID
Sécurité: Pas d'injections, utilise colonnes valides

[USER]
"Combien d'événements avec GoldsteinScale < -5 ?"
```

### Étape 6: LLM Generation (Groq)
```
Input: 3000+ token prompt
Model: llama-3.3-70b-versatile
Temperature: 0.3
Max_tokens: 700

Output: SELECT COUNT(DISTINCT GLOBALEVENTID) as total
        FROM events_clean
        WHERE Year = 2025 AND GoldsteinScale < -5
```

### Étape 7: SQL Validation
```
Checklist:
  ✓ GLOBALEVENTID existe
  ✓ GoldsteinScale existe
  ✓ events_clean existe
  ✓ Year existe
  ✓ Pas d'injections

Status: VALIDE
```

### Étape 8: BigQuery Execution
```
Project: gdelt-494812
Dataset: benin_2025
Temps: 2.3 secondes

Résultat:
  [{"total": 856}]
```

### Étape 9: Response Building
```
{
  "status": "success",
  "user_message": "856 événements graves détectés",
  "data": [{"total": 856}],
  "chart_type": "kpi",
  "sql": "SELECT COUNT(...)",
  "metadata": {
    "time_seconds": 2.3,
    "row_count": 1,
    "explanation": "..."
  }
}
```

### Étape 10: Chart Selection
```
choose_chart(df, question):
  • df.shape = (1, 1)
  → Type: KPI

build_chart(df, chart_plan):
  → return None (KPI affiché directement)
```

### Étape 11: HTTP Response
```
Status: 200 OK
Content-Type: application/json
Body: {...response...}
```

### Étape 12: Frontend Display
```
HTML reçoit JSON
Affiche: "856"
         (visualisation KPI)
```

---

## Points Clés de Design

### 1. Séparation Frontend/Backend
- **Frontend**: HTML/JS pur (gdelt-assistant_v2.html)
- **Backend**: API FastAPI (api.py)
- Communication: HTTP JSON

### 2. LLM Intelligence
- **Modèle**: llama-3.3-70b-versatile
- **Température**: 0.3 (déterministe)
- **Tokens**: Max 700
- **Contexte**: 3000+ tokens de prompt système

### 3. Sécurité SQL
- Validation stricte vs column_dictionary
- Blocage injections SQL
- Auto-correction erreurs syntaxe
- Joins sécurisés (GLOBALEVENTID)

### 4. Visualisations Intelligentes
- Détection automatique type données
- Sélection graphique appropriée
- Styles cohérents (PALETTE)
- Support: Plotly + Folium Maps

### 5. Scalabilité
- BigQuery pour requêtes lourdes
- Caching optionnel (via logger)
- Timeouts configurables
- Logging optionnel

---

## Dépendances Externes

### APIs
1. **Groq Cloud** - LLM (llama-3.3-70b-versatile)
2. **Google BigQuery** - Data warehouse (gdelt-494812)
3. **Google Cloud Auth** - Authentication

### Librairies Python
```
google-cloud-bigquery>=3.14.0
groq>=0.9.0
pandas>=2.0
plotly>=5.17.0
folium>=0.14.0
python-dotenv>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
```

### Frontend
```
HTML5
JavaScript (fetch API)
Plotly.js (graphiques)
Folium (maps)
```

---

## Tests et Validation

### Mode Console (Sans interface)
```bash
python -c "from assistant.core.nl2sql import process_user_question; 
import json
response = process_user_question('Combien ?')
print(json.dumps(response, indent=2))"
```

### Mode API (Documentation interactive)
```
http://localhost:8000/docs
→ Swagger UI
→ Try it out
```

### Mode Frontend
```
open assistant/ui/gdelt-assistant_v2.html
→ Interface Web complète
```

---

## Monitoring et Logs

### Logs optionnels
```
assistant/logs/
  assistant_interactions.csv

Colonnes:
  timestamp, question, sql, status, row_count, time_seconds, error
```

Pour activer: `mkdir -p assistant/logs`

### Monitoring
- BigQuery Job ID: Visible dans metadata
- Temps d'exécution: Retourné dans response
- Erreurs: Détails dans response JSON

---
