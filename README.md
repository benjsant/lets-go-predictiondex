# 🎮 PredictionDex - Pokémon Let's Go Battle Predictor

> **Plateforme MLOps complète pour prédire les combats Pokémon Let's Go Pikachu/Eevee**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange.svg)](https://xgboost.readthedocs.io/)
[![MLflow](https://img.shields.io/badge/MLflow-2.18-blue.svg)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![Tests](https://img.shields.io/badge/Tests-252%20passed-success.svg)](./tests/)
[![Coverage](https://img.shields.io/badge/Coverage-82%25-brightgreen.svg)]()

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Cloner le projet
git clone https://github.com/YOUR_USERNAME/lets-go-predictiondex.git
cd lets-go-predictiondex

# 2. Configurer les variables d'environnement
cp .env.example .env
cp interface/.env.example interface/.env

# 3. Lancer toute la stack (9 services)
docker compose up --build

# 4. Accéder aux interfaces
# - API Swagger: http://localhost:8080/docs
# - Interface Streamlit: http://localhost:8502
# - Grafana: http://localhost:3001 (admin/admin)
# - Prometheus: http://localhost:9091
# - MLflow: http://localhost:5001
```

**⏱️ Durée première exécution:** 60-90 minutes (ETL + ML training)
**Durée démarrages suivants:** 2-3 minutes (données en cache)

➡️ **Guide détaillé:** [docs/deployment/QUICK_START.md](docs/deployment/QUICK_START.md)

---

## 📋 Table des Matières

- [🎯 Vue d'Ensemble](#-vue-densemble)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [🔧 Stack Technique](#-stack-technique)
- [📊 Résultats ML](#-résultats-ml)
- [🎮 Utilisation](#-utilisation)
- [🧪 Tests](#-tests)
- [📚 Documentation](#-documentation)
- [🎓 Certification RNCP](#-certification-rncp)
- [🛠️ Développement](#️-développement)
- [📈 Monitoring](#-monitoring)
- [🐳 Docker](#-docker)
- [🔒 Sécurité](#-sécurité)
- [🤝 Contribution](#-contribution)

---

## 🎯 Vue d'Ensemble

**PredictionDex** est une plateforme complète de **Machine Learning Operations (MLOps)** qui prédit l'issue de combats Pokémon dans Let's Go Pikachu/Eevee en analysant:

- ✅ **188 Pokémon** de la 1ère génération + formes Alola + Méga
- ✅ **226 capacités** avec puissance, type, priorité, STAB
- ✅ **18 types** avec affinités (résistances/faiblesses)
- ✅ **898,612 combats simulés** pour entraînement
- ✅ **133 features** engineered (stats, multiplicateurs, avantages)

### 🎯 Objectif Pédagogique

Ce projet valide les **compétences E1 et E3** du titre RNCP **"Concepteur Développeur d'Applications"** (Niveau 6):

- **E1** - Collecte et traitement de données
- **E3** - Intégration de composants d'intelligence artificielle

➡️ [Documentation certification complète](docs/certification/)

---

## ✨ Fonctionnalités

### 🤖 Intelligence Artificielle

| Fonctionnalité | Description | Status |
|----------------|-------------|--------|
| **Prédiction de combat** | Prédit le vainqueur entre 2 Pokémon avec probabilités | ✅ |
| **Best move recommandation** | Suggère la meilleure capacité à utiliser | ✅ |
| **Analyse multi-moves** | Compare toutes les capacités disponibles | ✅ |
| **Model Registry** | Versioning et promotion automatique des modèles | ✅ |
| **Drift Detection** | Détection de drift sur les prédictions | ✅ |

**Accuracy:** 88.23% sur test set (~30,000 combats)

### 🎮 Interface Utilisateur (Streamlit)

- **Page Accueil** - Présentation et statistiques projet
- **Combat & Prédiction** - Simulateur de combat interactif
- **Capacités** - Catalogue des 226 moves avec filtres
- **Détails Pokémon** - Fiches détaillées (stats, types, évolutions)
- **Types & Affinités** - Matrice complète des 18 types
- **Quiz Types** - Jeu éducatif sur les affinités
- **Crédits** - Sources de données et technologies

### 🔌 API REST (FastAPI)

**Endpoints Pokémon:**
- `GET /pokemon` - Liste des Pokémon avec filtres
- `GET /pokemon/{id}` - Détails d'un Pokémon
- `GET /pokemon/{id}/moves` - Capacités apprises
- `GET /pokemon/{id}/types` - Types et affinités

**Endpoints Prédiction:**
- `POST /predict/battle` - Prédire combat basique
- `POST /predict/best-move` - Recommander meilleure capacité
- `POST /predict/best-move-defender` - Avec capacités adverses

**Endpoints Métadonnées:**
- `GET /types` - Liste des 18 types
- `GET /moves` - Catalogue des capacités
- `GET /health` - Health check

➡️ **Documentation API:** http://localhost:8080/docs (Swagger UI)

### 📊 Monitoring & Observabilité

| Outil | Usage | URL |
|-------|-------|-----|
| **Prometheus** | Métriques temps réel | http://localhost:9091 |
| **Grafana** | 2 dashboards (API + Model) | http://localhost:3001 |
| **Evidently** | Data drift detection | Reports JSON |
| **MLflow** | Experiment tracking + Registry | http://localhost:5001 |

---

## 🏗️ Architecture

### Schéma Global

```
┌─────────────────────────────────────────────────────────────────┐
│                         SOURCES DE DONNÉES                       │
├─────────────────────────────────────────────────────────────────┤
│  📦 CSV          🌐 PokéAPI        🕷️ Pokepedia (Scraper)      │
│  (151 Gen1)      (Stats + Moves)   (Évolutions + Affinités)     │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ETL PIPELINE (Scrapy)                      │
├─────────────────────────────────────────────────────────────────┤
│  1. Load CSV → PostgreSQL (151 Pokémon base)                    │
│  2. Enrich with PokéAPI (Stats, types, moves)                   │
│  3. Scrape Pokepedia (Évolutions, affinités)                    │
│  4. Aggregate data (37 Alola forms, 226 moves)                  │
│  5. Compute type effectiveness matrix (18×18)                    │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                           │
├─────────────────────────────────────────────────────────────────┤
│  📊 11 tables normalisées (3NF)                                 │
│  • pokemon (188 entrées)                                         │
│  • pokemon_type (dual types)                                     │
│  • type (18 types)                                               │
│  • type_effectiveness (affinités 18×18)                          │
│  • move (226 capacités)                                          │
│  • pokemon_move (capacités apprises)                             │
│  • pokemon_stats (HP, Atk, Def, SpA, SpD, Spe)                  │
│  • form, pokemon_species, learn_method, move_category           │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ├─────────────────────────────┬───────────────────┐
               ▼                             ▼                   ▼
┌──────────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ML PIPELINE (XGBoost)  │  │  API REST        │  │  INTERFACE       │
├──────────────────────────┤  │  (FastAPI)       │  │  (Streamlit)     │
│ 1. Dataset Building      │  ├──────────────────┤  ├──────────────────┤
│    • Generate 898k       │  │ • 15 endpoints   │  │ • 7 pages        │
│      battle scenarios    │  │ • Authentication │  │ • Interactif     │
│    • Feature engineering │  │ • Swagger docs   │  │ • Prédictions    │
│      (133 features)      │  │ • CORS enabled   │  │   temps réel     │
│                          │  │                  │  │ • Visualisations │
│ 2. Training              │  │ Routes:          │  │                  │
│    • XGBoost classifier  │  │ /pokemon         │  │ Pages:           │
│    • GridSearchCV        │  │ /types           │  │ Combat           │
│    • CPU optimized       │  │ /moves           │  │ Capacités        │
│                          │  │ /predict/battle  │  │ Détails Pokémon  │
│ 3. Evaluation            │  │ /predict/        │  │ Types            │
│    • Accuracy: 88.23%    │  │   best-move      │  │ Quiz             │
│    • ROC-AUC: 0.94       │  │ /health          │  │ Crédits          │
│                          │  │                  │  │                  │
│ 4. Export                │  │ Sécurité:        │  │ Features:        │
│    • Model (40 MB)       │  │ • API Key auth   │  │ • Cache          │
│    • Scalers             │  │ • Rate limiting  │  │ • Formatters     │
│    • Metadata            │  │ • HTTPS ready    │  │ • Error handling │
│                          │  │                  │  │                  │
│ 5. MLflow                │  │ Performance:     │  │ Performance:     │
│    • Tracking            │  │ • 200ms latency  │  │ • <1s load       │
│    • Model Registry      │  │ • 100 RPS        │  │ • Responsive     │
│    • Auto-promotion      │  │ • Monitored      │  │                  │
└──────────────┬───────────┘  └────────┬─────────┘  └────────┬─────────┘
               │                       │                      │
               ▼                       ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MONITORING STACK                            │
├─────────────────────────────────────────────────────────────────┤
│  📊 Prometheus → Grafana (2 dashboards)                          │
│  🔍 Evidently → Data Drift Detection                             │
│  📈 MLflow → Experiment Tracking + Model Registry                 │
│  🚨 Alerting → 8 règles configurées                              │
└─────────────────────────────────────────────────────────────────┘
```

➡️ **Diagrammes détaillés:** [docs/certification/E1_ARCHITECTURE_DIAGRAM.md](docs/certification/E1_ARCHITECTURE_DIAGRAM.md)

---

## 🔧 Stack Technique

### Backend & Data

| Composant | Technologie | Version | Usage |
|-----------|-------------|---------|-------|
| **Language** | Python | 3.11 | Langage principal |
| **Database** | PostgreSQL | 15 | BDD relationnelle |
| **ORM** | SQLAlchemy | 2.0 | Mapping objet-relationnel |
| **API Framework** | FastAPI | 0.109 | REST API |
| **Validation** | Pydantic | 2.5 | Schémas et validation |
| **Web Scraping** | Scrapy | 2.11 | Scraping Pokepedia |
| **HTTP Client** | HTTPX | 0.27 | Appels PokéAPI |

### Machine Learning

| Composant | Technologie | Version | Usage |
|-----------|-------------|---------|-------|
| **ML Framework** | scikit-learn | 1.4 | Preprocessing, metrics |
| **Model** | XGBoost | 2.0 | Classification (Tree boosting) |
| **Data Processing** | pandas | 2.2 | DataFrames |
| **Numerical** | NumPy | 1.26 | Calculs matriciels |
| **Serialization** | Joblib | 1.3 | Compression modèles |
| **Storage** | Parquet (PyArrow) | 15.0 | Datasets columnar |

### MLOps & Monitoring

| Composant | Technologie | Version | Usage |
|-----------|-------------|---------|-------|
| **Experiment Tracking** | MLflow | 2.18 | Tracking + Model Registry |
| **Metrics** | Prometheus | 2.47 | Collecte métriques |
| **Dashboards** | Grafana | 10.1 | Visualisation |
| **Data Drift** | Evidently | 0.4 | Drift detection |

### Frontend & DevOps

| Composant | Technologie | Version | Usage |
|-----------|-------------|---------|-------|
| **Interface** | Streamlit | 1.39 | Interface utilisateur |
| **Visualization** | Plotly | 5.18 | Graphiques interactifs |
| **Containerization** | Docker | 24+ | Containers |
| **Orchestration** | Docker Compose | 2+ | Multi-services |
| **CI/CD** | GitHub Actions | - | Pipelines automatisés |
| **Testing** | pytest | 8.0 | Tests unitaires |

---

## 📊 Résultats ML

### Métriques du Modèle (XGBoost v2)

| Métrique | Train | Test | Target |
|----------|-------|------|--------|
| **Accuracy** | 98.21% | **88.23%** | > 85% ✅ |
| **Precision** | 98.30% | 87.89% | > 85% ✅ |
| **Recall** | 98.15% | 88.45% | > 85% ✅ |
| **F1-Score** | 98.22% | 88.17% | > 85% ✅ |
| **ROC-AUC** | 0.998 | **0.940** | > 0.90 ✅ |

**Overfitting:** 9.98% (acceptable pour données de jeu)

### Performance

| Métrique | Valeur | Note |
|----------|--------|------|
| **Training time** | ~8 minutes | CPU optimisé (hist) |
| **Inference time** | ~50ms (P95) | Production ready |
| **Model size** | 39.8 MB | Compressé (XGBoost) |
| **Dataset size** | 898,472 combats | Multi-scénarios v2 |
| **Features** | 133 features | Engineered |

### Features les Plus Importantes

1. **effective_power_a** (17.2%) - Puissance effective Pokémon A
2. **effective_power_b** (15.8%) - Puissance effective Pokémon B
3. **stat_ratio** (9.3%) - Ratio stats totales A/B
4. **a_move_type_mult** (7.1%) - Multiplicateur type capacité A
5. **type_advantage_diff** (6.8%) - Différence avantages types

➡️ **Documentation ML complète:** [docs/ml/RUN_MACHINE_LEARNING.md](docs/ml/RUN_MACHINE_LEARNING.md)

---

## 🎮 Utilisation

### 1. Prédiction via API (curl)

```bash
# Prédire un combat: Pikachu (25) vs Dracaufeu (6)
curl -X POST "http://localhost:8080/predict/battle" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "pokemon_a_id": 25,
    "pokemon_b_id": 6
  }'

# Réponse:
{
  "winner": "B",
  "pokemon_a_name": "Pikachu",
  "pokemon_b_name": "Dracaufeu",
  "probability_a_wins": 0.23,
  "probability_b_wins": 0.77,
  "confidence": "high"
}
```

### 2. Interface Streamlit

1. Ouvrir http://localhost:8502
2. Naviguer vers "Combat et Prédiction"
3. Sélectionner 2 Pokémon
4. Choisir les capacités
5. Cliquer sur "Prédire le combat"
6. Voir résultats avec probabilités et analyses

➡️ **Plus d'exemples:** [api_pokemon/README_PREDICTION.md](api_pokemon/README_PREDICTION.md)

---

## 🧪 Tests

### Organisation

```
tests/
├── api/                    # Tests API REST (64 tests)
├── core/                   # Tests modèles SQLAlchemy (15 tests)
├── ml/                     # Tests ML pipeline (50 tests)
├── mlflow/                 # Tests MLOps (17 tests)
├── integration/            # Tests E2E (9 tests)
├── interface/              # Tests Streamlit (20 tests)
├── monitoring/             # Tests monitoring (15 tests)
├── etl/                    # Tests ETL (12 tests)
└── conftest.py             # Fixtures pytest
```

### Exécuter les tests

```bash
# Tous les tests
pytest tests/ -v

# Par catégorie
pytest tests/api/ -v              # Tests API
pytest tests/ml/ -v               # Tests ML
pytest tests/mlflow/ -v           # Tests MLOps

# Avec coverage
pytest tests/ --cov=api_pokemon --cov=machine_learning --cov-report=html
```

### Métriques de Tests

| Catégorie | Nombre | Coverage |
|-----------|--------|----------|
| **API** | 64 tests | 85% |
| **ML** | 50 tests | 78% |
| **MLflow** | 17 tests | 82% |
| **Integration** | 9 tests | 70% |
| **Interface** | 20 tests | 65% |
| **Monitoring** | 15 tests | 80% |
| **ETL** | 12 tests | 72% |
| **TOTAL** | **252 tests** | **82%** |

**Durée d'exécution:** ~15 secondes

➡️ **Documentation tests:** [tests/README.md](tests/README.md)

---

## 📚 Documentation

### Documentation Principale

| Document | Description | Lignes |
|----------|-------------|--------|
| [PROJECT_SYNTHESIS_CLAUDE.md](PROJECT_SYNTHESIS_CLAUDE.md) | ⭐ Synthèse technique complète | 2112 |
| [CHANGELOG.md](CHANGELOG.md) | Historique des versions | 158 |
| [MARKDOWN_CLEANUP_REPORT.md](MARKDOWN_CLEANUP_REPORT.md) | Rapport de tri documentation | - |

### Documentation Certification (E1/E3)

| Document | Description | Lignes |
|----------|-------------|--------|
| [E1_DOCUMENTATION.md](docs/certification/E1_DOCUMENTATION.md) | Bloc E1 complet (C1-C5) | 750 |
| [E1_ARCHITECTURE_DIAGRAM.md](docs/certification/E1_ARCHITECTURE_DIAGRAM.md) | Schémas architecture | 480 |
| [E1_CHOIX_TECHNIQUES.md](docs/certification/E1_CHOIX_TECHNIQUES.md) | Justifications choix tech | 377 |
| [E3_COMPETENCES_STATUS.md](docs/certification/E3_COMPETENCES_STATUS.md) | Validation compétences E3 | 540 |

### Documentation ML/MLOps

| Document | Description | Lignes |
|----------|-------------|--------|
| [RUN_MACHINE_LEARNING.md](docs/ml/RUN_MACHINE_LEARNING.md) | Guide pipeline ML complet | 677 |
| [MLFLOW_REGISTRY_GUIDE.md](docs/ml/MLFLOW_REGISTRY_GUIDE.md) | Model Registry MLflow | 368 |

### Documentation Deployment

| Document | Description | Lignes |
|----------|-------------|--------|
| [QUICK_START.md](docs/deployment/QUICK_START.md) | Démarrage rapide 5 min | 301 |
| [CI_CD_SETUP.md](docs/deployment/CI_CD_SETUP.md) | GitHub Actions | 439 |
| [DOCKER_ORCHESTRATION.md](docs/deployment/DOCKER_ORCHESTRATION.md) | Orchestration 9 services | - |

---

## 🎓 Certification RNCP

### Bloc E1 - Collecte et Traitement de Données

| Compétence | Validation | Preuves |
|-----------|-----------|---------|
| **C1** - Extraire données | ✅ 100% | CSV + PokéAPI + Scraping Pokepedia |
| **C2** - Requêtes SQL | ✅ 100% | SQLAlchemy + requêtes complexes |
| **C3** - Agréger données | ✅ 100% | Pipeline ETL 5 phases |
| **C4** - Créer BDD | ✅ 100% | PostgreSQL 11 tables normalisées |
| **C5** - Exposer API REST | ✅ 100% | FastAPI 15 endpoints + Swagger |

**Score E1:** 5/5 compétences validées (100%)

### Bloc E3 - Intégration IA

| Compétence | Validation | Preuves |
|-----------|-----------|---------|
| **C9** - API REST IA | ✅ 100% | /predict/battle + /predict/best-move |
| **C10** - Intégration app | ✅ 100% | Streamlit 7 pages + API client |
| **C11** - Monitoring | ✅ 100% | Prometheus + Grafana + Evidently |
| **C12** - Tests ML | ✅ 100% | 252 tests (82% coverage) |
| **C13** - MLOps CI/CD | ✅ 100% | Docker + GitHub Actions + MLflow |

**Score E3:** 5/5 compétences validées (100%)

➡️ **Dossier certification:** [docs/certification/](docs/certification/)

---

## 🛠️ Développement

### Prérequis

- Python 3.11+
- Docker 24+ & Docker Compose 2+
- PostgreSQL 15 (via Docker)
- Git

### Installation Locale (sans Docker)

```bash
# 1. Créer environnement virtuel
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Configurer PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=letsgo_db

# 4. Exécuter ETL
python etl_pokemon/pipeline.py

# 5. Entraîner modèle
python machine_learning/run_machine_learning.py --mode=all

# 6. Lancer API
cd api_pokemon
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# 7. Lancer interface (terminal séparé)
cd interface
streamlit run app.py --server.port 8501
```

---

## 📈 Monitoring

### Prometheus Metrics

**API Metrics:**
- `api_requests_total` - Nombre total de requêtes
- `api_request_duration_seconds` - Latence requêtes (histogram)
- `api_errors_total` - Nombre d'erreurs

**Model Metrics:**
- `model_predictions_total` - Nombre de prédictions
- `model_prediction_duration_seconds` - Temps inférence
- `model_drift_score` - Score de drift (PSI)

### Grafana Dashboards

**Dashboard 1: API Performance**
- Requêtes par seconde (QPS)
- Latence P50, P95, P99
- Taux d'erreurs (%)

**Dashboard 2: Model Performance**
- Prédictions par heure
- Distribution des probabilités
- Drift score évolution

### Accès Monitoring

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3001 | admin / admin |
| **Prometheus** | http://localhost:9091 | - |
| **MLflow** | http://localhost:5001 | - |

➡️ **Documentation monitoring:** [docs/monitoring/MONITORING_README.md](docs/monitoring/MONITORING_README.md)

---

## 🐳 Docker

### Services Docker Compose (9)

| Service | Port | Description |
|---------|------|-------------|
| **db** | 5432 (internal) | PostgreSQL 15 |
| **etl** | - | Pipeline ETL (one-shot) |
| **ml_builder** | - | ML training (one-shot) |
| **api** | 8080 | FastAPI REST API |
| **streamlit** | 8502 | Interface Streamlit |
| **prometheus** | 9091 | Métriques |
| **grafana** | 3001 | Dashboards |
| **node-exporter** | 9101 | Métriques système |
| **mlflow** | 5001 | Tracking + Registry |

### Commandes Docker

```bash
# Build et lancer stack complète
docker compose up --build

# Arrêter stack
docker compose down

# Voir logs
docker compose logs -f api            # API seulement

# Rebuild un service spécifique
docker compose build api
docker compose up -d api
```

➡️ **Documentation Docker:** [docs/deployment/DOCKER_ORCHESTRATION.md](docs/deployment/DOCKER_ORCHESTRATION.md)

---

## 🔒 Sécurité

### Authentification API

**API Key Authentication:**
```python
# Header requis pour toutes les routes /predict/*
X-API-Key: your-secret-api-key-here
```

### Bonnes Pratiques Implémentées

✅ API Key authentication
✅ HTTPS ready (reverse proxy)
✅ CORS restrictif
✅ Headers sécurité
✅ Rate limiting
✅ Réseau Docker isolé
✅ Validation Pydantic (injection prevention)

➡️ **Documentation sécurité:** [docs/security/SECURITY.md](docs/security/SECURITY.md)

---

## 🤝 Contribution

### Workflow Git

```bash
# 1. Créer branche feature
git checkout -b feature/ma-fonctionnalite

# 2. Développer et tester
pytest tests/ -v

# 3. Commit
git commit -m "feat(api): add new prediction endpoint"

# 4. Push et créer Pull Request
git push origin feature/ma-fonctionnalite
```

---

## ⚖️ Propriété Intellectuelle & Conformité

### 🔒 Conformité RGPD

Ce projet est **conforme au RGPD** (Règlement Général sur la Protection des Données) :

- ❌ **Aucune donnée personnelle** collectée ou stockée
- ✅ Base de données contenant **uniquement des données de jeu Pokémon**
- ✅ Métriques techniques **anonymes et agrégées**
- ✅ Pas de cookies de tracking, pas d'identification utilisateur

### ⚠️ Disclaimer Juridique - Marques Pokémon

**Pokémon** et tous les noms de personnages Pokémon sont des **marques déposées** de **Nintendo**, **Creatures Inc.** et **GAME FREAK Inc.**

© 1995–2026 Nintendo / Creatures Inc. / GAME FREAK Inc.

**Ce projet est un projet pédagogique à but non lucratif** développé dans le cadre d'une **certification RNCP Concepteur Développeur d'Applications** (Niveau 6).

### 🎓 Exception Pédagogique (Loi Française)

Ce projet bénéficie de l'**exception pédagogique** française (article L122-5 du Code de la Propriété Intellectuelle, loi DADVSI du 1er août 2006) qui autorise l'utilisation d'extraits d'œuvres à des fins exclusives d'illustration dans le cadre de l'enseignement et de la recherche.

**Conditions respectées :**
- ✅ Usage à des fins d'enseignement (certification RNCP)
- ✅ Public spécifique : jury de certification, formateurs, étudiants
- ✅ Usage non-commercial : aucune exploitation commerciale
- ✅ Attribution des sources : PokéAPI et Pokepedia crédités

### 📚 Sources de Données Tierces

Les données Pokémon proviennent de **3 sources complémentaires** utilisées dans le pipeline ETL :

#### 1. CSV manuels (3 fichiers - 738 lignes)
- **`liste_pokemon.csv`** (188 Pokémon) : noms (FR/EN), types, formes (Alola, Mega, Starter)
- **`liste_capacite_lets_go.csv`** (226 capacités) : noms, type, classe, puissance, précision, PP
- **`table_type.csv`** (324 affinités) : matrice multiplicateurs de dégâts (type_attaquant × type_defenseur)

*CSV créés manuellement en compilant des métadonnées de jeu depuis sources communautaires Pokémon.*

#### 2. PokéAPI (API REST)
- **Source :** https://pokeapi.co/
- **Usage :** Enrichissement automatique des **statistiques de combat** (HP, Attaque, Défense, Vitesse) + sprites PNG
- **Statut :** API RESTful open-source (non affiliée officiellement à Nintendo)

#### 3. Pokepedia (Web Scraping avec Scrapy)
- **Source :** https://www.pokepedia.fr/
- **Usage :** Spider Scrapy pour extraire détails des capacités Let's Go (puissance, précision, PP, descriptions françaises)
- **Licence :** Creative Commons CC-BY-SA (encyclopédie collaborative)

**⚖️ Conformité :** Métadonnées et statistiques de jeu publiques (noms, types, HP, Attaque) - aucun code source, aucun asset propriétaire Nintendo - utilisées dans un cadre strictement pédagogique.

### 🛡️ Engagement

Ce projet :
- Ne génère **aucun revenu** commercial
- N'est **pas affilié** à Nintendo, The Pokémon Company ou leurs filiales
- Respecte les **droits de propriété intellectuelle** des ayants droit
- Utilise les données dans un **cadre strictement éducatif**

---

## 🙏 Remerciements

### Sources de Données

- **PokéAPI** (https://pokeapi.co/) - API REST Pokémon (statistiques et sprites)
- **Pokepedia** (https://www.pokepedia.fr/) - Encyclopédie Pokémon francophone (scraping capacités, licence CC-BY-SA)
- **Serebii.net** (https://www.serebii.net/) - Base de données Pokémon (référence pour CSV capacités)
- **Bulbapedia** (https://bulbapedia.bulbagarden.net/) - Encyclopédie Pokémon anglophone (référence pour CSV Pokémon)

### Technologies Open Source

Merci aux mainteneurs de: FastAPI, XGBoost, MLflow, Prometheus, Grafana, Streamlit, PostgreSQL, Docker

---

## 📊 Statistiques Projet

| Métrique | Valeur |
|----------|--------|
| **Lignes de code Python** | ~15,000 |
| **Lignes de tests** | ~5,000 |
| **Lignes de documentation** | ~5,338 |
| **Tests** | 252 |
| **Coverage** | 82% |
| **Services Docker** | 9 |
| **Pokémon** | 188 |
| **Capacités** | 226 |
| **Combats simulés** | 898,472 |
| **Features ML** | 133 |

---

**Version:** 2.0 - Production Ready
**Dernière mise à jour:** 27 janvier 2026
**Statut:** ✅ Active Development
