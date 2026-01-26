# 🐳 Stack Docker - Configuration Complète

**Date**: 26 janvier 2026  
**Projet**: PredictionDex  
**Services**: 9 conteneurs Docker orchestrés

---

## 📦 Services

### 1. **PostgreSQL** (`db`)
- **Image**: `postgres:15`
- **Port**: 5432
- **Usage**: Base de données principale
- **Health check**: `pg_isready`
- **Volumes**: `postgres_data:/var/lib/postgresql/data`

### 2. **ETL Pipeline** (`etl`)
- **Dockerfile**: `docker/Dockerfile.etl`
- **Dépend de**: `db`
- **Usage**: Import données Pokémon (PokéAPI + Pokepedia)
- **Mode**: One-shot (s'arrête après exécution)

### 3. **ML Builder** (`ml_builder`)
- **Dockerfile**: `docker/Dockerfile.ml`
- **Dépend de**: `etl`
- **Usage**: Entraînement modèle XGBoost
- **Mode**: One-shot (s'arrête après entraînement)
- **Volumes**: `./models` (export modèles)

### 4. **API FastAPI** (`api`)
- **Dockerfile**: `docker/Dockerfile.api`
- **Port**: 8000
- **Dépend de**: `db`, `etl`, `ml_builder`
- **Usage**: API REST + prédictions ML
- **Endpoints**:
  - `/docs` - Swagger UI
  - `/health` - Health check
  - `/metrics` - Métriques Prometheus
  - `/predict/battle` - Prédictions
- **Networks**: `default`, `monitoring`

### 5. **Streamlit** (`streamlit`)
- **Dockerfile**: `docker/Dockerfile.streamlit`
- **Port**: 8501
- **Dépend de**: `api`
- **Usage**: Interface utilisateur web

### 6. **Prometheus** (`prometheus`)
- **Image**: `prom/prometheus:v2.47.0`
- **Port**: 9090
- **Usage**: Collecte métriques
- **Config**: `docker/prometheus/prometheus.yml`
- **Scrape interval**: 15s
- **Retention**: 15 jours
- **Volumes**: 
  - `./docker/prometheus:/etc/prometheus`
  - `prometheus_data:/prometheus`

### 7. **Grafana** (`grafana`)
- **Image**: `grafana/grafana:10.1.0`
- **Port**: 3000
- **Dépend de**: `prometheus`, `api`
- **Usage**: Dashboards monitoring
- **Auth**: Anonymous (auto-login Admin)
- **Dashboards**:
  - Model Performance (`model_performance.json`)
  - API Performance (`api_performance.json`)
- **Volumes**:
  - `./docker/grafana/provisioning:/etc/grafana/provisioning`
  - `./docker/grafana/dashboards:/var/lib/grafana/dashboards`
  - `grafana_data:/var/lib/grafana`

### 8. **Node Exporter** (`node-exporter`)
- **Image**: `prom/node-exporter:v1.6.1`
- **Port**: 9100
- **Usage**: Métriques système (CPU, RAM, Disk)

### 9. **MLflow** (`mlflow`)
- **Dockerfile**: `docker/Dockerfile.mlflow`
- **Port**: 5000
- **Dépend de**: `db`
- **Usage**: Model Registry + Tracking
- **Backend**: PostgreSQL
- **Volumes**:
  - `mlflow_data:/app/mlruns`
  - `./models:/app/models`

---

## 🌐 Réseaux

### `default`
Bridge network par défaut pour communication inter-services.

### `monitoring`
Bridge network dédié au monitoring (Prometheus, Grafana, API).

---

## 💾 Volumes

| Volume | Usage |
|--------|-------|
| `postgres_data` | Données PostgreSQL persistantes |
| `prometheus_data` | Métriques Prometheus (15 jours) |
| `grafana_data` | Config Grafana + dashboards |
| `mlflow_data` | Artifacts MLflow |

---

## 🚀 Commandes

### Démarrage

```bash
# Démarrage complet
docker-compose up -d

# Démarrage avec rebuild
docker-compose up -d --build

# Démarrage services spécifiques
docker-compose up -d db api prometheus grafana
```

### Arrêt

```bash
# Arrêt tous services
docker-compose down

# Arrêt + suppression volumes
docker-compose down -v

# Arrêt service spécifique
docker-compose stop api
```

### Logs

```bash
# Logs tous services
docker-compose logs -f

# Logs service spécifique
docker-compose logs -f api

# Logs dernières 100 lignes
docker-compose logs --tail=100 api
```

### Rebuild

```bash
# Rebuild tous services
docker-compose build --no-cache

# Rebuild service spécifique
docker-compose build --no-cache api

# Rebuild parallèle
docker-compose build --parallel
```

### Inspection

```bash
# Liste services
docker-compose ps

# Inspection service
docker inspect letsgo_api

# Stats temps réel
docker stats letsgo_api letsgo_prometheus

# Réseau
docker network inspect lets-go-predictiondex_monitoring
```

---

## 🔧 Configuration avancée

### Variables d'environnement (.env)

```bash
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password

# API
API_BASE_URL=http://api:8000
DEV_MODE=true

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000
DISABLE_MLFLOW_TRACKING=false

# ML Pipeline
ML_MODE=all                    # all, dataset, train, evaluate
ML_SCENARIO_TYPE=all           # best_move, random_move, all
ML_TUNE_HYPERPARAMS=true
ML_GRID_TYPE=fast              # fast or extended
ML_SKIP_IF_EXISTS=true         # Skip training if model exists
```

### Health Checks

Tous les services critiques ont des health checks :

```yaml
# API
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s

# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U letsgo_user"]
  interval: 5s
  timeout: 5s
  retries: 5

# MLflow
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

### Ordre de démarrage

Grâce à `depends_on` avec `condition`:

```
db (healthy)
  └─> etl (completed_successfully)
       └─> ml_builder (completed_successfully)
            └─> api (healthy)
                 └─> streamlit
```

MLflow démarre en parallèle après `db`.  
Prometheus/Grafana démarrent indépendamment.

---

## 🧪 Scripts de test

### 1. Validation stack
```bash
python scripts/validate_docker_stack.py
```
Vérifie que tous les services sont opérationnels.

### 2. Génération métriques
```bash
# Mode réaliste (5 min)
python scripts/generate_monitoring_data.py

# Mode burst (10 min)
python scripts/generate_monitoring_data.py --mode burst --duration 10
```

### 3. Test MLflow
```bash
python scripts/test_mlflow_integration.py
```
Crée un run de test dans MLflow.

### 4. Démarrage guidé
```bash
python scripts/quick_start_docker.py
```
Script interactif pour démarrer la stack.

### 5. Tests monitoring
```bash
# Tests automatisés
pytest tests/monitoring/test_generate_metrics.py -v

# Génération standalone
python tests/monitoring/test_generate_metrics.py generate 5
```

---

## 📊 Monitoring

### Métriques disponibles

**API:**
- `api_requests_total{method, endpoint, status}`
- `api_request_duration_seconds{method, endpoint}`
- `api_errors_total{method, endpoint, error_type}`

**ML:**
- `model_predictions_total{model_name}`
- `model_prediction_latency_seconds{model_name}`
- `model_prediction_confidence{model_name}`

**Système:**
- `node_cpu_seconds_total`
- `node_memory_MemTotal_bytes`
- `node_disk_io_time_seconds_total`

### Dashboards Grafana

1. **Model Performance**
   - Prédictions/sec
   - Latence (P50, P95, P99)
   - Confiance moyenne
   - Distribution types Pokémon

2. **API Performance**
   - Requêtes/sec par endpoint
   - Latence requêtes
   - Taux d'erreur (4xx, 5xx)
   - Uptime

### Alertes Prometheus

Configurées dans `docker/prometheus/alerts.yml`:
- High prediction latency (> 500ms)
- Low model confidence (< 60%)
- High error rate (> 5%)

---

## 🐛 Troubleshooting

### Service ne démarre pas

```bash
# Voir les logs
docker-compose logs <service>

# Redémarrer
docker-compose restart <service>

# Rebuild
docker-compose up -d --build <service>
```

### Port déjà utilisé

```bash
# Trouver processus sur port
sudo lsof -i :8000

# Changer le port dans docker-compose.yml
ports:
  - "8001:8000"  # Host:Container
```

### Volumes corrompus

```bash
# Supprimer volumes
docker-compose down -v

# Redémarrer from scratch
docker-compose up -d
```

### Problèmes réseau

```bash
# Recréer réseau
docker network prune
docker-compose up -d
```

### Métriques non visibles

```bash
# 1. Vérifier endpoint API
curl http://localhost:8000/metrics

# 2. Vérifier Prometheus targets
# Ouvrir http://localhost:9090/targets
# Tous les targets doivent être "UP"

# 3. Générer des données
python scripts/generate_monitoring_data.py --duration 5
```

---

## 📈 Performance

### Ressources recommandées

| Service | CPU | RAM | Disk |
|---------|-----|-----|------|
| PostgreSQL | 1 core | 512 MB | 1 GB |
| API | 1 core | 512 MB | - |
| Streamlit | 0.5 core | 256 MB | - |
| Prometheus | 0.5 core | 512 MB | 5 GB |
| Grafana | 0.5 core | 256 MB | 1 GB |
| MLflow | 0.5 core | 256 MB | 2 GB |

**Total**: ~4 cores, 2.5 GB RAM, 10 GB disk

### Limites Docker

Configurer dans `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

---

## 🔐 Sécurité

### Recommandations production

1. **Changer les mots de passe**
   ```bash
   POSTGRES_PASSWORD=<strong_password>
   GRAFANA_ADMIN_PASSWORD=<strong_password>
   ```

2. **Désactiver anonymous Grafana**
   ```yaml
   - GF_AUTH_ANONYMOUS_ENABLED=false
   - GF_AUTH_DISABLE_LOGIN_FORM=false
   ```

3. **Ajouter HTTPS**
   Utiliser nginx reverse proxy avec SSL.

4. **Limiter accès réseau**
   ```yaml
   api:
     ports:
       - "127.0.0.1:8000:8000"  # Localhost uniquement
   ```

5. **Scanner vulnérabilités**
   ```bash
   docker scan letsgo_api
   ```

---

## 📚 Références

- [Docker Compose docs](https://docs.docker.com/compose/)
- [Prometheus docs](https://prometheus.io/docs/)
- [Grafana docs](https://grafana.com/docs/)
- [MLflow docs](https://mlflow.org/docs/latest/)
- [FastAPI deployment](https://fastapi.tiangolo.com/deployment/)

---

**Dernière mise à jour**: 26 janvier 2026  
**Version**: 1.0  
**Auteur**: PredictionDex Team
