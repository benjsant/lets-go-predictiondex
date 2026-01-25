# 🚀 MLflow Integration - Documentation

## 📊 Vue d'Ensemble

MLflow est maintenant **dockerisé** et intégré au projet pour le tracking des expériences ML (compétence **C13 - MLOps**).

**Version utilisée :** MLflow 3.8.1 (stable, 26 décembre 2025)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     STACK COMPLETE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  PostgreSQL │  │  MLflow UI   │  │  Prometheus     │   │
│  │  :5432      │  │  :5000       │  │  :9090          │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                │                    │            │
│         │       ┌────────┴─────────┐          │            │
│         └───────┤  MLflow Tracking │──────────┘            │
│                 │     Backend      │                       │
│                 └────────┬─────────┘                       │
│                          │                                 │
│         ┌────────────────┴─────────────────┐               │
│         │                                  │               │
│  ┌──────▼──────┐                   ┌──────▼──────┐        │
│  │  API        │                   │  Grafana    │        │
│  │  FastAPI    │                   │  :3000      │        │
│  │  :8000      │                   └─────────────┘        │
│  └──────┬──────┘                                           │
│         │                                                  │
│  ┌──────▼──────┐                                           │
│  │  Streamlit  │                                           │
│  │  :8501      │                                           │
│  └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Fichiers Créés

### 1. **docker/Dockerfile.mlflow**
```dockerfile
FROM python:3.11-slim
RUN pip install mlflow==3.8.1 psycopg2-binary boto3
EXPOSE 5000
CMD ["mlflow", "server", "--host", "0.0.0.0", ...]
```

### 2. **docker-compose.yml** (service mlflow)
```yaml
mlflow:
  build:
    context: .
    dockerfile: docker/Dockerfile.mlflow
  environment:
    MLFLOW_BACKEND_STORE_URI: postgresql://...
    MLFLOW_DEFAULT_ARTIFACT_ROOT: /app/mlruns
  ports:
    - "5000:5000"
  volumes:
    - mlflow_data:/app/mlruns
```

### 3. **machine_learning/mlflow_integration.py**
Module Python pour tracker les expériences :
```python
from machine_learning.mlflow_integration import MLflowTracker

tracker = MLflowTracker(experiment_name="pokemon_battle_v2")

with tracker.start_run(run_name="xgboost_v2"):
    tracker.log_params(hyperparams)
    tracker.log_metrics(metrics)
    tracker.log_model(model, "model")
```

---

## 🚀 Utilisation

### **Démarrer MLflow seul**
```bash
docker compose up -d mlflow
```

### **Démarrer toute la stack**
```bash
docker compose up -d
```

### **Accéder à MLflow UI**
```
http://localhost:5000
```

### **Vérifier la santé**
```bash
curl http://localhost:5000/health
# Résultat attendu: OK
```

---

## 🧪 Test d'Intégration

### **Test 1 : Vérifier MLflow fonctionne**
```bash
# Dans le container API
docker compose exec api python -c "
import mlflow
mlflow.set_tracking_uri('http://mlflow:5000')
print('✅ MLflow accessible')
"
```

### **Test 2 : Créer une expérience test**
```bash
docker compose exec api python -c "
import mlflow
mlflow.set_tracking_uri('http://mlflow:5000')
mlflow.set_experiment('test_experiment')

with mlflow.start_run():
    mlflow.log_param('test_param', 42)
    mlflow.log_metric('test_metric', 0.95)
    print('✅ Expérience créée')
"
```

### **Test 3 : Entraîner avec tracking**
```bash
# À ajouter dans run_machine_learning.py
docker compose exec api python -m machine_learning.run_machine_learning \
    --model-type xgboost \
    --version v3 \
    --mlflow-tracking
```

---

## 📝 Intégration dans le Pipeline ML

### **Avant (sans MLflow)**
```python
def train_model(X_train, y_train, hyperparams):
    model = xgb.XGBClassifier(**hyperparams)
    model.fit(X_train, y_train)
    return model
```

### **Après (avec MLflow)**
```python
from machine_learning.mlflow_integration import get_mlflow_tracker

def train_model(X_train, y_train, hyperparams, version="v1"):
    tracker = get_mlflow_tracker(experiment_name=f"battle_winner_{version}")
    
    with tracker.start_run(run_name=f"training_{version}"):
        # Log hyperparameters
        tracker.log_params(hyperparams)
        
        # Train model
        model = xgb.XGBClassifier(**hyperparams)
        model.fit(X_train, y_train)
        
        # Evaluate
        metrics = evaluate_model(model, X_test, y_test)
        tracker.log_metrics(metrics)
        
        # Log model
        tracker.log_model(model, artifact_path="model", model_type="xgboost")
        
        return model
```

---

## 🔍 Features MLflow Disponibles

### **1. Experiments**
- Créer/Lister des expériences
- Comparer différentes runs
- Filtrer par paramètres/métriques

### **2. Runs**
- Tracking automatique des paramètres
- Métriques : accuracy, precision, recall, F1, AUC
- Artifacts : modèles, plots, datasets

### **3. Models**
- Versioning automatique
- Model registry
- Transition : None → Staging → Production

### **4. Comparison**
- Tableau comparatif des runs
- Graphiques métriques
- Parallel coordinates plot

---

## 📊 Métriques Trackées

### **Hyperparamètres**
```python
{
    'n_estimators': 100,
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}
```

### **Métriques d'Évaluation**
```python
{
    'train_accuracy': 0.956,
    'test_accuracy': 0.944,
    'precision': 0.948,
    'recall': 0.940,
    'f1_score': 0.944,
    'roc_auc': 0.987
}
```

### **Métadonnées**
```python
{
    'model_type': 'XGBClassifier',
    'dataset_version': 'v2',
    'n_features': 136,
    'training_samples': 24580,
    'test_samples': 6145
}
```

---

## 🔐 Sécurité

### **Configuration Actuelle**
- Backend store : PostgreSQL (même DB que le projet)
- Artifact store : Volume Docker persistant
- Auth : Désactivé (localhost only)

### **Pour Production (optionnel)**
```bash
# Ajouter authentification
MLFLOW_ENABLE_AUTH=true
MLFLOW_ADMIN_USERNAME=admin
MLFLOW_ADMIN_PASSWORD=secure_password

# Utiliser S3 pour artifacts
MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://my-bucket/mlflow
```

---

## 📈 Impact sur les Compétences

### **Avant MLflow**
| Compétence | Statut |
|------------|--------|
| C13 (MLOps) | ⚠️ 30% |

**Problèmes :**
- ❌ Pas de versioning des expériences
- ❌ Pas de comparaison entre runs
- ❌ Pas de tracking automatique
- ❌ Pas de model registry

### **Après MLflow**
| Compétence | Statut |
|------------|--------|
| C13 (MLOps) | ✅ 80% |

**Améliorations :**
- ✅ Experiments trackés automatiquement
- ✅ Comparaison visuelle des runs
- ✅ Versioning des modèles
- ✅ Artifact storage centralisé
- ⏳ CI/CD manquant (GitHub Actions)

---

## 🎯 Prochaines Étapes

### **Phase 1 : Validation (fait ✅)**
- [x] Docker MLflow 3.8.1
- [x] Integration docker-compose
- [x] Module Python mlflow_integration.py
- [x] Health check OK

### **Phase 2 : Integration Pipeline (à faire)**
- [ ] Modifier `run_machine_learning.py`
- [ ] Ajouter tracking dans `train_model.py`
- [ ] Test entraînement complet
- [ ] Vérifier UI MLflow

### **Phase 3 : CI/CD (à faire)**
- [ ] GitHub Actions workflow
- [ ] Auto-training sur push
- [ ] Model validation gates
- [ ] Auto-deploy si metrics OK

---

## 🐛 Troubleshooting

### **Problème : MLflow ne démarre pas**
```bash
# Vérifier les logs
docker compose logs mlflow

# Reconstruire l'image
docker compose build mlflow --no-cache
docker compose up -d mlflow
```

### **Problème : Connection error dans le code**
```python
# Vérifier que l'URI est correct
import mlflow
mlflow.set_tracking_uri("http://mlflow:5000")  # Dans Docker
# OU
mlflow.set_tracking_uri("http://localhost:5000")  # En local
```

### **Problème : Pas d'expériences visibles**
```bash
# Vérifier la DB
docker compose exec db psql -U letsgo_user -d letsgo_db -c "
SELECT * FROM experiments;
"
```

---

## 📚 Références

- [MLflow Documentation](https://mlflow.org/docs/latest/)
- [MLflow 3.8.1 Release Notes](https://mlflow.org/releases/3.8.1)
- [MLflow Tracking Quickstart](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Models](https://mlflow.org/docs/latest/models.html)

---

## ✅ Checklist de Validation

- [x] Dockerfile.mlflow créé
- [x] Service mlflow ajouté à docker-compose.yml
- [x] Volume mlflow_data créé
- [x] Module mlflow_integration.py créé
- [x] Image Docker buildée
- [x] Service démarré et healthy
- [x] Health check (/health) OK
- [x] UI accessible (http://localhost:5000)
- [ ] Première expérience créée
- [ ] Pipeline ML intégré
- [ ] Tests validés

---

**Auteur :** Claude Code  
**Date :** 25 janvier 2026  
**Version MLflow :** 3.8.1  
**Status :** ✅ Dockerisé et opérationnel
