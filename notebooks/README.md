# Notebooks Jupyter - R&D ML

Ce dossier contient les notebooks Jupyter pour la recherche et développement du modèle ML.

⚠️ **Important**: Ces notebooks sont **uniquement pour la R&D**. Le code production se trouve dans `machine_learning/`.

## Structure

```
notebooks/
├── 01_exploration.ipynb              # EDA et analyse des données
├── 02_feature_engineering.ipynb      # Création et sélection des features
├── 03_training_evaluation.ipynb      # Entraînement et évaluation du modèle
└── README.md
```

## Workflow

### 1. Exploration des Données

**Notebook**: [01_exploration.ipynb](01_exploration.ipynb)

**Objectifs**:
- Charger le dataset `data/ml/raw/battle_samples.parquet`
- Analyser la distribution des features
- Identifier les valeurs manquantes
- Visualiser les corrélations
- Analyser la distribution de la target

### 2. Feature Engineering

**Notebook**: [02_feature_engineering.ipynb](02_feature_engineering.ipynb)

**Objectifs**:
- Encoder les variables catégorielles
- Créer de nouvelles features si nécessaire
- Normaliser/standardiser les features numériques
- Sélection des features importantes

### 3. Entraînement et Évaluation

**Notebook**: [03_training_evaluation.ipynb](03_training_evaluation.ipynb)

**Objectifs**:
- Tester plusieurs modèles (Logistic Regression, Random Forest, etc.)
- Tuning des hyperparamètres
- Évaluer les performances (accuracy, F1, confusion matrix)
- Sélectionner le modèle final
- Exporter le modèle vers `models/`

## Lancer Jupyter

```bash
# Depuis la racine du projet
jupyter notebook

# Ou Jupyter Lab
jupyter lab
```

## Prérequis

```bash
pip install jupyter pandas numpy scikit-learn matplotlib seaborn pyarrow
```

## Export vers Production

Une fois le modèle validé dans les notebooks, le code doit être réécrit dans:
- [machine_learning/train_model.py](../machine_learning/train_model.py)

---

**Date de création**: 2026-01-20
