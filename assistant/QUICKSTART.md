#  Quickstart Assistant

## Installation (une fois)

```bash
# À la racine du projet
source .venv/bin/activate
pip install -r requirements.txt

# Configuration Google Cloud
gcloud auth application-default login

# Créer .env
cat > .env << 'EOF'
GROQ_API_KEY=votre_clé_groq
GROQ_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3
EOF
```

---

## Trois Façons de Lancer

###  Interface Web HTML + API (RECOMMANDÉ)
```bash
# Terminal 1 - Lancer l'API (OBLIGATOIRE EN PREMIER)
uvicorn api:app --reload
```
 Attend: "Application startup complete on 0.0.0.0:8000"

```bash
# Terminal 2 - Ouvrir l'interface dans le navigateur
open http://localhost:8000
# (L'API sert l'interface HTML - ne pas ouvrir le fichier directement !)
```

###  API REST uniquement (pour développeurs)
```bash
uvicorn api:app --reload
```
 Documentation: http://localhost:8000/docs

###  Mode Ligne de Commande
```bash
python -c "from assistant.core.nl2sql import process_user_question; response = process_user_question('Combien d'événements en 2025 ?'); print(response['user_message'])"
```
Affiche directement: `31504 événements`

---

## Structure

```
assistant/
 README.md              ← Vue d'ensemble
 QUICKSTART.md          ← Ce fichier (démarrage)
 ARCHITECTURE.md        ← Diagrammes & flux
 ui/
   gdelt-assistant_v2.html ← Interface Web
 core/                  ← Moteur (11 modules)
 metadata/              ← Schéma (500+ colonnes)
 prompts/               ← Prompts LLM
 ui/                    ← Composants réutilisables

api.py (racine)        ← API REST entry point
```

---

## Exemples Questions

```
"Combien d'événements en 2025 ?"
→ Retourne: 31,504

"Top 5 médias"
→ Retourne: Table punchng.com, dailypost.ng, ...

"Évolution mensuelle tonalité"
→ Retourne: Graphique ligne

"Où conflits ?"
→ Retourne: Carte Folium
```

---

## Dépannage Rapide

| Erreur | Solution |
|--------|----------|
| API ne démarre pas | Vérifier port 8000 libre: `lsof -i :8000` |
| HTML refuse de se connecter | S'assurer que l'API est lancée (Terminal 1) |
| `ModuleNotFoundError: groq` | `pip install groq` |
| BigQuery auth | `gcloud auth application-default login` |
| Column not found | Vérifier `metadata/column_dictionary.py` |

---

## Points Clés

- **LLM**: Groq llama-3.3-70b (température 0.3)
- **Validation**: Auto-correction SQL intégrée
- **BigQuery**: 3 tables (events, mentions, gkg)
- **Jointures**: GLOBALEVENTID uniquement
- **Logger**: Enregistrement optionnel des interactions

---

Voir [README.md](README.md) pour la doc complète.
Voir [ARCHITECTURE.md](ARCHITECTURE.md) pour les diagrammes.
