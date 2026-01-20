# Datasets ML - Classification

Ce dossier contient les datasets pour le modèle de classification ML.

## Structure

```
data/ml/
├── raw/
│   └── battle_samples.parquet      # Données brutes générées depuis PostgreSQL
├── processed/
│   ├── train.parquet                # Train set (80%)
│   └── test.parquet                 # Test set (20%)
└── README.md
```

## Génération des Données

**Script**: [machine_learning/build_classification_dataset.py](../../machine_learning/build_classification_dataset.py)

```bash
# Générer le dataset ML
python machine_learning/build_classification_dataset.py
```

## Format

**Type**: Parquet (pandas + pyarrow)

**Features**:
- Pokémon attaquant: type_1, type_2, attack, sp_attack
- Pokémon défenseur: type_1, type_2, defense, sp_defense
- Capacité: type, category, power, accuracy
- Métier: type_multiplier

**Target**: `is_effective ∈ {0, 1}`

**Règle**: `is_effective = 1 if type_multiplier >= 2 else 0`

## Taille Estimée

- **Lignes**: ~500K - 1M (après échantillonnage)
- **Taille**: 50-100 MB

## Utilisation

```python
import pandas as pd

# Charger le train set
train_df = pd.read_parquet("data/ml/processed/train.parquet")

# Charger le test set
test_df = pd.read_parquet("data/ml/processed/test.parquet")
```

---

**Date de création**: 2026-01-20
