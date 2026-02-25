# Modèles ML

Artefacts des modèles entraînés pour la prédiction de combats.

## Fichiers

```
models/
├── battle_winner_model_v1.pkl     # Modèle v1 (best_move)
├── battle_winner_model_v2.pkl     # Modèle v2 (multi-scénarios)
├── battle_winner_scalers_v1.pkl   # Scalers v1
├── battle_winner_scalers_v2.pkl   # Scalers v2
└── battle_winner_metadata.pkl     # Métadonnées
```

## v1 vs v2

**v1** : entraîné sur 34k échantillons (scénario best_move uniquement). 94.24% accuracy. Simple et rapide.

**v2** : entraîné sur ~898k échantillons (3 scénarios). 96.26% accuracy sur le test set, avec GridSearchCV. Plus robuste sur des situations de combat variées, fonctionne mieux avec le paramètre `available_moves_b` de l'API.

En production, on recommande le **v2** pour sa robustesse sauf contrainte de ressources.

## Charger un modèle

```python
# Dans l'API (automatique)
from api_pokemon.services import prediction_service
model = prediction_service.prediction_model
model.load()

# Dans un notebook
import joblib
model = joblib.load('models/battle_winner_model_v2.pkl')
scalers = joblib.load('models/battle_winner_scalers_v2.pkl')
```

## Métadonnées

Le fichier `battle_winner_metadata.pkl` contient : version, type de modèle, liste des 135 features, métriques, hyperparamètres, date d'entraînement, infos sur le feature engineering.

## Régénérer

```bash
# v1
python machine_learning/run_machine_learning.py --mode=all --dataset-version=v1 --version=v1

# v2 avec GridSearchCV
python machine_learning/run_machine_learning.py \
  --mode=all --dataset-version=v2 --scenario-type=all \
  --tune-hyperparams --grid-type=extended --version=v2
```
