# 🐳 Docker - Configuration des Services

> Images Docker et orchestration des services

## 📋 Vue d'ensemble

Le projet utilise Docker Compose pour orchestrer 9 services :
- **3 services applicatifs** : API, ETL, ML Builder
- **1 interface** : Streamlit
- **1 base de données** : PostgreSQL
- **3 services monitoring** : Prometheus, Grafana, MLflow
- **1 outil admin** : pgAdmin

## 📁 Structure

```
docker/
├── Dockerfile.api            # Image API FastAPI
├── Dockerfile.etl            # Image ETL Pipeline
├── Dockerfile.ml             # Image ML Builder (XGBoost)
├── Dockerfile.mlflow         # Image MLflow Server
├── Dockerfile.streamlit      # Image Interface Streamlit
├── Dockerfile.tests          # Image Tests (pytest)
├── api_entrypoint.py         # Entrypoint API
├── etl_entrypoint.py         # Entrypoint ETL
├── ml_entrypoint.py          # Entrypoint ML
├── wait_for_db.py            # Script d'attente BDD
├── grafana/                  # Configuration Grafana
│   ├── dashboards/           # Dashboards JSON
│   └── provisioning/         # Auto-provisioning
├── prometheus/               # Configuration Prometheus
│   └── prometheus.yml        # Scrape config
└── pgadmin4/                 # Configuration pgAdmin
    └── servers.json          # Serveurs pré-configurés
```

## 🚀 Utilisation

### Démarrage complet

```bash
# Construire et démarrer tous les services
docker compose up --build

# En arrière-plan
docker compose up -d

# Reconstruire un service spécifique
docker compose build api
docker compose up api
```

### Services individuels

```bash
# Seulement la BDD
docker compose up db

# ETL uniquement
docker compose up etl

# API + dépendances
docker compose up api
```

## 📊 Services et Ports

| Service | Image | Port | URL |
|---------|-------|------|-----|
| `db` | postgres:15 | 5432 | - |
| `api` | Dockerfile.api | 8080 | http://localhost:8080/docs |
| `streamlit` | Dockerfile.streamlit | 8502 | http://localhost:8502 |
| `prometheus` | prom/prometheus | 9091 | http://localhost:9091 |
| `grafana` | grafana/grafana | 3001 | http://localhost:3001 |
| `mlflow` | Dockerfile.mlflow | 5001 | http://localhost:5001 |
| `pgadmin` | dpage/pgadmin4 | 5050 | http://localhost:5050 |
| `etl` | Dockerfile.etl | - | (one-shot) |
| `ml_builder` | Dockerfile.ml | - | (one-shot) |

## 🔧 Configuration

### Variables d'environnement (`.env`)

```env
# PostgreSQL
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password

# API
API_KEY=your-secure-api-key
API_KEY_REQUIRED=true

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# Mode développement
DEV_MODE=true
```

### Volumes persistants

```yaml
volumes:
  postgres_data:    # Données PostgreSQL
  pgadmin_data:     # Configuration pgAdmin
  grafana_data:     # Dashboards Grafana
  mlflow_data:      # Artifacts MLflow
```

## 🏗️ Ordre de Démarrage

```
db (PostgreSQL)
    │
    ├──► etl (one-shot)
    │         │
    │         ▼
    │    ml_builder (one-shot)
    │         │
    ▼         ▼
    ├──► api ◄────────┐
    │                 │
    ├──► streamlit ───┘
    │
    ├──► prometheus ──► grafana
    │
    └──► mlflow
```

## 🧪 Tests en Docker

```bash
# Exécuter tous les tests
docker compose run --rm tests

# Tests avec coverage
docker compose run --rm tests pytest --cov=api_pokemon --cov=machine_learning
```

## 🔍 Commandes Utiles

```bash
# Voir les logs
docker compose logs -f api
docker compose logs -f --tail=100 ml_builder

# Accéder à un conteneur
docker compose exec api bash
docker compose exec db psql -U letsgo_user -d letsgo_db

# Nettoyer tout
docker compose down -v --rmi all

# Rebuild sans cache
docker compose build --no-cache
```

## 📈 Monitoring

### Grafana
- **URL** : http://localhost:3001
- **Login** : admin / admin
- **Dashboards** :
  - API Performance
  - Model Metrics

### Prometheus
- **URL** : http://localhost:9091
- **Targets** : API (8080/metrics)

### MLflow
- **URL** : http://localhost:5001
- **Experiments** : pokemon-battle-prediction
