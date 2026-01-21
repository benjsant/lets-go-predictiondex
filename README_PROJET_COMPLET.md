# Let's Go PredictionDex - Documentation Complète du Projet

> **Application Full-Stack de Prédiction de Combats Pokémon**
> ETL + Machine Learning + API REST + Interface Streamlit

![Python](https://img.shields.io/badge/Python-3.11-blue)
![XGBoost](https://img.shields.io/badge/XGBoost-3.x-green)
![Accuracy](https://img.shields.io/badge/Accuracy-94.24%25-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture du Système](#architecture-du-système)
3. [Stack Technologique](#stack-technologique)
4. [Structure du Projet](#structure-du-projet)
5. [Pipeline ETL](#pipeline-etl)
6. [Pipeline Machine Learning](#pipeline-machine-learning)
7. [API REST](#api-rest)
8. [Interface Utilisateur](#interface-utilisateur)
9. [Déploiement](#déploiement)
10. [Exemples d'Utilisation](#exemples-dutilisation)
11. [Métriques et Performances](#métriques-et-performances)
12. [Développement](#développement)
13. [Tests](#tests)
14. [Documentation Complémentaire](#documentation-complémentaire)

---

## 🎯 Vue d'Ensemble

### Objectif

**Let's Go PredictionDex** est une application qui aide les enfants à choisir la meilleure capacité Pokémon lors d'un combat dans Pokémon Let's Go Pikachu/Eevee. Elle utilise un modèle de Machine Learning (XGBoost) entraîné sur 34,040 combats simulés pour prédire avec **94.24% d'accuracy** quelle capacité maximisera les chances de victoire.

### Cas d'Usage

```
Situation: Un enfant joue à Pokémon Let's Go et rencontre un Salamèche sauvage.
          Il utilise son Carapuce et doit choisir une capacité.

Action:   L'enfant ouvre l'application et sélectionne:
          - Pokémon A: Carapuce
          - Pokémon B: Salamèche
          - Capacités disponibles: [Charge, Pistolet à O, Hydrocanon, Surf]

Résultat: L'application recommande "Hydrocanon" avec 99.75% de chances de victoire
          car:
          • Eau est super efficace contre Feu (2x)
          • STAB bonus s'applique (1.5x) - Carapuce est type Eau
          • Puissance élevée (110)
```

### Fonctionnalités Principales

- ✅ **Prédiction de Combat**: Recommande la meilleure capacité avec probabilité de victoire
- ✅ **Base de Données Complète**: 188 Pokémon Let's Go, 226 capacités, 324 règles de types
- ✅ **Modèle ML Performant**: 94.24% accuracy, 98.96% ROC-AUC
- ✅ **API REST**: Endpoints FastAPI avec documentation Swagger
- ✅ **Interface Web**: Application Streamlit intuitive
- ✅ **Déploiement Docker**: Architecture microservices avec docker-compose

---

## 🏗️ Architecture du Système

### Diagramme Global

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌─────▼─────┐
    │ Streamlit│            │  Swagger  │
    │   UI     │            │   Docs    │
    │  :8501   │            │  :8000    │
    └────┬─────┘            └─────┬─────┘
         │                        │
         │    HTTP REST API       │
         └────────┬───────────────┘
                  │
         ┌────────▼─────────┐
         │   FastAPI        │
         │   (uvicorn)      │
         │   Port 8000      │
         └────────┬─────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
 ┌────▼─────┐ ┌──▼──────┐ ┌──▼──────────┐
 │ Pokemon  │ │  Move   │ │ Prediction  │
 │ Service  │ │ Service │ │  Service    │
 └────┬─────┘ └────┬────┘ └──┬──────────┘
      │            │          │
      │            │      ┌───▼────────┐
      │            │      │  XGBoost   │
      │            │      │  Model     │
      │            │      │  (94.24%)  │
      │            │      └────────────┘
      │            │
      └────────┬───┴──────────┘
               │
        ┌──────▼───────┐
        │ SQLAlchemy   │
        │   ORM        │
        └──────┬───────┘
               │
        ┌──────▼───────────┐
        │  PostgreSQL 15   │
        │  (11 tables)     │
        │  Port 5432       │
        └──────▲───────────┘
               │
     ┌─────────┴──────────┐
     │                    │
┌────▼─────┐      ┌───────▼────┐
│   ETL    │      │     ML      │
│ Pipeline │      │  Dataset    │
│          │      │  Builder    │
└──────────┘      └─────────────┘
```

### Architecture Docker

```yaml
Services Docker Compose:
├── letsgo_postgres    # Base de données (persistent volume)
├── letsgo_etl         # Pipeline ETL (one-shot)
├── letsgo_ml          # Générateur dataset ML (one-shot)
├── letsgo_api         # API FastAPI (daemon)
└── letsgo_streamlit   # Interface Streamlit (daemon)

Dépendances:
  postgres → etl → ml
           ↓      ↓
           api → streamlit
```

---

## 🛠️ Stack Technologique

### Backend

| Technologie | Version | Rôle |
|------------|---------|------|
| **Python** | 3.11 | Langage principal |
| **PostgreSQL** | 15 | Base de données relationnelle |
| **SQLAlchemy** | Latest | ORM |
| **FastAPI** | Latest | Framework API REST |
| **Uvicorn** | Latest | Serveur ASGI |

### Machine Learning

| Technologie | Version | Rôle |
|------------|---------|------|
| **XGBoost** | 3.x | Modèle de classification |
| **scikit-learn** | Latest | Feature engineering, scalers |
| **Pandas** | Latest | Data manipulation |
| **NumPy** | Latest | Calcul numérique |
| **PyArrow** | Latest | Format Parquet |

### Frontend & Deployment

| Technologie | Version | Rôle |
|------------|---------|------|
| **Streamlit** | Latest | Interface web |
| **Docker** | Latest | Containerisation |
| **docker-compose** | Latest | Orchestration |

### Data Collection

| Source | Type | Données |
|--------|------|---------|
| **CSV Files** | Fichiers locaux | Pokémon, capacités, types |
| **PokéAPI** | REST API | Stats, sprites, enrichissement |
| **Poképédia** | Web scraping (Scrapy) | Méthodes d'apprentissage |

---

## 📁 Structure du Projet

```
lets-go-predictiondex/
│
├── core/                          # Modèles & Database (Partagé)
│   ├── db/
│   │   ├── base.py                # SQLAlchemy Base
│   │   ├── session.py             # Factory de connexion DB
│   │   └── guards/                # Fonctions upsert (idempotence)
│   │       ├── pokemon.py
│   │       ├── move.py
│   │       └── ...
│   ├── models/                    # Modèles SQLAlchemy ORM
│   │   ├── pokemon.py             # Pokémon (form-level)
│   │   ├── move.py                # Capacités (avec priority)
│   │   ├── type_effectiveness.py  # Matrice des types
│   │   ├── pokemon_species.py
│   │   ├── pokemon_stat.py
│   │   └── ...
│   └── schemas/                   # Schémas Pydantic (validation API)
│       ├── pokemon.py
│       ├── move.py
│       └── ...
│
├── etl_pokemon/                   # Pipeline ETL
│   ├── data/csv/                  # Données sources
│   │   ├── liste_pokemon.csv
│   │   ├── liste_capacite_lets_go.csv
│   │   └── table_type.csv
│   ├── scripts/
│   │   ├── etl_load_csv.py       # Script ETL principal
│   │   ├── etl_enrich_pokeapi.py # Enrichissement PokéAPI
│   │   └── etl_post_process.py   # Post-traitement
│   └── pokepedia_scraper/         # Spider Scrapy
│
├── machine_learning/              # Pipeline ML
│   ├── build_battle_winner_dataset.py  # Génère dataset combats
│   ├── train_model.py                   # Script production training
│   ├── test_model_inference.py          # Test prédictions
│   └── README.md                        # Doc ML complète
│
├── data/ml/                       # Datasets ML générés
│   └── battle_winner/
│       ├── raw/matchups.parquet   # 34,040 matchups bruts
│       ├── processed/
│       │   ├── train.parquet      # 27,232 échantillons
│       │   └── test.parquet       # 6,808 échantillons
│       └── features/              # (Non utilisé, features en runtime)
│
├── models/                        # Modèles ML entraînés
│   ├── battle_winner_model_v1.pkl      # XGBoost (983 KB)
│   ├── battle_winner_scalers_v1.pkl    # 2 StandardScalers (1.7 KB)
│   └── battle_winner_metadata.pkl      # Métadonnées (2.8 KB)
│
├── notebooks/                     # Jupyter Notebooks (Expérimentation)
│   ├── 01_exploration.ipynb       # EDA du dataset
│   ├── 02_feature_engineering.ipynb  # Pipeline features (133 colonnes)
│   └── 03_training_evaluation.ipynb  # Training & évaluation
│
├── api_pokemon/                   # API FastAPI
│   ├── main.py                    # Point d'entrée API
│   ├── routes/
│   │   ├── pokemon_route.py
│   │   ├── moves_route.py
│   │   ├── type_route.py
│   │   └── prediction_route.py    # Endpoints ML
│   ├── services/
│   │   ├── pokemon_service.py
│   │   ├── move_service.py
│   │   ├── type_service.py
│   │   └── prediction_service.py  # Logique ML inference
│   ├── requirements.txt
│   └── README_PREDICTION.md       # Doc endpoint /predict
│
├── interface/                     # Interface Streamlit
│   ├── app.py                     # Page d'accueil
│   ├── pages/
│   │   ├── 1_Moves.py             # Recherche capacités
│   │   ├── 2_Compare.py           # Comparaison Pokémon
│   │   └── 3_Credits.py
│   ├── services/
│   │   └── api_client.py          # Client HTTP pour API
│   └── requirements_streamlit.txt
│
├── docker/                        # Configuration Docker
│   ├── Dockerfile.api
│   ├── Dockerfile.etl
│   ├── Dockerfile.ml
│   ├── Dockerfile.streamlit
│   └── *_entrypoint.py
│
├── docs/                          # Documentation
│   └── sql/                       # Exemples SQL
│
├── docker-compose.yml             # Orchestration microservices
├── .env                           # Variables d'environnement
├── README.md                      # README principal (sommaire)
├── E1_DOCUMENTATION.md            # Doc compétence E1 (ETL/DB)
├── E1_ARCHITECTURE_DIAGRAM.md     # Diagrammes architecture
├── E3_STRUCTURE.md                # Structure ML pour E3
├── HANDOFF_CONTEXT.md             # Contexte développement
├── API_EXAMPLES.md                # Exemples API réels
└── README_PROJET_COMPLET.md       # ⬅️ CE DOCUMENT
```

---

## 🔄 Pipeline ETL

### 1. Sources de Données

#### CSV (Référence)

**Fichiers:**
- `liste_pokemon.csv` - 188 Pokémon (ID, nom FR/EN/JP, types, forme)
- `liste_capacite_lets_go.csv` - 226 capacités (nom, type, catégorie, puissance, précision, damage_type)
- `table_type.csv` - 324 règles d'efficacité des types (18 × 18 matrice)

#### PokéAPI (Enrichissement)

**URL:** `https://pokeapi.co/api/v2/`

**Données récupérées:**
- Stats de base (HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed)
- Sprites (URLs des images)
- Height, weight
- Rate-limited: 1 requête/seconde

#### Poképédia (Web Scraping)

**Spider Scrapy:** `etl_pokemon/pokepedia_scraper/`

**Données scrapées:**
- Méthodes d'apprentissage des capacités (niveau, CT, tuteur, évolution)
- Niveaux d'apprentissage
- ~2,471 relations Pokémon-Capacité

### 2. Mapping Priority des Capacités

**Innovation clé:** Les capacités ont des priorités qui affectent l'ordre d'attaque.

```python
PRIORITY_FROM_DAMAGE_TYPE = {
    # +2: Moves protection
    "protection_change_plusieur": 2,    # Abri
    "prioritaire_deux": 2,              # Ruse

    # +1: Quick attacks
    "prioritaire": 1,                   # Vive-Attaque, Aqua-Jet
    "prioritaire_conditionnel": 1,      # Coup Bas

    # 0: Normal priority (default)
    "offensif": 0,
    "deux_tours": 0,                    # Lance-Soleil, etc.

    # -5: Counter moves
    "renvoi_degat_double_physique": -5, # Riposte
    "renvoi_degat_double_special": -5   # Voile Miroir
}
```

### 3. Schéma de Base de Données

**11 tables normalisées (3NF):**

```sql
-- Référence
form (id, name)
move_category (id, name)
learn_method (id, name)

-- Entités principales
pokemon_species (id, pokedex_number, name_fr, name_en, name_jp)
pokemon (id, species_id, form_id, sprite_url, height_m, weight_kg)
pokemon_stat (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
type (id, name)
move (id, name, type_id, category_id, power, accuracy, priority, damage_type, description)

-- Associations
pokemon_type (pokemon_id, type_id, slot)  -- 1-2 types par Pokémon
pokemon_move (pokemon_id, move_id, learn_method_id, learn_level)
type_effectiveness (attacking_type_id, defending_type_id, multiplier)
```

### 4. Exécution ETL

**Script:** `etl_pokemon/scripts/etl_load_csv.py`

```bash
# Depuis l'hôte
POSTGRES_HOST=localhost python etl_pokemon/scripts/etl_load_csv.py

# Depuis Docker
docker compose up etl
```

**Durée:** ~3 minutes (avec rate limiting PokéAPI)

**Idempotence:** Toutes les opérations utilisent des guards (upsert) pour permettre la ré-exécution sans duplication.

---

## 🤖 Pipeline Machine Learning

### 1. Génération du Dataset

**Script:** `machine_learning/build_battle_winner_dataset.py`

**Stratégie:**
1. Créer tous les matchups possibles: 188 × 188 = 35,344 combinaisons
2. Pour chaque matchup, sélectionner la meilleure capacité offensive pour chaque Pokémon
3. Calculer les features de combat (stats, types, STAB, efficacité)
4. Déterminer le gagnant basé sur puissance effective et priorité
5. Échantillonnage intelligent pour équilibrer le dataset

**Output:**
- `data/ml/battle_winner/raw/matchups.parquet` - 34,040 matchups
- `data/ml/battle_winner/processed/train.parquet` - 27,232 échantillons (80%)
- `data/ml/battle_winner/processed/test.parquet` - 6,808 échantillons (20%)

### 2. Features (38 → 133 après encodage)

#### Features Brutes (38 colonnes)

**Pokémon A (Attaquant):**
- Stats: hp, attack, defense, sp_attack, sp_defense, speed
- Types: type_1, type_2 (catégoriel)
- Capacité: move_power, move_type, move_priority, move_stab, move_type_mult

**Pokémon B (Défenseur):**
- Stats: hp, attack, defense, sp_attack, sp_defense, speed
- Types: type_1, type_2 (catégoriel)
- Capacité: move_power, move_type, move_priority, move_stab, move_type_mult

**Features dérivées:**
- `speed_diff` = a_speed - b_speed
- `hp_diff` = a_hp - b_hp
- `a_total_stats`, `b_total_stats`
- `a_moves_first` (binaire: qui attaque en premier basé sur priority/speed)

#### Pipeline Feature Engineering (133 colonnes finales)

**Étape 1: One-Hot Encoding** (38 → 107 colonnes)
- Encode 6 features catégoriels (a_type_1, a_type_2, b_type_1, b_type_2, a_move_type, b_move_type)
- Crée ~102 colonnes binaires pour 18 types
- Drop colonnes catégorielles originales

**Étape 2: Normalisation (StandardScaler #1)**
- Normalise 18 features numériques (stats, powers, diffs)
- Fit sur train, transform sur test

**Étape 3: Création de Features Dérivées** (+6 colonnes)
```python
stat_ratio = a_total_stats / (b_total_stats + 1)
type_advantage_diff = a_move_type_mult - b_move_type_mult
effective_power_a = a_move_power × a_move_stab × a_move_type_mult
effective_power_b = b_move_power × b_move_stab × b_move_type_mult
effective_power_diff = effective_power_a - effective_power_b
priority_advantage = a_move_priority - b_move_priority
```

**Étape 4: Normalisation (StandardScaler #2)**
- Normalise les 6 features dérivées

**Résultat:** 133 features (107 one-hot + 6 dérivées + 20 pré-normalisées)

### 3. Entraînement du Modèle

**Script:** `machine_learning/train_model.py`

**Modèles testés:**

| Modèle | Test Accuracy | Precision | Recall | F1 | ROC-AUC |
|--------|--------------|-----------|--------|------|---------|
| Logistic Regression | 90.88% | 90.83% | 90.93% | 90.88% | 97.13% |
| Random Forest | 93.48% | 93.46% | 93.51% | 93.48% | 98.59% |
| **XGBoost (choisi)** | **94.24%** | **94.22%** | **94.26%** | **94.24%** | **98.96%** |

**Hyperparamètres XGBoost:**
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

**Features les plus importantes (Random Forest):**
1. `stat_ratio` (15.0%)
2. `effective_power_diff` (9.0%)
3. `hp_diff` (8.8%)
4. `a_total_stats` (5.3%)
5. `b_total_stats` (4.6%)

### 4. Exports

**Modèle:** `models/battle_winner_model_v1.pkl` (983 KB)
**Scalers:** `models/battle_winner_scalers_v1.pkl` (1.7 KB - dict avec 2 scalers)
**Metadata:** `models/battle_winner_metadata.pkl` (2.8 KB)

```python
# Metadata contient:
{
    'model_type': 'XGBClassifier',
    'version': 'v1',
    'n_features': 133,
    'feature_columns': ['a_hp', 'a_attack', ...],  # Liste des 133 colonnes
    'metrics': {
        'train_accuracy': 0.9887,
        'test_accuracy': 0.9424,
        'test_precision': 0.9427,
        'test_recall': 0.9421,
        'test_f1': 0.9424,
        'test_roc_auc': 0.9896
    },
    'trained_at': '2026-01-21T12:31:18',
    'hyperparameters': {...}
}
```

---

## 🌐 API REST

### Endpoints

**Base URL:** `http://localhost:8000`
**Documentation:** `http://localhost:8000/docs`

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{"status": "ok"}
```

#### 2. Pokemon Endpoints

##### Liste des Pokémon

```http
GET /pokemon/
```

**Response:** `List[PokemonListItem]`

##### Recherche par nom

```http
GET /pokemon/search?name={name}&lang=fr
```

##### Détails d'un Pokémon

```http
GET /pokemon/{id}
```

**Response:**
```json
{
  "id": 7,
  "species_id": 7,
  "form_id": 1,
  "sprite_url": "https://...",
  "height_m": 0.5,
  "weight_kg": 9.0,
  "species": {
    "pokedex_number": 7,
    "name_fr": "Carapuce",
    "name_en": "Squirtle",
    "name_jp": "ゼニガメ"
  },
  "stats": {
    "hp": 44,
    "attack": 48,
    "defense": 65,
    "sp_attack": 50,
    "sp_defense": 64,
    "speed": 43
  },
  "pokemon_types": [
    {"type": {"name": "Eau"}, "slot": 1}
  ],
  "pokemon_moves": [...]
}
```

##### Faiblesses d'un Pokémon

```http
GET /pokemon/{id}/weaknesses
```

#### 3. Moves Endpoints

```http
GET /moves/                    # Liste toutes les capacités
GET /moves/search?name={name}  # Recherche par nom
GET /moves/{id}                # Détails d'une capacité
```

#### 4. Types Endpoints

```http
GET /types/                    # Liste tous les types
GET /types/{id}/effectiveness  # Matrice d'efficacité
```

#### 5. Prediction Endpoints (ML)

##### Prédire la Meilleure Capacité

```http
POST /predict/best-move
Content-Type: application/json

{
  "pokemon_a_id": 7,
  "pokemon_b_id": 4,
  "available_moves": ["Charge", "Pistolet à O", "Hydrocanon", "Surf"]
}
```

**Response:**
```json
{
  "pokemon_a_id": 7,
  "pokemon_a_name": "Carapuce",
  "pokemon_b_id": 4,
  "pokemon_b_name": "Salamèche",
  "recommended_move": "Hydrocanon",
  "win_probability": 0.9975,
  "all_moves": [
    {
      "move_name": "Hydrocanon",
      "move_type": "Eau",
      "move_power": 110,
      "effective_power": 110.0,
      "type_multiplier": 2.0,
      "stab": 1.5,
      "priority": 0,
      "score": 264.0,
      "win_probability": 0.9975,
      "predicted_winner": "A"
    },
    ...
  ]
}
```

##### Informations du Modèle ML

```http
GET /predict/model-info
```

**Response:**
```json
{
  "model_type": "XGBClassifier",
  "version": "v1",
  "n_features": 133,
  "metrics": {
    "test_accuracy": 0.9424,
    "test_precision": 0.9427,
    "test_recall": 0.9421,
    "test_f1": 0.9424,
    "test_roc_auc": 0.9896
  },
  "trained_at": "2026-01-21T12:31:18",
  "hyperparameters": {...}
}
```

### Service de Prédiction

**File:** `api_pokemon/services/prediction_service.py`

**Composants:**

1. **PredictionModel Singleton**
   - Charge le modèle une fois au démarrage
   - Cache en mémoire pour inférence rapide

2. **Sélection de Capacité**
   - `select_best_move_for_matchup()` - Choisit la meilleure capacité
   - Score = `power × stab × type_mult × (accuracy/100) + priority × 50`

3. **Préparation de Features**
   - `prepare_features_for_prediction()` - Construit 38 features brutes
   - `apply_feature_engineering()` - Transforme en 133 features

4. **Prédiction**
   - `predict_best_move()` - Fonction principale
   - Pour chaque capacité disponible:
     - Simule matchup avec meilleure contre-capacité adverse
     - Calcule features
     - Prédit probabilité de victoire
   - Classe par probabilité décroissante

---

## 🖥️ Interface Utilisateur

### Streamlit Application

**URL:** `http://localhost:8501`

**Pages:**

1. **Home** - Page d'accueil avec navigation
2. **Moves** - Recherche de Pokémon et affichage de leurs capacités
3. **Compare** - Comparaison de deux Pokémon (types, stats, faiblesses)
4. **Credits** - Informations sur le projet

**Features:**
- Sprites Pokémon
- Badges de types avec couleurs
- Visualisation des stats
- Calculateur de faiblesses
- Design responsive avec colonnes Streamlit

**Client API:** `interface/services/api_client.py`

```python
class APIClient:
    def __init__(self, base_url: str = "http://api:8000"):
        self.base_url = base_url

    def get_pokemon_list(self) -> List[dict]:
        response = requests.get(f"{self.base_url}/pokemon/")
        return response.json()
```

---

## 🚀 Déploiement

### Docker Compose

**Fichier:** `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pokemon_user"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  etl:
    depends_on:
      db:
        condition: service_healthy
    # One-shot execution

  ml:
    depends_on:
      etl:
        condition: service_completed_successfully
    # One-shot execution

  api:
    depends_on:
      db:
        condition: service_healthy
      etl:
        condition: service_completed_successfully
    ports:
      - "8000:8000"
    # Daemon

  streamlit:
    depends_on:
      api:
        condition: service_started
    ports:
      - "8501:8501"
    # Daemon

volumes:
  postgres_data:
```

### Commandes

#### Démarrage Complet

```bash
docker compose up --build
```

**Ordre d'exécution:**
1. PostgreSQL démarre (avec healthcheck)
2. ETL charge les données (one-shot)
3. ML génère le dataset (one-shot)
4. API démarre (daemon)
5. Streamlit démarre (daemon)

#### Démarrage Sélectif

```bash
# Base de données uniquement
docker compose up -d db

# API uniquement (assume DB ready)
docker compose up -d api

# Tout arrêter
docker compose down

# Tout arrêter + supprimer les volumes
docker compose down -v
```

### Développement Local (hors Docker)

#### Prérequis

```bash
# Python 3.11+
python --version

# PostgreSQL 15
psql --version

# Créer virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

#### Installation

```bash
# Installer toutes les dépendances
pip install -r api_pokemon/requirements.txt
pip install -r machine_learning/requirements.txt
pip install -r etl_pokemon/requirements.txt
pip install -r interface/requirements_streamlit.txt
```

#### Exécution Manuelle

```bash
# 1. Démarrer PostgreSQL (Docker ou local)
docker compose up -d db

# 2. Lancer l'ETL
POSTGRES_HOST=localhost python etl_pokemon/scripts/etl_load_csv.py

# 3. Générer le dataset ML
POSTGRES_HOST=localhost python machine_learning/build_battle_winner_dataset.py

# 4. Entraîner le modèle (optionnel, modèles déjà fournis)
python machine_learning/train_model.py

# 5. Démarrer l'API
cd api_pokemon
uvicorn main:app --reload --port 8000

# 6. Démarrer Streamlit (nouveau terminal)
cd interface
streamlit run app.py
```

#### Jupyter Notebooks

```bash
jupyter notebook notebooks/
```

**Notebooks disponibles:**
- `01_exploration.ipynb` - EDA
- `02_feature_engineering.ipynb` - Pipeline features
- `03_training_evaluation.ipynb` - Training & évaluation

---

## 📊 Exemples d'Utilisation

Voir [API_EXAMPLES.md](API_EXAMPLES.md) pour des exemples complets avec résultats réels.

### Exemple 1: Carapuce vs Salamèche

**Requête:**
```bash
curl -X POST http://localhost:8000/predict/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 7,
    "pokemon_b_id": 4,
    "available_moves": ["Charge", "Pistolet à O", "Hydrocanon", "Surf"]
  }'
```

**Résultat:**
- **Capacité recommandée:** Hydrocanon
- **Probabilité de victoire:** 99.75%
- **Raison:** Eau super efficace contre Feu (2x) + STAB (1.5x) + haute puissance (110)

### Exemple 2: Bulbizarre vs Salamèche

**Requête:**
```bash
curl -X POST http://localhost:8000/predict/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 1,
    "pokemon_b_id": 4,
    "available_moves": ["Charge", "Fouet Lianes", "Tranch'"'"'Herbe", "Lance-Soleil"]
  }'
```

**Résultat:**
- **Capacité recommandée:** Lance-Soleil
- **Probabilité de victoire:** 1.98% (FAIBLE)
- **Raison:** Plante faible contre Feu (0.5x), malgré STAB et haute puissance

---

## 📈 Métriques et Performances

### Métriques ML

| Métrique | Train | Test |
|----------|-------|------|
| **Accuracy** | 98.87% | **94.24%** |
| **Precision** | - | 94.27% |
| **Recall** | - | 94.21% |
| **F1-Score** | - | 94.24% |
| **ROC-AUC** | - | **98.96%** |

**Overfitting Check:** Gap train-test = 4.63% (minimal overfitting)

### Confusion Matrix (Test Set)

```
              Predicted
              A wins  B wins
Actual  A     3215    193      (94.3% correct)
        B      199    3201     (94.1% correct)

Total: 6808 samples
Errors: 392 (5.76%)
```

### Latence API

| Endpoint | Latence Moyenne |
|----------|----------------|
| `/health` | < 5ms |
| `/pokemon/{id}` | 30-50ms |
| `/predict/best-move` | 200-400ms (4 capacités) |
| `/predict/model-info` | < 10ms |

**Note:** Latence prédiction dépend du nombre de capacités testées (~50-100ms par capacité).

### Taille des Données

| Composant | Taille |
|-----------|--------|
| **Base de données** | ~5 MB |
| **Dataset ML (Parquet)** | 6-13 MB |
| **Modèle XGBoost** | 983 KB |
| **Scalers** | 1.7 KB |
| **Metadata** | 2.8 KB |

---

## 🧪 Tests

### Tests Unitaires ML

**Fichier:** `test_prediction_api.py`

```bash
# Exécuter les tests
POSTGRES_HOST=localhost python test_prediction_api.py
```

**Tests:**
1. Chargement du modèle
2. Bulbizarre vs Salamèche (désavantage type)
3. Salamèche vs Bulbizarre (avantage type)
4. Carapuce vs Salamèche (super efficace)

### Tests API Endpoints

**Fichier:** `api_pokemon/test_prediction_endpoint.py`

```bash
python api_pokemon/test_prediction_endpoint.py
```

**Tests:**
1. Health check
2. Model info
3. Predict best move
4. Reverse matchup
5. Error cases (invalid ID, empty moves)

---

## 📚 Documentation Complémentaire

| Document | Description |
|----------|-------------|
| [README.md](README.md) | README principal (vue d'ensemble) |
| [E1_DOCUMENTATION.md](E1_DOCUMENTATION.md) | Documentation compétence E1 (ETL, DB) |
| [E3_STRUCTURE.md](E3_STRUCTURE.md) | Structure ML pour E3 |
| [machine_learning/README.md](machine_learning/README.md) | Documentation ML complète |
| [api_pokemon/README_PREDICTION.md](api_pokemon/README_PREDICTION.md) | Doc endpoint /predict |
| [API_EXAMPLES.md](API_EXAMPLES.md) | Exemples API avec résultats réels |
| [HANDOFF_CONTEXT.md](HANDOFF_CONTEXT.md) | Contexte développement |
| [E1_ARCHITECTURE_DIAGRAM.md](E1_ARCHITECTURE_DIAGRAM.md) | Diagrammes architecture |

---

## 🤝 Contributeurs

Projet développé dans le cadre d'une formation en Data Engineering et Machine Learning.

---

## 📄 Licence

Projet éducatif - Pokémon © Nintendo/Game Freak.

---

## 🎯 Roadmap

### Améliorations Futures

- [ ] **ML:**
  - Prédiction de dégâts (regression)
  - Simulation multi-tours
  - Support des objets tenus et abilities
  - Détection de drift (Evidently)

- [ ] **API:**
  - Cache Redis
  - Pagination
  - Rate limiting
  - GraphQL endpoint

- [ ] **UI:**
  - Animations de combat
  - Team builder (6 Pokémon)
  - Explication des prédictions (SHAP values)
  - Mode multilingue

- [ ] **DevOps:**
  - CI/CD (GitHub Actions)
  - Tests automatisés (pytest)
  - Model versioning (MLflow)
  - Monitoring (Prometheus + Grafana)

---

## 📞 Support

Pour toute question ou bug:
- Consulter la documentation dans `/docs/`
- Lire les README spécifiques à chaque module
- Vérifier les exemples dans `API_EXAMPLES.md`

---

**Dernière mise à jour:** 2026-01-21
**Version:** 1.0.0
**Modèle ML:** battle_winner_v1 (94.24% accuracy)
