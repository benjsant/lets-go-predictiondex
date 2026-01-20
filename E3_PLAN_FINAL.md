# Plan E3 Final - Implémentation ML & MLOps

**Date**: 2026-01-20
**Basé sur**: Plan ChatGPT + Améliorations proposées

---

## 🎯 Objectif ML

### Question Métier
**"Cette capacité est-elle efficace contre ce Pokémon défenseur ?"**

### Type de ML
- **Classification binaire supervisée**
- **Target**: `is_effective ∈ {0, 1}`
- **Règle**: `is_effective = 1 if type_multiplier >= 2 else 0`

### Justification
✅ Simple et explicable
✅ Aligné avec les règles Pokémon officielles
✅ Défendable en jury
✅ Suffisant pour valider le bloc E3

---

## 📊 Dataset ML

### Source
Base PostgreSQL (188 Pokémon, 226 capacités damaging)

### Taille Théorique
```
188 × 188 × 226 = 7,982,656 combinaisons possibles
```

### Stratégie d'Échantillonnage Intelligent

**Problème**: Dataset complet trop large et avec beaucoup de bruit

**Solution**:
1. Garder **TOUTES** les combinaisons efficaces (type_multiplier >= 2)
2. Échantillonner **15%** des combinaisons non efficaces
3. Résultat: ~500K-1M lignes (optimal pour RandomForest)

### Features (19 au total)

| Catégorie | Features | Type |
|-----------|----------|------|
| **Attacker** (4) | type_1, type_2, attack, sp_attack | categorical + numerical |
| **Defender** (4) | type_1, type_2, defense, sp_defense | categorical + numerical |
| **Move** (4) | type, category, power, accuracy | categorical + numerical |
| **Computed** (7) | type_multiplier, is_stab, stat_ratio, has_dual_type_attacker, has_dual_type_defender | numerical + boolean |

### Target
```python
is_effective = 1 if type_multiplier >= 2 else 0
```

### Format
- **Raw**: `data/ml/raw/battle_samples.parquet`
- **Train**: `data/ml/processed/train.parquet` (80%)
- **Test**: `data/ml/processed/test.parquet` (20%)
- **Split**: Stratified (preserve class distribution)

---

## 🧠 Modèle ML

### Modèles à Tester (Notebooks)
1. **Logistic Regression** (baseline)
2. **Random Forest** ⭐ (recommandé)
3. **XGBoost** (optionnel si temps disponible)

### Modèle Final Retenu
**RandomForestClassifier**

**Hyperparamètres suggérés**:
```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    random_state=42,
    n_jobs=-1
)
```

**Justification**:
- ✅ Robuste aux données brutes (pas besoin de scaling)
- ✅ Gère bien les features catégorielles (après encoding)
- ✅ Interprétable (feature importance)
- ✅ Performant sans tuning excessif
- ✅ Très bien accepté en jury

### Métriques de Performance Attendues
- **Accuracy**: >= 85%
- **F1-Score**: >= 80%
- **Precision/Recall**: Équilibrés

---

## 🔄 Workflow de Développement

### Phase 1: Dataset Generation ✅ (En cours)
**Script**: [machine_learning/build_classification_dataset.py](machine_learning/build_classification_dataset.py)

**Actions**:
1. ✅ Créer le script de génération
2. ⏳ Exécuter le script (via Docker)
3. ⏳ Valider la qualité du dataset

**Commande**:
```bash
docker compose exec api python machine_learning/build_classification_dataset.py
```

---

### Phase 2: Notebooks Jupyter (R&D)

#### Notebook 1: Exploration
**Fichier**: [notebooks/01_exploration.ipynb](notebooks/01_exploration.ipynb)

**Objectifs**:
- Charger `data/ml/processed/train.parquet`
- EDA (Exploratory Data Analysis)
- Distribution des features
- Corrélations
- Distribution de la target (is_effective)
- Identification des valeurs manquantes
- Visualisations (histogrammes, boxplots, heatmap)

---

#### Notebook 2: Feature Engineering
**Fichier**: [notebooks/02_feature_engineering.ipynb](notebooks/02_feature_engineering.ipynb)

**Objectifs**:
- Encoder les features catégorielles:
  - LabelEncoder pour les types
  - OneHotEncoder pour move_category
- Normalisation si nécessaire (RandomForest n'en a pas besoin)
- Sélection des features importantes
- Validation de la pipeline de preprocessing

---

#### Notebook 3: Training & Evaluation
**Fichier**: [notebooks/03_training_evaluation.ipynb](notebooks/03_training_evaluation.ipynb)

**Objectifs**:
- Tester plusieurs modèles (Logistic Regression, Random Forest)
- Comparer les performances
- Tuning des hyperparamètres (GridSearchCV ou RandomizedSearchCV)
- Évaluation finale:
  - Accuracy, Precision, Recall, F1-Score
  - Confusion Matrix
  - Feature Importance (pour RandomForest)
  - ROC Curve / AUC
- Export du modèle final vers `models/`

---

### Phase 3: Script Production

**Fichier**: [machine_learning/train_model.py](machine_learning/train_model.py)

**Objectifs**:
- Reprendre le code validé dans les notebooks
- Script reproductible (pas d'interaction manuelle)
- Charger train/test depuis `data/ml/processed/`
- Entraîner RandomForestClassifier
- Évaluer les performances
- Exporter:
  - `models/pokemon_move_model.joblib`
  - `models/model_metadata.json`

**Commande**:
```bash
python machine_learning/train_model.py
```

**Output** (`models/model_metadata.json`):
```json
{
  "model_type": "RandomForestClassifier",
  "version": "1.0.0",
  "features": ["attacker_type_1", "attacker_type_2", ...],
  "accuracy": 0.92,
  "f1_score": 0.91,
  "precision": 0.90,
  "recall": 0.92,
  "created_at": "2026-01-20T15:30:00",
  "created_by": "train_model.py",
  "train_samples": 800000,
  "test_samples": 200000,
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 15,
    "random_state": 42
  }
}
```

---

### Phase 4: Intégration API

#### 4.1 Feature Builder
**Fichier**: [api_pokemon/ml/feature_builder.py](api_pokemon/ml/feature_builder.py)

**Rôle**: Construire le vecteur de features depuis les IDs (attacker_id, defender_id, move_id)

```python
def build_features(attacker_id: int, defender_id: int, move_id: int, session) -> dict:
    """
    Query DB and build feature vector.

    Returns:
        dict: Feature vector ready for model prediction
    """
    # Query Pokemon stats and types
    # Query Move properties
    # Calculate type_multiplier, is_stab, stat_ratio, etc.
    # Return dict with all features
```

---

#### 4.2 Model Loader
**Fichier**: [api_pokemon/ml/model_loader.py](api_pokemon/ml/model_loader.py)

**Rôle**: Charger le modèle au démarrage de l'API

```python
import joblib
from pathlib import Path

def load_model():
    """Load ML model from disk."""
    model_path = Path("models/pokemon_move_model.joblib")
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = joblib.load(model_path)
    print(f"✅ Model loaded: {model_path}")
    return model
```

---

#### 4.3 Predictor
**Fichier**: [api_pokemon/ml/predictor.py](api_pokemon/ml/predictor.py)

**Rôle**: Logique de prédiction

```python
class Predictor:
    def __init__(self, model):
        self.model = model

    def predict(self, features: dict) -> dict:
        """
        Make prediction.

        Returns:
            dict: {
                "is_effective": int,
                "probability": float,
                "confidence": str
            }
        """
        # Convert features dict to numpy array
        # Model prediction
        # Calculate probability and confidence
        # Return structured response
```

---

#### 4.4 Predict Route
**Fichier**: [api_pokemon/routes/predict_route.py](api_pokemon/routes/predict_route.py)

**Endpoint**: `POST /predict`

**Request**:
```json
{
  "attacker_id": 1,
  "defender_id": 4,
  "move_id": 33
}
```

**Response**:
```json
{
  "is_effective": 1,
  "probability": 0.87,
  "confidence": "high",
  "type_multiplier": 2.0,
  "move_category": "physique",
  "recommendation": "Super efficace ! Cette capacité Plante inflige des dégâts doublés contre ce type Eau.",
  "metadata": {
    "model_version": "1.0.0",
    "prediction_time_ms": 12
  }
}
```

---

#### 4.5 Integration in Main
**Fichier**: [api_pokemon/main.py](api_pokemon/main.py)

**Modifications**:
```python
from api_pokemon.ml.model_loader import load_model
from api_pokemon.routes import predict_route

# Global model instance
ml_model = None

@app.on_event("startup")
async def startup_event():
    global ml_model
    try:
        ml_model = load_model()
        print("✅ ML Model loaded successfully")
    except Exception as e:
        print(f"⚠️  ML Model not loaded: {e}")
        # API can still work without ML

# Include predict router
app.include_router(predict_route.router, prefix="/predict", tags=["ML Prediction"])
```

---

### Phase 5: Tests Automatisés (C12)

#### Test 1: Dataset
**Fichier**: [tests/ml/test_dataset_ml.py](tests/ml/test_dataset_ml.py)

**Tests**:
- ✅ Dataset files exist
- ✅ Train/test split ratio (80/20)
- ✅ No missing values in critical features
- ✅ Target distribution (should be close to 50/50 after sampling)
- ✅ Feature types are correct

---

#### Test 2: Model Loading
**Fichier**: [tests/ml/test_model_loading.py](tests/ml/test_model_loading.py)

**Tests**:
- ✅ Model file exists
- ✅ Model loads successfully
- ✅ Metadata file exists and is valid JSON
- ✅ Simple prediction works (sanity check)

---

#### Test 3: Predict Endpoint
**Fichier**: [tests/ml/test_predict_endpoint.py](tests/ml/test_predict_endpoint.py)

**Tests**:
- ✅ Endpoint returns 200 for valid input
- ✅ Response has correct structure
- ✅ Probability is between 0 and 1
- ✅ Invalid IDs return 404
- ✅ Missing fields return 422

---

#### Test 4: Model Performance
**Fichier**: [tests/ml/test_model_performance.py](tests/ml/test_model_performance.py)

**Tests**:
- ✅ Accuracy >= 0.85 on test set
- ✅ F1-score >= 0.80
- ✅ No extreme predictions (all probabilities != 0 or 1)

**Commande**:
```bash
pytest tests/ml/ -v
```

---

### Phase 6: Monitoring (C11)

#### 6.1 Evidently Configuration
**Fichier**: [monitoring/evidently_config.py](monitoring/evidently_config.py)

**Configuration**:
- Data drift detection
- Prediction drift detection
- Report generation

---

#### 6.2 Data Drift Monitor
**Fichier**: [monitoring/monitor_data_drift.py](monitoring/monitor_data_drift.py)

**Fonctionnalités**:
- Compare reference data (train set) vs current data (new predictions)
- Detect distribution changes in features
- Generate HTML report
- Alert if drift detected

**Commande**:
```bash
python monitoring/monitor_data_drift.py
```

**Output**: `reports/data_drift_report.html`

---

#### 6.3 Prediction Monitor
**Fichier**: [monitoring/monitor_predictions.py](monitoring/monitor_predictions.py)

**Métriques**:
- Total predictions count
- Ratio effective/not-effective (should be stable)
- Prediction latency
- Model load time

---

### Phase 7: Interface Streamlit (C10)

**Fichier**: [interface/pages/3_🤖_ML_Predict.py](interface/pages/3_🤖_ML_Predict.py)

**Fonctionnalités**:
1. **Sélection Pokémon Attaquant** (dropdown avec images)
2. **Sélection Pokémon Défenseur** (dropdown avec images)
3. **Sélection Capacité** (dropdown avec détails)
4. **Bouton "Prédire l'Efficacité"**
5. **Affichage Résultat**:
   - Badge efficace/non efficace (vert/rouge)
   - Probabilité avec barre de progression
   - Multiplicateur de type
   - Recommandation textuelle
   - Graphique de confiance (gauge chart)
6. **Historique des prédictions** (optionnel)

**Interface**:
```python
import streamlit as st
import requests

st.title("🤖 Prédiction d'Efficacité ML")

# Fetch Pokemon list from API
pokemon_list = requests.get("http://api:8000/pokemon/").json()

# Dropdowns
attacker = st.selectbox("Pokémon Attaquant", pokemon_list)
defender = st.selectbox("Pokémon Défenseur", pokemon_list)
move = st.selectbox("Capacité", ...)

if st.button("Prédire"):
    response = requests.post("http://api:8000/predict", json={
        "attacker_id": attacker["id"],
        "defender_id": defender["id"],
        "move_id": move["id"]
    })
    result = response.json()

    # Display result
    if result["is_effective"]:
        st.success(f"✅ Efficace ! (probabilité: {result['probability']:.1%})")
    else:
        st.error(f"❌ Pas efficace (probabilité: {result['probability']:.1%})")

    st.info(result["recommendation"])
```

---

### Phase 8: Documentation Finale

**Fichier**: [E3_RAPPORT.md](E3_RAPPORT.md)

**Contenu**:
- Présentation du projet
- Problème ML et justification
- Architecture du dataset
- Choix du modèle (RandomForest) et justification
- Résultats (métriques de performance)
- Intégration API et Streamlit
- Tests automatisés
- Monitoring
- Chaîne MLOps (Docker, CI/CD)
- Démonstration E3 (compétences C9-C13)
- Conclusion et perspectives

---

## 📋 Compétences E3 - Mapping

| Compétence | Description | Couverture | Fichiers Clés |
|------------|-------------|------------|---------------|
| **C9** | Développer et exposer un modèle IA via API | ✅ Endpoint `/predict` | `api_pokemon/routes/predict_route.py`, `api_pokemon/ml/` |
| **C10** | Intégrer le modèle dans une application | ✅ Page Streamlit | `interface/pages/3_🤖_ML_Predict.py` |
| **C11** | Monitorer les performances du modèle | ✅ Evidently | `monitoring/` |
| **C12** | Implémenter des tests automatisés | ✅ pytest | `tests/ml/` |
| **C13** | Mettre en place une chaîne MLOps | ✅ Docker, scripts reproductibles | `docker-compose.yml`, `machine_learning/train_model.py` |

---

## 🚀 Ordre d'Exécution Recommandé

### Semaine 1: Dataset & Notebooks
1. ✅ [Créer build_classification_dataset.py](machine_learning/build_classification_dataset.py)
2. ⏳ Exécuter et générer le dataset
3. ⏳ Créer notebooks 01, 02, 03
4. ⏳ Expérimenter et valider le modèle

### Semaine 2: Production & API
5. ⏳ Créer train_model.py
6. ⏳ Entraîner et exporter le modèle
7. ⏳ Créer les modules API ML (feature_builder, model_loader, predictor)
8. ⏳ Créer l'endpoint /predict
9. ⏳ Intégrer dans main.py

### Semaine 3: Tests & Monitoring
10. ⏳ Créer les tests automatisés (4 fichiers)
11. ⏳ Configurer Evidently
12. ⏳ Implémenter monitoring

### Semaine 4: Interface & Documentation
13. ⏳ Créer la page Streamlit ML Predict
14. ⏳ Rédiger E3_RAPPORT.md
15. ⏳ Préparer la démonstration jury

---

## 💡 Message Clé pour le Jury

> "Le modèle de Machine Learning est conçu comme un **service indépendant**, entraîné **hors production** via des scripts reproductibles, intégré dans une **API REST FastAPI**, monitoré avec **Evidently**, testé avec **pytest**, et exposé via une **interface Streamlit**. L'ensemble de la chaîne MLOps est **dockerisée** et **automatisée**, démontrant une approche **industrielle** et **scalable**."

---

## 📊 Métriques de Succès

### Dataset
- ✅ 500K-1M lignes
- ✅ Classes équilibrées (50/50)
- ✅ 19 features pertinentes

### Modèle
- ✅ Accuracy >= 85%
- ✅ F1-Score >= 80%
- ✅ Feature importance interprétable

### API
- ✅ Endpoint /predict fonctionnel
- ✅ Latence < 100ms
- ✅ Healthcheck OK

### Tests
- ✅ 15+ tests automatisés
- ✅ Coverage >= 80%

### Interface
- ✅ Page Streamlit fonctionnelle
- ✅ UX intuitive
- ✅ Résultats clairs

---

**Statut Actuel**: Phase 1 en cours (Dataset Generation)
**Prochaine Étape**: Exécuter `build_classification_dataset.py` via Docker
