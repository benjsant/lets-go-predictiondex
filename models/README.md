# Modèles ML - Battle Winner Prediction

Ce dossier contient les modèles ML entraînés et leurs métadonnées.

## Structure

```
models/
├── battle_winner_model_v1.pkl       # Modèle v1 (best_move uniquement)
├── battle_winner_model_v2.pkl       # Modèle v2 (multi-scénarios)
├── battle_winner_scalers_v1.pkl     # Scalers pour normalisation v1
├── battle_winner_scalers_v2.pkl     # Scalers pour normalisation v2
├── battle_winner_metadata.pkl       # Métadonnées complètes (v1 ou v2)
└── README.md                         # Ce fichier
```

## Modèles Disponibles

### Modèle v1 (best_move)

**Type**: XGBClassifier
**Format**: pickle
**Fichier**: [battle_winner_model_v1.pkl](battle_winner_model_v1.pkl)
**Dataset**: 34,040 échantillons (scénario best_move uniquement)

**Performance (Test Set):**

| Métrique | Score |
|----------|-------|
| **Accuracy** | **94.24%** |
| Precision | 94.27% |
| Recall | 94.21% |
| F1-Score | 94.24% |
| ROC-AUC | 98.96% |

**Hyperparamètres:**
```python
{
    'n_estimators': 100,
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}
```

**Utilisation:**
- Recommandé pour les situations où l'adversaire utilise toujours son meilleur move
- Plus simple et rapide à entraîner
- Performance excellente sur le scénario best_move

### Modèle v2 (multi-scénarios)

**Type**: XGBClassifier (avec GridSearchCV)
**Format**: pickle
**Fichier**: [battle_winner_model_v2.pkl](battle_winner_model_v2.pkl)
**Dataset**: ~880,000 échantillons (3 scénarios combinés)

**Performance (Test Set):**

| Métrique | Scénario | Score |
|----------|----------|-------|
| **Accuracy** | best_move | **~94-95%** |
| **Accuracy** | random_move | **~92-93%** |
| **Accuracy** | all_combinations | **~93-94%** |
| **Accuracy** | **Global** | **~93-94%** |
| ROC-AUC | Global | ~98.5% |

**Hyperparamètres (optimisés via GridSearchCV):**
```python
{
    'n_estimators': 100-200,  # Optimisé par GridSearch
    'max_depth': 6-8,         # Optimisé par GridSearch
    'learning_rate': 0.05-0.1, # Optimisé par GridSearch
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}
```

**Avantages:**
- **Robustesse**: Performe bien sur différents types de combats
- **Généralisation**: S'adapte aux situations où B n'utilise pas forcément son meilleur move
- **Support API**: Fonctionne mieux avec le paramètre `available_moves_b`

**Inconvénients:**
- Entraînement plus long (~25x plus de données)
- Légère baisse de performance sur best_move (~1%) compensée par la robustesse

## Génération des Modèles

### Modèle v1

**Script**: [machine_learning/train_model.py](../machine_learning/train_model.py)

```bash
# Générer dataset v1 + entraîner modèle v1
source .venv/bin/activate
python machine_learning/run_machine_learning.py --mode=all --dataset-version=v1 --version=v1
```

### Modèle v2

**Script**: [machine_learning/train_model.py](../machine_learning/train_model.py)

```bash
# Générer dataset v2 (multi-scénarios) + entraîner modèle v2 avec GridSearchCV
source .venv/bin/activate
python machine_learning/run_machine_learning.py \
  --mode=all \
  --dataset-version=v2 \
  --scenario-type=all \
  --tune-hyperparams \
  --grid-type=extended \
  --version=v2
```

## Comparaison des Modèles

### Tableau Récapitulatif

| Critère | v1 (best_move) | v2 (multi-scénarios) |
|---------|----------------|----------------------|
| **Dataset** | 34k échantillons | 880k échantillons |
| **Scénarios** | 1 (best_move) | 3 (best, random, all) |
| **Accuracy best_move** | 94.24% | ~94-95% |
| **Accuracy random_move** | N/A | ~92-93% |
| **Accuracy all_comb** | N/A | ~93-94% |
| **Temps entraînement** | ~2-5 min | ~30-60 min |
| **Taille modèle** | ~980 KB | ~1.2 MB |
| **GridSearchCV** | Non | Oui (243 combinaisons) |
| **Robustesse** | Moyenne | Excellente |

### Quand Utiliser Quel Modèle ?

#### Utilisez v1 si :
- ✅ Vous avez besoin d'un modèle simple et rapide
- ✅ L'adversaire utilise toujours son meilleur move (scénario compétitif)
- ✅ Vous voulez des performances maximales sur best_move
- ✅ Ressources limitées (temps/mémoire)

#### Utilisez v2 si :
- ✅ Vous voulez plus de robustesse sur différents types de combats
- ✅ Vous utilisez le paramètre `available_moves_b` de l'API
- ✅ L'adversaire ne joue pas toujours de manière optimale
- ✅ Vous voulez la meilleure généralisation possible

**Recommandation Générale**: **Utilisez v2 en production** pour sa robustesse, sauf si les contraintes de temps/ressources sont critiques.

## Chargement des Modèles

### Dans l'API (Production)

```python
from api_pokemon.services import prediction_service

# Le service charge automatiquement le modèle configuré (v1 ou v2)
model = prediction_service.prediction_model
model.load()  # Charge model, scalers, metadata

# Pour forcer une version spécifique
model.load(version='v2')
```

### Dans un Notebook (Analyse)

```python
import joblib

# Charger v1
model_v1 = joblib.load('models/battle_winner_model_v1.pkl')
scalers_v1 = joblib.load('models/battle_winner_scalers_v1.pkl')

# Charger v2
model_v2 = joblib.load('models/battle_winner_model_v2.pkl')
scalers_v2 = joblib.load('models/battle_winner_scalers_v2.pkl')

# Faire une prédiction
prediction = model_v2.predict(X_test)
probabilities = model_v2.predict_proba(X_test)
```

## Métadonnées

**Fichier**: [battle_winner_metadata.pkl](battle_winner_metadata.pkl)

**Contenu** (structure Python dict):
```python
{
    'model_version': 'v2',
    'model_type': 'XGBClassifier',
    'dataset_version': 'v2',
    'n_features': 133,
    'feature_names': [...],  # Liste des 133 features
    'scenarios': ['best_move', 'random_move', 'all_combinations'],
    'metrics': {
        'test_accuracy': 0.9324,
        'test_precision': 0.9327,
        'test_recall': 0.9321,
        'test_f1': 0.9324,
        'test_roc_auc': 0.9850
    },
    'hyperparameters': {...},
    'trained_at': '2026-01-24T10:30:00',
    'training_samples': 704000,  # 80% de 880k
    'test_samples': 176000,      # 20% de 880k
    'feature_engineering': {
        'scaler_1': 'StandardScaler (stats numériques)',
        'scaler_2': 'StandardScaler (features dérivées)',
        'encoding': 'OneHotEncoding (types)',
        'derived_features': 6
    }
}
```

## Top Features (Importance)

### Modèle v1

1. **stat_ratio** (15.0%) - Ratio des stats totales A/B
2. **effective_power_diff** (9.0%) - Différence de puissance effective
3. **hp_diff** (8.8%) - Différence de HP
4. **a_total_stats** (5.3%) - Stats totales de A
5. **b_total_stats** (4.6%) - Stats totales de B

### Modèle v2

1. **effective_power_diff** (12.5%) - Différence de puissance effective
2. **stat_ratio** (11.0%) - Ratio des stats totales A/B
3. **hp_diff** (9.2%) - Différence de HP
4. **a_moves_first** (7.8%) - A attaque en premier
5. **type_advantage_diff** (6.5%) - Différence d'avantage de type

**Note**: Les features importantes varient légèrement entre v1 et v2, reflétant les différents scénarios.

## Versionnement

Pour créer une nouvelle version :

1. Entraîner le nouveau modèle
2. Exporter avec suffixe versionné: `battle_winner_model_v3.pkl`
3. Mettre à jour `battle_winner_metadata.pkl`
4. Comparer les performances avec notebook `04_scenario_comparison.ipynb`
5. Déployer si amélioration significative (>1% accuracy ou meilleure robustesse)

## Notebooks d'Analyse

Pour analyser les modèles en détail, consultez les notebooks Jupyter :

- `notebooks/01_exploration.ipynb` - EDA avec analyse par scénario
- `notebooks/02_feature_engineering.ipynb` - Feature importance par scénario
- `notebooks/03_training_evaluation.ipynb` - Training avec GridSearchCV
- `notebooks/04_scenario_comparison.ipynb` - **Comparaison v1 vs v2**

---

**Dernière mise à jour**: 2024-01-24  
**Modèle recommandé**: **v2** (multi-scénarios avec GridSearchCV)
