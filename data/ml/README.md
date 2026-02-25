# Datasets ML

Datasets pour l'entraînement du modèle de prédiction de combat.

## Structure

```
data/ml/battle_winner/
├── raw/matchups.parquet              # Données brutes (188x188 matchups)
├── processed/
│   ├── train.parquet                 # Train set (80%)
│   └── test.parquet                  # Test set (20%)
└── features/
    ├── X_train.parquet, X_test.parquet   # Features normalisées
    └── y_train.parquet, y_test.parquet   # Labels
```

## Versions

**v1** : 34 040 échantillons. Scénario unique (best_move pour A et B). Train/test 80/20.

**v2** : ~898 000 échantillons, 3 scénarios :
- `best_move` (~34k) : meilleur move pour chaque Pokémon
- `random_move` (~10k) : B utilise un move aléatoire
- `all_combinations` (~854k) : toutes les combinaisons de moves

## Générer

```bash
python machine_learning/run_machine_learning.py --mode=dataset --dataset-version=v1
python machine_learning/run_machine_learning.py --mode=dataset --dataset-version=v2 --scenario-type=all
```

## Features

38 features brutes (stats A/B, types, move power/accuracy/category/priority) → one-hot encoding des types (~102 colonnes) + 6 features dérivées (stat_ratio, effective_power_diff, hp_diff, type_advantage_diff, a_moves_first, stab_advantage) → 135 features finales.

Target : `winner` (0 = B gagne, 1 = A gagne). Distribution équilibrée 50/50.
