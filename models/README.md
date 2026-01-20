# Modèles ML - Classification

Ce dossier contient les modèles ML entraînés et leurs métadonnées.

## Structure

```
models/
├── pokemon_move_model.joblib        # Modèle final (RandomForest)
├── model_metadata.json              # Métadonnées du modèle
└── README.md
```

## Modèle Final

**Type**: RandomForestClassifier
**Format**: joblib
**Fichier**: [pokemon_move_model.joblib](pokemon_move_model.joblib)

## Génération du Modèle

**Script**: [machine_learning/train_model.py](../machine_learning/train_model.py)

```bash
# Entraîner et exporter le modèle
python machine_learning/train_model.py
```

## Métadonnées

**Fichier**: [model_metadata.json](model_metadata.json)

**Contenu**:
```json
{
  "model_type": "RandomForestClassifier",
  "version": "1.0.0",
  "features": [
    "attacker_type_1", "attacker_type_2",
    "attacker_attack", "attacker_sp_attack",
    "defender_type_1", "defender_type_2",
    "defender_defense", "defender_sp_defense",
    "move_type", "move_category",
    "move_power", "move_accuracy",
    "type_multiplier"
  ],
  "accuracy": 0.92,
  "f1_score": 0.91,
  "created_at": "2026-01-20T15:00:00",
  "created_by": "train_model.py",
  "train_samples": 800000,
  "test_samples": 200000
}
```

## Chargement du Modèle

### Dans l'API

```python
# api_pokemon/ml/model_loader.py
import joblib

def load_model(model_path: str):
    """Load the ML model from disk."""
    model = joblib.load(model_path)
    return model
```

### Dans un Notebook

```python
import joblib

# Charger le modèle
model = joblib.load("models/pokemon_move_model.joblib")

# Faire une prédiction
prediction = model.predict(X_test)
```

## Versionnement

Pour versionner un nouveau modèle:

1. Entraîner le nouveau modèle
2. Exporter avec un nom versionné: `pokemon_move_model_v1.1.0.joblib`
3. Mettre à jour `model_metadata.json`
4. Comparer les performances avec l'ancien modèle
5. Déployer si amélioration significative

---

**Date de création**: 2026-01-20
