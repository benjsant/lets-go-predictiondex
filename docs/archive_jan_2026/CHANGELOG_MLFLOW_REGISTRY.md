# Changelog - MLflow Model Registry Integration

**Date** : 25 janvier 2025  
**Version** : Phase 2 - MLflow Model Registry  
**Objectif** : Centraliser la gestion des modèles ML avec versioning et promotion automatique

---

## 🎯 Objectif de cette Session

Après avoir optimisé les performances CPU du ML (Phase 1), cette session implémente le **MLflow Model Registry** pour :
- ✅ Centraliser les modèles entraînés dans un registry versionné
- ✅ Promouvoir automatiquement les meilleurs modèles en Production
- ✅ Charger les modèles depuis l'API sans dépendance aux fichiers locaux
- ✅ Simplifier le rollback et la comparaison des versions

---

## 📦 Fichiers Modifiés

### 1. **machine_learning/mlflow_integration.py**
**Changements** : Ajout de 5 nouvelles fonctions pour le Model Registry

```python
# Nouvelles fonctions
def register_model(model_name, description) -> str
def promote_to_production(model_name, version) -> bool
def promote_best_model(model_name, metric, minimum_metric_value) -> bool
def compare_models(model_name) -> pd.DataFrame
def load_model_from_registry(model_name, stage, version) -> Dict

# Amélioration de log_model()
def log_model(model, scalers=None, metadata=None)
    # Loggue maintenant aussi scalers.pkl et metadata.pkl comme artifacts
```

**Fonctionnalités** :
- ✅ `register_model()` : Enregistre le modèle du run actif dans le registry
- ✅ `promote_to_production()` : Transition vers Production, archive l'ancienne version
- ✅ `promote_best_model()` : Promotion automatique si métrique >= seuil
- ✅ `compare_models()` : Retourne DataFrame comparant toutes les versions
- ✅ `load_model_from_registry()` : Charge modèle + scalers + metadata depuis le registry
- ✅ `log_model()` : Loggue maintenant scalers et metadata comme artifacts supplémentaires

---

### 2. **machine_learning/run_machine_learning.py**
**Changements** : Intégration du registry dans les 3 modes (train/evaluate, compare, all)

```python
# Après chaque export_model() et tracker.log_model()
version_number = tracker.register_model(
    model_name="battle_winner_predictor",
    description=f"{model_name} - Accuracy: {accuracy:.4f}"
)

# Promotion automatique si accuracy >= 0.85
if version_number and metrics['test_accuracy'] >= 0.85:
    tracker.promote_to_production("battle_winner_predictor", version_number)
    print("🎯 Model meets quality threshold (accuracy >= 0.85)")
    print("✅ Model promoted to Production stage")
else:
    print("⚠️  Model registered but not promoted (accuracy < 0.85)")
```

**Impact** :
- ✅ **3 emplacements modifiés** : modes 'train/evaluate', 'compare', 'all'
- ✅ **Enregistrement automatique** après chaque entraînement
- ✅ **Promotion automatique** si accuracy >= 85%
- ✅ **Scalers et metadata** loggés comme artifacts pour chargement complet

---

### 3. **machine_learning/train_model.py**
**Changements** : Ajout de l'intégration MLflow Registry dans le script standalone

```python
# Nouvel import
try:
    from machine_learning.mlflow_integration import MLflowTracker
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# Après export_model()
if MLFLOW_AVAILABLE and model_path and not args.no_mlflow:
    tracker = MLflowTracker(experiment_name=f"battle_winner_{args.version}")
    tracker.start_run(run_name=f"train_model_{args.version}_{timestamp}")
    
    tracker.log_params({...})
    tracker.log_metrics(metrics)
    tracker.log_model(model, scalers=scalers, metadata={'feature_columns': feature_columns})
    
    # Register + auto-promote
    version_number = tracker.register_model("battle_winner_predictor", description)
    if version_number and metrics['test_accuracy'] >= 0.85:
        tracker.promote_to_production("battle_winner_predictor", version_number)
    
    tracker.end_run()
```

**Nouvelle option** :
```bash
python machine_learning/train_model.py --no-mlflow  # Désactiver le registry
```

**Impact** :
- ✅ **Script standalone** maintenant compatible avec le registry
- ✅ **Enregistrement automatique** après entraînement
- ✅ **Option --no-mlflow** pour tests sans MLflow
- ✅ **Scalers et metadata** loggés pour chargement complet

---

### 4. **api_pokemon/services/prediction_service.py**
**Changements** : Chargement depuis MLflow Registry avec fallback local

```python
# Nouveaux imports
try:
    from machine_learning.mlflow_integration import load_model_from_registry
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# Nouvelle méthode load()
def load(self):
    use_mlflow = os.getenv('USE_MLFLOW_REGISTRY', 'true').lower() == 'true'
    
    # 1. Try MLflow Registry (Production stage)
    if use_mlflow and MLFLOW_AVAILABLE:
        model_bundle = load_model_from_registry(
            model_name="battle_winner_predictor",
            stage="Production"
        )
        if model_bundle:
            self._model = model_bundle['model']
            self._scalers = model_bundle['scalers']
            self._metadata = model_bundle['metadata']
            print("✅ Model loaded from MLflow Registry")
            return
    
    # 2. Fallback: Load from local files
    print("⚠️ Falling back to local files...")
    self._model = joblib.load("models/battle_winner_model_v2.pkl")
    ...
```

**Variables d'environnement** :
```bash
USE_MLFLOW_REGISTRY=true           # Enable/disable registry (default: true)
MLFLOW_MODEL_NAME=battle_winner_predictor
MLFLOW_MODEL_STAGE=Production      # Production, Staging, Archived
MLFLOW_TRACKING_URI=http://mlflow:5000
```

**Impact** :
- ✅ **Chargement automatique** depuis Production stage
- ✅ **Fallback robuste** sur fichiers locaux si échec
- ✅ **Logs clairs** pour diagnostiquer la source du modèle
- ✅ **Compatible** avec environnements sans MLflow

---

## 🔄 Workflow Complet

### Avant (sans Model Registry)

```
1. Entraînement → models/battle_winner_model_v2.pkl
2. API → Charge depuis fichiers locaux
3. Rollback → Remplacer manuellement les fichiers .pkl
4. Comparaison → Impossible sans garder tous les .pkl
```

### Après (avec Model Registry)

```
1. Entraînement → models/*.pkl + MLflow Registry (versioning)
2. Promotion automatique → Production stage si accuracy >= 0.85
3. API → Charge depuis Production stage (avec fallback local)
4. Comparaison → MLflow UI ou compare_models()
5. Rollback → Promouvoir une version précédente en 1 clic
```

---

## 📊 Exemple d'Utilisation

### Scénario 1 : Entraînement et Déploiement Automatique

```bash
# 1. Entraîner un modèle
$ python machine_learning/train_model.py --use-gridsearch --version v4

Output:
✅ Model trained and exported
✅ Logged to MLflow (run: train_model_v4_20250125_1430)
✅ Registered as version 4 in Model Registry
🎯 Model meets quality threshold (accuracy >= 0.85)
✅ Model promoted to Production stage

# 2. L'API recharge automatiquement
# Au prochain appel de prédiction :
🔍 Loading ML model...
   Trying MLflow Model Registry (battle_winner_predictor @ Production)...
✅ Model loaded from MLflow Registry
   Version: 4
```

### Scénario 2 : Comparaison et Rollback

```python
from machine_learning.mlflow_integration import MLflowTracker

tracker = MLflowTracker()
tracker.start_run()

# Comparer toutes les versions
df = tracker.compare_models("battle_winner_predictor")
print(df)
"""
version  stage       accuracy  f1_score  roc_auc   created_at
4        Production  0.8723    0.8654    0.9234    2025-01-25 14:30
3        Staging     0.8512    0.8401    0.9102    2025-01-25 12:15
2        Archived    0.8203    0.8123    0.8956    2025-01-24 18:45
"""

# Rollback à la version 3 si problème
tracker.promote_to_production("battle_winner_predictor", version=3)
# ✅ Version 3 transitioned to Production
# ✅ Previous Production version archived
```

---

## 🧪 Tests Prévus

### Tests Unitaires

```bash
# Test 1 : Enregistrement et promotion
tests/mlflow/test_model_registry.py
- test_register_model()
- test_promote_to_production()
- test_promote_best_model()
- test_compare_models()
- test_load_model_from_registry()

# Test 2 : Intégration API
tests/integration/test_mlflow_to_api.py
- test_e2e_mlflow_to_api()
- test_api_fallback_to_local()
```

### Tests Manuels

```bash
# 1. Entraîner et vérifier registry
python machine_learning/train_model.py --use-gridsearch
# → Vérifier MLflow UI : Models → battle_winner_predictor

# 2. Tester chargement API
docker compose up api
curl http://localhost:8000/api/v1/pokemon/1/predict-against/4
# → Logs API : "✅ Model loaded from MLflow Registry"

# 3. Tester fallback
USE_MLFLOW_REGISTRY=false docker compose up api
# → Logs API : "⚠️ Falling back to local files..."
```

---

## 📈 Métriques et Seuils

### Seuil de Promotion Automatique

```python
PROMOTION_THRESHOLD = 0.85  # accuracy >= 85%

# Modifiable dans :
# - machine_learning/run_machine_learning.py (lignes ~1076, ~1113, ~1174)
# - machine_learning/train_model.py (ligne ~644)
```

### Métriques Loggées

```python
{
    'train_accuracy': 0.8956,
    'test_accuracy': 0.8723,   # ⭐ Critère de promotion
    'test_precision': 0.8654,
    'test_recall': 0.8598,
    'test_f1': 0.8626,
    'test_roc_auc': 0.9234,
    'overfitting': 0.0233
}
```

---

## 🐛 Problèmes Résolus

### Problème 1 : Scalers et Metadata Non Disponibles

**Avant** : `load_model_from_registry()` retournait seulement le modèle

**Solution** : 
- Modifier `log_model()` pour logger `scalers.pkl` et `metadata.pkl` comme artifacts
- Modifier `load_model_from_registry()` pour télécharger et charger ces artifacts
- Retourner un dict `{'model': ..., 'scalers': ..., 'metadata': ..., 'version': ...}`

### Problème 2 : Import Circulaire dans l'API

**Avant** : `from machine_learning.mlflow_integration import load_model_from_registry` causait des erreurs

**Solution** :
- Wrap l'import dans un try/except
- Définir `MLFLOW_AVAILABLE = False` si échec
- L'API fonctionne avec ou sans MLflow

### Problème 3 : Promotion Non Automatique

**Avant** : Fallait promouvoir manuellement depuis MLflow UI

**Solution** :
- Ajouter `promote_best_model()` qui vérifie le seuil automatiquement
- Intégrer dans run_machine_learning.py et train_model.py
- Logs clairs : "🎯 Model meets threshold" ou "⚠️ Not promoted"

---

## 📚 Documentation Créée

1. **MLFLOW_REGISTRY_GUIDE.md** (ce fichier)
   - Architecture et workflow
   - Utilisation complète (train, load, compare, rollback)
   - Troubleshooting
   - Variables d'environnement

2. **CHANGELOG_MLFLOW_REGISTRY.md** (fichier actuel)
   - Modifications détaillées par fichier
   - Exemples d'utilisation
   - Tests prévus

---

## ✅ Résumé des Changements

| Fichier | Fonctionnalités Ajoutées | Impact |
|---------|-------------------------|--------|
| `mlflow_integration.py` | 5 fonctions registry + amélioration log_model | ⭐⭐⭐ Core registry |
| `run_machine_learning.py` | Register + promote dans 3 modes | ⭐⭐⭐ Enregistrement auto |
| `train_model.py` | Intégration registry + option --no-mlflow | ⭐⭐ Script standalone |
| `prediction_service.py` | Load from registry + fallback local | ⭐⭐⭐ API sans fichiers |

---

## 🚀 Prochaines Étapes

### Phase 3 : Tests Complets

1. ✅ Écrire tests unitaires pour le Model Registry
2. ✅ Écrire tests d'intégration ML → API
3. ✅ Tester fallback sur fichiers locaux
4. ✅ Valider promotion automatique

### Phase 4 : Validation Docker

1. ✅ `docker compose up --build`
2. ✅ Vérifier MLflow service démarre
3. ✅ Vérifier ml_builder enregistre modèle
4. ✅ Vérifier API charge depuis registry
5. ✅ Tester prédictions end-to-end

---

**Statut** : ✅ MLflow Model Registry intégré et documenté  
**Prochain** : Tests complets → docker compose up 🚀
