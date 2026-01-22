# Plan d'Action E3 - Compétences Restantes

**Date:** 2026-01-22
**Projet:** Let's Go PredictionDex
**Branche:** remodif_architecture

---

## État des Compétences E3

### ✅ Compétences VALIDÉES

#### C9. Développer une API REST exposant un modèle d'IA
**Statut:** ✅ VALIDÉ
**Preuves:**
- FastAPI REST API fonctionnelle (`api_pokemon/main.py`)
- Endpoint `/predict/battle` expose le modèle XGBoost
- Documentation Swagger disponible à `/docs`
- Service de prédiction isolé (`api_pokemon/services/prediction_service.py`)
- Standards de qualité: Pydantic validation, error handling, logging

**Fichiers clés:**
- `api_pokemon/routes/prediction.py` (endpoint)
- `api_pokemon/services/prediction_service.py` (business logic)
- `api_pokemon/schemas/prediction.py` (validation schemas)

---

#### C10. Intégrer l'API d'un modèle dans une application
**Statut:** ✅ VALIDÉ
**Preuves:**
- Streamlit interface (`interface/app.py` + 7 pages)
- Service client API (`interface/services/api_client.py`)
- Pages interactives: Compare, Combat Classique, Quiz Types
- Respect des normes d'accessibilité (Streamlit accessibility features)
- Documentation technique de l'API utilisée (`API_EXAMPLES.md`)

**Fichiers clés:**
- `interface/services/api_client.py` (HTTP client)
- `interface/services/prediction_service.py` (Streamlit-side prediction logic)
- `interface/pages/2_Compare.py` (battle prediction UI)
- `interface/pages/5_Combat_Classique.py` (battle simulator)

---

### ⚠️ Compétences PARTIELLEMENT VALIDÉES (nécessitent améliorations)

#### C11. Monitorer un modèle d'IA
**Statut:** ⚠️ PARTIEL (20% complété)

**Ce qui existe:**
- ✅ Métriques de base exportées (`models/battle_winner_metadata.pkl`)
  - Accuracy: 94.24%
  - Features count: 133
  - Train/test split: 80/20
- ✅ Tests d'inférence (`machine_learning/test_model_inference.py`)
- ✅ Docker health checks basiques

**Ce qui manque:**
- ❌ **Prometheus** pour collecte de métriques temps réel
- ❌ **Grafana** pour dashboards de monitoring
- ❌ Collecte de métriques API (latency, request count, error rate)
- ❌ Alerting sur dégradation de performance
- ❌ Détection de drift des données
- ❌ Logs structurés (actuellement: print statements)

**Actions requises:** Voir section "Actions à mener" ci-dessous

---

#### C12. Programmer les tests automatisés d'un modèle d'IA
**Statut:** ⚠️ PARTIEL (40% complété)

**Ce qui existe:**
- ✅ Tests d'inférence de modèle (`machine_learning/test_model_inference.py`)
- ✅ Validation des données d'entrée (Pydantic schemas)
- ✅ Tests API endpoints (`test_prediction_api.py`, `api_pokemon/test_prediction_endpoint.py`)
- ✅ Tests unitaires ETL (`etl_pokemon/tests/`)

**Ce qui manque:**
- ❌ Tests de validation du dataset (quality checks)
- ❌ Tests de préparation des données (preprocessing pipeline tests)
- ❌ Tests d'entraînement automatisés (training pipeline tests)
- ❌ Tests d'évaluation automatisés (metrics validation)
- ❌ Tests de régression du modèle (performance degradation checks)
- ❌ CI/CD pipeline pour exécuter les tests automatiquement

**Actions requises:** Voir section "Actions à mener" ci-dessous

---

#### C13. Créer une chaîne de livraison continue MLOps
**Statut:** ⚠️ PARTIEL (30% complété)

**Ce qui existe:**
- ✅ Docker multi-container orchestration
- ✅ Déploiement automatisé (docker-compose up)
- ✅ Gestion des dépendances (requirements.txt)
- ✅ Séparation environnements (dev/prod via .env)

**Ce qui manque:**
- ❌ **Pipeline CI/CD** (GitHub Actions / GitLab CI)
- ❌ **MLflow** pour versioning et tracking des modèles
- ❌ Tests automatisés dans pipeline CI
- ❌ Packaging du modèle (containerisation séparée)
- ❌ Déploiement automatique sur validation
- ❌ Rollback automatique en cas d'échec
- ❌ Configuration MLOps (model registry, artifact store)

**Actions requises:** Voir section "Actions à mener" ci-dessous

---

## Fichiers Obsolètes Identifiés

### À SUPPRIMER (Cleanup)

**Modèles ML obsolètes** (31 MB total):
```bash
models/battle_winner_rf_v1.pkl              # 28 MB - OLD: Random Forest model
models/random_forest_v1.pkl                 # OLD: Unused RF variant
models/random_forest_no_multiplier_v1.pkl   # OLD: Unused RF variant
models/battle_winner_xgb_v1.pkl             # DUPLICATE: Same as battle_winner_model_v1.pkl
models/model_metadata.pkl                   # OLD: Uses deprecated joblib format
```

**Fichiers de dataset inutilisés:**
```bash
machine_learning/build_classification_dataset.py  # UNUSED: Different target (move effectiveness)
```

### À ARCHIVER (Consolidation documentation)

**27 fichiers .md** dans la racine (garder les essentiels, archiver le reste):

**GARDER (Documentation active):**
- `README.md` - Vue d'ensemble du projet
- `E1_DOCUMENTATION.md` - Compétences E1 validées
- `E3_PLAN_FINAL.md` - Plan E3 (remplacer par ce nouveau document)
- `ML_MODEL_DOCUMENTATION.md` - Documentation du modèle ML
- `API_EXAMPLES.md` - Exemples d'utilisation API

**ARCHIVER vers `/docs/archive/`:**
- `BUGFIXES_APPLIED.md`
- `FINAL_ADJUSTMENTS.md`
- `DOCKER_TEST_REPORT.md`
- `COMPARE_PAGES_SIMPLIFICATION.md`
- `CORRECTIONS_MODELE_V1.md`
- `OPPONENT_MOVE_SELECTION_ANALYSIS.md`
- `POKEMON_DETAIL_FIXES.md`
- `POKEMON_THEME.md`
- `STREAMLIT_*.md` (5 fichiers)
- `API_AND_MODEL_ANALYSIS.md`
- `HANDOFF_CONTEXT.md`
- `MODEL_ACCURACY_EXPLANATION.md`

---

## Actions à Mener (Par Ordre de Priorité)

### 🔴 PRIORITÉ 1: Script ML Unifié (C12, C13)

**Objectif:** Créer un script `run_machine_learning.py` qui orchestre TOUT le pipeline ML.

**Étapes:**
1. **Dataset Preparation**
   - Load data from DB
   - Generate Pokemon matchups
   - Feature engineering
   - Train/test split
   - Export processed datasets

2. **Model Training**
   - Load preprocessed data
   - Train XGBoost model
   - Hyperparameter tuning (optionnel)
   - Cross-validation

3. **Model Evaluation**
   - Calculate metrics (accuracy, precision, recall, F1)
   - Generate confusion matrix
   - ROC curve analysis
   - Feature importance

4. **Model Selection**
   - Compare multiple models (XGBoost, RandomForest, etc.)
   - Select best model based on metrics
   - Export best model artifacts

5. **Model Export**
   - Save model to `/models/`
   - Save scalers to `/models/`
   - Save metadata to `/models/`
   - Update MLflow tracking (si implémenté)

**Fichier à créer:**
```
machine_learning/run_machine_learning.py
```

**Commande d'exécution:**
```bash
python machine_learning/run_machine_learning.py --mode=all
python machine_learning/run_machine_learning.py --mode=dataset
python machine_learning/run_machine_learning.py --mode=train
python machine_learning/run_machine_learning.py --mode=evaluate
```

**Validation:** Compétences C12 (tests automatisés intégrés)

---

### 🔴 PRIORITÉ 2: Tests Automatisés Complets (C12)

**Objectif:** Valider TOUS les aspects du pipeline ML avec tests automatisés.

#### A. Tests de Dataset
**Fichier:** `machine_learning/tests/test_dataset.py`

**Tests requis:**
- ✅ Validation de la structure du dataset
- ✅ Validation des types de données
- ✅ Vérification de l'absence de valeurs nulles
- ✅ Validation des ranges de valeurs (stats, multipliers)
- ✅ Validation de la distribution des classes (équilibre winner A/B)
- ✅ Validation de la cohérence des features (STAB, type multipliers)

#### B. Tests de Preprocessing
**Fichier:** `machine_learning/tests/test_preprocessing.py`

**Tests requis:**
- ✅ Test de one-hot encoding
- ✅ Test de normalization (StandardScaler)
- ✅ Test de feature engineering (derived features)
- ✅ Test de train/test split (80/20)
- ✅ Test de cohérence des transformations

#### C. Tests d'Entraînement
**Fichier:** `machine_learning/tests/test_training.py`

**Tests requis:**
- ✅ Test d'entraînement du modèle (reproductibilité)
- ✅ Test de convergence (pas d'overfitting)
- ✅ Test de métriques minimales (accuracy >= 90%)
- ✅ Test de sauvegarde des artifacts

#### D. Tests d'Évaluation
**Fichier:** `machine_learning/tests/test_evaluation.py`

**Tests requis:**
- ✅ Test de prédiction sur données de test
- ✅ Test de calcul des métriques
- ✅ Test de génération des rapports (confusion matrix)
- ✅ Test de feature importance

#### E. Tests de Régression
**Fichier:** `machine_learning/tests/test_regression.py`

**Tests requis:**
- ✅ Test que le nouveau modèle ne dégrade PAS les performances
- ✅ Test de non-régression sur dataset fixe
- ✅ Test de stabilité des prédictions

**Validation:** Compétence C12 complète

---

### 🔴 PRIORITÉ 3: Monitoring avec Prometheus + Grafana (C11)

**Objectif:** Monitorer le modèle en temps réel en production.

#### A. Intégration Prometheus

**Fichier:** `api_pokemon/monitoring/metrics.py`

**Métriques à collecter:**
- `api_requests_total` (Counter) - Nombre total de requêtes
- `api_request_duration_seconds` (Histogram) - Latence des requêtes
- `api_errors_total` (Counter) - Nombre d'erreurs
- `model_predictions_total` (Counter) - Nombre de prédictions
- `model_prediction_duration_seconds` (Histogram) - Latence du modèle
- `model_confidence_score` (Gauge) - Score de confiance moyen
- `model_accuracy` (Gauge) - Accuracy sur batch récent

**Configuration:**
- Ajouter `prometheus-client` à `requirements.txt`
- Exposer endpoint `/metrics` dans FastAPI
- Collecter métriques dans `prediction_service.py`

**Fichier Docker Compose:**
```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./docker/prometheus.yml:/etc/prometheus/prometheus.yml
```

#### B. Dashboards Grafana

**Fichier:** `docker/grafana/dashboards/model_monitoring.json`

**Dashboards à créer:**
1. **API Performance**
   - Request rate (req/s)
   - Latency (p50, p95, p99)
   - Error rate

2. **Model Performance**
   - Prediction rate
   - Prediction latency
   - Confidence distribution
   - Accuracy over time

3. **Resource Usage**
   - CPU usage
   - Memory usage
   - Disk I/O

**Configuration:**
```yaml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  volumes:
    - ./docker/grafana/dashboards:/var/lib/grafana/dashboards
    - ./docker/grafana/provisioning:/etc/grafana/provisioning
  depends_on:
    - prometheus
```

#### C. Alerting

**Fichier:** `docker/prometheus/alerts.yml`

**Alertes à configurer:**
- Latence API > 500ms
- Error rate > 5%
- Model accuracy < 90%
- Resource usage > 80%

**Validation:** Compétence C11 complète

---

### 🟡 PRIORITÉ 4: MLflow pour Tracking (C11, C13)

**Objectif:** Tracker tous les experiments ML et versionner les modèles.

#### A. Intégration MLflow

**Fichier:** `machine_learning/mlflow_tracking.py`

**Fonctionnalités:**
- Tracking des hyperparamètres
- Tracking des métriques d'entraînement
- Logging des artifacts (models, scalers)
- Model registry

**Configuration:**
```yaml
mlflow:
  image: ghcr.io/mlflow/mlflow:latest
  ports:
    - "5000:5000"
  volumes:
    - ./mlruns:/mlruns
  command: mlflow server --backend-store-uri sqlite:///mlruns/mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0
```

#### B. Modification du script d'entraînement

**Fichier:** `machine_learning/train_model.py`

**Ajouts requis:**
```python
import mlflow
import mlflow.sklearn

with mlflow.start_run():
    # Log hyperparameters
    mlflow.log_params({
        'n_estimators': 100,
        'max_depth': 8,
        'learning_rate': 0.1,
    })

    # Train model
    model.fit(X_train, y_train)

    # Log metrics
    mlflow.log_metrics({
        'accuracy': 0.9424,
        'precision': 0.94,
        'recall': 0.94,
        'f1': 0.94,
    })

    # Log model
    mlflow.sklearn.log_model(model, "model")
```

**Validation:** Compétences C11 (tracking) et C13 (versioning)

---

### 🟡 PRIORITÉ 5: Pipeline CI/CD (C13)

**Objectif:** Automatiser tests, validation, packaging et déploiement.

#### A. GitHub Actions Workflow

**Fichier:** `.github/workflows/ml_pipeline.yml`

**Étapes du pipeline:**

1. **Lint & Format**
   - black (formatting)
   - flake8 (linting)
   - mypy (type checking)

2. **Tests**
   - Run all unit tests
   - Run integration tests
   - Run model tests
   - Generate coverage report

3. **Build Docker Images**
   - Build API image
   - Build ML image
   - Build Streamlit image
   - Push to registry

4. **Deploy**
   - Deploy to staging
   - Run smoke tests
   - Deploy to production (manual approval)

**Fichier exemple:**
```yaml
name: ML Pipeline

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest machine_learning/tests/ --cov

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: docker-compose build
      - name: Push images
        run: docker-compose push
```

#### B. Pre-commit Hooks

**Fichier:** `.pre-commit-config.yaml`

**Hooks:**
- black (formatting)
- flake8 (linting)
- mypy (type checking)
- pytest (tests rapides)

**Validation:** Compétence C13 complète

---

### 🟢 PRIORITÉ 6: Documentation & Nettoyage

**Objectif:** Finaliser la documentation et nettoyer le projet.

#### A. Nettoyage des fichiers obsolètes

**Script de nettoyage:**
```bash
# Supprimer modèles obsolètes
rm models/battle_winner_rf_v1.pkl
rm models/random_forest_v1.pkl
rm models/random_forest_no_multiplier_v1.pkl
rm models/battle_winner_xgb_v1.pkl
rm models/model_metadata.pkl

# Archiver documentation
mkdir -p docs/archive
mv BUGFIXES_APPLIED.md docs/archive/
mv FINAL_ADJUSTMENTS.md docs/archive/
mv DOCKER_TEST_REPORT.md docs/archive/
# ... (autres fichiers listés ci-dessus)
```

#### B. Mise à jour README.md

**Sections à ajouter:**
- Architecture MLOps
- Monitoring avec Prometheus/Grafana
- MLflow tracking
- CI/CD pipeline
- Instructions de contribution
- Roadmap

#### C. Mise à jour E3_DOCUMENTATION.md

**Contenu:**
- Preuve de validation pour chaque compétence C9-C13
- Captures d'écran des dashboards Grafana
- Logs MLflow
- Pipeline CI/CD
- Métriques de monitoring

---

## Timeline Recommandé

| Semaine | Priorité | Tâche | Temps estimé | Validation |
|---------|----------|-------|--------------|------------|
| **Semaine 1** | 🔴 | Script `run_machine_learning.py` | 2 jours | C12, C13 |
| | 🔴 | Tests automatisés complets | 3 jours | C12 |
| **Semaine 2** | 🔴 | Prometheus + métriques API | 2 jours | C11 |
| | 🔴 | Grafana dashboards | 1 jour | C11 |
| | 🔴 | Alerting | 1 jour | C11 |
| **Semaine 3** | 🟡 | MLflow intégration | 2 jours | C11, C13 |
| | 🟡 | Pipeline CI/CD | 2 jours | C13 |
| | 🟡 | Pre-commit hooks | 0.5 jour | C13 |
| **Semaine 4** | 🟢 | Nettoyage fichiers | 0.5 jour | - |
| | 🟢 | Documentation finale | 1.5 jours | - |
| | 🟢 | Validation E3 | 1 jour | - |

**Total estimé:** 17 jours de développement

---

## Résumé des Compétences E3

| Compétence | Statut Actuel | Actions Requises | Validation |
|------------|---------------|------------------|------------|
| **C9** | ✅ Validé | Aucune | API REST fonctionnelle |
| **C10** | ✅ Validé | Aucune | Streamlit intégré |
| **C11** | ⚠️ 20% | Prometheus + Grafana + Alerting | Dashboards monitoring |
| **C12** | ⚠️ 40% | Tests automatisés complets | Suite de tests complète |
| **C13** | ⚠️ 30% | MLflow + CI/CD pipeline | Pipeline fonctionnel |

---

## Prochaines Étapes Immédiates

1. **Valider ce plan** avec l'équipe/formateur
2. **Créer les branches Git** pour chaque priorité
3. **Commencer par Priorité 1**: Script ML unifié
4. **Implémenter progressivement** selon timeline
5. **Tester à chaque étape**
6. **Documenter au fur et à mesure**

---

**Auteur:** Claude Code
**Date de révision:** 2026-01-22
**Version:** 1.0
