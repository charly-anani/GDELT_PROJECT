#!/bin/bash
# Script de déploiement local avec Docker

set -e

echo "🚀 GDELT Assistant - Script de Déploiement Local"
echo "================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    echo "Installer Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✅ Docker trouvé${NC}"

# Vérifier .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé${NC}"
    echo "Copier .env.example en .env et le remplir:"
    cp .env.example .env
    echo -e "${YELLOW}Veuillez éditer .env avec vos credentials${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Fichier .env trouvé${NC}"

# Vérifier credentials.json
if [ ! -f credentials.json ]; then
    echo -e "${YELLOW}⚠️  Fichier credentials.json non trouvé${NC}"
    echo "Télécharger le fichier de Google Cloud Console et le placer à la racine"
    exit 1
fi

echo -e "${GREEN}✅ Fichier credentials.json trouvé${NC}"
echo ""

# Build
echo "📦 Construction de l'image Docker..."
docker build -t gdelt-assistant:latest .
echo -e "${GREEN}✅ Image construite${NC}"
echo ""

# Run
echo "🎯 Lancement du container..."
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  gdelt-assistant:latest

echo ""
echo -e "${GREEN}✅ Serveur lancé sur http://localhost:8000${NC}"
