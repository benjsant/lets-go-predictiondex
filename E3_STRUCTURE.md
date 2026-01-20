# Structure E3 - Intelligence Artificielle & MLOps

## 📂 Architecture du Projet E3

```
lets-go-predictiondex/
│
├── data/
│   ├── datasets/                    # Datasets existants (build_dataset_ml_v1.py)
│   │   └── pokemon_damage_ml.parquet
│   └── ml/                          # ← NOUVEAU: Datasets ML pour classification
│       ├── raw/
│       │   └── battle_samples.parquet        # Données brutes pour ML
│       ├── processed/
│       │   ├── train.parquet                 # Train set
│       │   └── test.parquet                  # Test set
│       └── README.md
│
├── notebooks/                       # ← NOUVEAU: Notebooks Jupyter (R&D uniquement)
│   ├── 01_exploration.ipynb         # EDA et analyse des données
│   ├── 02_feature_engineering.ipynb # Création et sélection des features
│   ├── 03_training_evaluation.ipynb # Entraînement et évaluation du modèle
│   └── README.md
│
├── models/                          # ← NOUVEAU: Modèles ML exportés
│   ├── pokemon_move_model.joblib    # Modèle final (RandomForest)
│   ├── model_metadata.json          # Métadonnées du modèle
│   └── README.md
│
├── machine_learning/                # Scripts ML production
│   ├── build_dataset_ml_v1.py       # ✅ Existant: génération dataset dégâts
│   ├── build_classification_dataset.py  # ← NOUVEAU: génération dataset classification
│   ├── train_model.py               # ← NOUVEAU: entraînement du modèle
│   └── requirements.txt
│
├── api_pokemon/
│   ├── main.py                      # ✅ Existant
│   ├── routes/
│   │   ├── pokemon_route.py         # ✅ Existant
│   │   ├── moves_route.py           # ✅ Existant
│   │   └── predict_route.py         # ← NOUVEAU: endpoint ML /predict
│   ├── services/
│   │   ├── pokemon_service.py       # ✅ Existant
│   │   ├── move_service.py          # ✅ Existant
│   │   └── ml_service.py            # ← NOUVEAU: service de prédiction ML
│   └── ml/
│       ├── __init__.py
│       ├── model_loader.py          # ← NOUVEAU: chargement du modèle au démarrage
│       └── predictor.py             # ← NOUVEAU: logique de prédiction
│
├── tests/
│   ├── api/                         # ✅ Existant: tests API
│   └── ml/                          # ← NOUVEAU: tests ML
│       ├── test_dataset_ml.py       # Test génération dataset
│       ├── test_model_loading.py    # Test chargement modèle
│       ├── test_predict_endpoint.py # Test endpoint /predict
│       └── test_model_performance.py # Test performance modèle
│
├── monitoring/                      # ← NOUVEAU: Monitoring ML
│   ├── evidently_config.py          # Configuration Evidently
│   ├── monitor_data_drift.py        # Détection data drift
│   └── monitor_predictions.py       # Monitoring prédictions
│
└── interface/
    └── pages/
        ├── 0_🏠_Home.py             # ✅ Existant
        ├── 1_⚔️_Moves.py            # ✅ Existant
        ├── 2_🔍_Compare.py          # ✅ Existant
        ├── 3_🤖_ML_Predict.py       # ← NOUVEAU: page prédiction ML
        └── 4_ℹ️_Credits.py          # ✅ Existant
```

---

## 🎯 Problème ML

### Question Métier
**"Cette capacité est-elle efficace contre ce Pokémon défenseur ?"**

### Type de Machine Learning
- **Classification binaire supervisée**
- **Target**: `is_effective ∈ {0, 1}`
- **Règle**: `is_effective = 1 if multiplicateur_type >= 2 else 0`

### Justification
- ✅ Simple et explicable
- ✅ Alignée avec les règles Pokémon officielles
- ✅ Défendable en jury
- ✅ Permet de démontrer les compétences E3

---

## 📊 Dataset ML

### Source
Base de données PostgreSQL existante:
- Table `pokemon` (stats + types)
- Table `move` (capacités + types)
- Table `type_effectiveness` (multiplicateurs de types)

### Features

**Pokémon Attaquant** (5 features):
- `attacker_type_1` (categorical)
- `attacker_type_2` (categorical, nullable)
- `attacker_attack` (numeric)
- `attacker_sp_attack` (numeric)

**Pokémon Défenseur** (5 features):
- `defender_type_1` (categorical)
- `defender_type_2` (categorical, nullable)
- `defender_defense` (numeric)
- `defender_sp_defense` (numeric)

**Capacité** (4 features):
- `move_type` (categorical)
- `move_category` (categorical: physique/spéciale/statut)
- `move_power` (numeric)
- `move_accuracy` (numeric)

**Feature Métier** (1 feature):
- `type_multiplier` (numeric: 0, 0.25, 0.5, 1, 2, 4)

**Total**: 15 features

### Target (Label)
```python
is_effective = 1 if type_multiplier >= 2 else 0
```

### Format
- **Format**: Parquet (pandas + pyarrow)
- **Taille estimée**: ~50-100 MB
- **Lignes estimées**:
  - Attaquants: 188 Pokémon
  - Défenseurs: 188 Pokémon
  - Capacités: 226 moves
  - Total: 188 × 188 × 226 ≈ 8M lignes (échantillonnage recommandé)

---

## 🧠 Modèle ML

### Modèles à Tester (dans notebooks)
1. **Logistic Regression** (baseline)
2. **Random Forest** (modèle final recommandé)
3. Optionnel: XGBoost, LightGBM

### Modèle Final Retenu
**RandomForestClassifier**

**Justification**:
- ✅ Robuste aux données brutes
- ✅ Gère bien les features catégorielles (après encoding)
- ✅ Interprétable (feature importance)
- ✅ Performant sans tuning excessif
- ✅ Très bien accepté en jury

### Export du Modèle
```python
import joblib

# Entraînement
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Export
joblib.dump(model, "models/pokemon_move_model.joblib")

# Métadonnées
metadata = {
    "model_type": "RandomForestClassifier",
    "features": list(X_train.columns),
    "accuracy": accuracy_score(y_test, y_pred),
    "f1_score": f1_score(y_test, y_pred),
    "created_at": "2026-01-20"
}
import json
with open("models/model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

---

## 🌐 API ML

### Endpoint Principal
```
POST /predict
```

### Input (Request Body)
```json
{
  "attacker_id": 1,
  "defender_id": 4,
  "move_id": 33
}
```

### Output (Response)
```json
{
  "is_effective": 1,
  "probability": 0.87,
  "confidence": "high",
  "type_multiplier": 2.0,
  "recommendation": "Super efficace ! Cette capacité inflige des dégâts doublés."
}
```

### Chargement du Modèle
- **Quand**: Au démarrage de l'API (événement `startup`)
- **Une seule fois**: Stocké en mémoire
- **Fichier**: [api_pokemon/ml/model_loader.py](api_pokemon/ml/model_loader.py)

```python
# api_pokemon/main.py
from api_pokemon.ml.model_loader import load_model

model = None

@app.on_event("startup")
async def startup_event():
    global model
    model = load_model("models/pokemon_move_model.joblib")
    print("✅ ML Model loaded successfully")
```

---

## 🧪 Tests Automatisés (C12)

### Tests à Implémenter

1. **[tests/ml/test_dataset_ml.py](tests/ml/test_dataset_ml.py)**
   - Test génération du dataset
   - Vérification des features
   - Vérification de la target
   - Vérification des valeurs nulles

2. **[tests/ml/test_model_loading.py](tests/ml/test_model_loading.py)**
   - Test chargement du modèle
   - Vérification des métadonnées
   - Test de prédiction simple

3. **[tests/ml/test_predict_endpoint.py](tests/ml/test_predict_endpoint.py)**
   - Test endpoint `/predict`
   - Test validation des inputs
   - Test format de la réponse

4. **[tests/ml/test_model_performance.py](tests/ml/test_model_performance.py)**
   - Test accuracy >= seuil (ex: 0.85)
   - Test F1-score >= seuil
   - Test sur le test set

### Exécution
```bash
# Tous les tests
pytest tests/

# Tests ML uniquement
pytest tests/ml/

# Avec coverage
pytest --cov=api_pokemon --cov=machine_learning tests/
```

---

## 📈 Monitoring (C11)

### Outils
- **Evidently**: Détection de drift (data + predictions)

### Métriques à Monitorer

1. **Data Drift**
   - Distribution des features
   - Détection de changements

2. **Prediction Drift**
   - Distribution des prédictions
   - Ratio efficace/non efficace

3. **Performance**
   - Accuracy sur nouvelles données
   - F1-score
   - Confusion matrix

### Implementation
```python
# monitoring/monitor_data_drift.py
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=train_df, current_data=new_data)
report.save_html("reports/data_drift_report.html")
```

---

## 🔁 MLOps / CI-CD (C13)

### Docker
- ✅ Tous les services déjà dockerisés
- ✅ Hot reload activé en mode dev

### Tests Automatiques
```yaml
# .github/workflows/test.yml (à créer)
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and test
        run: |
          docker compose up --build -d
          docker compose exec -T api pytest tests/
```

### Versionnement
- **Code**: Git
- **Dataset**: Versioning via date dans le nom du fichier
- **Modèle**: Versioning via metadata.json

---

## 🎨 Interface Streamlit

### Nouvelle Page: ML Predict

**Emplacement**: [interface/pages/3_🤖_ML_Predict.py](interface/pages/3_🤖_ML_Predict.py)

**Fonctionnalités**:
1. Sélection Pokémon attaquant (dropdown)
2. Sélection Pokémon défenseur (dropdown)
3. Sélection capacité (dropdown)
4. Bouton "Prédire l'efficacité"
5. Affichage résultat:
   - Prédiction (efficace/non efficace)
   - Probabilité
   - Multiplicateur de type
   - Recommandation textuelle
   - Graphique de confiance

---

## 📋 Compétences E3 Couvertes

| Compétence | Description | Couverture |
|------------|-------------|------------|
| **C9** | Développer et exposer un modèle IA via API | ✅ Endpoint `/predict` |
| **C10** | Intégrer le modèle dans une application | ✅ Page Streamlit ML Predict |
| **C11** | Monitorer les performances du modèle | ✅ Evidently (data drift + predictions) |
| **C12** | Implémenter des tests automatisés | ✅ pytest (dataset, model, endpoint) |
| **C13** | Mettre en place une chaîne MLOps | ✅ Docker, CI/CD, versioning |

---

## 🚀 Plan de Développement

### Phase 1: Dataset ML
1. Créer `machine_learning/build_classification_dataset.py`
2. Générer `data/ml/raw/battle_samples.parquet`
3. Split train/test → `data/ml/processed/`

### Phase 2: Notebooks R&D
1. `01_exploration.ipynb` - EDA
2. `02_feature_engineering.ipynb` - Features
3. `03_training_evaluation.ipynb` - Entraînement

### Phase 3: Modèle Production
1. Créer `machine_learning/train_model.py`
2. Exporter `models/pokemon_move_model.joblib`
3. Créer `models/model_metadata.json`

### Phase 4: API ML
1. Créer `api_pokemon/ml/model_loader.py`
2. Créer `api_pokemon/ml/predictor.py`
3. Créer `api_pokemon/routes/predict_route.py`
4. Intégrer dans `api_pokemon/main.py`

### Phase 5: Tests
1. `tests/ml/test_dataset_ml.py`
2. `tests/ml/test_model_loading.py`
3. `tests/ml/test_predict_endpoint.py`

### Phase 6: Monitoring
1. `monitoring/evidently_config.py`
2. `monitoring/monitor_data_drift.py`

### Phase 7: Interface
1. `interface/pages/3_🤖_ML_Predict.py`

---

**Date de création**: 2026-01-20
**Statut**: Structure préparée, en attente du plan détaillé ChatGPT
