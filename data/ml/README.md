# Datasets ML - Battle Winner Prediction

> Datasets pour l'entraînement du modèle de prédiction de combat

## Structure

```
data/ml/
├── battle_winner/
│ ├── raw/
│ │ └── matchups.parquet # Données brutes (188×188 matchups)
│ ├── processed/
│ │ ├── train.parquet # Train set (80%)
│ │ └── test.parquet # Test set (20%)
│ └── features/
│ ├── X_train.parquet # Features normalisées (train)
│ ├── X_test.parquet # Features normalisées (test)
│ ├── y_train.parquet # Labels (train)
│ └── y_test.parquet # Labels (test)
└── README.md
```

## Datasets Disponibles

### Dataset v1 (best_move)
- **Échantillons** : 34,040 (188 × 188 matchups)
- **Scénario** : Les deux Pokémon utilisent leur meilleur move
- **Train/Test** : 80% / 20%

### Dataset v2 (multi-scénarios)
- **Échantillons** : ~898,000
- **Scénarios** :
 - `best_move` (~34k) : Meilleur move pour A et B
 - `random_move` (~10k) : B utilise un move aléatoire
 - `all_combinations` (~854k) : Toutes les combinaisons de moves
- **Train/Test** : 80% / 20%

## Génération

```bash
# Dataset v1
python machine_learning/run_machine_learning.py --mode=dataset --dataset-version=v1

# Dataset v2 (multi-scénarios)
python machine_learning/run_machine_learning.py --mode=dataset --dataset-version=v2 --scenario-type=all
```

## Features (133 colonnes)

**Features brutes (38)** :
- Stats Pokémon A : hp, attack, defense, sp_attack, sp_defense, speed
- Stats Pokémon B : hp, attack, defense, sp_attack, sp_defense, speed
- Types : type_1, type_2 (A et B)
- Move : power, accuracy, type, category, priority

**Features dérivées (6)** :
- `stat_ratio` : Ratio stats totales A/B
- `effective_power_diff` : Différence de puissance effective
- `hp_diff` : Différence de HP
- `type_advantage_diff` : Différence avantage de type
- `a_moves_first` : A attaque en premier (vitesse)
- `stab_advantage` : Avantage STAB

**One-hot encoding** : ~89 colonnes (types)

## Utilisation

```python
import pandas as pd

# Charger les features normalisées
X_train = pd.read_parquet("data/ml/battle_winner/features/X_train.parquet")
X_test = pd.read_parquet("data/ml/battle_winner/features/X_test.parquet")
y_train = pd.read_parquet("data/ml/battle_winner/features/y_train.parquet")
y_test = pd.read_parquet("data/ml/battle_winner/features/y_test.parquet")

# Charger les données brutes
train_df = pd.read_parquet("data/ml/battle_winner/processed/train.parquet")
```

## Target

- **Colonne** : `winner`
- **Valeurs** : `0` (B gagne) ou `1` (A gagne)
- **Distribution** : ~50% / 50% (balancé)

---

**Dernière mise à jour** : 31 janvier 2026
