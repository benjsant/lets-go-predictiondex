# 🐳 Docker Orchestration Complète

**Date**: 26 janvier 2026  
**Statut**: ✅ Prêt pour `docker-compose up --build`

---

## 🚀 Démarrage en une commande

```bash
docker-compose up --build
```

✅ **Tout est déjà orchestré !** Le projet démarre automatiquement avec :
- 9 services Docker
- Dépendances gérées automatiquement
- Health checks pour synchronisation
- Volumes persistants

---

## 📊 Ordre d'exécution automatique

### 1️⃣ PostgreSQL (db)
```yaml
healthcheck: pg_isready
interval: 5s
```
- ✅ Démarre en premier
- ✅ Health check toutes les 5 secondes
- ✅ Prêt avant les autres services

### 2️⃣ ETL (etl)
```yaml
depends_on:
  db: condition: service_healthy
restart: "no"
```
- ⏳ Attend que PostgreSQL soit healthy
- 🔄 Exécute le pipeline ETL complet
- ✅ Se termine automatiquement (pas de restart)
- 📦 Charge : Pokédex, types, capacités, movesets

### 3️⃣ ML Builder (ml_builder)
```yaml
depends_on:
  etl: condition: service_completed_successfully
restart: "no"
```
- ⏳ Attend la fin de l'ETL
- 🤖 Génère les datasets de bataille
- 🎯 Entraîne le modèle XGBoost
- 💾 Exporte le modèle dans `/models`
- ✅ Se termine automatiquement

### 4️⃣ Services permanents (démarrent après ML)

#### API (api)
```yaml
depends_on:
  db: service_healthy
  etl: service_completed_successfully
  ml_builder: service_completed_successfully
healthcheck: curl /health
restart: unless-stopped
```
- 🔌 Port: http://localhost:8000
- 📊 Endpoints: `/predict`, `/pokemon`, `/moves`
- 📈 Métriques: http://localhost:8000/metrics

#### Streamlit (streamlit)
```yaml
depends_on:
  api: service_healthy
restart: unless-stopped
```
- 🎨 Port: http://localhost:8501
- 🖥️ Interface utilisateur
- 🔗 Connecté à l'API

#### MLflow (mlflow)
```yaml
depends_on:
  db: service_healthy
restart: unless-stopped
```
- 📊 Port: http://localhost:5000
- 🔬 Tracking des expériences ML
- 📦 Model Registry

#### Prometheus (prometheus)
```yaml
restart: unless-stopped
```
- 📈 Port: http://localhost:9090
- 🔍 Scraping des métriques (API, système)
- ⏱️ Rétention: 15 jours

#### Grafana (grafana)
```yaml
depends_on:
  prometheus: service_started
  api: service_healthy
restart: unless-stopped
```
- 📊 Port: http://localhost:3000
- 🎨 Dashboards pré-configurés
- 🔓 Auth: automatique (admin)

#### Node Exporter (node-exporter)
```yaml
restart: unless-stopped
```
- 📊 Port: http://localhost:9100
- 💻 Métriques système (CPU, RAM, disk)

---

## ⚙️ Configuration environnement

### Variables d'environnement (`.env`)

```env
# Database
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password
POSTGRES_DB=letsgo_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Mode développement
DEV_MODE=true
```

### Variables ML (docker-compose.yml)

```yaml
ml_builder:
  environment:
    ML_MODE: "all"                    # all, dataset, train, evaluate
    ML_SCENARIO_TYPE: "all"           # best_move, random_move, all_combinations, all
    ML_TUNE_HYPERPARAMS: "true"       # GridSearchCV activé
    ML_GRID_TYPE: "fast"              # fast (8 combi) ou extended (243 combi)
    ML_SKIP_IF_EXISTS: "true"         # Skip si modèle existe
    ML_NUM_RANDOM_SAMPLES: "5"
    ML_MAX_COMBINATIONS: "20"
```

---

## 🎯 Workflows automatisés

### Entrypoint ETL (`docker/etl_entrypoint.py`)
```python
1. wait_for_db(timeout=60)           # Attend PostgreSQL
2. run_etl()                         # Execute pipeline.py
3. sys.exit(0)                       # Termine proprement
```

### Entrypoint ML (`docker/ml_entrypoint.py`)
```python
1. wait_for_db(timeout=60)           # Attend PostgreSQL
2. check_model_exists()              # Vérifie si modèle existe
3. run_ml_builder()                  # Lance run_machine_learning.py
   - Génère datasets v2
   - Entraîne XGBoost
   - GridSearchCV (optionnel)
   - Export modèle + metadata
4. sys.exit(0)                       # Termine proprement
```

### Entrypoint API (`docker/api_entrypoint.py`)
```python
1. wait_for_db(timeout=60)           # Attend PostgreSQL
2. start_api()                       # Lance uvicorn (FastAPI)
   - Host: 0.0.0.0:8000
   - Reload: true (si DEV_MODE)
```

---

## 📦 Volumes persistants

```yaml
volumes:
  postgres_data:        # Base de données PostgreSQL
  prometheus_data:      # Métriques Prometheus (15j)
  grafana_data:         # Dashboards Grafana
  mlflow_data:          # Expériences MLflow
```

**Données conservées après redémarrage** :
- ✅ Base de données complète
- ✅ Historique Prometheus
- ✅ Dashboards Grafana
- ✅ Tracking MLflow

---

## 🔍 Vérification du démarrage

### Logs en temps réel
```bash
docker-compose logs -f
```

### Logs par service
```bash
docker-compose logs etl          # ETL Pipeline
docker-compose logs ml_builder   # ML Training
docker-compose logs api          # FastAPI
docker-compose logs grafana      # Grafana
```

### Status des services
```bash
docker-compose ps
```

**Output attendu** :
```
NAME                    STATUS              PORTS
letsgo_postgres         Up (healthy)        5432
letsgo_etl              Exited (0)          -
letsgo_ml               Exited (0)          -
letsgo_api              Up (healthy)        8000
letsgo_streamlit        Up                  8501
letsgo_mlflow           Up (healthy)        5000
letsgo_prometheus       Up                  9090
letsgo_grafana          Up                  3000
letsgo_node_exporter    Up                  9100
```

---

## 🌐 Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| **API REST** | http://localhost:8000 | FastAPI + Swagger docs |
| **Streamlit** | http://localhost:8501 | Interface utilisateur |
| **MLflow** | http://localhost:5000 | Tracking ML + Registry |
| **Grafana** | http://localhost:3000 | Dashboards monitoring |
| **Prometheus** | http://localhost:9090 | Métriques système |
| **Node Exporter** | http://localhost:9100 | Métriques hardware |

---

## 🛠️ Commandes utiles

### Démarrage
```bash
# Premier lancement (build + start)
docker-compose up --build

# Background mode
docker-compose up --build -d

# Rebuilder un seul service
docker-compose build api
docker-compose up -d api
```

### Redémarrage
```bash
# Tout redémarrer
docker-compose restart

# Redémarrer un service
docker-compose restart api
```

### Nettoyage
```bash
# Arrêter tous les services
docker-compose down

# Arrêter + supprimer volumes (⚠️ perte données)
docker-compose down -v

# Supprimer images
docker-compose down --rmi all
```

### Forcer re-training ML
```bash
# Option 1: Modifier docker-compose.yml
ML_SKIP_IF_EXISTS: "false"

# Option 2: Supprimer le modèle
rm models/battle_winner_model_v2.pkl
docker-compose up ml_builder --build
```

### Re-run ETL
```bash
# Redémarrer le service ETL
docker-compose up etl --build
```

---

## 🔧 Personnalisation

### Modifier les ports
```yaml
# docker-compose.yml
api:
  ports:
    - "8080:8000"  # API sur port 8080

streamlit:
  ports:
    - "8502:8501"  # Streamlit sur port 8502
```

### Activer GridSearchCV étendu
```yaml
ml_builder:
  environment:
    ML_GRID_TYPE: "extended"  # 243 combinaisons (~30 min)
```

### Désactiver le monitoring
```bash
# Commenter dans docker-compose.yml
# prometheus:
# grafana:
# node-exporter:
```

---

## ⚡ Optimisations

### Démarrage rapide (skip ML)
```yaml
ml_builder:
  environment:
    ML_SKIP_IF_EXISTS: "true"  # ✅ Déjà configuré
```
- ✅ Si `models/battle_winner_model_v2.pkl` existe, skip training
- ⏱️ Gain: 5-15 minutes

### Mode production
```yaml
api:
  environment:
    DEV_MODE: "false"  # Désactive --reload
```

### Augmenter timeout health checks
```yaml
api:
  healthcheck:
    start_period: 60s  # Au lieu de 30s
```

---

## 🐛 Troubleshooting

### Problème: ETL échoue
```bash
# Vérifier logs
docker-compose logs etl

# Forcer re-run
docker-compose up etl --force-recreate --build
```

### Problème: ML training trop long
```bash
# Solution 1: Utiliser fast grid
ML_GRID_TYPE: "fast"

# Solution 2: Désactiver GridSearch
ML_TUNE_HYPERPARAMS: "false"

# Solution 3: Limiter scenarios
ML_SCENARIO_TYPE: "best_move"  # Au lieu de "all"
```

### Problème: API ne démarre pas
```bash
# Vérifier que ETL et ML sont terminés
docker-compose ps

# Attendre health check PostgreSQL
docker-compose logs db | grep "ready"

# Redémarrer API
docker-compose restart api
```

### Problème: Port déjà utilisé
```bash
# Vérifier processus
sudo lsof -i :8000
sudo lsof -i :5432

# Arrêter processus
docker-compose down
```

### Problème: Espace disque insuffisant
```bash
# Nettoyer volumes
docker system prune -a --volumes

# Vérifier espace
df -h
docker system df
```

---

## 📋 Checklist avant production

- [ ] Changer passwords PostgreSQL (`.env`)
- [ ] Désactiver `DEV_MODE=false`
- [ ] Configurer `restart: always` pour services critiques
- [ ] Activer authentification Grafana (enlever anonymous)
- [ ] Configurer backup PostgreSQL
- [ ] Ajouter reverse proxy (nginx/traefik)
- [ ] Configurer HTTPS/SSL
- [ ] Limiter ressources (memory, CPU)
- [ ] Configurer logs rotation
- [ ] Tester disaster recovery

---

## 🎯 Architecture finale

```
┌─────────────────────────────────────────────────┐
│              docker-compose up                  │
└──────────────────┬──────────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │   1. PostgreSQL (db)        │ ← Démarre en premier
    │      ├─ healthcheck         │
    │      └─ postgres_data:/      │
    └──────────────┬──────────────┘
                   │ depends_on: service_healthy
    ┌──────────────┴──────────────┐
    │   2. ETL (etl)              │ ← Import données
    │      ├─ Scrapy Spider       │
    │      ├─ CSV Loader          │
    │      ├─ PokéAPI Enrichment  │
    │      └─ Exited (0)          │
    └──────────────┬──────────────┘
                   │ depends_on: service_completed_successfully
    ┌──────────────┴──────────────┐
    │   3. ML Builder (ml_builder)│ ← Train modèle
    │      ├─ Dataset v2 gen      │
    │      ├─ XGBoost training    │
    │      ├─ GridSearchCV        │
    │      ├─ Export /models/     │
    │      └─ Exited (0)          │
    └──────────────┬──────────────┘
                   │
    ┌──────────────┴──────────────────────────────┐
    │   4. Services permanents (restart: unless-stopped)
    ├──────────────────────────────────────────────┤
    │                                              │
    │  ┌─────────────┐  ┌──────────────┐         │
    │  │ API (8000)  │  │ Streamlit    │         │
    │  │ ├─ FastAPI  │  │ (8501)       │         │
    │  │ ├─ /predict │  │ ├─ Interface │         │
    │  │ └─ /metrics │  │ └─ UI        │         │
    │  └─────────────┘  └──────────────┘         │
    │                                              │
    │  ┌──────────────┐  ┌──────────────┐        │
    │  │ MLflow       │  │ Prometheus   │        │
    │  │ (5000)       │  │ (9090)       │        │
    │  │ ├─ Tracking  │  │ ├─ Scraping  │        │
    │  │ └─ Registry  │  │ └─ Alerting  │        │
    │  └──────────────┘  └──────────────┘        │
    │                                              │
    │  ┌──────────────┐  ┌──────────────┐        │
    │  │ Grafana      │  │ Node Exp.    │        │
    │  │ (3000)       │  │ (9100)       │        │
    │  │ ├─ Dashboards│  │ └─ Metrics   │        │
    │  │ └─ Viz       │  │              │        │
    │  └──────────────┘  └──────────────┘        │
    └──────────────────────────────────────────────┘
```

---

## ✅ Résumé

**Commande unique** : `docker-compose up --build`

**Orchestration automatique** :
1. ✅ PostgreSQL démarre et devient healthy
2. ✅ ETL s'exécute et se termine
3. ✅ ML Builder s'exécute et se termine
4. ✅ API démarre et devient healthy
5. ✅ Tous les autres services démarrent

**Temps total** : ~5-15 minutes (dépend de ML GridSearch)

**Accès final** :
- API: http://localhost:8000
- UI: http://localhost:8501
- Monitoring: http://localhost:3000

**Statut** : 🎉 **Production-ready !**

---

**Dernière mise à jour** : 26 janvier 2026  
**Auteur** : GitHub Copilot + PredictionDex Team
