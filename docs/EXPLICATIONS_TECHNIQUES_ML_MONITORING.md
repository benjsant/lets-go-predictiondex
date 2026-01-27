# 🧠 Explications Techniques Détaillées - ML & Monitoring

**Date:** 27 janvier 2026
**Objectif:** Comprendre en profondeur le fonctionnement du ML, Grafana, Evidently et leur intégration

---

## 📋 Table des Matières

1. [Pipeline Machine Learning Complet](#1-pipeline-machine-learning-complet)
2. [Monitoring Prometheus](#2-monitoring-prometheus)
3. [Visualisation Grafana](#3-visualisation-grafana)
4. [Drift Detection Evidently](#4-drift-detection-evidently)
5. [Intégration Complète](#5-intégration-complète)

---

## 1. Pipeline Machine Learning Complet

### 🎯 Vue d'Ensemble du Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   PIPELINE ML COMPLET                       │
└─────────────────────────────────────────────────────────────┘

Étape 1: Génération Dataset
────────────────────────────
PostgreSQL (188 Pokémon × 226 Moves)
         ↓
    Simulation Combats
    (3 scénarios × 898,472 combats)
         ↓
    battles_dataset_v2.parquet (220 MB)


Étape 2: Feature Engineering
─────────────────────────────
38 features brutes
         ↓
    One-Hot Encoding (types)
    + Normalisation (StandardScaler)
    + Features dérivées (ratios, diffs)
         ↓
    133 features engineered


Étape 3: Training
──────────────────
XGBoost Classifier
    ├─ n_estimators: 100
    ├─ max_depth: 6
    ├─ learning_rate: 0.1
    ├─ tree_method: 'hist' (CPU optimisé)
    └─ n_jobs: -1 (tous les cores)
         ↓
    Model trained (8 minutes)


Étape 4: Évaluation
────────────────────
Test Set (20% = 179,694 combats)
         ↓
    Métriques calculées:
    ├─ Accuracy: 88.23%
    ├─ Precision: 87.91%
    ├─ Recall: 88.57%
    ├─ F1-Score: 88.24%
    └─ ROC-AUC: 0.940


Étape 5: Export & Registry
───────────────────────────
Compression Joblib (zlib level 3)
         ↓
    Fichiers locaux:
    ├─ battle_winner_model_v2.pkl (39.8 MB)
    ├─ battle_winner_scalers_v2.pkl (12 KB)
    └─ battle_winner_metadata_v2.pkl (8 KB)
         ↓
    MLflow Model Registry
    ├─ Model enregistré (version 1)
    ├─ Artifacts uploadés
    └─ Auto-promotion si accuracy >= 85%


Étape 6: Serving
────────────────
API FastAPI
    ├─ Load model depuis MLflow (priorité 1)
    ├─ Fallback fichiers locaux (priorité 2)
    └─ Préload au startup (évite timeout)
         ↓
    Endpoint /predict/best-move
    ├─ Input: Pokemon A, Pokemon B, Moves disponibles
    ├─ Processing: Feature engineering + XGBoost predict
    └─ Output: Meilleur coup + probabilité victoire
```

---

### 📊 Étape 1: Génération Dataset - Détails

**Fichier:** `machine_learning/build_battle_winner_dataset_v2.py`

**Principe:**

Nous simulons **898,472 combats** entre tous les Pokémon avec différents movesets pour créer un dataset d'entraînement réaliste.

**3 Scénarios de Combat:**

#### Scénario 1: Best Move vs Best Move (299,491 combats)

```python
def generate_scenario_1_battles(db: Session):
    """
    Scénario réaliste: chaque Pokémon utilise son meilleur coup offensif.

    Pour chaque paire (Pokemon A, Pokemon B):
    1. Sélectionner meilleur coup offensif de A contre B
    2. Sélectionner meilleur coup offensif de B contre A
    3. Calculer features combat (stats, types, STAB, effectiveness)
    4. Simuler combat simplifié (qui frappe en premier, damage estimé)
    5. Déterminer vainqueur
    """
    type_effectiveness = load_type_chart(db)
    all_pokemon = db.query(Pokemon).all()  # 188 Pokémon

    battles = []

    for poke_a in all_pokemon:
        for poke_b in all_pokemon:
            if poke_a.id == poke_b.id:
                continue  # Pas de combat contre soi-même

            # Meilleur coup A
            best_move_a = select_best_offensive_move(
                poke_a, poke_b, type_effectiveness
            )

            # Meilleur coup B
            best_move_b = select_best_offensive_move(
                poke_b, poke_a, type_effectiveness
            )

            # Calculer features
            features = compute_battle_features(
                poke_a, poke_b,
                best_move_a, best_move_b
            )

            # Simuler combat
            winner = simulate_battle(
                poke_a, poke_b,
                best_move_a, best_move_b,
                type_effectiveness
            )

            battles.append({
                **features,
                'winner': 1 if winner == 'A' else 0
            })

    return battles

# Nombre combats: 188 × 187 = 35,156 matchups
# Mais avec movesets variés: ~299,491 combats
```

**Logique `simulate_battle()`:**

```python
def simulate_battle(poke_a, poke_b, move_a, move_b, type_eff):
    """
    Simulation simplifiée combat Pokémon.

    Règles:
    1. Priorité des moves (ex: Vive-Attaque = +1 priority)
    2. Si même priorité → Vitesse la plus élevée frappe en premier
    3. Damage = (Power × STAB × Type Multiplier × Attack/Defense ratio)
    4. HP diminuent jusqu'à KO
    5. Vainqueur = dernier debout
    """
    # Déterminer ordre attaque
    if move_a.priority > move_b.priority:
        first_attacker = 'A'
    elif move_a.priority < move_b.priority:
        first_attacker = 'B'
    else:
        first_attacker = 'A' if poke_a.speed > poke_b.speed else 'B'

    # HP initiaux
    hp_a = poke_a.stats.hp
    hp_b = poke_b.stats.hp

    # Combat tour par tour
    while hp_a > 0 and hp_b > 0:
        if first_attacker == 'A':
            # A attaque B
            damage = calculate_damage(poke_a, poke_b, move_a, type_eff)
            hp_b -= damage

            if hp_b <= 0:
                return 'A'  # A gagne

            # B contre-attaque
            damage = calculate_damage(poke_b, poke_a, move_b, type_eff)
            hp_a -= damage

            if hp_a <= 0:
                return 'B'  # B gagne

        else:
            # B attaque A (même logique inversée)
            ...

    return 'A' if hp_a > hp_b else 'B'
```

**Calcul Damage:**

```python
def calculate_damage(attacker, defender, move, type_eff):
    """
    Formule damage Pokémon simplifiée.

    Basée sur la vraie formule Pokémon mais simplifiée pour ML:
    Damage = (Power × STAB × Effectiveness × Stat Ratio) / 10
    """
    # Power brute
    power = move.power or 50

    # STAB (Same Type Attack Bonus = ×1.5)
    stab = 1.5 if move.type_id in [t.type_id for t in attacker.types] else 1.0

    # Type effectiveness (0, 0.25, 0.5, 1, 2, 4)
    effectiveness = get_type_multiplier(
        move.type_id,
        [t.type_id for t in defender.types],
        type_eff
    )

    # Stat ratio (Attack/Defense ou Sp.Attack/Sp.Defense)
    if move.category == 'physique':
        stat_ratio = attacker.stats.attack / (defender.stats.defense + 1)
    else:  # spécial
        stat_ratio = attacker.stats.sp_attack / (defender.stats.sp_defense + 1)

    # Damage final
    damage = (power * stab * effectiveness * stat_ratio) / 10

    # Variation aléatoire ±10%
    import random
    damage *= random.uniform(0.9, 1.1)

    return max(1, int(damage))  # Minimum 1 HP
```

---

#### Scénario 2: Random Moves (299,491 combats)

```python
def generate_scenario_2_battles(db: Session):
    """
    Scénario aléatoire: movesets random pour plus de diversité.

    Pour chaque paire (Pokemon A, Pokemon B):
    1. Sélectionner 1 coup random parmi tous les coups appris
    2. Répéter plusieurs fois avec différents coups
    3. Même simulation que scénario 1
    """
    for poke_a in all_pokemon:
        for poke_b in all_pokemon:
            # Obtenir tous les coups appris
            moves_a = [pm.move for pm in poke_a.moves if pm.move.power]
            moves_b = [pm.move for pm in poke_b.moves if pm.move.power]

            # Générer 5 combats random
            for _ in range(5):
                move_a = random.choice(moves_a)
                move_b = random.choice(moves_b)

                # Même logique simulation
                features = compute_battle_features(...)
                winner = simulate_battle(...)
                battles.append({**features, 'winner': winner})

    return battles
```

---

#### Scénario 3: Type Advantage Focus (299,490 combats)

```python
def generate_scenario_3_battles(db: Session):
    """
    Scénario avantage type: focus sur matchups stratégiques.

    Pour chaque paire (Pokemon A, Pokemon B):
    1. Sélectionner coup super efficace de A si existe (×2 ou ×4)
    2. Sinon coup neutre
    3. Même logique pour B
    4. Simulation combat
    """
    for poke_a in all_pokemon:
        for poke_b in all_pokemon:
            # Chercher coup super efficace
            super_effective_move_a = find_super_effective_move(
                poke_a, poke_b, type_effectiveness
            )

            if super_effective_move_a:
                move_a = super_effective_move_a
            else:
                move_a = select_best_offensive_move(poke_a, poke_b)

            # Même logique pour B
            move_b = ...

            # Simulation
            features = compute_battle_features(...)
            winner = simulate_battle(...)
            battles.append({**features, 'winner': winner})

    return battles
```

---

### 🧮 Étape 2: Feature Engineering - Détails

**Fichier:** `machine_learning/run_machine_learning.py` (fonction `engineer_features()`)

**Input:** 38 features brutes
**Output:** 133 features engineered

#### 38 Features Brutes

```python
raw_features = {
    # Pokemon A (14 features)
    'a_hp': int,                # Points de Vie
    'a_attack': int,            # Attaque
    'a_defense': int,           # Défense
    'a_sp_attack': int,         # Attaque Spéciale
    'a_sp_defense': int,        # Défense Spéciale
    'a_speed': int,             # Vitesse
    'a_total_stats': int,       # Somme stats (calculé)
    'a_type_1': str,            # Type primaire (ex: "électrik")
    'a_type_2': str,            # Type secondaire (ex: "vol", ou "none")
    'a_move_power': float,      # Puissance coup
    'a_move_type': str,         # Type coup (ex: "électrik")
    'a_move_priority': int,     # Priorité coup (-6 à +5)
    'a_move_stab': float,       # STAB (1.0 ou 1.5)
    'a_move_type_mult': float,  # Multiplicateur type (0, 0.25, 0.5, 1, 2, 4)

    # Pokemon B (14 features) - mêmes colonnes préfixées 'b_'
    'b_hp': int,
    'b_attack': int,
    # ... (14 features identiques)

    # Features dérivées de base (4 features)
    'speed_diff': int,          # a_speed - b_speed
    'hp_diff': int,             # a_hp - b_hp
    'a_moves_first': int,       # 1 si A frappe en premier, 0 sinon

    # Target
    'winner': int               # 1 si A gagne, 0 si B gagne
}
```

---

#### Transformation en 133 Features

**Étape 2.1: One-Hot Encoding des Types**

```python
def engineer_features(df_raw):
    """
    Transform 38 raw features → 133 engineered features.
    """
    # Types uniques dans le jeu (18 types)
    unique_types = [
        'plante', 'poison', 'feu', 'vol', 'eau', 'insecte',
        'combat', 'normal', 'sol', 'spectre', 'psy', 'acier',
        'ténèbres', 'glace', 'fée', 'électrik', 'dragon', 'roche',
        'none'  # Pour Pokémon mono-type
    ]

    # One-hot encoding pour 6 colonnes catégorielles
    categorical_cols = [
        'a_type_1',      # → 19 colonnes (a_type_1_plante, a_type_1_feu, ...)
        'a_type_2',      # → 19 colonnes
        'b_type_1',      # → 19 colonnes
        'b_type_2',      # → 19 colonnes
        'a_move_type',   # → 19 colonnes
        'b_move_type'    # → 19 colonnes
    ]

    X = df_raw.copy()

    for col in categorical_cols:
        dummies = pd.get_dummies(X[col], prefix=col, drop_first=False)
        X = pd.concat([X, dummies], axis=1)

    # Supprimer colonnes catégorielles originales
    X = X.drop(columns=categorical_cols)

    # Résultat: 32 features numériques + 6×19 = 146 colonnes
    # Mais certains types n'apparaissent jamais (ex: a_type_2_dragon très rare)
    # Donc ~133 colonnes after cleanup
```

---

**Étape 2.2: Normalisation Features Numériques**

```python
    # Features à normaliser (StandardScaler)
    numeric_features = [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power',
        'a_total_stats', 'b_total_stats',
        'speed_diff', 'hp_diff'
    ]

    # StandardScaler: (X - mean) / std
    scaler = StandardScaler()
    X[numeric_features] = scaler.fit_transform(X[numeric_features])

    # Exemple transformation:
    # a_hp = 300 → (300 - mean_hp) / std_hp → 1.34 (z-score)
    # a_attack = 50 → (50 - mean_attack) / std_attack → -0.87
```

---

**Étape 2.3: Features Dérivées**

```python
    # Créer 6 nouvelles features intelligentes

    # 1. Ratio stats totales (qui est globalement plus fort ?)
    X['stat_ratio'] = df_raw['a_total_stats'] / (df_raw['b_total_stats'] + 1)
    # Exemple: 500 / 400 = 1.25 (A 25% plus fort)

    # 2. Différence avantage type
    X['type_advantage_diff'] = df_raw['a_move_type_mult'] - df_raw['b_move_type_mult']
    # Exemple: 2.0 - 0.5 = 1.5 (A super efficace, B peu efficace)

    # 3. Puissance effective A (avec STAB + type)
    X['effective_power_a'] = (
        df_raw['a_move_power'] *
        df_raw['a_move_stab'] *
        df_raw['a_move_type_mult']
    )
    # Exemple: 90 × 1.5 (STAB) × 2.0 (super efficace) = 270

    # 4. Puissance effective B
    X['effective_power_b'] = (
        df_raw['b_move_power'] *
        df_raw['b_move_stab'] *
        df_raw['b_move_type_mult']
    )

    # 5. Différence puissance effective
    X['effective_power_diff'] = X['effective_power_a'] - X['effective_power_b']
    # Exemple: 270 - 120 = 150 (A beaucoup plus dangereux)

    # 6. Avantage priorité (qui frappe en premier ?)
    X['priority_advantage'] = df_raw['a_move_priority'] - df_raw['b_move_priority']
    # Exemple: +1 (Vive-Attaque) - 0 (move normal) = 1

    # Normaliser les nouvelles features
    scaler_new = StandardScaler()
    new_features = [
        'stat_ratio', 'type_advantage_diff',
        'effective_power_a', 'effective_power_b',
        'effective_power_diff', 'priority_advantage'
    ]
    X[new_features] = scaler_new.fit_transform(X[new_features])

    return X  # Shape: (898472, 133)
```

---

### 🤖 Étape 3: Training XGBoost - Détails

**Fichier:** `machine_learning/run_machine_learning.py` (fonction `train_model()`)

**Hyperparamètres XGBoost:**

```python
DEFAULT_XGBOOST_PARAMS = {
    # Nombre d'arbres de décision
    'n_estimators': 100,
    # 100 arbres équilibrés: pas d'overfitting, bon accuracy

    # Profondeur maximale arbres
    'max_depth': 6,
    # 6 niveaux: capture patterns complexes sans overfitting

    # Taux d'apprentissage
    'learning_rate': 0.1,
    # 0.1 = équilibre vitesse/accuracy

    # Méthode construction arbres
    'tree_method': 'hist',
    # 'hist' = Histogramme-based algorithm (3-5× plus rapide que 'exact')

    # Parallélisation CPU
    'n_jobs': -1,
    # -1 = utiliser tous les cores CPU disponibles

    # Random seed (reproductibilité)
    'random_state': 42,

    # Objective function
    'objective': 'binary:logistic',
    # Classification binaire (A gagne=1, B gagne=0)

    # Métriques évaluation
    'eval_metric': 'logloss',
    # Log loss = mesure qualité probabilités prédites
}
```

**Code training:**

```python
def train_model(X_train, y_train, X_test, y_test, hyperparams):
    """
    Entraînement XGBoost Classifier.

    Args:
        X_train: (718,778 samples, 133 features)
        y_train: (718,778 labels)
        X_test: (179,694 samples, 133 features)
        y_test: (179,694 labels)

    Returns:
        model: XGBoost model trained
        metrics: dict avec accuracy, precision, recall, F1, ROC-AUC
    """
    import xgboost as xgb
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

    # Créer modèle
    model = xgb.XGBClassifier(**hyperparams)

    # Training (8 minutes sur CPU 8 cores)
    print("🚀 Training XGBoost...")
    start_time = time.time()

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=10  # Afficher progression tous les 10 arbres
    )

    training_time = time.time() - start_time
    print(f"✅ Training completed in {training_time:.1f}s")

    # Prédictions test set
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]  # Probabilités classe 1

    # Calcul métriques
    metrics = {
        'test_accuracy': accuracy_score(y_test, y_pred),
        # 88.23% - Prédit le bon gagnant 88 fois sur 100

        'test_precision': precision_score(y_test, y_pred),
        # 87.91% - Quand prédit "A gagne", c'est vrai 88% du temps

        'test_recall': recall_score(y_test, y_pred),
        # 88.57% - Détecte 88.57% des vrais "A gagne"

        'test_f1': f1_score(y_test, y_pred),
        # 88.24% - Moyenne harmonique précision/recall

        'test_roc_auc': roc_auc_score(y_test, y_pred_proba),
        # 0.940 - Excellente discrimination (0.5=random, 1.0=parfait)

        'training_time_seconds': training_time,
        # ~480s (8 minutes)

        'n_features': X_train.shape[1],
        # 133 features

        'n_samples_train': len(X_train),
        # 718,778 combats

        'n_samples_test': len(X_test)
        # 179,694 combats
    }

    return model, metrics
```

**Output training (exemple):**

```
[0]     validation-logloss:0.61234
[10]    validation-logloss:0.42156
[20]    validation-logloss:0.36789
[30]    validation-logloss:0.33456
...
[90]    validation-logloss:0.28912
[100]   validation-logloss:0.28901  ← Convergence

✅ Training completed in 478.3s

Metrics:
  test_accuracy: 0.8823 (88.23%)
  test_precision: 0.8791
  test_recall: 0.8857
  test_f1: 0.8824
  test_roc_auc: 0.9403
```

---

### 💾 Étape 4: Export & Compression - Détails

**Fichier:** `machine_learning/run_machine_learning.py` (fonction `export_model()`)

**Compression Joblib:**

```python
def export_model(model, scalers, metadata, version='v2'):
    """
    Export modèle + scalers + metadata avec compression.

    Compression zlib level 3:
    - Sans compression: 401 MB (RandomForest) ou 120 MB (XGBoost)
    - Avec compression: 39.8 MB (XGBoost zlib-3) → -67% taille
    """
    import joblib
    from pathlib import Path

    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)

    # Export modèle (compression zlib niveau 3)
    model_path = models_dir / f'battle_winner_model_{version}.pkl'
    joblib.dump(model, model_path, compress=('zlib', 3))
    print(f"✅ Model saved: {model_path} ({model_path.stat().st_size / 1e6:.1f} MB)")

    # Export scalers (compression zlib niveau 9 car petit fichier)
    scalers_path = models_dir / f'battle_winner_scalers_{version}.pkl'
    joblib.dump(scalers, scalers_path, compress=('zlib', 9))
    print(f"✅ Scalers saved: {scalers_path} ({scalers_path.stat().st_size / 1e3:.1f} KB)")

    # Export metadata (JSON pour lisibilité)
    metadata_path = models_dir / f'battle_winner_metadata_{version}.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved: {metadata_path}")

# Output:
# ✅ Model saved: models/battle_winner_model_v2.pkl (39.8 MB)
# ✅ Scalers saved: models/battle_winner_scalers_v2.pkl (12.3 KB)
# ✅ Metadata saved: models/battle_winner_metadata_v2.json (8.1 KB)
```

**Contenu metadata.json:**

```json
{
  "model_type": "XGBClassifier",
  "version": "v2",
  "trained_at": "2026-01-27T14:32:15",
  "dataset_version": "v2",
  "n_features": 133,
  "n_samples_train": 718778,
  "n_samples_test": 179694,
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "tree_method": "hist",
    "n_jobs": -1
  },
  "metrics": {
    "test_accuracy": 0.8823,
    "test_precision": 0.8791,
    "test_recall": 0.8857,
    "test_f1": 0.8824,
    "test_roc_auc": 0.9403,
    "train_accuracy": 0.9821,
    "train_roc_auc": 0.9987
  },
  "training_time_seconds": 478.3,
  "features": [
    "a_hp", "a_attack", "a_defense", ...,
    "a_type_1_électrik", "a_type_1_feu", ...,
    "stat_ratio", "type_advantage_diff", ...
  ]
}
```

---

## 2. Monitoring Prometheus

### 🎯 Architecture Prometheus

```
┌─────────────────────────────────────────────────────┐
│              PROMETHEUS MONITORING                  │
└─────────────────────────────────────────────────────┘

API FastAPI (port 8080)
    │
    ├─ PrometheusMiddleware (api_pokemon/monitoring/metrics.py)
    │  ├─ Intercept toutes les requêtes
    │  ├─ Mesure latence (start → end)
    │  ├─ Track status codes (200, 404, 500)
    │  └─ Update métriques Prometheus
    │
    ├─ /metrics endpoint (exposition métriques)
    │  └─ Format: Prometheus text exposition format
    │
    └─ track_prediction() dans routes
       └─ Log métriques ML spécifiques

         ↓ Scrape HTTP GET /metrics

Prometheus Server (port 9091)
    │
    ├─ Scrape config (docker/prometheus/prometheus.yml)
    │  ├─ job 'api' → scrape_interval: 10s
    │  ├─ job 'prometheus' → self-monitoring
    │  └─ job 'node' → node-exporter (métriques système)
    │
    ├─ TSDB (Time Series Database)
    │  └─ Stockage métriques par timestamp
    │
    └─ Alert Manager (rules: docker/prometheus/alerts.yml)
       ├─ HighAPILatency (P95 > 500ms pendant 2min)
       ├─ HighErrorRate (errors/s > 0.05 pendant 2min)
       ├─ HighModelLatency (P95 > 100ms pendant 2min)
       └─ HighCPUUsage (> 80% pendant 5min)

         ↓ Query PromQL

Grafana (port 3001)
    │
    ├─ Datasource: Prometheus
    ├─ Dashboard API Performance
    └─ Dashboard Model Performance

         ↓ Visualisation

Utilisateur (Jury Soutenance)
```

---

### 📊 Métriques Collectées - Détail

**Fichier:** `api_pokemon/monitoring/metrics.py`

#### Métriques API

```python
from prometheus_client import Counter, Histogram, Gauge

# 1. Compteur requêtes totales
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']  # Labels pour segmentation
)

# Exemple utilisation:
# api_requests_total.labels(method='POST', endpoint='/predict/best-move', status='200').inc()
# → Incrémente compteur

# Requêtes PromQL:
# api_requests_total                                    → Toutes requêtes
# api_requests_total{endpoint="/predict/best-move"}    → Seulement prédictions
# rate(api_requests_total[5m])                         → Requêtes/seconde (5min window)
```

```python
# 2. Histogramme latence requêtes
api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]  # Buckets latence
)

# Exemple utilisation:
# start = time.time()
# response = await call_next(request)
# duration = time.time() - start
# api_request_duration_seconds.labels(method='POST', endpoint='/predict/best-move').observe(duration)
# → Enregistre durée dans histogramme

# Requêtes PromQL:
# histogram_quantile(0.50, rate(api_request_duration_seconds_bucket[5m]))  → P50 (médiane)
# histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))  → P95
# histogram_quantile(0.99, rate(api_request_duration_seconds_bucket[5m]))  → P99
```

---

#### Métriques ML

```python
# 3. Compteur prédictions modèle
model_predictions_total = Counter(
    'model_predictions_total',
    'Total number of model predictions',
    ['model_version']  # Label version modèle
)

# Exemple:
# model_predictions_total.labels(model_version='v2').inc()

# Requêtes PromQL:
# rate(model_predictions_total[5m])  → Prédictions/seconde
# sum(model_predictions_total)       → Total prédictions depuis démarrage
```

```python
# 4. Histogramme latence prédiction ML
model_prediction_duration_seconds = Histogram(
    'model_prediction_duration_seconds',
    'Model prediction duration in seconds',
    ['model_version'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]  # Latence ML (plus rapide qu'API)
)

# Exemple:
# start = time.time()
# prediction = model.predict(features)
# duration = time.time() - start
# model_prediction_duration_seconds.labels(model_version='v2').observe(duration)

# Requêtes PromQL:
# histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))  → P95 latence ML
```

```python
# 5. Gauge confiance modèle
model_confidence_score = Gauge(
    'model_confidence_score',
    'Model prediction confidence score (0-1)',
    ['model_version']
)

# Exemple:
# probability = model.predict_proba(features)[0]
# confidence = max(probability)  # Max des 2 probabilités (classe 0, classe 1)
# model_confidence_score.labels(model_version='v2').set(confidence)

# Requêtes PromQL:
# model_confidence_score        → Dernière valeur confiance
# avg_over_time(model_confidence_score[1h])  → Moyenne confiance dernière heure
```

```python
# 6. Histogramme distribution probabilités victoire
model_win_probability = Histogram(
    'model_win_probability',
    'Distribution of win probabilities',
    ['model_version'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]  # 11 buckets
)

# Exemple:
# win_prob = model.predict_proba(features)[0][1]  # Probabilité classe "A gagne"
# model_win_probability.labels(model_version='v2').observe(win_prob)

# Requêtes PromQL:
# histogram_quantile(0.50, rate(model_win_probability_bucket[1h]))  → Médiane probabilité
# sum(rate(model_win_probability_bucket{le="0.6"}[1h]))  → % prédictions incertaines (<60%)
```

---

### 🔍 Middleware Prometheus - Code Détaillé

**Fichier:** `api_pokemon/monitoring/metrics.py:154-213`

```python
class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware FastAPI pour tracking automatique métriques Prometheus.

    Intercept toutes les requêtes HTTP et log:
    - Nombre requêtes (par méthode/endpoint/status)
    - Latence requête
    - Erreurs
    - Métriques système (CPU, RAM)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track metrics.

        Flow:
        1. Request arrive
        2. Start timer
        3. Call next handler (route API)
        4. Response générée
        5. Stop timer
        6. Update métriques Prometheus
        7. Return response
        """
        # Skip /metrics endpoint (éviter boucle infinie)
        if request.url.path == "/metrics":
            return await call_next(request)

        # Start timer
        start_time = time.time()

        try:
            # Call API handler (ex: predict_best_move())
            response = await call_next(request)

            # Stop timer
            duration = time.time() - start_time

            # Track successful request
            track_request(
                method=request.method,        # 'POST'
                endpoint=request.url.path,    # '/predict/best-move'
                status=response.status_code,  # 200
                duration=duration             # 0.327 seconds
            )

            # Update system metrics (CPU, RAM)
            update_system_metrics()

            return response

        except Exception as e:
            # Track error
            duration = time.time() - start_time

            track_error(
                method=request.method,
                endpoint=request.url.path,
                error_type=type(e).__name__  # 'ValueError', 'DatabaseError'
            )

            # Also track as failed request (status 500)
            track_request(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                duration=duration
            )

            # Re-raise exception
            raise
```

**Fonction tracking:**

```python
def track_request(method: str, endpoint: str, status: int, duration: float):
    """
    Track une requête API.

    Updates:
    - api_requests_total (Counter)
    - api_request_duration_seconds (Histogram)
    """
    # Increment counter
    api_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()

    # Record duration
    api_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)
```

---

### 📈 Queries PromQL Utiles

**Dans Prometheus UI (http://localhost:9091):**

```promql
# 1. Request Rate (requêtes/seconde)
rate(api_requests_total[5m])

# 2. Request Rate par endpoint
sum(rate(api_requests_total[5m])) by (endpoint)

# 3. Latence P95 API
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# 4. Error Rate
rate(api_errors_total[5m])

# 5. Success Rate (%)
sum(rate(api_requests_total{status=~"2.."}[5m])) /
sum(rate(api_requests_total[5m])) * 100

# 6. Prédictions ML par seconde
rate(model_predictions_total[5m])

# 7. Latence P95 modèle ML
histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))

# 8. CPU usage
system_cpu_usage_percent

# 9. Memory usage (%)
(system_memory_usage_bytes / (system_memory_usage_bytes + system_memory_available_bytes)) * 100

# 10. Top 5 endpoints les plus lents
topk(5, histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])))
```

---

## 3. Visualisation Grafana

### 📊 Dashboards Grafana - Architecture

```
Grafana (http://localhost:3001)
    │
    ├─ Datasource Configuration
    │  └─ Prometheus: http://prometheus:9090
    │
    ├─ Dashboard 1: API Performance
    │  │  (docker/grafana/dashboards/api_performance.json)
    │  │
    │  ├─ Panel 1: Request Rate
    │  │  └─ Query: rate(api_requests_total[5m])
    │  │
    │  ├─ Panel 2: Latency P50/P95/P99
    │  │  └─ Query: histogram_quantile(0.95, rate(...))
    │  │
    │  ├─ Panel 3: Error Rate
    │  │  └─ Query: rate(api_errors_total[5m])
    │  │
    │  ├─ Panel 4: Status Codes Distribution
    │  │  └─ Query: sum(rate(...)) by (status)
    │  │
    │  └─ Panel 5: Response Time Heatmap
    │     └─ Query: histogram buckets
    │
    └─ Dashboard 2: Model Performance
       │  (docker/grafana/dashboards/model_performance.json)
       │
       ├─ Panel 1: Predictions per Second
       │  └─ Query: rate(model_predictions_total[5m])
       │
       ├─ Panel 2: Model Latency P95
       │  └─ Query: histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))
       │
       ├─ Panel 3: Confidence Score Over Time
       │  └─ Query: model_confidence_score
       │
       └─ Panel 4: Win Probability Distribution
          └─ Query: rate(model_win_probability_bucket[1h])
```

---

### 🎨 Créer un Panel Grafana (Exemple)

**Panel: Latence P95 Prédictions ML**

1. **Ouvrir Grafana:** http://localhost:3001 (admin/admin)
2. **Create → Dashboard → Add Panel**
3. **Configuration:**

```
Title: Model Prediction Latency (P95)

Query:
  histogram_quantile(0.95,
    rate(model_prediction_duration_seconds_bucket{model_version="v2"}[5m])
  )

Visualization: Time series (line chart)

Y-axis:
  - Unit: seconds (s)
  - Min: 0
  - Max: auto

Thresholds:
  - Green: 0 - 0.05s (< 50ms)
  - Yellow: 0.05 - 0.1s (50-100ms)
  - Red: > 0.1s (> 100ms)

Legend:
  - Show: Yes
  - Values: Last, Min, Max, Avg
```

4. **Apply**

**Résultat:** Graph montrant latence P95 du modèle ML en temps réel.

---

## 4. Drift Detection Evidently

### 🔍 Fonctionnement Evidently AI

**Fichier:** `api_pokemon/monitoring/drift_detection.py`

#### Architecture Drift Detection

```
┌────────────────────────────────────────────────────────┐
│            EVIDENTLY DRIFT DETECTION                   │
└────────────────────────────────────────────────────────┘

Training (one-time)
    │
    ├─ X_train.parquet (718,778 samples)
    │  └─ Sample 10,000 random samples
    │     → Reference Dataset (baseline)
    │
    └─ Save reference data
       └─ data/datasets/X_train_reference.parquet


Production (continuous)
    │
    ├─ API Prediction /predict/best-move
    │  └─ drift_detector.add_prediction(features, prediction, probability)
    │
    ├─ Production Buffer (in-memory)
    │  ├─ Max size: 1,000 predictions
    │  └─ Auto-save every 1,000 predictions
    │
    ├─ Trigger Report (2 conditions)
    │  ├─ Buffer full (1,000 predictions)
    │  └─ OU 1 hour elapsed
    │
    └─ Generate Drift Report
       │
       ├─ Create Production Dataset from buffer
       │  └─ Convert buffer → pandas DataFrame
       │
       ├─ Evidently Report
       │  ├─ DataDriftPreset (auto-configure tests)
       │  └─ Compare Production vs Reference
       │
       ├─ Calculate Drift Metrics
       │  ├─ Dataset Drift: True/False
       │  ├─ Number of drifted features: 5/133
       │  └─ Share of drifted features: 3.7%
       │
       ├─ Save Outputs
       │  ├─ HTML Dashboard (interactive)
       │  ├─ JSON Report (metrics)
       │  └─ Production Data (parquet for retraining)
       │
       └─ Clear Buffer (reset to 0)
```

---

#### Code Drift Detection - Détails

```python
class DriftDetector:
    """
    Singleton drift detection avec Evidently AI 0.7.

    Design Pattern: Singleton (1 seule instance dans l'app)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return  # Déjà initialisé

        self._initialized = True

        # 1. Load reference data (training set)
        self._load_reference_data()
        # → Charge X_train.parquet, sample 10k lignes, crée Evidently Dataset

        # 2. Production buffer
        self.production_buffer = []  # List[Dict]
        self.max_buffer_size = 1000

        # 3. Auto-report config
        self.report_frequency = timedelta(hours=1)
        self.last_report_time = datetime.now()

    def _load_reference_data(self):
        """
        Load reference data from training set.

        Steps:
        1. Read X_train.parquet (718,778 samples, 133 features)
        2. Sample 10,000 random rows (reproductible avec random_state=42)
        3. Convert to Evidently Dataset
        """
        try:
            # Try local path
            ref_file = Path("data/datasets/X_train.parquet")
            if not ref_file.exists():
                # Try Docker mount
                ref_file = Path("/app/data/datasets/X_train.parquet")

            if not ref_file.exists():
                self.logger.warning("Reference data not found. Drift detection disabled.")
                self.reference_data = None
                return

            # Load & sample
            reference_df = pd.read_parquet(ref_file)
            sampled_df = reference_df.sample(n=min(10000, len(reference_df)), random_state=42)

            # Create Evidently Dataset
            from evidently import Dataset, DataDefinition
            self.data_definition = DataDefinition()
            self.reference_data = Dataset.from_pandas(
                sampled_df,
                data_definition=self.data_definition
            )

            self.logger.info(f"✅ Reference data loaded: {sampled_df.shape}")

        except Exception as e:
            self.logger.error(f"Failed to load reference data: {e}")
            self.reference_data = None
```

---

#### Ajout Prédiction au Buffer

```python
    def add_prediction(self, features: Dict, prediction: int, probability: float):
        """
        Add prediction to production buffer.

        Called by API after each prediction:
        api_pokemon/routes/prediction_route.py:88-96

        Args:
            features: Dict avec features input (ex: pokemon_a_id, pokemon_b_id, move_name)
            prediction: 0 (B gagne) ou 1 (A gagne)
            probability: Probabilité victoire (0.0 à 1.0)
        """
        if self.reference_data is None:
            return  # Drift detection disabled

        # Add to buffer with timestamp
        prediction_data = {
            **features,  # Unpack features dict
            'predicted_winner': prediction,
            'win_probability': probability,
            'timestamp': datetime.now().isoformat()
        }

        self.production_buffer.append(prediction_data)

        # Check if buffer is full (trigger auto-report)
        if len(self.production_buffer) >= self.max_buffer_size:
            self.logger.info(f"Buffer full ({self.max_buffer_size}). Generating drift report.")
            self.generate_drift_report()
            self.production_buffer = []  # Clear buffer

        # Check if it's time to generate report (1 hour elapsed)
        if datetime.now() - self.last_report_time >= self.report_frequency:
            if len(self.production_buffer) > 0:
                self.generate_drift_report()
                self.production_buffer = []
```

---

#### Génération Rapport Drift

```python
    def generate_drift_report(self) -> Dict:
        """
        Generate drift report using Evidently AI 0.7.

        Steps:
        1. Convert buffer → pandas DataFrame
        2. Create Evidently Dataset (production)
        3. Create Evidently Report with DataDriftPreset
        4. Run report (compare production vs reference)
        5. Save HTML dashboard + JSON metrics
        6. Return drift summary
        """
        if self.reference_data is None:
            return {}

        if len(self.production_buffer) == 0:
            return {}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # 1. Create DataFrame from buffer
            production_df = pd.DataFrame(self.production_buffer)

            # 2. Create Evidently Dataset
            production_dataset = Dataset.from_pandas(
                production_df,
                data_definition=self.data_definition
            )

            # 3. Create Evidently Report with DataDriftPreset
            from evidently import Report
            from evidently.presets import DataDriftPreset

            report = Report([DataDriftPreset()])

            # 4. Run report (compare production vs reference)
            report.run(
                current_data=production_dataset,
                reference_data=self.reference_data
            )

            # 5. Save JSON
            report_file = self.drift_reports_dir / f"drift_report_{timestamp}.json"
            with open(report_file, 'w') as f:
                f.write(report.json())

            # 6. Save HTML dashboard
            dashboard_file = self.drift_reports_dir / f"drift_dashboard_{timestamp}.html"
            report.save_html(str(dashboard_file))

            self.logger.info(f"✅ Drift report generated: {dashboard_file}")

            # 7. Extract drift summary from report
            drift_dict = report.as_dict()
            metrics_data = drift_dict.get('metrics', [])

            # Find DatasetDriftMetric in metrics list
            drift_result = {}
            for metric in metrics_data:
                if 'DatasetDriftMetric' in str(type(metric)):
                    drift_result = metric.get('result', {})
                    break

            drift_summary = {
                'timestamp': timestamp,
                'n_features': drift_result.get('number_of_columns', 0),
                'n_drifted_features': drift_result.get('number_of_drifted_columns', 0),
                'share_drifted_features': drift_result.get('share_of_drifted_columns', 0),
                'dataset_drift': drift_result.get('dataset_drift', False),
            }

            # Save summary JSON
            summary_file = self.drift_reports_dir / f"drift_summary_{timestamp}.json"
            with open(summary_file, 'w') as f:
                json.dump(drift_summary, f, indent=2)

            # Update last report time
            self.last_report_time = datetime.now()

            self.logger.info(
                f"Drift detected: {drift_summary['n_drifted_features']}/{drift_summary['n_features']} features "
                f"({drift_summary['share_drifted_features']:.1%})"
            )

            return drift_summary

        except Exception as e:
            self.logger.error(f"Failed to generate drift report: {e}", exc_info=True)
            return {}
```

---

#### Interprétation Rapport Evidently

**Fichier HTML:** `drift_dashboard_20260127_143052.html`

**Sections du rapport:**

1. **Dataset Summary**
   - Reference dataset: 10,000 samples, 133 features
   - Production dataset: 1,000 samples, 133 features

2. **Dataset Drift**
   - Drift detected: **True** ou **False**
   - Share of drifted features: **3.7%** (5/133 features)

3. **Feature Drift Details**
   - Liste des 5 features driftées:
     - `a_hp`: drift score 0.234 (distribution changée)
     - `b_attack`: drift score 0.189
     - `effective_power_a`: drift score 0.156
     - `stat_ratio`: drift score 0.145
     - `a_move_type_mult`: drift score 0.123

4. **Distribution Plots**
   - Histogrammes reference (bleu) vs production (orange)
   - Permet de voir visuellement le shift de distribution

**Que faire si drift détecté ?**

1. **Analyser les causes:**
   - Nouvelles combinaisons Pokémon utilisées ?
   - Meta-game a changé (nouveaux mouvements populaires) ?
   - Données production != données training ?

2. **Actions:**
   - **Si drift minime (< 10%):** Continuer monitoring
   - **Si drift modéré (10-30%):** Retraining modèle recommandé
   - **Si drift sévère (> 30%):** Retraining urgent + investigation

3. **Retraining:**
   ```bash
   # Récupérer production data sauvegardée
   # api_pokemon/monitoring/drift_data/production_data_*.parquet

   # Fusionner avec training set
   # Retrainer modèle avec nouvelles données
   python machine_learning/run_machine_learning.py --mode=retrain --production-data=...

   # Auto-promotion via MLflow si accuracy > 85%
   ```

---

## 5. Intégration Complète

### 🔗 Flow Complet: Prédiction → Monitoring → Drift Detection

```
USER REQUEST
    │
    │  POST /predict/best-move
    │  {
    │    "pokemon_a_id": 25,
    │    "pokemon_b_id": 1,
    │    "available_moves": ["Fatal-Foudre"]
    │  }
    │
    ▼
┌─────────────────────────────────────────────┐
│  1. PrometheusMiddleware                    │
│     - Start timer                           │
│     - Track request START                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  2. API Route /predict/best-move            │
│     - Validate input (Pydantic)             │
│     - Load model from MLflow Registry       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  3. prediction_service.predict_best_move()  │
│     - Query Pokemon A & B from PostgreSQL   │
│     - Select best move B (opponent)         │
│     - Prepare features (38 raw features)    │
│     - Feature engineering (133 features)    │
│     - XGBoost predict                       │
│     - Return result                         │
└─────────────────┬───────────────────────────┘
                  │
                  │  result = {
                  │    "recommended_move": "Fatal-Foudre",
                  │    "win_probability": 0.8734,
                  │    "all_moves": [...]
                  │  }
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  4. Track Prediction Metrics (Prometheus)   │
│     - track_prediction(                     │
│         model_version="v2",                 │
│         duration=0.327s,                    │
│         confidence=0.8734,                  │
│         win_prob=0.8734                     │
│       )                                     │
│     - Update Prometheus metrics:            │
│       • model_predictions_total += 1        │
│       • model_prediction_duration += 0.327s │
│       • model_confidence_score = 0.8734     │
│       • model_win_probability += 0.8734     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  5. Drift Detection (Evidently)             │
│     - drift_detector.add_prediction(        │
│         features={...},                     │
│         prediction=1,                       │
│         probability=0.8734                  │
│       )                                     │
│     - Add to buffer (now: 543/1000)         │
│     - If buffer full → generate_report()    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  6. PrometheusMiddleware (END)              │
│     - Stop timer (duration: 0.327s)         │
│     - Track request SUCCESS                 │
│     - api_requests_total += 1               │
│     - api_request_duration += 0.327s        │
│     - Update system metrics (CPU, RAM)      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  7. Return JSON Response                    │
│     {                                       │
│       "recommended_move": "Fatal-Foudre",   │
│       "win_probability": 0.8734,            │
│       ...                                   │
│     }                                       │
└─────────────────────────────────────────────┘
                  │
                  ▼
              USER


BACKGROUND (Continuous)
═══════════════════════

Prometheus (every 10s)
    │
    ├─ Scrape /metrics endpoint
    │  └─ Get latest metric values
    │
    ├─ Store in TSDB (Time Series Database)
    │  └─ Timeseries data with timestamps
    │
    └─ Evaluate Alert Rules
       ├─ If P95 latency > 500ms for 2min → Alert
       └─ If error rate > 5% for 2min → Alert


Grafana (real-time)
    │
    ├─ Query Prometheus every 5s
    │  └─ Refresh dashboards
    │
    └─ Display visualizations
       ├─ Request rate graph
       ├─ Latency heatmap
       └─ Model performance charts


Evidently (every 1000 predictions OR 1 hour)
    │
    ├─ Buffer reaches 1000 predictions
    │  └─ Trigger drift report generation
    │
    ├─ Compare production vs reference
    │  └─ Statistical tests (KS test, Chi-square, etc.)
    │
    ├─ Generate HTML + JSON reports
    │  └─ Save to api_pokemon/monitoring/drift_reports/
    │
    └─ Clear buffer (reset to 0)
```

---

**Voilà ! Vous avez maintenant une compréhension complète du ML et du Monitoring.**

**Créé le:** 27 janvier 2026
**Pour:** Certification RNCP E1/E3
**Niveau:** Explications détaillées production-ready
