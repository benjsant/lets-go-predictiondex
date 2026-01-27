# 🎓 Guide de Démonstration Complète - PredictionDex

**Date:** 27 janvier 2026
**Pour:** Soutenance Certification RNCP E1/E3
**Durée totale:** 25-30 minutes

---

## 📋 Table des Matières

1. [Préparation Avant Démonstration](#1-préparation-avant-démonstration-5-min)
2. [Démonstration Complète (20 min)](#2-démonstration-complète-20-min)
3. [Questions/Réponses Anticipées](#3-questionsréponses-anticipées)

---

## 1. Préparation Avant Démonstration (5 min)

### ✅ Checklist Pré-Démo

```bash
# 1. Vérifier que tout est arrêté
cd /path/to/lets-go-predictiondex
docker-compose down -v

# 2. Nettoyer containers/volumes
docker system prune -f
docker volume prune -f

# 3. Vérifier les fichiers requis
ls -lh models/battle_winner_model_v2.pkl         # Modèle ML
ls -lh data/datasets/X_train.parquet             # Reference data Evidently
ls -lh data/datasets/battles_dataset_v2.parquet  # Dataset ML

# 4. Vérifier .env
cat .env
# Doit contenir:
# - POSTGRES_* (credentials DB)
# - API_KEYS (clé API)
# - MLFLOW_TRACKING_URI=http://mlflow:5000

# 5. Démarrer l'infrastructure complète
docker-compose up -d

# 6. Attendre que tout soit prêt (2 minutes)
echo "⏳ Attente services (2 min)..."
sleep 120

# 7. Vérifier les services
docker-compose ps
# Tous doivent être "Up" (healthy)
```

### 🔍 Vérification Rapide Endpoints

```bash
# API
curl http://localhost:8080/health
# Réponse: {"status":"healthy"}

# MLflow
curl http://localhost:5001/health
# Réponse: {"status":"ok"}

# Prometheus
curl http://localhost:9091/-/healthy
# Réponse: "Prometheus is Healthy."

# Streamlit
curl http://localhost:8502
# Réponse: HTML (page chargée)

# Grafana
curl http://localhost:3001/api/health
# Réponse: {"commit":"...","database":"ok"}
```

**Si un service est down:**
```bash
# Vérifier les logs
docker-compose logs api
docker-compose logs mlflow
docker-compose logs streamlit

# Redémarrer le service problématique
docker-compose restart api
```

---

## 2. Démonstration Complète (20 min)

### 🎯 Plan de Démonstration

| Étape | Durée | Objectif | Compétences |
|-------|-------|----------|-------------|
| 1. Architecture Projet | 2 min | Vue d'ensemble | E1, E3 |
| 2. Pipeline ETL | 3 min | Collecte données | C1, C2, C3 |
| 3. Base de Données | 2 min | Stockage structuré | C4 |
| 4. Machine Learning | 4 min | Modèle IA | C12 |
| 5. API REST | 3 min | Exposition modèle | C9, C10 |
| 6. Interface Streamlit | 2 min | Application finale | C10 |
| 7. Monitoring | 3 min | Métriques + Drift | C11 |
| 8. CI/CD MLOps | 3 min | Livraison continue | C13 |

---

### Étape 1: Architecture Projet (2 min)

**Objectif:** Montrer la vue d'ensemble du projet

**Script:**

> "PredictionDex est une application MLOps complète pour prédire le meilleur coup Pokémon.
> L'architecture suit une approche microservices avec 9 conteneurs Docker."

**Montrer:**

```bash
# 1. Afficher l'arborescence
tree -L 2 -I '.venv|__pycache__|node_modules'

# 2. Montrer docker-compose.yml
cat docker-compose.yml | head -40
```

**Expliquer les 9 services:**

```yaml
services:
  db:           # PostgreSQL - Base de données
  etl:          # Pipeline ETL - Collecte données
  ml_builder:   # Training ML - Entraînement modèle
  api:          # FastAPI - Exposition modèle IA
  streamlit:    # Interface utilisateur
  mlflow:       # Model Registry - Versioning modèle
  prometheus:   # Métriques temps réel
  grafana:      # Dashboards visualisation
  node-exporter:# Métriques système
```

**Diagramme à montrer:**

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ PokéAPI     │────▶│ ETL Pipeline │────▶│ PostgreSQL  │
│ Pokepedia   │     │ (Scrapy)     │     │ (11 tables) │
│ CSV Files   │     └──────────────┘     └─────────────┘
└─────────────┘                                │
                                               │
                    ┌──────────────────────────┘
                    ▼
            ┌──────────────┐
            │  ML Builder  │
            │  (XGBoost)   │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐     ┌─────────────┐
            │ MLflow       │────▶│ FastAPI     │
            │ (Registry)   │     │ (Predict)   │
            └──────────────┘     └─────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            ┌──────────────┐   ┌─────────────┐  ┌──────────────┐
            │ Streamlit    │   │ Prometheus  │  │ Evidently    │
            │ (Interface)  │   │ (Metrics)   │  │ (Drift)      │
            └──────────────┘   └─────┬───────┘  └──────────────┘
                                     ▼
                              ┌─────────────┐
                              │ Grafana     │
                              │ (Dashboards)│
                              └─────────────┘
```

---

### Étape 2: Pipeline ETL (3 min) - **C1, C2, C3**

**Objectif:** Démontrer la collecte et nettoyage des données

#### C1: Extraction Données Automatisée

**Script:**

> "Le pipeline ETL collecte automatiquement les données depuis 3 sources hétérogènes."

**Montrer le code ETL:**

```bash
# 1. Scraper Pokepedia (scraping web)
cat etl_pokemon/pokepedia_scraper/pokepedia_scraper/spiders/lgpe_moves_sql_spider.py | head -50
```

**Expliquer:**

```python
class LgpeMovesSpider(scrapy.Spider):
    """Spider Scrapy pour scraper les capacités Pokepedia"""

    name = 'lgpe_moves_sql'
    start_urls = ['https://www.pokepedia.fr/Liste_des_capacités']

    def parse(self, response):
        # Extraction HTML table → SQL inserts
        for row in response.css('table.sortable tr'):
            move_name = row.css('td:nth-child(2) a::text').get()
            move_type = row.css('td:nth-child(3)::text').get()
            # ... extraction 10+ champs
            yield {
                'name': move_name,
                'type': move_type,
                'power': power,
                'accuracy': accuracy,
                # ...
            }
```

**Montrer l'appel PokéAPI:**

```bash
cat etl_pokemon/scripts/etl_enrich_pokeapi.py | grep -A 10 "def fetch_from_pokeapi"
```

```python
def fetch_from_pokeapi(pokemon_id: int):
    """Appel API REST PokéAPI pour enrichir données"""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    response = requests.get(url, timeout=10)
    data = response.json()

    # Extraction stats, types, sprites
    return {
        'hp': data['stats'][0]['base_stat'],
        'attack': data['stats'][1]['base_stat'],
        # ... 6 stats
        'sprite_url': data['sprites']['front_default']
    }
```

**Montrer le CSV:**

```bash
head -5 data/csv/pokemon_species.csv
```

**Résultat:** 3 sources automatisées ✅

---

#### C2: Requêtes SQL Extraction

**Montrer les requêtes SQL:**

```bash
# 1. Exemple requête complexe extraction
cat core/db/guards/pokemon.py | grep -A 20 "def get_pokemon_with_moves"
```

```python
def get_pokemon_with_moves(db: Session, pokemon_id: int):
    """Requête SQL jointure multiple pour extraction données"""
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.stats),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
            joinedload(Pokemon.moves).joinedload(PokemonMove.move)
        )
        .filter(Pokemon.id == pokemon_id)
        .first()
    )
```

**Expliquer:**
- ✅ Requête SQL avec jointures (4 tables)
- ✅ Optimisation eager loading (N+1 évité)
- ✅ Extraction complète données Pokémon

---

#### C3: Agrégation et Nettoyage

**Montrer le script d'agrégation:**

```bash
cat etl_pokemon/scripts/etl_post_process.py | head -80
```

**Expliquer les étapes:**

```python
def aggregate_and_clean_data(db: Session):
    """Agrégation multi-sources + nettoyage"""

    # 1. Suppression entrées corrompues
    corrupted = db.query(Pokemon).filter(Pokemon.stats == None).all()
    for p in corrupted:
        db.delete(p)

    # 2. Homogénéisation formats
    for move in db.query(Move).all():
        # Normaliser noms (accents, casse)
        move.name = normalize_move_name(move.name)

        # Convertir types string → ID
        move.type_id = get_or_create_type(db, move.type_name)

    # 3. Agrégation affinités types
    for type_a in all_types:
        for type_b in all_types:
            multiplier = calculate_effectiveness(type_a, type_b)
            # Insérer dans table type_effectiveness
            db.add(TypeEffectiveness(
                attacking_type_id=type_a.id,
                defending_type_id=type_b.id,
                multiplier=multiplier
            ))

    db.commit()
```

**Résultat:** Données nettoyées et agrégées ✅

---

### Étape 3: Base de Données (2 min) - **C4, C5**

#### C4: Base de Données PostgreSQL

**Script:**

> "La base PostgreSQL est normalisée 3NF avec 11 tables et contraintes d'intégrité."

**Montrer le schéma:**

```bash
# Connexion PostgreSQL
docker-compose exec db psql -U letsgo_user -d letsgo_db

# Liste tables
\dt

# Schéma table pokemon
\d pokemon

# Schéma table type_effectiveness
\d type_effectiveness

# Quitter
\q
```

**Expliquer la normalisation:**

```sql
-- Table pokemon (entité principale)
CREATE TABLE pokemon (
    id SERIAL PRIMARY KEY,
    species_id INT REFERENCES pokemon_species(id),
    form_id INT REFERENCES forms(id),
    sprite_url VARCHAR(255),
    UNIQUE(species_id, form_id)  -- Contrainte unicité
);

-- Table pokemon_type (relation N-M)
CREATE TABLE pokemon_type (
    pokemon_id INT REFERENCES pokemon(id) ON DELETE CASCADE,
    type_id INT REFERENCES types(id),
    slot INT CHECK (slot IN (1, 2)),
    PRIMARY KEY (pokemon_id, slot)
);

-- Table type_effectiveness (matrice affinités)
CREATE TABLE type_effectiveness (
    attacking_type_id INT REFERENCES types(id),
    defending_type_id INT REFERENCES types(id),
    multiplier FLOAT CHECK (multiplier IN (0, 0.25, 0.5, 1, 2, 4)),
    PRIMARY KEY (attacking_type_id, defending_type_id)
);
```

**Montrer les données:**

```sql
-- Compter Pokémon
SELECT COUNT(*) FROM pokemon;
-- Résultat: 188

-- Compter capacités
SELECT COUNT(*) FROM moves;
-- Résultat: 226

-- Afficher affinités type Feu
SELECT
    t1.name AS attacking_type,
    t2.name AS defending_type,
    te.multiplier
FROM type_effectiveness te
JOIN types t1 ON te.attacking_type_id = t1.id
JOIN types t2 ON te.defending_type_id = t2.id
WHERE t1.name = 'feu'
ORDER BY te.multiplier DESC;
```

**Résultat:** Base normalisée 3NF ✅ (C4)

---

#### C5: Partage Données (API)

**Script:**

> "L'API FastAPI expose les données via interface REST."

**Montrer Swagger:**

```bash
# Ouvrir navigateur
firefox http://localhost:8080/docs
```

**Démontrer les endpoints:**

1. **GET /pokemon/** - Liste tous les Pokémon
   ```bash
   curl http://localhost:8080/pokemon/ | jq '.[0:2]'
   ```

2. **GET /pokemon/25** - Détails Pikachu
   ```bash
   curl http://localhost:8080/pokemon/25 | jq
   ```

3. **GET /types/affinities** - Matrice affinités
   ```bash
   curl http://localhost:8080/types/affinities | jq '.[0:5]'
   ```

**Résultat:** Données partagées via API REST ✅ (C5)

---

### Étape 4: Machine Learning (4 min) - **C12**

**Objectif:** Démontrer le pipeline ML complet

#### Pipeline ML Complet

**Script:**

> "Le modèle XGBoost est entraîné sur 898,472 combats simulés avec 88.23% d'accuracy."

**Montrer le pipeline ML:**

```bash
# 1. Structure fichiers ML
ls -lh machine_learning/
```

```
run_machine_learning.py     # Pipeline ML principal (1239 lignes)
train_model.py              # Wrapper entraînement
build_battle_winner_dataset_v2.py  # Génération dataset
mlflow_integration.py       # MLflow tracking
```

**Montrer le code principal:**

```bash
cat machine_learning/run_machine_learning.py | grep -A 30 "def run_dataset_preparation"
```

**Expliquer les étapes:**

```python
def run_machine_learning_pipeline():
    """Pipeline ML complet"""

    # 1. Préparation dataset (898,472 combats)
    X_train, X_test, y_train, y_test = run_dataset_preparation()

    # 2. Feature engineering (133 features)
    X_train_eng = engineer_features(X_train)
    X_test_eng = engineer_features(X_test)

    # 3. Training XGBoost
    model = train_model(X_train_eng, y_train, hyperparams={
        'n_estimators': 100,
        'max_depth': 6,
        'learning_rate': 0.1,
        'tree_method': 'hist',  # CPU optimisé
        'n_jobs': -1            # Tous les cores
    })

    # 4. Évaluation
    metrics = evaluate_model(model, X_test_eng, y_test)
    # Résultat: 88.23% accuracy

    # 5. Export modèle (compression Joblib)
    export_model(model, scalers, metadata, version='v2')

    # 6. Enregistrement MLflow
    tracker.log_model(model, artifact_path='model')
    tracker.register_model(model_name='battle_winner_predictor')
    tracker.promote_best_model(metric='test_accuracy', minimum=0.80)
```

**Montrer le dataset:**

```bash
# Taille dataset
ls -lh data/datasets/battles_dataset_v2.parquet
# ~220 MB (898,472 combats)

# Explorer dataset
python3 << EOF
import pandas as pd
df = pd.read_parquet('data/datasets/battles_dataset_v2.parquet')
print(f"Combats: {len(df):,}")
print(f"Features: {df.shape[1]}")
print(f"\nColonnes:\n{df.columns.tolist()[:20]}")
print(f"\nDistribution gagnants:\n{df['winner'].value_counts()}")
EOF
```

**Résultat attendu:**

```
Combats: 898,472
Features: 39

Colonnes:
['a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense',
 'a_speed', 'a_type_1', 'a_type_2', 'b_hp', 'b_attack', ...]

Distribution gagnants:
1    456,234  (Pokemon A gagne)
0    442,238  (Pokemon B gagne)
```

---

#### C12: Tests Automatisés ML

**Montrer les tests ML:**

```bash
# 1. Structure tests ML
ls -lh tests/ml/
```

```
test_dataset_preparation.py      # Tests dataset (25 tests)
test_feature_engineering.py      # Tests features (15 tests)
test_model_training.py           # Tests entraînement (10 tests)
```

**Exécuter les tests:**

```bash
# Tests ML
pytest tests/ml/ -v

# Résultat:
# ========================= 50 passed in 12.34s =========================
```

**Montrer un test exemple:**

```bash
cat tests/ml/test_feature_engineering.py | head -40
```

```python
def test_engineer_features_output_shape():
    """Test: feature engineering produit 133 features"""
    df_raw = create_mock_battle_df()  # 38 features brutes

    df_engineered = engineer_features(df_raw)

    assert df_engineered.shape[1] == 133  # 133 features engineered
    assert 'effective_power_a' in df_engineered.columns
    assert 'stat_ratio' in df_engineered.columns

def test_model_accuracy_threshold():
    """Test: accuracy > 80% requis"""
    model, metrics = train_and_evaluate_model()

    assert metrics['test_accuracy'] > 0.80
    assert metrics['test_roc_auc'] > 0.85
```

**Résultat:** Tests automatisés ML ✅ (C12)

---

### Étape 5: API REST (3 min) - **C9, C10**

#### C9: API REST Exposant Modèle IA

**Script:**

> "L'API FastAPI expose le modèle XGBoost via endpoint /predict/best-move."

**Ouvrir Swagger:**

```bash
firefox http://localhost:8080/docs
```

**Montrer l'endpoint de prédiction:**

1. **Cliquer sur POST /predict/best-move**
2. **Cliquer "Try it out"**
3. **Remplir le JSON:**

```json
{
  "pokemon_a_id": 25,
  "pokemon_b_id": 1,
  "available_moves": ["Fatal-Foudre", "Vive-Attaque", "Queue de Fer", "Tonnerre"]
}
```

4. **Cliquer "Execute"**

**Résultat attendu:**

```json
{
  "pokemon_a_id": 25,
  "pokemon_a_name": "Pikachu",
  "pokemon_b_id": 1,
  "pokemon_b_name": "Bulbizarre",
  "recommended_move": "Fatal-Foudre",
  "win_probability": 0.8734,
  "all_moves": [
    {
      "move_name": "Fatal-Foudre",
      "move_type": "électrik",
      "move_power": 150,
      "type_multiplier": 1.0,
      "stab": 1.5,
      "win_probability": 0.8734,
      "predicted_winner": "A"
    },
    {
      "move_name": "Tonnerre",
      "move_type": "électrik",
      "move_power": 110,
      "type_multiplier": 1.0,
      "stab": 1.5,
      "win_probability": 0.8456,
      "predicted_winner": "A"
    }
  ]
}
```

**Montrer le code API:**

```bash
cat api_pokemon/routes/prediction_route.py | head -110
```

**Expliquer:**

```python
@router.post("/best-move", response_model=PredictBestMoveResponse)
def predict_best_move(request: PredictBestMoveRequest, db: Session):
    """
    Prédiction ML via API REST.

    Sécurité:
    - API Key requise (SHA-256)
    - Validation Pydantic schema
    - Rate limiting (30 req/min)

    Monitoring:
    - Métriques Prometheus
    - Drift detection Evidently
    - Logs structurés
    """
    # 1. Validation input (Pydantic)
    # 2. Load modèle depuis MLflow Registry
    # 3. Prédiction XGBoost
    # 4. Track métriques Prometheus
    # 5. Log drift Evidently
    # 6. Retour JSON
```

**Tester avec curl:**

```bash
curl -X POST http://localhost:8080/predict/best-move \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "pokemon_a_id": 25,
    "pokemon_b_id": 6,
    "available_moves": ["Fatal-Foudre", "Tonnerre"]
  }' | jq
```

**Résultat:** API REST exposant IA ✅ (C9)

---

#### C10: Intégration API dans Application

**Script:**

> "L'interface Streamlit intègre l'API pour fournir une expérience utilisateur."

**Ouvrir Streamlit:**

```bash
firefox http://localhost:8502
```

**Démonstration interactive:**

1. **Page d'accueil** - Présentation projet
2. **Aller dans "Combat et Prédiction"** (menu gauche)
3. **Sélectionner:**
   - Ton Pokémon: Pikachu (#25)
   - Adversaire: Dracaufeu (#6)
   - Capacités: Fatal-Foudre, Tonnerre, Vive-Attaque, Queue de Fer
4. **Cliquer "Prédire"**

**Résultat affiché:**

```
✅ Capacité recommandée: Fatal-Foudre

Probabilité de victoire: 87.3%

Toutes les capacités testées:
┌─────────────────┬─────────────┬────────────────────┐
│ Capacité        │ Probabilité │ Type               │
├─────────────────┼─────────────┼────────────────────┤
│ Fatal-Foudre    │ 87.3%       │ électrik (×1.0)    │
│ Tonnerre        │ 84.6%       │ électrik (×1.0)    │
│ Vive-Attaque    │ 45.2%       │ normal (×1.0)      │
│ Queue de Fer    │ 38.7%       │ acier (×0.5)       │
└─────────────────┴─────────────┴────────────────────┘
```

**Montrer le code Streamlit:**

```bash
cat interface/services/api_client.py | grep -A 20 "def predict_best_move"
```

```python
def predict_best_move(
    pokemon_a_id: int,
    pokemon_b_id: int,
    available_moves: List[str]
) -> Dict:
    """Appel API REST depuis Streamlit."""
    payload = {
        "pokemon_a_id": pokemon_a_id,
        "pokemon_b_id": pokemon_b_id,
        "available_moves": available_moves
    }

    response = requests.post(
        f"{API_BASE_URL}/predict/best-move",
        json=payload,
        headers={"X-API-Key": API_KEY},
        timeout=60
    )

    return response.json()
```

**Résultat:** API intégrée dans app ✅ (C10)

---

### Étape 6: Interface Streamlit (2 min)

**Script:**

> "L'interface Streamlit propose 8 pages interactives pour l'utilisateur final."

**Tour rapide des pages:**

1. **🏠 Accueil** - Présentation projet, features, guide
2. **1. Capacités** - Catalogue 226 capacités avec filtres
3. **2. Combat et Prédiction** - ⭐ Prédiction ML principale
4. **3. Détails Pokémon** - Fiches 188 Pokémon
5. **4. Types et Affinités** - Matrice 18×18 types
6. **5. Quiz Types** - Quiz interactif affinités
7. **6. Crédits** - Sources données, remerciements
8. **10. API Documentation** - Guide utilisation API

**Montrer quelques fonctionnalités:**

- **Filtres dynamiques** (types, puissance, catégorie)
- **Visualisations** (stats radar, heatmap affinités)
- **Thème Pokémon** (couleurs types, sprites animés)

---

### Étape 7: Monitoring (3 min) - **C11**

**Objectif:** Démontrer le monitoring complet du modèle IA

#### 7.1 Prometheus (Métriques Temps Réel)

**Ouvrir Prometheus:**

```bash
firefox http://localhost:9091
```

**Montrer les métriques clés:**

1. **Dans la barre de recherche, taper:**

   ```promql
   # Nombre total de prédictions
   model_predictions_total

   # Latence P95 des prédictions
   histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))

   # Distribution probabilités victoire
   model_win_probability

   # Confiance modèle
   model_confidence_score
   ```

2. **Cliquer "Execute" puis "Graph"**

**Expliquer les métriques:**

```python
# api_pokemon/monitoring/metrics.py

# Métriques API
api_requests_total          # Counter - Nombre requêtes
api_request_duration_seconds # Histogram - Latence requêtes
api_errors_total            # Counter - Erreurs

# Métriques ML
model_predictions_total     # Counter - Prédictions totales
model_prediction_duration_seconds  # Histogram - Latence modèle
model_confidence_score      # Gauge - Confiance (0-1)
model_win_probability       # Histogram - Distribution probas

# Métriques système
system_cpu_usage_percent    # Gauge - CPU %
system_memory_usage_bytes   # Gauge - RAM utilisée
```

---

#### 7.2 Grafana (Dashboards)

**Ouvrir Grafana:**

```bash
firefox http://localhost:3001
# Login: admin / admin
```

**Montrer les dashboards:**

1. **Dashboard "API Performance"**
   - Request Rate (requêtes/sec)
   - Latency P50, P95, P99
   - Error Rate
   - Status codes distribution

2. **Dashboard "Model Performance"**
   - Predictions per second
   - Model latency histogram
   - Confidence score over time
   - Win probability distribution

**Créer un panel en direct (optionnel):**

```promql
# Panel: Latence P95 API
histogram_quantile(0.95,
  rate(api_request_duration_seconds_bucket{endpoint="/predict/best-move"}[5m])
)
```

---

#### 7.3 Evidently AI (Drift Detection)

**Script:**

> "Evidently détecte automatiquement le drift des features du modèle."

**Montrer le code drift:**

```bash
cat api_pokemon/monitoring/drift_detection.py | head -100
```

**Expliquer le fonctionnement:**

```python
class DriftDetector:
    """Singleton drift detection avec Evidently AI 0.7"""

    def __init__(self):
        # 1. Load reference data (training set)
        self.reference_data = Dataset.from_pandas(
            pd.read_parquet('data/datasets/X_train.parquet').sample(10000)
        )

        # 2. Buffer production predictions
        self.production_buffer = []  # Max 1000 predictions

        # 3. Auto-report every hour
        self.report_frequency = timedelta(hours=1)

    def add_prediction(self, features, prediction, probability):
        """
        Ajout prédiction au buffer.

        Déclenche automatiquement:
        - Report drift si buffer plein (1000 predictions)
        - Report drift si 1h écoulée
        """
        self.production_buffer.append({
            **features,
            'prediction': prediction,
            'probability': probability,
            'timestamp': datetime.now()
        })

        # Auto-generate report si conditions remplies
        if len(self.production_buffer) >= 1000:
            self.generate_drift_report()

    def generate_drift_report(self):
        """
        Génère rapport drift avec Evidently.

        Outputs:
        - HTML dashboard interactif
        - JSON metrics
        - Production data sauvegardée (parquet)
        """
        production_df = pd.DataFrame(self.production_buffer)
        production_dataset = Dataset.from_pandas(production_df)

        # Evidently Report
        report = Report([DataDriftPreset()])
        report.run(production_dataset, self.reference_data)

        # Save HTML
        report.save_html('drift_dashboard_{timestamp}.html')

        # Extract metrics
        drift_summary = {
            'n_features': ...,
            'n_drifted_features': ...,
            'share_drifted_features': ...,
            'dataset_drift': True/False
        }

        return drift_summary
```

**Montrer un rapport drift:**

```bash
# Lister les rapports générés
ls -lh api_pokemon/monitoring/drift_reports/

# Ouvrir le dernier rapport HTML
firefox api_pokemon/monitoring/drift_reports/drift_dashboard_$(ls -t api_pokemon/monitoring/drift_reports/ | head -1)
```

**Expliquer le rapport Evidently:**

- 📊 **Dataset Summary** - Nombre features, samples
- 🔍 **Dataset Drift** - Drift détecté ou non (True/False)
- 📈 **Feature Drift** - Liste features driftées (ex: 5/133 features)
- 📉 **Drift Score** - Score 0-1 pour chaque feature
- 📊 **Distribution Plots** - Histogrammes reference vs production

**Résultat:** Monitoring complet modèle IA ✅ (C11)

---

### Étape 8: CI/CD MLOps (3 min) - **C13**

**Objectif:** Démontrer la chaîne de livraison continue

#### GitHub Actions Workflows

**Ouvrir GitHub:**

```bash
firefox https://github.com/votre-username/lets-go-predictiondex/actions
```

**Montrer les 4 workflows:**

1. **Tests** (.github/workflows/tests.yml)
2. **Docker Build** (.github/workflows/docker-build.yml)
3. **ML Pipeline** (.github/workflows/ml-pipeline.yml)
4. **Lint & Security** (.github/workflows/lint.yml)

**Expliquer chaque workflow:**

---

#### Workflow 1: Tests

**Montrer le fichier:**

```bash
cat .github/workflows/tests.yml
```

**Expliquer:**

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        # Health checks automatiques

    steps:
      - Checkout code
      - Setup Python 3.11
      - Cache pip dependencies
      - Install requirements
      - Run pytest (252 tests)
      - Generate coverage (82%)
      - Upload to Codecov
      - Generate coverage badge
```

**Résultat:** Tests automatiques sur chaque commit ✅

---

#### Workflow 2: Docker Build

**Expliquer:**

```yaml
name: Docker Build

jobs:
  build-and-test:
    strategy:
      matrix:
        service: [api, etl, ml, streamlit, mlflow]  # Build parallèle

    steps:
      - Docker Buildx setup
      - Cache Docker layers (performance)
      - Build image
      - Save + upload artifact

  integration-test:
    needs: build-and-test

    steps:
      - Download all artifacts
      - Load Docker images
      - docker-compose up -d
      - Health checks (API, MLflow, Prometheus)
      - Run integration tests
      - Logs si échec
```

**Résultat:** Build + tests intégration automatiques ✅

---

#### Workflow 3: ML Pipeline

**Expliquer:**

```yaml
name: ML Pipeline

on:
  push:
    paths:
      - 'machine_learning/**'
      - 'data/ml/**'
  workflow_dispatch:  # Trigger manuel

jobs:
  test-ml:
    services:
      postgres: ...
      mlflow: ...  # MLflow server intégré

    steps:
      - Run ML tests (50 tests)

      - Train model (si manuel)
        python run_machine_learning.py --mode=train

      - Validate metrics (accuracy > 80%)
        assert metrics['test_accuracy'] > 0.80

      - Upload model artifacts (90 jours)

      - Comment PR avec métriques
```

**Déclencher un training manuel:**

1. **Actions → ML Pipeline**
2. **Run workflow**
3. **Paramètres:**
   - dataset_version: v2
   - model_version: ci_test
4. **Run workflow**

**Résultat:** Pipeline ML automatisé ✅

---

#### Workflow 4: Lint & Security

**Expliquer:**

```yaml
name: Lint and Format

jobs:
  lint:
    - Black (code formatting)
    - isort (imports sorting)
    - Flake8 (style guide PEP8)
    - Pylint (code quality)
    - Mypy (type checking)

  security:
    - Bandit (security linter)
    - Safety (dependency vulnerabilities)
    - Upload security reports
```

**Résultat:** Qualité code + sécurité automatiques ✅

---

### Résumé Démonstration (1 min)

**Script de conclusion:**

> "En résumé, PredictionDex est un projet MLOps complet qui démontre:
>
> **E1 - Collecte et Traitement Données:**
> - ✅ ETL automatisé (3 sources: PokéAPI, Pokepedia, CSV)
> - ✅ Base PostgreSQL normalisée 3NF (11 tables)
> - ✅ Agrégation et nettoyage données (898,472 combats)
> - ✅ API REST pour partage données
>
> **E3 - Intégration IA Production:**
> - ✅ Modèle XGBoost 88.23% accuracy (133 features)
> - ✅ API REST exposant modèle IA (FastAPI + Swagger)
> - ✅ Interface Streamlit intégrée (8 pages)
> - ✅ Monitoring complet (Prometheus + Grafana + Evidently)
> - ✅ Tests automatisés ML (252 tests, coverage 82%)
> - ✅ CI/CD MLOps (4 workflows GitHub Actions)
> - ✅ MLflow Model Registry (auto-promotion)
>
> Le projet est production-ready avec 9 services Docker orchestrés."

---

## 3. Questions/Réponses Anticipées

### Q1: "Comment garantissez-vous la qualité des données collectées ?"

**Réponse:**

> "Nous avons 3 mécanismes de validation:
>
> 1. **Guards Pydantic** - Validation schéma lors de l'insertion
>    ```python
>    class PokemonGuard(BaseModel):
>        species_id: int
>        hp: int = Field(ge=1, le=255)
>        attack: int = Field(ge=1, le=255)
>        # ...
>    ```
>
> 2. **Contraintes SQL** - Intégrité base de données
>    ```sql
>    CHECK (hp BETWEEN 1 AND 255)
>    FOREIGN KEY (species_id) REFERENCES pokemon_species(id)
>    UNIQUE (species_id, form_id)
>    ```
>
> 3. **Post-processing** - Nettoyage après collecte
>    - Suppression entrées NULL/corrompues
>    - Dédoublonnage
>    - Normalisation formats (accents, casse)"

---

### Q2: "Comment gérez-vous le versioning des modèles ML ?"

**Réponse:**

> "Nous utilisons MLflow Model Registry avec 3 stages:
>
> 1. **None** - Modèle entraîné, pas encore enregistré
> 2. **Staging** - Modèle en test
> 3. **Production** - Modèle servi par l'API
> 4. **Archived** - Anciennes versions
>
> **Auto-promotion intelligente:**
> ```python
> if test_accuracy >= 0.85:
>     promote_to_production(model_version)
>     archive_old_production_models()
> ```
>
> **Fallback automatique:**
> Si MLflow indisponible, l'API charge le modèle depuis fichiers locaux."

---

### Q3: "Comment détectez-vous la dégradation du modèle ?"

**Réponse:**

> "Nous utilisons Evidently AI pour détecter le drift:
>
> 1. **Reference data** - 10,000 échantillons training set
> 2. **Production buffer** - 1,000 dernières prédictions
> 3. **Auto-reports** - Génération automatique chaque heure
>
> **Métriques drift:**
> - Dataset drift: True/False
> - Features driftées: 5/133 (3.7%)
> - Drift score par feature (0-1)
>
> **Actions si drift détecté:**
> - Alert équipe ML
> - Retraining modèle avec nouvelles données
> - A/B test nouveau modèle vs ancien"

---

### Q4: "Quelle est votre stratégie de tests ?"

**Réponse:**

> "Pyramide de tests à 3 niveaux:
>
> **1. Tests Unitaires (200 tests)**
> - Services API (64 tests)
> - Core models (15 tests)
> - ML pipeline (50 tests)
> - MLflow (17 tests)
>
> **2. Tests Intégration (9 tests)**
> - MLflow → API
> - API → PostgreSQL
> - End-to-end predictions
>
> **3. Tests Système (CI/CD)**
> - Health checks services
> - Docker compose up
> - Smoke tests
>
> **Coverage: 82%** (cible: 80%+)"

---

### Q5: "Comment sécurisez-vous l'API ?"

**Réponse:**

> "3 couches de sécurité:
>
> **1. Authentification API Key**
> ```python
> # SHA-256 hashing (jamais plaintext)
> valid_keys = {hashlib.sha256(key.encode()).hexdigest()
>               for key in os.getenv('API_KEYS').split(',')}
> ```
>
> **2. Validation Input**
> ```python
> # Pydantic schemas
> class PredictRequest(BaseModel):
>     pokemon_a_id: int = Field(ge=1, le=188)
>     pokemon_b_id: int = Field(ge=1, le=188)
>     available_moves: List[str] = Field(min_items=1, max_items=4)
> ```
>
> **3. Security Scanning**
> - Bandit (code vulnerabilities)
> - Safety (dependencies CVEs)
> - GitHub Actions automatique"

---

### Q6: "Combien de temps pour déployer en production ?"

**Réponse:**

> "**1 commande, 2 minutes:**
>
> ```bash
> # Clone repo
> git clone https://github.com/you/lets-go-predictiondex
> cd lets-go-predictiondex
>
> # Configure .env
> cp .env.example .env
> nano .env  # Ajouter API_KEYS, credentials
>
> # Deploy
> docker-compose up -d
>
> # Attendre 2 minutes (services ready)
> # ✅ API: http://localhost:8080
> # ✅ Streamlit: http://localhost:8502
> # ✅ MLflow: http://localhost:5001
> # ✅ Grafana: http://localhost:3001
> ```
>
> **Rollback instantané:**
> ```bash
> docker-compose down
> git checkout v1.9.0
> docker-compose up -d
> ```"

---

## 🎯 Checklist Finale Démonstration

### Avant la Soutenance

- [ ] Tester docker-compose up -d (démarrage clean)
- [ ] Vérifier tous les endpoints (health checks)
- [ ] Préparer 2-3 exemples prédictions
- [ ] Générer un rapport drift Evidently frais
- [ ] Vérifier que les dashboards Grafana s'affichent
- [ ] Tester l'interface Streamlit (toutes les pages)
- [ ] Vérifier les logs (pas d'erreurs critiques)

### Pendant la Soutenance

- [ ] Parler clairement et lentement
- [ ] Montrer le code source (pas juste les résultats)
- [ ] Expliquer les choix techniques (pourquoi XGBoost, PostgreSQL, etc.)
- [ ] Anticiper les questions (voir section Q&A)
- [ ] Garder un navigateur avec onglets pré-ouverts:
  - Swagger API (localhost:8080/docs)
  - Streamlit (localhost:8502)
  - Grafana (localhost:3001)
  - Prometheus (localhost:9091)
  - MLflow (localhost:5001)
  - GitHub Actions

### Après la Démonstration

- [ ] Noter les questions posées (pour amélioration)
- [ ] Demander feedback jury
- [ ] Proposer démo live supplémentaire si besoin

---

**Durée totale:** 25-30 minutes
**Niveau:** Production-Ready
**Score attendu:** 9-10/10 pour E1/E3

---

**Créé le:** 27 janvier 2026
**Pour:** Certification RNCP Niveau 6 - Concepteur Développeur d'Applications
**Blocs:** E1 (Données) + E3 (IA Production)
