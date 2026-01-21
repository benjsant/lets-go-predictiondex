# Handoff Context - Projet Let's Go PredictionDex

## Résumé du Projet

Application de prédiction de combats Pokémon Let's Go Pikachu/Eevee pour aider les enfants à choisir la meilleure capacité contre un adversaire.

## Architecture

```
lets-go-predictiondex/
├── core/                      # Modèles SQLAlchemy et guards
│   ├── models/                # Pokemon, Move, Type, Stats, etc.
│   └── db/guards/             # Fonctions upsert (move.py, pokemon.py, etc.)
├── etl_pokemon/               # Pipeline ETL
│   ├── data/csv/              # Données sources (liste_pokemon.csv, liste_capacite_lets_go.csv)
│   └── scripts/etl_load_csv.py
├── machine_learning/          # Scripts ML
│   ├── build_battle_winner_dataset.py  # Génère le dataset de combats
│   ├── train_model.py                   # Script production pour entraînement
│   ├── test_model_inference.py          # Test des prédictions
│   ├── README.md                        # Documentation ML complète
│   └── build_dataset_ml_v1.py          # Ancien script (damage prediction)
├── data/ml/battle_winner/     # Données ML générées
│   ├── raw/matchups.parquet   # 34,040 matchups
│   ├── processed/             # train.parquet, test.parquet
│   └── features/              # X_train.parquet, X_test.parquet, scalers
├── notebooks/                 # Jupyter notebooks
│   ├── 01_exploration.ipynb   # EDA du dataset
│   ├── 02_feature_engineering.ipynb  # Préparation features (133 colonnes)
│   └── 03_training_evaluation.ipynb  # Training (XGBoost 94.24% accuracy)
├── models/                    # Modèles entraînés
│   ├── battle_winner_model_v1.pkl     # XGBoost (983K)
│   ├── battle_winner_scalers_v1.pkl   # 2 StandardScalers (1.7K)
│   ├── battle_winner_metadata.pkl     # Métadonnées (2.8K)
│   └── battle_winner_rf_v1.pkl        # Random Forest (backup, 28M)
└── api/                       # FastAPI (à compléter)
```

## Travail Complété

### 1. BDD - Colonne `priority` ajoutée au modèle Move
- `core/models/move.py` : Ajout de `priority = Column(Integer, default=0, nullable=False)`
- `core/db/guards/move.py` : Paramètre `priority` dans `upsert_move()`
- `etl_pokemon/scripts/etl_load_csv.py` : Mapping `PRIORITY_FROM_DAMAGE_TYPE`

Valeurs de priorité:
- +2: Abri, Ruse
- +1: Vive-Attaque, Aqua-Jet, Éclats Glace, Coup Bas, Pika-Sprint
- 0: Normal (offensif, multi_coups, deux_tours, etc.)
- -5: Riposte, Voile Miroir

### 2. Dataset Battle Winner
- Script: `machine_learning/build_battle_winner_dataset.py`
- 34,040 matchups (188 Pokémon × 188 Pokémon)
- 38 colonnes raw → 133 features après encoding
- Target: `winner` (0 = A gagne, 1 = B gagne)
- Split: 80% train (27,232) / 20% test (6,808)

### 3. Notebooks ML Exécutés
- **01_exploration.ipynb**: EDA, distribution équilibrée 50/50
- **02_feature_engineering.ipynb**: One-hot encoding types, normalisation, 6 features dérivées
- **03_training_evaluation.ipynb**: 3 modèles entraînés

### 4. Résultats des Modèles

| Modèle | Test Accuracy | F1-Score | ROC-AUC |
|--------|--------------|----------|---------|
| Logistic Regression | 90.88% | 90.83% | 97.13% |
| Random Forest | 93.48% | 93.48% | 98.59% |
| **XGBoost** | **94.24%** | **94.24%** | **98.96%** |

Top Features (Random Forest):
1. `stat_ratio` (15%)
2. `effective_power_diff` (9%)
3. `hp_diff` (8.8%)
4. `a_total_stats` (5.3%)
5. `b_total_stats` (4.6%)

### 5. Script de Production `train_model.py` ✅

**Fichier**: `machine_learning/train_model.py`

Script automatisé qui reproduit fidèlement le pipeline des notebooks:
- ✅ Charge train/test depuis parquet
- ✅ Feature engineering (133 features finales):
  - One-hot encoding des 6 features catégorielles (types) → ~102 colonnes
  - Normalisation 1: StandardScaler sur stats numériques
  - Création de 6 features dérivées (stat_ratio, effective_power_diff, etc.)
  - Normalisation 2: StandardScaler sur features dérivées
- ✅ Entraîne XGBoost (hyperparamètres identiques au notebook 03)
- ✅ Évalue performances: accuracy, precision, recall, F1, ROC-AUC
- ✅ Exporte 3 artifacts:
  - `battle_winner_model_v1.pkl` (983K)
  - `battle_winner_scalers_v1.pkl` (1.7K - dict avec 2 scalers)
  - `battle_winner_metadata.pkl` (2.8K)

**Usage**: `python machine_learning/train_model.py`

**Résultats vérifiés**: 94.24% test accuracy (identique aux notebooks)

## Travail Restant (TODO)

### 1. Intégration API `/predict`
Créer endpoint FastAPI:
```python
POST /predict/best_move
{
  "pokemon_a_id": 1,
  "pokemon_b_id": 4,
  "moves_a": ["Lance-Soleil", "Charge", "Bomb-Beurk"]
}

Response:
{
  "recommended_move": "Bomb-Beurk",
  "win_probability": 0.85,
  "move_scores": [...]
}
```

### 2. Tests ML
- Tests unitaires pour le pipeline
- Tests d'intégration pour l'API

### 3. Documentation E3
- Documenter le pipeline ML complet
- Métriques et justifications des choix

## Commandes Utiles

```bash
# Activer l'environnement
source .venv/bin/activate

# Lancer les conteneurs Docker (BDD PostgreSQL)
docker-compose up -d

# Exécuter l'ETL (avec localhost car hors Docker)
POSTGRES_HOST=localhost python etl_pokemon/scripts/etl_load_csv.py

# Générer le dataset ML
POSTGRES_HOST=localhost python machine_learning/build_battle_winner_dataset.py

# Entraîner le modèle en production
python machine_learning/train_model.py

# Tester les prédictions
python machine_learning/test_model_inference.py

# Lancer Jupyter
jupyter notebook notebooks/
```

## Connexion BDD

```python
# Depuis l'hôte (hors Docker)
POSTGRES_HOST=localhost

# Depuis Docker
POSTGRES_HOST=db

# Variables d'env (voir .env)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=pokemon_db
```

## Notes Importantes

1. **Le problème ML est correct**: 94% accuracy est normal (pas de data leakage)
2. **Cas d'usage**: Recommander la meilleure capacité à un enfant contre un Pokémon adverse
3. **Moves exclus**: Bluff (premier tour), Croc Fatal (jamais KO), Balayage (poids), moves réactifs
4. **deux_tours**: Priorité 0, mais puissance /2 dans le calcul

## Fichiers Clés à Lire

1. `machine_learning/README.md` - **Documentation complète du pipeline ML**
2. `machine_learning/train_model.py` - **Script de production pour entraînement**
3. `machine_learning/build_battle_winner_dataset.py` - Logique de génération du dataset
4. `notebooks/03_training_evaluation.ipynb` - Résultats du training
5. `etl_pokemon/scripts/etl_load_csv.py` - ETL et mapping des priorités
6. `core/models/move.py` - Modèle Move avec priority
