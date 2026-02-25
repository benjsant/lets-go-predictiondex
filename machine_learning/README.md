# Machine Learning

Scripts pour entraîner et évaluer le modèle de prédiction de gagnant de combat Pokémon.

## Structure

```
machine_learning/
├── build_battle_winner_dataset.py     # Dataset v1 (best_move)
├── build_battle_winner_dataset_v2.py  # Dataset v2 (multi-scénarios)
├── run_machine_learning.py            # Pipeline ML complet
├── train_model.py                     # Entraînement
└── test_model_inference.py            # Test rapide des prédictions
```

## Lancer le pipeline complet

```bash
source .venv/bin/activate
python machine_learning/run_machine_learning.py --mode=all
```

Ça génère le dataset depuis PostgreSQL, fait le feature engineering (135 features), entraîne le modèle XGBoost, évalue les performances et exporte les artefacts.

Modes disponibles : `all`, `dataset`, `train`, `evaluate`, `compare` (XGBoost vs RandomForest).

Options utiles :
- `--dataset-version=v2` : dataset multi-scénarios
- `--tune-hyperparams` : active GridSearchCV
- `--grid-type=extended` : grille étendue (243 combinaisons)
- `--version=v2` : version des artefacts exportés

## Dataset v1 vs v2

**v1** : 34 040 échantillons. Les deux Pokémon utilisent leur meilleur move offensif. C'est le dataset original, simple et rapide. Accuracy : 94.24%.

**v2** : ~898 000 échantillons, 3 scénarios combinés :
- `best_move` (~34k) : identique à v1
- `random_move` (~10k) : B utilise un move aléatoire
- `all_combinations` (~836k) : toutes les combinaisons possibles de moves A vs B

Le v2 donne un modèle plus robuste, capable de gérer des situations variées. Entraînement plus long (25x plus de données).

```bash
# Générer le dataset v2
POSTGRES_HOST=localhost python machine_learning/build_battle_winner_dataset_v2.py \
  --scenario-type=all \
  --num-random-samples=10000 \
  --max-combinations=100000
```

## Résultats

### v1 (test set)

| Métrique | Score |
|----------|-------|
| Accuracy | 94.24% |
| F1-Score | 94.24% |
| ROC-AUC | 98.96% |

### v2 (test set)

| Métrique | Score |
|----------|-------|
| Accuracy | 96.26% |
| F1-Score | 96.26% |
| ROC-AUC | 99.5% |

Les features les plus importantes : stat_ratio (ratio des stats totales), effective_power_diff, hp_diff.

## Feature engineering

```
38 features brutes
  → One-hot encoding des types (~102 colonnes)
  → Normalisation (StandardScaler)
  → 6 features dérivées (stat_ratio, effective_power_diff, etc.)
  → 2e normalisation
  → 135 features finales
```

## Hyperparamètres XGBoost

```python
{
    'n_estimators': 200,
    'max_depth': 10,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}
```

## Notes

- Dataset balancé 50/50 (A gagne / B gagne)
- Pas de data leakage : le target est calculé par simulation
- Overfitting acceptable (gap train/test ~1.97%)
- Random seed fixé à 42
