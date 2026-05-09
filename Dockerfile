# Utiliser image Python légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système (gcc pour les packages C)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port 8000
EXPOSE 8000

# Commande de démarrage - bind sur 0.0.0.0 pour accès externe
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
