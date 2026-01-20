#!/bin/bash

# Script de vérification de la configuration Docker
# Pour PredictionDex - Pokémon Let's Go

set -e

echo "🔍 Vérification de la configuration Docker pour PredictionDex"
echo "=============================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
ERRORS=0
WARNINGS=0
SUCCESS=0

# Fonction de vérification
check_file() {
    local file=$1
    local desc=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $desc: $file"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $desc: $file (MANQUANT)"
        ((ERRORS++))
    fi
}

check_dir() {
    local dir=$1
    local desc=$2

    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $desc: $dir"
        ((SUCCESS++))
    else
        echo -e "${YELLOW}⚠${NC} $desc: $dir (MANQUANT)"
        ((WARNINGS++))
    fi
}

echo "1. Vérification des Dockerfiles"
echo "--------------------------------"
check_file "docker/Dockerfile.api" "Dockerfile API"
check_file "docker/Dockerfile.etl" "Dockerfile ETL"
check_file "docker/Dockerfile.ml" "Dockerfile ML"
check_file "docker/Dockerfile.streamlit" "Dockerfile Streamlit"
check_file "docker/entrypoint.py" "Entrypoint API"
echo ""

echo "2. Vérification de docker-compose.yml"
echo "--------------------------------------"
check_file "docker-compose.yml" "Docker Compose"
check_file ".env" "Variables d'environnement"
check_file ".dockerignore" "Docker ignore"
echo ""

echo "3. Vérification des fichiers requirements"
echo "------------------------------------------"
check_file "api_pokemon/requirements.txt" "Requirements API"
check_file "etl_pokemon/requirements.txt" "Requirements ETL"
check_file "machine_learning/requirements.txt" "Requirements ML"
check_file "interface/requirements_streamlit.txt" "Requirements Streamlit"
echo ""

echo "4. Vérification des fichiers __init__.py"
echo "-----------------------------------------"
check_file "core/__init__.py" "__init__ core"
check_file "core/db/__init__.py" "__init__ core/db"
check_file "api_pokemon/__init__.py" "__init__ api_pokemon"
check_file "api_pokemon/routes/__init__.py" "__init__ api_pokemon/routes"
check_file "api_pokemon/services/__init__.py" "__init__ api_pokemon/services"
check_file "etl_pokemon/__init__.py" "__init__ etl_pokemon"
check_file "machine_learning/__init__.py" "__init__ machine_learning"
check_file "interface/__init__.py" "__init__ interface"
echo ""

echo "5. Vérification de la structure des répertoires"
echo "------------------------------------------------"
check_dir "api_pokemon" "API directory"
check_dir "api_pokemon/routes" "API routes"
check_dir "api_pokemon/services" "API services"
check_dir "core" "Core directory"
check_dir "core/models" "Core models"
check_dir "core/schemas" "Core schemas"
check_dir "core/db" "Core DB"
check_dir "core/db/guards" "Core guards"
check_dir "etl_pokemon" "ETL directory"
check_dir "etl_pokemon/scripts" "ETL scripts"
check_dir "etl_pokemon/data/csv" "ETL CSV data"
check_dir "machine_learning" "ML directory"
check_dir "interface" "Interface directory"
check_dir "interface/pages" "Interface pages"
check_dir "docker" "Docker directory"
check_dir "data" "Data directory"
check_dir "data/datasets" "Datasets directory"
echo ""

echo "6. Vérification des fichiers principaux"
echo "----------------------------------------"
check_file "api_pokemon/main.py" "API main"
check_file "etl_pokemon/run_all_in_one.py" "ETL runner"
check_file "machine_learning/build_dataset_ml_v1.py" "ML builder"
check_file "interface/app.py" "Streamlit app"
check_file "core/db/session.py" "DB session"
check_file "core/db/base.py" "DB base"
echo ""

echo "7. Vérification du contenu .env"
echo "--------------------------------"
if [ -f ".env" ]; then
    if grep -q "POSTGRES_USER" .env && \
       grep -q "POSTGRES_PASSWORD" .env && \
       grep -q "POSTGRES_DB" .env && \
       grep -q "DEV_MODE" .env; then
        echo -e "${GREEN}✓${NC} Fichier .env contient les variables nécessaires"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} Fichier .env incomplet"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗${NC} Fichier .env manquant"
    ((ERRORS++))
fi
echo ""

echo "=============================================================="
echo "Résumé de la vérification"
echo "=============================================================="
echo -e "${GREEN}Succès: $SUCCESS${NC}"
echo -e "${YELLOW}Avertissements: $WARNINGS${NC}"
echo -e "${RED}Erreurs: $ERRORS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 Configuration Docker validée avec succès!${NC}"
    echo ""
    echo "Vous pouvez maintenant lancer:"
    echo "  docker-compose up --build"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Des erreurs ont été détectées. Veuillez les corriger avant de continuer.${NC}"
    echo ""
    exit 1
fi
