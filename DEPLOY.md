# Guide de Déploiement - GDELT Bénin Assistant

## 1. Préparation pour le Déploiement

### Variables d'Environnement Requises
Créer un fichier `.env` avec:
```
GOOGLE_CLOUD_PROJECT=gdelt-494812
GROQ_API_KEY=votre_clé_groq_ici
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Authentification Google Cloud
1. Télécharger le fichier de credentials JSON depuis Google Cloud Console
2. Le placer à la racine ou passer le chemin dans `GOOGLE_APPLICATION_CREDENTIALS`

---

## 2. Déploiement Localement avec Docker

### Build l'image
```bash
docker build -t gdelt-assistant:latest .
```

### Lancer le container
```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=votre_clé \
  -e GOOGLE_CLOUD_PROJECT=gdelt-494812 \
  -v ~/.config/gcloud:/root/.config/gcloud \
  gdelt-assistant:latest
```

Accéder à: **http://localhost:8000**

---

## 3. Déploiement sur Railway (Recommandé)

### Étapes:

1. **Créer un compte** sur [railway.app](https://railway.app)

2. **Connecter GitHub** (optionnel, pour déploiement auto)
   - Ou utiliser Railway CLI

3. **Installer Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

4. **Se connecter**:
   ```bash
   railway login
   ```

5. **Initialiser le projet**:
   ```bash
   railway init
   ```

6. **Ajouter les variables d'environnement**:
   ```bash
   railway variables set GROQ_API_KEY=votre_clé
   railway variables set GOOGLE_CLOUD_PROJECT=gdelt-494812
   ```

7. **Ajouter le fichier credentials** (Google Cloud):
   ```bash
   # Créer un secret Google Cloud Service Account en base64
   cat ~/path/to/credentials.json | base64
   # Puis ajouter en variable Railway
   railway variables set GOOGLE_CREDENTIALS_B64=base64_encodé
   ```

8. **Modifier api.py** pour lire credentials depuis env (optionnel):
   ```python
   import os, json, base64
   
   if 'GOOGLE_CREDENTIALS_B64' in os.environ:
       creds = base64.b64decode(os.environ['GOOGLE_CREDENTIALS_B64'])
       with open('/tmp/creds.json', 'w') as f:
           f.write(creds.decode())
       os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/creds.json'
   ```

9. **Déployer**:
   ```bash
   railway up
   ```

10. **Obtenir l'URL publique**:
    ```bash
    railway env
    # Railway génère une URL: https://votre-app.railway.app
    ```

---

## 4. Déploiement sur Render (Alternative)

### Étapes:

1. **Créer un compte** sur [render.com](https://render.com)

2. **Créer un "New Web Service"**

3. **Connecter GitHub** et sélectionner le repo

4. **Configuration Render**:
   - **Runtime**: Python
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn api:app --host 0.0.0.0 --port 8000`
   - **Port**: 8000

5. **Ajouter les variables d'environnement**:
   - `GROQ_API_KEY`
   - `GOOGLE_CLOUD_PROJECT`
   - `GOOGLE_APPLICATION_CREDENTIALS` (chemin dans container)

6. **Upload credentials**:
   - Ajouter le fichier credentials.json au repo (privé) ou utiliser des variables encodées

7. **Déployer**: Render déploie automatiquement à chaque push

---

## 5. Tester le Déploiement

### Test de santé:
```bash
curl https://votre-app.railway.app/api/health
```

Réponse attendue:
```json
{"status": "ok", "version": "2.0"}
```

### Test avec une question:
```bash
curl -X POST https://votre-app.railway.app/api/question \
  -H "Content-Type: application/json" \
  -d '{"question":"Combien d'"'"'événements?"}'
```

### Accéder à l'interface:
```
https://votre-app.railway.app
```

---

## 6. Architecture de Déploiement

```
┌─────────────────────────────────┐
│   Interface Web (HTML/JS)        │ ← http://votre-app.railway.app
│   (gdelt-assistant_v2.html)      │
└──────────────┬──────────────────┘
               │
               │ fetch() API calls
               │
┌──────────────▼──────────────────┐
│   FastAPI Server (api.py)         │ ← Port 8000
│   - GET /                         │
│   - POST /api/question            │
│   - GET /api/health              │
└──────────────┬──────────────────┘
               │
               │ Query execution
               │
┌──────────────▼──────────────────┐
│   Google Cloud BigQuery           │
│   (gdelt-494812.benin_2025)      │
└────────────────────────────────┘
               │
        LLM Insights
               │
┌──────────────▼──────────────────┐
│   Groq Cloud API                  │
│   (llama-3.3-70b-versatile)      │
└────────────────────────────────┘
```

---

## 7. Checklist Pré-Déploiement

- ✅ `requirements.txt` à jour et testé localement
- ✅ `Dockerfile` construit et testé: `docker build -t test . && docker run -p 8000:8000 test`
- ✅ Variables d'environnement définies sur la plateforme
- ✅ Credentials Google Cloud disponibles
- ✅ GROQ API key valide
- ✅ Test localement avec `uvicorn api:app`
- ✅ Pas de fichiers .env commités dans Git

---

## 8. Troubleshooting

### Erreur: "BigQuery not found"
→ Vérifier `GOOGLE_APPLICATION_CREDENTIALS` et credentials.json

### Erreur: "Groq API key invalid"
→ Vérifier `GROQ_API_KEY` dans les variables d'environnement

### Port non accessible
→ S'assurer que `--host 0.0.0.0` dans le démarrage

### CORS errors
→ Vérifier que CORS est activé dans `api.py` (déjà configuré)

---

## 9. Commandes Utiles

### Railway
```bash
railway login                    # Se connecter
railway init                     # Initialiser
railway variables               # Voir les variables
railway variables set KEY=VAL   # Ajouter une variable
railway up                      # Déployer
railway logs                    # Voir les logs
railway down                    # Arrêter le déploiement
```

### Docker Local
```bash
docker build -t gdelt-assistant .        # Build
docker run -p 8000:8000 gdelt-assistant # Run
docker ps                               # Voir les containers
docker logs <container_id>              # Voir les logs
docker stop <container_id>              # Arrêter
```

---

## Contact & Support

Pour des questions:
- Consulter les logs de la plateforme
- Vérifier les variables d'environnement
- Tester localement d'abord
