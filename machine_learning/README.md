# Machine Learning - Battle Winner Prediction

Ce dossier contient tous les scripts pour entraîner et évaluer le modèle de prédiction de gagnant de combat Pokémon.

## Structure

```
machine_learning/
├── build_battle_winner_dataset_orm.py  # Génère le dataset (SQLAlchemy ORM) en simulant des duels
├── run_machine_learning.py             # Pipeline ML complet (orchestration)
├── train_model.py                       # Script de production pour entraîner le modèle
├── test_model_inference.py              # Test rapide des prédictions
├── analyze_data_for_ml.py               # Analyse exploratoire (legacy)
└── temp/                                # Versions alternatives (psycopg2, etc.)
```

## Workflow Complet

### Option 1: Pipeline Complet (Recommandé)

Exécute toutes les étapes automatiquement avec le nouveau script d'orchestration:

```bash
# Depuis la racine du projet
source .venv/bin/activate
python machine_learning/run_machine_learning.py --mode=all
```

**Ce que ça fait:**
1. Génère le dataset depuis PostgreSQL (ORM) en simulant des duels.
2. Feature engineering (133 features).
3. Entraîne le modèle XGBoost pour prédire le gagnant.
4. Évalue les performances (Accuracy, ROC-AUC).
5. Exporte les artifacts (modèle, scalers, metadata).

**Modes disponibles:**
- `--mode=all` - Pipeline complet
- `--mode=dataset` - Génération dataset uniquement
- `--mode=train` - Entraînement uniquement
- `--mode=evaluate` - Évaluation uniquement
- `--mode=compare` - Compare XGBoost vs RandomForest

**Options avancées:**
- `--tune-hyperparams` - Active GridSearchCV (plus lent)
- `--skip-export-features` - Ne pas exporter les features (plus rapide)
- `--version=v2` - Spécifier version des artifacts
- `--scenario-type=all` - Filtrer par scénario (future: worst_case, random, etc.)

### Option 2: Étapes Manuelles

#### 1️⃣ Générer le Dataset

Génère 34,040 matchups (188 Pokémon × 188 Pokémon) avec sélection automatique du meilleur move pour **chaque** Pokémon (A et B) afin de simuler des combats réalistes.

```bash
source .venv/bin/activate
POSTGRES_HOST=localhost python machine_learning/build_battle_winner_dataset_orm.py
```

**Outputs**:
- `data/ml/battle_winner/raw/matchups.parquet` (34,040 samples)
- `data/ml/battle_winner/processed/train.parquet` (27,232 samples, 80%)
- `data/ml/battle_winner/processed/test.parquet` (6,808 samples, 20%)

**Note**: Utilise SQLAlchemy ORM pour la cohérence avec le reste du projet (API, ETL).

#### 2️⃣ Entraîner le Modèle

Entraîne un modèle XGBoost sur le dataset généré.

```bash
source .venv/bin/activate
python machine_learning/train_model.py
```

**Options**:
- `--use-gridsearch` - Active GridSearchCV pour tuning
- `--skip-export-features` - Ne pas exporter les features
- `--version=v2` - Version des artifacts
- `--scenario-type=all` - Filtrer par scénario

**Opérations effectuées**:
1. Charge les datasets train/test depuis les fichiers parquet
2. Feature engineering:
   - One-hot encoding des types (6 features → ~102 colonnes)
   - Normalisation des features numériques (StandardScaler)
   - Création de 6 features dérivées (stat_ratio, effective_power_diff, etc.)
   - Normalisation des features dérivées (deuxième StandardScaler)
3. Entraînement du modèle XGBoost
4. Évaluation des performances (accuracy, precision, recall, F1, ROC-AUC)
5. Export des artifacts

**Outputs**:
- `models/battle_winner_model_v1.pkl` (modèle XGBoost entraîné)
- `models/battle_winner_scalers_v1.pkl` (2 scalers pour normalisation)
- `models/battle_winner_metadata.pkl` (métadonnées: features, métriques, hyperparamètres)
- `data/ml/battle_winner/features/X_train.parquet` (features normalisées pour train)
- `data/ml/battle_winner/features/X_test.parquet` (features normalisées pour test)
- `data/ml/battle_winner/features/y_train.parquet` (labels train)
- `data/ml/battle_winner/features/y_test.parquet` (labels test)

### 3. Tester les Prédictions

Teste rapidement que le modèle peut être chargé et utilisé pour des prédictions.

```bash
source .venv/bin/activate
python machine_learning/test_model_inference.py
```

## Résultats du Modèle

### Performance (Test Set)

| Métrique | Score |
|----------|-------|
| **Accuracy** | **94.24%** |
| Precision | 94.27% |
| Recall | 94.21% |
| F1-Score | 94.24% |
| ROC-AUC | 98.96% |

### Top Features (Importance)

1. **stat_ratio** (15.0%) - Ratio des stats totales A/B
2. **effective_power_diff** (9.0%) - Différence de puissance effective
3. **hp_diff** (8.8%) - Différence de HP
4. **a_total_stats** (5.3%) - Stats totales de A
5. **b_total_stats** (4.6%) - Stats totales de B

## Options du Script

### `train_model.py`

```bash
python machine_learning/train_model.py [OPTIONS]

Options:
  --skip-export-features    Ne pas exporter les features normalisées (gain de temps/espace)
```

## Architecture du Modèle

### XGBoost Hyperparameters

```python
{
    'n_estimators': 100,
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'n_jobs': -1,
    'eval_metric': 'logloss'
}
```

### Feature Engineering Pipeline

```
Raw Features (38 colonnes)
    ↓
[One-Hot Encoding] → Types Pokémon + Types Move (~102 colonnes)
    ↓
[Normalisation 1] → Stats numériques (StandardScaler)
    ↓
[Derived Features] → 6 nouvelles features calculées
    ↓
[Normalisation 2] → Features dérivées (StandardScaler)
    ↓
Final Features (133 colonnes)
```

## Dépendances

Voir `requirements.txt` à la racine du projet:
- pandas
- numpy
- scikit-learn
- xgboost
- pyarrow (pour parquet)

## Notes Importantes

1. **Dataset Balancé**: Le dataset est parfaitement balancé (50% A wins, 50% B wins)
2. **Pas de Data Leakage**: Le target `winner` est calculé via simulation complexe, pas directement dérivé des features
3. **Overfitting Minimal**: Gap train/test de 4.63% (acceptable pour XGBoost)
4. **Reproducibilité**: Random seed fixé à 42 pour tous les processus aléatoires

## Prochaines Étapes

1. **Intégration API**: Créer endpoint `/predict/best_move` dans FastAPI
2. **Tests**: Tests unitaires pour le pipeline ML
3. **Monitoring**: Tracking des performances en production
4. **Documentation E3**: Documenter le pipeline complet pour validation académique
