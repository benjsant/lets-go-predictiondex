# MLflow Model Registry - Guide d'Utilisation

## 📋 Vue d'ensemble

Le **MLflow Model Registry** est maintenant intégré dans le projet PredictionDex pour :
- ✅ **Centraliser** les modèles ML entraînés
- ✅ **Versionner** automatiquement chaque modèle
- ✅ **Promouvoir** les meilleurs modèles en Production
- ✅ **Charger** les modèles depuis l'API sans fichiers locaux

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  ML Training    │─────▶│  MLflow Registry │─────▶│  API Service    │
│  (run_machine_  │      │  (versioning +   │      │  (load from     │
│   learning.py,  │      │   promotion)     │      │   registry)     │
│   train_model)  │      └──────────────────┘      └─────────────────┘
└─────────────────┘              │
                                 │
                         ┌───────▼─────────┐
                         │   MLflow UI     │
                         │ (http://:5000)  │
                         └─────────────────┘
```

## 🚀 Fonctionnalités Implémentées

### 1. **Enregistrement Automatique des Modèles**
Chaque entraînement enregistre automatiquement le modèle dans le registry :

```python
# machine_learning/run_machine_learning.py
version_number = tracker.register_model(
    model_name="battle_winner_predictor",
    description=f"{model_name} - Accuracy: {accuracy:.4f}"
)
```

### 2. **Promotion Automatique en Production**
Les modèles avec `accuracy >= 0.85` sont automatiquement promus :

```python
if version_number and metrics['test_accuracy'] >= 0.85:
    tracker.promote_to_production("battle_winner_predictor", version_number)
    print("✅ Model promoted to Production")
```

### 3. **Chargement depuis l'API**
L'API charge automatiquement le modèle en Production depuis le registry :

```python
# api_pokemon/services/prediction_service.py
model_bundle = load_model_from_registry(
    model_name="battle_winner_predictor",
    stage="Production"  # or "Staging"
)
```

### 4. **Comparaison des Versions**
Comparer toutes les versions d'un modèle :

```python
df = tracker.compare_models("battle_winner_predictor")
print(df)
```

Output example:
```
version  stage       accuracy  f1_score  roc_auc   created_at
3        Production  0.8723    0.8654    0.9234    2025-01-25 14:30
2        Staging     0.8512    0.8401    0.9102    2025-01-25 12:15
1        Archived    0.8203    0.8123    0.8956    2025-01-24 18:45
```

## 📦 Artifacts Enregistrés

Pour chaque modèle, les artifacts suivants sont sauvegardés :
1. **model/** : Le modèle XGBoost ou RandomForest
2. **scalers.pkl** : Les StandardScalers pour la normalisation
3. **metadata.pkl** : Les feature_columns et métadonnées

Ces artifacts sont automatiquement téléchargés lors du chargement depuis l'API.

## 🛠️ Utilisation

### Entraîner et Enregistrer un Modèle

```bash
# Option 1 : Pipeline complet (run_machine_learning.py)
python machine_learning/run_machine_learning.py \
    --mode all \
    --model xgboost \
    --version v2

# Option 2 : Script standalone (train_model.py)
python machine_learning/train_model.py \
    --use-gridsearch \
    --grid-type fast \
    --version v3
```

**Résultat** :
- ✅ Modèle entraîné et exporté localement
- ✅ Modèle loggé dans MLflow avec run metrics
- ✅ Modèle enregistré dans le Model Registry (version auto-incrémentée)
- ✅ Promotion automatique en Production si accuracy >= 0.85

### Désactiver le Registry (pour tests)

```bash
# run_machine_learning.py : utilise --no-mlflow n'existe pas (toujours activé)
# train_model.py : 
python machine_learning/train_model.py --no-mlflow
```

### Charger depuis l'API

L'API charge automatiquement depuis le registry avec variables d'environnement :

```bash
# Dans docker-compose.yml ou .env
USE_MLFLOW_REGISTRY=true          # Enable registry loading (default: true)
MLFLOW_MODEL_NAME=battle_winner_predictor  # Model name (default)
MLFLOW_MODEL_STAGE=Production      # Stage to load (default: Production)
MLFLOW_TRACKING_URI=http://mlflow:5000
```

**Comportement** :
1. Essaie de charger depuis le registry (stage Production)
2. Fallback sur les fichiers locaux si échec ou registry désactivé
3. Logs clairs pour diagnostiquer

### Interface MLflow UI

Accéder à l'interface web MLflow :

```bash
# URL locale (après docker compose up)
http://localhost:5000

# Naviguer vers :
# 1. "Experiments" → Voir les runs et métriques
# 2. "Models" → Voir le Model Registry
#    - battle_winner_predictor
#      - Version 1 (Archived)
#      - Version 2 (Staging)
#      - Version 3 (Production) ← Active
```

**Actions disponibles** :
- 📊 Comparer les runs (métriques, hyperparamètres)
- 🏷️ Transition manuelle des stages (Staging → Production)
- 📝 Ajouter des descriptions et tags
- 📥 Télécharger les artifacts

## 🔄 Workflow Complet

### Scénario 1 : Entraînement et Déploiement Automatique

```bash
# 1. Entraîner un nouveau modèle
python machine_learning/train_model.py --use-gridsearch --version v4

# Output :
# ✅ Model trained and exported
# ✅ Logged to MLflow (run: train_model_v4_20250125_1430)
# ✅ Registered as version 4 in Model Registry
# 🎯 Model meets quality threshold (accuracy >= 0.85)
# ✅ Model promoted to Production stage

# 2. L'API recharge automatiquement le nouveau modèle
# (au prochain appel de prédiction, load() sera rappelé)
```

### Scénario 2 : Comparaison et Promotion Manuelle

```python
from machine_learning.mlflow_integration import MLflowTracker

tracker = MLflowTracker(experiment_name="battle_winner_production")
tracker.start_run(run_name="model_comparison")

# Comparer toutes les versions
df = tracker.compare_models("battle_winner_predictor")
print(df)

# Promouvoir manuellement la version 5
tracker.promote_to_production("battle_winner_predictor", version=5)
tracker.end_run()
```

### Scénario 3 : Rollback en cas de Problème

```python
# Si le modèle en Production pose problème, revenir à la version précédente
tracker.promote_to_production("battle_winner_predictor", version=2)

# L'API rechargera automatiquement la version 2 au prochain appel
```

## 🧪 Tests

### Test 1 : Enregistrement et Promotion

```bash
# Test avec train_model.py
pytest tests/mlflow/test_model_registry.py::test_register_and_promote -v

# Vérifie :
# - Enregistrement correct dans le registry
# - Promotion automatique si seuil atteint
# - Artifacts (scalers, metadata) présents
```

### Test 2 : Chargement depuis l'API

```bash
# Test end-to-end : entraînement → registry → API load
pytest tests/integration/test_mlflow_to_api.py::test_e2e_mlflow_to_api -v

# Vérifie :
# 1. Entraînement et enregistrement
# 2. Chargement depuis l'API
# 3. Prédiction fonctionnelle
```

### Test 3 : Fallback sur Fichiers Locaux

```bash
# Désactiver le registry et vérifier fallback
USE_MLFLOW_REGISTRY=false pytest tests/api/test_prediction_service.py -v

# Vérifie :
# - API charge depuis models/battle_winner_model_v2.pkl
# - Pas d'erreur si MLflow indisponible
```

## 📊 Métriques et Seuils

### Seuils de Promotion Automatique

```python
# Dans run_machine_learning.py et train_model.py
PROMOTION_THRESHOLD = 0.85  # accuracy >= 85%

# Modifier le seuil :
if metrics['test_accuracy'] >= 0.90:  # Seuil plus strict
    tracker.promote_to_production(model_name, version)
```

### Métriques Loggées

Pour chaque modèle :
- `train_accuracy` : Précision sur le jeu d'entraînement
- `test_accuracy` : Précision sur le jeu de test ⭐ (critère de promotion)
- `test_precision` : Précision (true positives / predicted positives)
- `test_recall` : Rappel (true positives / actual positives)
- `test_f1` : F1-score (harmonic mean of precision and recall)
- `test_roc_auc` : Area Under ROC Curve
- `overfitting` : train_accuracy - test_accuracy

## 🐛 Troubleshooting

### Erreur : "No model found in stage 'Production'"

**Cause** : Aucun modèle n'a été promu en Production
**Solution** :
```bash
# Option 1 : Entraîner un nouveau modèle (auto-promote si accuracy >= 0.85)
python machine_learning/train_model.py --use-gridsearch

# Option 2 : Promouvoir manuellement depuis MLflow UI
# Models → battle_winner_predictor → Version X → Transition to Production

# Option 3 : Utiliser Staging temporairement
export MLFLOW_MODEL_STAGE=Staging
```

### Erreur : "MLflow not available"

**Cause** : MLflow service non démarré ou inaccessible
**Solution** :
```bash
# Vérifier que MLflow tourne
docker compose ps mlflow

# Vérifier la connexion
curl http://localhost:5000/health

# Fallback : API utilise fichiers locaux automatiquement
# (vérifier logs API : "⚠️ MLflow not available, using local files")
```

### Modèle Non Promu Automatiquement

**Cause** : accuracy < 0.85
**Solution** :
```bash
# Voir les logs d'entraînement :
# "⚠️ Model registered but not promoted (accuracy < 0.85)"

# Option 1 : Améliorer le modèle (plus de données, meilleur grid)
python machine_learning/run_machine_learning.py \
    --mode all \
    --tune-hyperparams

# Option 2 : Abaisser le seuil temporairement (dev only)
# Modifier run_machine_learning.py ligne ~1076 :
if metrics['test_accuracy'] >= 0.80:  # Seuil plus bas

# Option 3 : Promotion manuelle
# MLflow UI → Models → battle_winner_predictor → Transition to Production
```

## 🌍 Variables d'Environnement

### API Service

```bash
# .env ou docker-compose.yml
USE_MLFLOW_REGISTRY=true           # Enable/disable registry loading
MLFLOW_MODEL_NAME=battle_winner_predictor
MLFLOW_MODEL_STAGE=Production      # Production, Staging, Archived
MLFLOW_TRACKING_URI=http://mlflow:5000
```

### ML Training

```bash
# .env
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_EXPERIMENT_NAME=battle_winner_production
```

## 📚 Références

### Fonctions Principales

**mlflow_integration.py** :
- `register_model(model_name, description)` : Enregistre le modèle du run actif
- `promote_to_production(model_name, version)` : Promouvoir en Production
- `promote_best_model(model_name, metric, threshold)` : Promotion automatique
- `compare_models(model_name)` : Comparer toutes les versions
- `load_model_from_registry(model_name, stage, version)` : Charger un modèle

**prediction_service.py** :
- `PredictionModel.load()` : Charge depuis registry avec fallback local

### Documentation MLflow Officielle

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)

---

## ✅ Résumé

Le MLflow Model Registry est maintenant intégré et permet :

1. **Entraînement** → Enregistrement automatique avec versioning
2. **Promotion** → Automatique si accuracy >= 0.85, sinon manuelle
3. **Chargement API** → Depuis registry (Production stage) avec fallback local
4. **Monitoring** → MLflow UI pour comparer et gérer les versions
5. **Rollback** → Revenir à une version précédente en 1 clic

**Prochaines étapes** : Tests complets + docker compose up 🚀
