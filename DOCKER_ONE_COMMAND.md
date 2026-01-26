# Guide de Déploiement - One Command

**Date**: 25 janvier 2026  
**Projet**: Let's Go PredictionDex  
**Objectif**: Déployer TOUT avec une seule commande

---

## 🚀 Déploiement en une commande

### Commande unique (RECOMMANDÉ)

```bash
docker compose up --build
```

**Cette commande lance automatiquement** :

1. ✅ **PostgreSQL** (db) - Base de données
2. ✅ **ETL** (etl) - Import des données Pokemon
3. ✅ **ML Builder** (ml_builder) - Entraînement du modèle
4. ✅ **API** (api) - FastAPI backend
5. ✅ **Streamlit** (streamlit) - Interface utilisateur
6. ✅ **MLflow** (mlflow) - Tracking ML
7. ✅ **Prometheus** (prometheus) - Métriques
8. ✅ **Grafana** (grafana) - Dashboards
9. ✅ **Node Exporter** (node-exporter) - Métriques système

**Durée totale** : ~5-10 minutes (selon ressources)

---

## ⚙️ Configuration automatique

### Ordre d'exécution STRICT ✅

Le docker-compose.yml impose un ordre séquentiel **avec arrêt complet en cas d'échec** :

```
1. 🗄️  BDD (db)
   ↓ healthcheck: pg_isready
   └─ ✅ HEALTHY ou ❌ ARRÊT TOTAL

2. 📥 ETL + 📊 MLFLOW (parallèle)
   ├─ etl
   │  ↓ depends_on: db (healthy)
   │  ↓ restart: "no"
   │  └─ ✅ EXIT 0 ou ❌ ARRÊT TOTAL
   └─ mlflow (optionnel pour déploiement)
      ↓ depends_on: db (healthy)
      ↓ healthcheck: /health
      └─ ✅ HEALTHY

3. 🤖 ML BUILDER (ml_builder)
   ↓ depends_on: etl (completed)
   ↓ restart: "no"
   ↓ DISABLE_MLFLOW_TRACKING=true (simplifie le déploiement)
   └─ ✅ EXIT 0 ou ❌ ARRÊT TOTAL

4. 🚀 API (api)
   ↓ depends_on: db (healthy) + etl + ml_builder (completed)
   ↓ healthcheck: /health
   └─ ✅ HEALTHY ou ❌ ARRÊT TOTAL

5. 🎨 STREAMLIT (streamlit)
   ↓ depends_on: api (healthy)
   └─ ✅ RUNNING

6. 📊 MONITORING
   ├─ prometheus (parallèle avec API)
   ├─ node-exporter (parallèle avec API)
   └─ grafana
      ↓ depends_on: prometheus + api (healthy)
      └─ ✅ RUNNING
```

**⚠️ IMPORTANT** : Si **un seul service échoue**, Docker Compose arrête **toute la chaîne**. Par exemple :
- Si ETL échoue → ML, API, Streamlit ne démarrent JAMAIS
- Si ML échoue → API, Streamlit ne démarrent JAMAIS  
- Si API échoue → Streamlit ne démarre JAMAIS

### Variables d'environnement (fichier `.env`)

Créer un fichier `.env` à la racine si nécessaire :

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password

# Dev mode
DEV_MODE=true

# ML Configuration (optionnel - valeurs par défaut dans docker-compose.yml)
ML_MODE=all
ML_SCENARIO_TYPE=all
ML_TUNE_HYPERPARAMS=true
ML_GRID_TYPE=fast
ML_NUM_RANDOM_SAMPLES=5
ML_MAX_COMBINATIONS=20
```

**Note** : Si le fichier `.env` n'existe pas, les valeurs par défaut du docker-compose.yml sont utilisées.

---

## 📊 Pipeline d'exécution automatique

### 1. Phase Database (30s)
```
db → PostgreSQL démarre
  ↓
healthcheck: pg_isready
  ↓
✅ db ready
```

### 2. Phase ETL (2-3 min)
```
etl → Attend db healthy
  ↓
etl_entrypoint.py
  ↓
etl_pokemon/pipeline.py
  ↓
Import ~200 Pokemon + moves + types
  ↓
✅ etl completed successfully
```

### 3. Phase ML (3-5 min)
```
ml_builder → Attend etl completed
  ↓
ml_entrypoint.py
  ↓
machine_learning/run_machine_learning.py
  ↓
Dataset generation (multi-scenarios)
  ↓
Feature engineering
  ↓
Model training (XGBoost + GridSearch)
  ↓
Export models to ./models/
  ↓
✅ ml_builder completed
```

### 4. Phase Services (30s)
```
api → Attend db + etl
  ↓
api_entrypoint.py
  ↓
FastAPI server (port 8000)
  ↓
healthcheck: /health
  ↓
✅ api healthy

streamlit → Attend api healthy
  ↓
Streamlit server (port 8501)
  ↓
✅ streamlit ready

mlflow → Attend db healthy
  ↓
MLflow server (port 5000)
  ↓
healthcheck: /health
  ↓
✅ mlflow healthy
```

### 5. Phase Monitoring (30s)
```
prometheus → Démarre immédiatement
  ↓
Scraping métriques (port 9090)
  ↓
✅ prometheus ready

grafana → Attend prometheus
  ↓
Dashboards provisionnés (port 3000)
  ↓
✅ grafana ready

node-exporter → Démarre immédiatement
  ↓
Métriques système (port 9100)
  ↓
✅ node-exporter ready
```

---

## 🎯 Services disponibles après déploiement

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | Backend FastAPI |
| **Swagger** | http://localhost:8000/docs | Documentation API |
| **Streamlit** | http://localhost:8501 | Interface utilisateur |
| **MLflow** | http://localhost:5000 | Tracking ML |
| **Grafana** | http://localhost:3000 | Dashboards monitoring |
| **Prometheus** | http://localhost:9090 | Métriques |
| **Node Exporter** | http://localhost:9100/metrics | Métriques système |

**Credentials Grafana** (si nécessaire) :
- Username: `admin`
- Password: `admin`

---

## 🔍 Vérification du déploiement

### Vérifier l'état des services

```bash
# Status de tous les services
docker compose ps

# Logs de tous les services
docker compose logs

# Logs d'un service spécifique
docker compose logs api
docker compose logs etl
docker compose logs ml_builder
```

### Health checks automatiques

```bash
# API
curl http://localhost:8000/health
# Réponse: {"status": "healthy", ...}

# MLflow
curl http://localhost:5000/health
# Réponse: OK

# Prometheus
curl http://localhost:9090/-/healthy
# Réponse: Prometheus is Healthy
```

### Vérifier les modèles ML

```bash
# Lister les modèles exportés
ls -lh models/

# Devrait contenir:
# battle_winner_model_v2.pkl
# battle_winner_metadata_v2.json
# battle_winner_scalers_v2.pkl
```

---

## 🛠️ Commandes utiles

### Démarrage

```bash
# Démarrage complet (build + start)
docker compose up --build

# Démarrage sans rebuild
docker compose up

# Démarrage en arrière-plan
docker compose up -d

# Démarrage d'un service spécifique
docker compose up api
```

### Arrêt

```bash
# Arrêt de tous les services
docker compose down

# Arrêt + suppression des volumes (⚠️ perte de données)
docker compose down -v

# Arrêt d'un service spécifique
docker compose stop api
```

### Rebuild

```bash
# Rebuild tous les services
docker compose build

# Rebuild un service spécifique
docker compose build api

# Rebuild avec no-cache
docker compose build --no-cache
```

### Logs

```bash
# Logs en temps réel
docker compose logs -f

# Logs d'un service
docker compose logs -f api

# 100 dernières lignes
docker compose logs --tail=100

# Logs depuis 10 minutes
docker compose logs --since 10m
```

### Maintenance

```bash
# Redémarrer un service
docker compose restart api

# Exécuter une commande dans un conteneur
docker compose exec api bash
docker compose exec db psql -U letsgo_user -d letsgo_db

# Voir l'utilisation des ressources
docker stats
```

---

## 🐛 Troubleshooting

### Problème : ETL échoue

**Symptôme** :
```
letsgo_etl exited with code 1
```

**Solution** :
```bash
# Vérifier les logs ETL
docker compose logs etl

# Redémarrer ETL
docker compose up etl

# Si nécessaire, rebuild
docker compose build etl
docker compose up etl
```

### Problème : ML Builder échoue

**Symptôme** :
```
letsgo_ml exited with code 1
```

**Solution** :
```bash
# Vérifier les logs ML
docker compose logs ml_builder

# Désactiver GridSearch pour accélérer
# Éditer docker-compose.yml:
# ML_TUNE_HYPERPARAMS: "false"

# Rebuild et restart
docker compose build ml_builder
docker compose up ml_builder
```

### Problème : API ne démarre pas

**Symptôme** :
```
api unhealthy
```

**Solution** :
```bash
# Vérifier les logs
docker compose logs api

# Vérifier que ETL est complété
docker compose ps

# Redémarrer
docker compose restart api
```

### Problème : Port déjà utilisé

**Symptôme** :
```
Error: bind: address already in use
```

**Solution** :
```bash
# Identifier le processus utilisant le port
sudo lsof -i :8000
sudo lsof -i :5000

# Tuer le processus
kill -9 <PID>

# Ou changer le port dans docker-compose.yml
# ports:
#   - "8001:8000"
```

### Problème : Manque de mémoire

**Symptôme** :
```
ml_builder killed (OOMKilled)
```

**Solution** :
```bash
# Augmenter la mémoire Docker (Docker Desktop)
# Settings > Resources > Memory: 8GB minimum

# Ou désactiver GridSearch
# ML_TUNE_HYPERPARAMS: "false"
```

---

## 📦 Volumes persistants

Les données suivantes sont persistées dans des volumes Docker :

| Volume | Contenu | Taille typique |
|--------|---------|----------------|
| `postgres_data` | Base de données | ~50 MB |
| `prometheus_data` | Métriques Prometheus | ~100 MB |
| `grafana_data` | Config Grafana | ~10 MB |
| `mlflow_data` | Artefacts MLflow | ~200 MB |

**Backup des volumes** :

```bash
# Backup PostgreSQL
docker compose exec db pg_dump -U letsgo_user letsgo_db > backup.sql

# Restore
docker compose exec -T db psql -U letsgo_user letsgo_db < backup.sql
```

**Nettoyer les volumes** :

```bash
# ⚠️ ATTENTION : Supprime toutes les données
docker compose down -v

# Nettoyer les volumes orphelins
docker volume prune
```

---

## 🚀 Mode développement

### Développement avec hot-reload

Les volumes sont montés pour permettre le hot-reload :

```yaml
api:
  volumes:
    - ./api_pokemon:/app/api_pokemon  # Hot-reload API
    - ./core:/app/core                 # Hot-reload models

streamlit:
  volumes:
    - ./interface:/app/interface       # Hot-reload Streamlit
```

**Modifications en temps réel** :
1. Éditer `api_pokemon/routes/prediction_route.py`
2. FastAPI recharge automatiquement
3. Tester : `curl http://localhost:8000/docs`

### Développement sans Docker

```bash
# 1. Démarrer uniquement la DB
docker compose up db -d

# 2. Setup environnement local
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# 3. Activer venv
source .venv/bin/activate

# 4. Lancer API en local
cd api_pokemon
uvicorn main:app --reload --port 8000

# 5. Lancer Streamlit en local
cd interface
streamlit run app.py
```

---

## 🎯 Configuration avancée

### Personnaliser le ML Pipeline

Éditer `docker-compose.yml` section `ml_builder` :

```yaml
environment:
  # Skip training if model exists (faster restarts)
  ML_SKIP_IF_EXISTS: "true"  # false to force retrain
  
  # Mode: all, dataset, train, evaluate
  ML_MODE: "train"
  
  # Scenarios: best_move, random_move, all_combinations, all
  ML_SCENARIO_TYPE: "best_move"
  
  # GridSearch: true/false
  ML_TUNE_HYPERPARAMS: "true"
  
  # Grid: fast (8 combos) or extended (243 combos)
  ML_GRID_TYPE: "fast"
  
  # Random sampling
  ML_NUM_RANDOM_SAMPLES: "10"
  
  # Max combinations
  ML_MAX_COMBINATIONS: "50"
```

### Désactiver des services

```bash
# Ne pas lancer Streamlit
docker compose up --scale streamlit=0

# Ne pas lancer Monitoring
docker compose up --scale prometheus=0 --scale grafana=0 --scale node-exporter=0

# Ne pas lancer MLflow
docker compose up --scale mlflow=0
```

---

## ✅ Checklist de déploiement

Avant de lancer `docker compose up --build` :

- [ ] Docker et Docker Compose installés
- [ ] Au moins 8GB RAM disponible
- [ ] Au moins 10GB espace disque
- [ ] Ports libres : 8000, 8501, 5000, 3000, 9090, 9100, 5432
- [ ] Connexion internet (pour pull images)
- [ ] Fichier `.env` créé (optionnel)

Après le démarrage :

- [ ] Tous les services sont `Up` ou `Exited (0)` : `docker compose ps`
- [ ] API health check : `curl localhost:8000/health`
- [ ] Interface accessible : http://localhost:8501
- [ ] Grafana accessible : http://localhost:3000
- [ ] MLflow accessible : http://localhost:5000
- [ ] Modèles exportés : `ls models/battle_winner_*.pkl`

---

## 🎉 Déploiement réussi !

Si tous les services sont opérationnels, le projet est prêt :

✅ **Base de données** remplie avec ~200 Pokemon  
✅ **Modèle ML** entraîné avec accuracy > 80%  
✅ **API** exposant le modèle de prédiction  
✅ **Interface** utilisateur interactive  
✅ **Monitoring** Prometheus + Grafana  
✅ **MLflow** pour tracking des expériences  

**Tester l'application** :
1. Ouvrir http://localhost:8501
2. Aller sur "Compare" (page 2)
3. Sélectionner 2 Pokemon
4. Voir la prédiction du combat

---

**Auteur** : GitHub Copilot + drawile  
**Date** : 25 janvier 2026  
**Version** : 1.0 - Production Ready
