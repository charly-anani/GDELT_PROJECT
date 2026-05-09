# Déploiement sur Render (Gratuit)

## ✅ Avantages Render
- Gratuit avec free tier
- Pas de trial qui expire
- Déploiement auto depuis GitHub
- Support variables d'environnement
- Domaine custom gratuit

---

## 🚀 Étapes Deployment Render

### 1. Créer le dossier `.git` et Committer le code

```bash
cd "/home/charly/Desktop/GDELT Project"

# Initialiser Git si pas déjà fait
git init
git add .
git commit -m "Initial commit - GDELT Assistant ready for deployment"
```

### 2. Pousser sur GitHub

```bash
# Créer un repo sur GitHub.com (https://github.com/new)
# Puis:
git remote add origin https://github.com/votre-utilisateur/gdelt-benin-assistant.git
git branch -M main
git push -u origin main
```

### 3. Aller sur Render.com

1. Créer compte: https://render.com (GitHub login recommandé)
2. Click "New +" → "Web Service"
3. Connecter GitHub repo "gdelt-benin-assistant"

### 4. Configuration Render

```
Name:                    gdelt-benin-assistant
Environment:             Python 3
Build Command:           pip install -r requirements.txt
Start Command:           uvicorn api:app --host 0.0.0.0 --port 8000
Instance Type:           Free (gratuit!)
```

### 5. Ajouter Variables d'Environnement

Dans Render Dashboard → Web Service → Environment:

```
GROQ_API_KEY = votre_clé_groq
GOOGLE_CLOUD_PROJECT = gdelt-494812
```

### 6. Upload Credentials Google Cloud

**Option A (Recommandé):**
Encoder en base64:
```bash
cat ~/path/to/credentials.json | base64
```

Puis créer variable:
```
GOOGLE_CREDENTIALS_B64 = (base64 encodé)
```

Et ajouter ce code dans `api.py` (après les imports):

```python
import os
import json
import base64

# Charger credentials depuis variable d'env
if 'GOOGLE_CREDENTIALS_B64' in os.environ:
    try:
        creds = base64.b64decode(os.environ['GOOGLE_CREDENTIALS_B64'])
        creds_path = '/tmp/credentials.json'
        with open(creds_path, 'w') as f:
            f.write(creds.decode())
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
    except Exception as e:
        print(f"Erreur loading credentials: {e}")
```

**Option B:**
Ajouter `credentials.json` au repo (plus simple mais moins sûr)

### 7. Deploy!

Render déploie automatiquement! Attendez 3-5 min.

**Accédez à:** `https://gdelt-benin-assistant.onrender.com`

---

## ✅ Test du Déploiement

```bash
# Health check
curl https://gdelt-benin-assistant.onrender.com/api/health

# Test question
curl -X POST https://gdelt-benin-assistant.onrender.com/api/question \
  -H "Content-Type: application/json" \
  -d '{"question":"Combien d'"'"'événements?"}'
```

---

## Durée
- Configuration: 5 min
- Build: 3-5 min
- Total: ~10 min

Vous êtes prêt!
