#!/bin/bash
# Script pour activer MLflow et enregistrer le modèle existant
# Usage: ./scripts/mlflow/enable_mlflow.sh

set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ACTIVATION MLFLOW & ENREGISTREMENT  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Étape 1: Vérifier que MLflow est UP
echo -e "${BLUE}Étape 1: Vérification MLflow Server${NC}"
MLFLOW_STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/health || echo "000")

if [ "$MLFLOW_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ MLflow Server est UP${NC}"
else
    echo -e "${RED}❌ MLflow Server n'est pas accessible (HTTP $MLFLOW_STATUS)${NC}"
    echo -e "${YELLOW}   Démarrage de MLflow...${NC}"
    docker compose up -d mlflow
    echo -e "${YELLOW}   Attente de 10 secondes...${NC}"
    sleep 10

    # Revérifier
    MLFLOW_STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/health || echo "000")
    if [ "$MLFLOW_STATUS" != "200" ]; then
        echo -e "${RED}❌ MLflow Server toujours inaccessible${NC}"
        echo -e "${YELLOW}   Vérifiez les logs: docker compose logs mlflow${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ MLflow Server démarré${NC}"
fi
echo ""

# Étape 2: Activer MLflow tracking (environnement)
echo -e "${BLUE}Étape 2: Configuration environnement${NC}"
export DISABLE_MLFLOW_TRACKING=false
export MLFLOW_TRACKING_URI=http://localhost:5001
export ML_SKIP_IF_EXISTS=false

echo -e "${GREEN}✅ Variables d'environnement configurées:${NC}"
echo "   - DISABLE_MLFLOW_TRACKING=false"
echo "   - MLFLOW_TRACKING_URI=http://localhost:5001"
echo "   - ML_SKIP_IF_EXISTS=false"
echo ""

# Étape 3: Enregistrer le modèle existant
echo -e "${BLUE}Étape 3: Enregistrement du modèle v2 dans MLflow${NC}"
echo ""

python3 scripts/mlflow/register_existing_model.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✅ SUCCÈS!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Le modèle v2 (96.24% accuracy) a été enregistré dans MLflow${NC}"
    echo ""
    echo -e "${BLUE}📊 Vérifier dans MLflow UI:${NC}"
    echo "   http://localhost:5001"
    echo ""
    echo -e "${BLUE}🔧 Pour que l'API utilise MLflow Registry:${NC}"
    echo "   1. Modifier docker-compose.yml ligne 128:"
    echo "      USE_MLFLOW_REGISTRY: \"true\""
    echo "   2. Redémarrer l'API:"
    echo "      docker compose restart api"
    echo ""
    echo -e "${BLUE}🚀 Pour entraîner un nouveau modèle avec MLflow:${NC}"
    echo "   export DISABLE_MLFLOW_TRACKING=false"
    echo "   export MLFLOW_TRACKING_URI=http://localhost:5001"
    echo "   python machine_learning/train_model.py --version v3"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ❌ ÉCHEC${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo -e "${RED}L'enregistrement du modèle a échoué${NC}"
    echo -e "${YELLOW}Vérifiez les logs ci-dessus pour plus de détails${NC}"
    exit 1
fi
