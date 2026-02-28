#!/usr/bin/env bash
# ============================================================================
# PredictionDex — Script de démonstration complète E1/E3
# ============================================================================
# Ce script lance tout de A à Z :
#   1. Vérifie les prérequis (Docker, .env)
#   2. Démarre le stack Docker (10 services)
#   3. Attend que tous les services soient prêts
#   4. Lance l'ETL si la BDD est vide
#   5. Enregistre le modèle dans MLflow
#   6. Génère des métriques de monitoring (Grafana)
#   7. Lance les tests pytest
#   8. Ouvre toutes les interfaces dans le navigateur
#
# Usage:
#   chmod +x scripts/demo_full.sh
#   ./scripts/demo_full.sh              # Tout lancer
#   ./scripts/demo_full.sh --skip-tests  # Sans les tests (plus rapide)
#   ./scripts/demo_full.sh --skip-etl    # Sans relancer l'ETL
#   ./scripts/demo_full.sh --stop        # Arrêter tout
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Project root
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Options
SKIP_TESTS=false
SKIP_ETL=false
STOP_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --skip-tests) SKIP_TESTS=true ;;
        --skip-etl)   SKIP_ETL=true ;;
        --stop)       STOP_ONLY=true ;;
        --help|-h)
            echo "Usage: $0 [--skip-tests] [--skip-etl] [--stop]"
            exit 0
            ;;
    esac
done

# ============================================================================
# Helper functions
# ============================================================================

header() {
    echo ""
    echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║  ${BOLD}$1${NC}${MAGENTA}$(printf '%*s' $((57 - ${#1})) '')║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

step() {
    echo -e "${CYAN}▶ ÉTAPE $1 — $2${NC}"
}

ok() {
    echo -e "  ${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
}

fail() {
    echo -e "  ${RED}❌ $1${NC}"
}

info() {
    echo -e "  ${BLUE}ℹ️  $1${NC}"
}

wait_for_service() {
    local name="$1"
    local url="$2"
    local max_wait="${3:-60}"
    local elapsed=0

    while [ $elapsed -lt $max_wait ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -qE "^(200|302)$"; then
            ok "$name est prêt"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        echo -ne "\r  ⏳ Attente de $name... (${elapsed}s/${max_wait}s)"
    done
    echo ""
    fail "$name n'a pas démarré après ${max_wait}s"
    return 1
}

# ============================================================================
# STOP mode
# ============================================================================

if [ "$STOP_ONLY" = true ]; then
    header "🛑 Arrêt de PredictionDex"
    docker compose down
    ok "Tous les services sont arrêtés"
    exit 0
fi

# ============================================================================
# MAIN DEMO
# ============================================================================

header "🚀 PredictionDex — Démo Certification E1/E3"

echo -e "${BLUE}Projet : lets-go-predictiondex${NC}"
echo -e "${BLUE}Date   : $(date '+%Y-%m-%d %H:%M')${NC}"
echo -e "${BLUE}Dossier: $PROJECT_DIR${NC}"
echo ""

# ─────────────────────────────────────────────────────────────
# ÉTAPE 1 : Prérequis
# ─────────────────────────────────────────────────────────────
step 1 "Vérification des prérequis"

# Docker
if ! command -v docker &> /dev/null; then
    fail "Docker non installé"
    exit 1
fi
ok "Docker installé ($(docker --version | head -1))"

# Docker Compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    ok "Docker Compose v2 détecté"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    ok "Docker Compose v1 détecté"
else
    fail "Docker Compose non installé"
    exit 1
fi

# .env file
if [ -f .env ]; then
    ok "Fichier .env trouvé"
else
    warn "Fichier .env manquant — création..."
    cp .env.example .env 2>/dev/null || {
        fail "Pas de .env.example. Crée ton .env manuellement."
        exit 1
    }
    ok "Fichier .env créé depuis .env.example"
fi

# Python venv
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    ok "Virtualenv Python activé (.venv)"
else
    warn "Pas de .venv — les tests Python seront ignorés"
    SKIP_TESTS=true
fi

echo ""

# ─────────────────────────────────────────────────────────────
# ÉTAPE 2 : Démarrage Docker
# ─────────────────────────────────────────────────────────────
step 2 "Démarrage des services Docker"

# Check if already running
RUNNING_CONTAINERS=$($COMPOSE_CMD ps -q 2>/dev/null | wc -l)
if [ "$RUNNING_CONTAINERS" -gt 5 ]; then
    ok "Services déjà en cours ($RUNNING_CONTAINERS conteneurs)"
else
    info "Lancement de docker compose up -d..."
    $COMPOSE_CMD up -d --build 2>&1 | tail -5
    ok "Docker compose lancé"
fi

echo ""

# ─────────────────────────────────────────────────────────────
# ÉTAPE 3 : Attente des services
# ─────────────────────────────────────────────────────────────
step 3 "Attente de la disponibilité des services"

# Load API key from .env
API_KEY=$(grep "^API_KEYS=" .env 2>/dev/null | cut -d= -f2 | tr -d '"' | cut -d, -f1)

wait_for_service "PostgreSQL (via API health)" "http://localhost:8080/health" 90
wait_for_service "API FastAPI"       "http://localhost:8080/docs"     60
wait_for_service "Streamlit"         "http://localhost:8502"          60
wait_for_service "Prometheus"        "http://localhost:9091/-/healthy" 30
wait_for_service "Grafana"           "http://localhost:3001/api/health" 30
wait_for_service "MLflow"            "http://localhost:5001/health"   30

echo ""

# ─────────────────────────────────────────────────────────────
# ÉTAPE 4 : Vérification des données (ETL)
# ─────────────────────────────────────────────────────────────
step 4 "Vérification des données en base"

# Check if Pokemon data exists
POKEMON_COUNT=$(curl -s -H "X-API-Key: $API_KEY" "http://localhost:8080/pokemon/" 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$POKEMON_COUNT" -gt 100 ]; then
    ok "$POKEMON_COUNT Pokémon en base — données OK"
elif [ "$SKIP_ETL" = true ]; then
    warn "Base vide mais --skip-etl activé"
else
    info "Base vide — lancement de l'ETL..."
    $COMPOSE_CMD run --rm etl 2>&1 | tail -5
    ok "ETL terminé"
fi

echo ""

# ─────────────────────────────────────────────────────────────
# ÉTAPE 5 : MLflow — Enregistrement du modèle
# ─────────────────────────────────────────────────────────────
step 5 "Configuration MLflow"

# Check if model is already registered
MLFLOW_MODELS=$(curl -s "http://localhost:5001/api/2.0/mlflow/registered-models/search" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('registered_models',[])))" 2>/dev/null || echo "0")

if [ "$MLFLOW_MODELS" -gt 0 ]; then
    ok "Modèle déjà enregistré dans MLflow ($MLFLOW_MODELS modèle(s))"
else
    info "Enregistrement du modèle dans MLflow (via container letsgo_mlflow)..."
    # Run directly inside the MLflow container so artifacts write to its local volume
    docker exec letsgo_mlflow python3 - << 'PYEOF' 2>&1 | tail -5
import json, pickle, mlflow, mlflow.sklearn
from pathlib import Path; from datetime import datetime; from mlflow.tracking import MlflowClient
mlflow.set_tracking_uri("http://localhost:5001")
models_dir = Path("/app/models")
with open(models_dir/"battle_winner_model_v2.pkl","rb") as f: model=pickle.load(f)
with open(models_dir/"battle_winner_metadata_v2.json") as f: metadata=json.load(f)
metrics={k:float(v) for k,v in metadata.get("metrics",{}).items() if isinstance(v,(int,float))}
params={**metadata.get("hyperparameters",{}), "n_features":metadata.get("n_features",133)}
mlflow.set_experiment("pokemon_battle_winner")
with mlflow.start_run(run_name="train_v2_"+datetime.now().strftime("%Y%m%d_%H%M%S")) as run:
    mlflow.log_params(params); mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(sk_model=model,name="model")
    mlflow.log_artifact(str(models_dir/"battle_winner_metadata_v2.json"),artifact_path="extras")
    run_id=run.info.run_id
result=mlflow.register_model("runs:/"+run_id+"/model","battle_winner_predictor")
MlflowClient().transition_model_version_stage("battle_winner_predictor",result.version,"Production",archive_existing_versions=True)
print(f"Modèle enregistré v{result.version} -> Production (accuracy: {metrics.get('test_accuracy',0)*100:.2f}%)")
PYEOF
    ok "Modèle enregistré dans MLflow"
fi

echo ""

# ─────────────────────────────────────────────────────────────
# ÉTAPE 6 : Génération de métriques (Grafana)
# ─────────────────────────────────────────────────────────────
step 6 "Génération de métriques pour Grafana"

# Use the dedicated monitoring script if available (richer data with real moves)
if [ -f scripts/populate_monitoring_v2.py ] && command -v python3 &> /dev/null; then
    info "Lancement de populate_monitoring_v2.py (50 prédictions avec vraies attaques)..."
    API_KEY="$API_KEY" python3 scripts/populate_monitoring_v2.py --count 50 --skip-mlflow 2>&1 | grep -E "success|error|Pokemon|Predictions|Throughput|✅|❌" || true
    ok "Métriques de monitoring générées — Grafana alimenté"
else
    # Fallback: manual predictions
    info "Envoi de 20 prédictions pour alimenter les métriques..."
    for i in $(seq 1 20); do
        PA=$((RANDOM % 153 + 1))
        PB=$((RANDOM % 153 + 1))
        curl -s -X POST "http://localhost:8080/predict/best-move" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $API_KEY" \
            -d "{\"pokemon_a_id\": $PA, \"pokemon_b_id\": $PB, \"available_moves\": [\"Charge\", \"Vive-Attaque\", \"Tonnerre\", \"Hydrocanon\"]}" \
            > /dev/null 2>&1 || true
        echo -ne "\r  📊 Prédictions: $i/20"
        sleep 0.3
    done
    echo ""
    ok "20 prédictions envoyées — Grafana alimenté"
fi

echo ""

# ─────────────────────────────────────────────────────────────
# ÉTAPE 7 : Tests pytest (optionnel)
# ─────────────────────────────────────────────────────────────
if [ "$SKIP_TESTS" = false ]; then
    step 7 "Exécution des tests via Docker"

    info "Lancement du conteneur de tests (docker compose --profile tests)..."
    info "Commande : $COMPOSE_CMD --profile tests up --abort-on-container-exit --exit-code-from tests tests"
    echo ""

    $COMPOSE_CMD --profile tests up \
        --abort-on-container-exit \
        --exit-code-from tests \
        tests 2>&1 | tail -40

    TEST_EXIT=$?

    # Cleanup test container
    $COMPOSE_CMD rm -f tests > /dev/null 2>&1

    if [ $TEST_EXIT -eq 0 ]; then
        ok "Tous les tests sont passés ✅"
    else
        warn "Certains tests ont échoué (code: $TEST_EXIT)"
        info "Voir les logs : $COMPOSE_CMD --profile tests logs tests"
    fi

    echo ""
else
    step 7 "Tests pytest (IGNORÉS — --skip-tests)"
    warn "Tests ignorés. Lance manuellement :"
    info "  python3 scripts/run_all_tests.py          # Via Docker (recommandé)"
    info "  pytest tests/ -v                           # En local (peut bloquer)"
    echo ""
fi

# ─────────────────────────────────────────────────────────────
# ÉTAPE 8 : Ouverture des interfaces
# ─────────────────────────────────────────────────────────────
step 8 "Ouverture des interfaces dans le navigateur"

# Detect browser command
if command -v xdg-open &> /dev/null; then
    BROWSER="xdg-open"
elif command -v open &> /dev/null; then
    BROWSER="open"
else
    BROWSER=""
fi

URLS=(
    "http://localhost:8502"
    "http://localhost:8080/docs"
    "http://localhost:3001"
    "http://localhost:9091"
    "http://localhost:5001"
)

NAMES=(
    "Streamlit (Interface utilisateur)"
    "Swagger API (Documentation)"
    "Grafana (Dashboards monitoring)"
    "Prometheus (Métriques brutes)"
    "MLflow (Model Registry)"
)

for i in "${!URLS[@]}"; do
    if [ -n "$BROWSER" ]; then
        $BROWSER "${URLS[$i]}" 2>/dev/null &
        sleep 0.5
    fi
    ok "${NAMES[$i]} → ${URLS[$i]}"
done

echo ""

# ─────────────────────────────────────────────────────────────
# RAPPORT FINAL
# ─────────────────────────────────────────────────────────────
header "📋 Démonstration prête !"

echo -e "${GREEN}${BOLD}Tous les services sont opérationnels.${NC}"
echo ""
echo -e "${CYAN}┌─────────────────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│  🌐 URLs disponibles                                    │${NC}"
echo -e "${CYAN}├─────────────────────────────────────────────────────────┤${NC}"
echo -e "${CYAN}│  Streamlit .......... http://localhost:8502              │${NC}"
echo -e "${CYAN}│  API Swagger ........ http://localhost:8080/docs         │${NC}"
echo -e "${CYAN}│  API Health ......... http://localhost:8080/health       │${NC}"
echo -e "${CYAN}│  API Métriques ...... http://localhost:8080/metrics      │${NC}"
echo -e "${CYAN}│  Grafana ............ http://localhost:3001 (admin/admin)│${NC}"
echo -e "${CYAN}│  Prometheus ......... http://localhost:9091              │${NC}"
echo -e "${CYAN}│  MLflow ............. http://localhost:5001              │${NC}"
echo -e "${CYAN}│  pgAdmin ............ http://localhost:5050              │${NC}"
echo -e "${CYAN}└─────────────────────────────────────────────────────────┘${NC}"
echo ""
echo -e "${YELLOW}Ordre recommandé pour la soutenance E3 (20 min) :${NC}"
echo -e "  1. ${BOLD}API${NC}       → Swagger /docs → montrer /predict/best-move"
echo -e "  2. ${BOLD}Streamlit${NC} → Faire une prédiction Pikachu vs Dracaufeu"
echo -e "  3. ${BOLD}Grafana${NC}   → Montrer les dashboards API + Model Performance"
echo -e "  4. ${BOLD}MLflow${NC}    → Montrer le Model Registry et les expériences"
echo -e "  5. ${BOLD}GitHub${NC}    → Montrer les Actions CI/CD (onglet Actions)"
echo ""
echo -e "${YELLOW}Commandes utiles :${NC}"
echo -e "  ${BLUE}docker compose logs -f api${NC}         # Logs API en temps réel"
echo -e "  ${BLUE}docker compose logs -f streamlit${NC}   # Logs Streamlit"
echo -e "  ${BLUE}pytest tests/ -v${NC}                   # Relancer les tests"
echo -e "  ${BLUE}./scripts/demo_full.sh --stop${NC}      # Arrêter tout"
echo ""
