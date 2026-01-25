# 🚀 Quick Start Guide - Let's Go Predictiondex

## ✅ Prérequis

- Docker & Docker Compose installés
- ~10 GB d'espace disque libre
- Connexion internet (pour le scraping initial)

## 📦 Lancement Complet

### Option 1 : Lancement complet (recommandé)

```bash
# 1. Cloner le projet (si pas déjà fait)
cd /mnt/Data/Dev/projet_python_ia_v1/lets-go-predictiondex

# 2. Vérifier que le fichier .env existe
cat .env

# 3. Lancer tous les services
docker compose up --build

# OU en mode détaché (arrière-plan)
docker compose up --build -d
```

### Option 2 : Lancement par étapes

```bash
# 1. Base de données uniquement
docker compose up db -d

# 2. ETL (scraping + transformation)
docker compose up etl --build

# 3. ML Pipeline (génération dataset + training)
docker compose up ml_builder --build

# 4. API + Interface
docker compose up api streamlit --build -d
```

## ⏱️ Temps d'Exécution Estimés

| Service | Durée | Description |
|---------|-------|-------------|
| `db` | ~10s | Démarrage PostgreSQL |
| `etl` | **15-30 min** | Scraping Pokepedia (153 Pokémon + 900 moves) |
| `ml_builder` | **45-60 min** | Génération 898k samples + Training XGBoost |
| `api` | ~5s | Démarrage FastAPI |
| `streamlit` | ~5s | Démarrage interface web |

**Total première exécution** : ~60-90 minutes

## 🔍 Vérification des Services

### Vérifier l'état des conteneurs

```bash
docker compose ps
```

**Sortie attendue :**
```
NAME                STATUS          PORTS
letsgo_postgres     Up (healthy)    0.0.0.0:5432->5432/tcp
letsgo_etl          Exited (0)      -
letsgo_ml           Exited (0)      -
letsgo_api          Up (healthy)    0.0.0.0:8000->8000/tcp
letsgo_streamlit    Up              0.0.0.0:8501->8501/tcp
```

### Vérifier les logs

```bash
# Tous les services
docker compose logs

# Service spécifique
docker compose logs ml_builder
docker compose logs api

# Suivre en temps réel
docker compose logs -f ml_builder
```

## 🌐 Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| **API FastAPI** | http://localhost:8000 | API REST predictions |
| **API Docs** | http://localhost:8000/docs | Documentation Swagger interactive |
| **Streamlit** | http://localhost:8501 | Interface utilisateur web |
| **PostgreSQL** | localhost:5432 | Base de données (credentials dans .env) |

## 🧪 Tests Manuels

### Test API avec curl

```bash
# Health check
curl http://localhost:8000/health

# Liste des Pokémon
curl http://localhost:8000/pokemon/ | jq .

# Prédiction best move
curl -X POST http://localhost:8000/predict/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a": {
      "name": "Pikachu",
      "moves": ["Tonnerre", "Fatal-Foudre", "Vive-Attaque", "Éclair"]
    },
    "pokemon_b": {
      "name": "Bulbizarre",
      "moves": ["Fouet Lianes", "Lance-Soleil", "Tranch-Herbe", "Charge"]
    }
  }' | jq .
```

### Tests ML automatisés (hors Docker)

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer tous les tests ML (50 tests)
pytest tests/ml/ -v

# Tests avec couverture
pytest tests/ml/ --cov=machine_learning --cov-report=html
```

## 🛑 Arrêt des Services

```bash
# Arrêt gracieux
docker compose down

# Arrêt + suppression des volumes (⚠️ supprime la DB)
docker compose down -v

# Arrêt + suppression images
docker compose down --rmi all
```

## 🔧 Configuration Avancée

### Modifier les paramètres ML

Éditer `docker-compose.yml` :

```yaml
ml_builder:
  environment:
    ML_MODE: "all"                    # dataset, train, evaluate, all
    ML_SCENARIO_TYPE: "all"           # best_move, random_move, all_combinations, all
    ML_TUNE_HYPERPARAMS: "true"       # Active GridSearchCV
    ML_GRID_TYPE: "fast"              # fast (8 combos) ou extended (243 combos)
    ML_NUM_RANDOM_SAMPLES: "5"        # Échantillons random_move
    ML_MAX_COMBINATIONS: "20"         # Max combos pour all_combinations (debug)
```

### Mode production (dataset complet)

```yaml
ml_builder:
  environment:
    ML_NUM_RANDOM_SAMPLES: "100"      # 100 samples random_move
    ML_MAX_COMBINATIONS: "999999"     # Toutes les combinaisons
    ML_GRID_TYPE: "extended"          # Recherche étendue hyperparamètres
```

⚠️ **Attention** : Mode production = plusieurs heures de calcul

## 📊 Validation du Modèle

### Vérifier les fichiers générés

```bash
# Modèles ML
ls -lh models/
# battle_winner_model_v2.pkl (9.7 MB)
# battle_winner_scalers_v2.pkl (11 KB)
# battle_winner_metadata_v2.json (7 KB)

# Dataset v2
ls -lh data/ml/battle_winner_v2/features/
# X_train.parquet
# X_test.parquet
# y_train.parquet
# y_test.parquet
```

### Vérifier les métriques du modèle

```bash
# Lire les metadata JSON
cat models/battle_winner_metadata_v2.json | jq '.metrics'
```

**Sortie attendue :**
```json
{
  "train_accuracy": 0.9644,
  "test_accuracy": 0.9559,
  "test_precision": 0.9585,
  "test_recall": 0.9601,
  "test_f1": 0.9593,
  "test_roc_auc": 0.9937
}
```

## 🐛 Dépannage

### Erreur : Port déjà utilisé

```bash
# Libérer le port 5432 (PostgreSQL)
sudo lsof -i :5432
sudo kill -9 <PID>

# Libérer le port 8000 (API)
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Erreur : ml_builder échoue

```bash
# Vérifier les logs détaillés
docker compose logs ml_builder | tail -100

# Vérifier que les dépendances sont installées
docker compose exec ml_builder pip list | grep -E "pandas|numpy|xgboost"
```

### Erreur : Base de données non accessible

```bash
# Vérifier la santé de la DB
docker compose exec db pg_isready -U letsgo_user -d letsgo_db

# Se connecter à la DB
docker compose exec db psql -U letsgo_user -d letsgo_db

# Compter les Pokémon
SELECT COUNT(*) FROM pokemon;
```

### Redémarrage complet propre

```bash
# Arrêt complet
docker compose down -v

# Nettoyer les images
docker compose down --rmi all

# Nettoyer les volumes
docker volume prune

# Rebuild complet
docker compose up --build
```

## 📚 Documentation Complète

- **Récapitulatif session** : [CHANGELOG_SESSION_25_01_2026.md](CHANGELOG_SESSION_25_01_2026.md)
- **Architecture ML** : [machine_learning/README.md](machine_learning/README.md)
- **API Documentation** : http://localhost:8000/docs (après démarrage)
- **Tests ML** : [tests/ml/](tests/ml/)

## 🎯 Vérifications Finales

✅ Checklist avant production :

```bash
# 1. Services lancés
docker compose ps | grep "Up"

# 2. API répond
curl http://localhost:8000/health

# 3. Modèle ML existe
ls -lh models/battle_winner_model_v2.pkl

# 4. Tests ML passent (hors Docker)
source .venv/bin/activate && pytest tests/ml/ -q
# ======== 50 passed in 26.79s ========
```

Si tous les checks passent : **Projet prêt pour production** 🚀

---

**Version** : v2.0  
**Date** : 25 Janvier 2026  
**Status** : Production-Ready ✅
