# Pokémon Let’s Go – PredictionDex

> 🎯 **Projet complet:** ETL → PostgreSQL → ML → MLflow Registry → API REST → Streamlit  
> 📊 **Version:** 2.0 (Production Ready)  
> ✅ **Status:** 5/5 Compétences E3 validées

---

## 📖 Documentation Complète

**👉 Voir [PROJECT_SYNTHESIS.md](./PROJECT_SYNTHESIS.md) pour la synthèse complète du projet**

---

## 📌 Présentation Rapide

**PredictionDex** est un projet complet de **Data Engineering + Machine Learning + MLOps** autour de *Pokémon Let's Go Pikachu & Évoli*.

**Objectifs:**
- Pipeline **ETL complet** (Pokepedia, PokéAPI, PostgreSQL)
- Modèle **ML optimisé** (XGBoost 88.23% accuracy)
- **API REST** avec prédictions battle (FastAPI)
- **MLflow Model Registry** avec auto-promotion
- **Monitoring** production (Prometheus + Grafana)
- **Interface** Streamlit (7 pages interactives)

**Pipeline complet:** ETL → stockage → ML Training → Registry → API → UI

---

## 🚀 Quick Start

```bash
# 1️⃣ Démarrage complet (1 commande)
docker compose up --build

# 2️⃣ Accès services
# - API: http://localhost:8000/docs
# - Streamlit: http://localhost:8501
# - MLflow: http://localhost:5000
# - Grafana: http://localhost:3000 (admin/admin)

# 3️⃣ Tests
pytest tests/ -v  # 252 tests
```

Voir [QUICK_START.md](./QUICK_START.md) pour plus de détails.

---

## 🎯 Compétences E3 Validées ✅

| Compétence | Status | Preuves |
|------------|--------|---------|
| **C9** - API REST avec IA | ✅ 100% | FastAPI + `/predict/battle` + Swagger |
| **C10** - Intégration app | ✅ 100% | Streamlit 7 pages + client API |
| **C11** - Monitoring | ✅ 100% | Prometheus + Grafana + Evidently |
| **C12** - Optimisation ML | ✅ 100% | XGBoost CPU + Compression + MLflow |
| **C13** - MLOps CI/CD | ✅ 100% | GitHub Actions + Model Registry |

**Score:** 5/5 | Voir [E3_COMPETENCES_STATUS.md](./E3_COMPETENCES_STATUS.md)

---

## 📊 Résultats ML

**Modèle Production (XGBoost v2):**
- Accuracy: **88.23%**
- Taille: **39.8 MB** (compressé)
- Latency: **~50ms** (P95)
- Features: **47** (stats + types + moves)

**Optimisations appliquées:**
- ✅ CPU multi-threading (`n_jobs=-1`)
- ✅ MLflow Model Registry + auto-promotion
- ✅ Compression joblib (5-10x)
- ✅ Monitoring Prometheus/Grafana

Voir [RUN_MACHINE_LEARNING.md](./RUN_MACHINE_LEARNING.md) pour le guide complet.

---

## 🔧 Stack Technique

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic  
**ML:** XGBoost, scikit-learn, MLflow, joblib  
**Monitoring:** Prometheus, Grafana, Evidently  
**DevOps:** Docker Compose, GitHub Actions, pytest (252 tests)

Voir [E1_CHOIX_TECHNIQUES.md](./E1_CHOIX_TECHNIQUES.md) pour les justifications.

---

## 📚 Documentation Complète

### Essentiels
- **[PROJECT_SYNTHESIS.md](./PROJECT_SYNTHESIS.md)** - 📖 Synthèse complète (COMMENCER ICI)
- **[QUICK_START.md](./QUICK_START.md)** - 🚀 Démarrage rapide
- **[E3_COMPETENCES_STATUS.md](./E3_COMPETENCES_STATUS.md)** - ✅ État compétences

### Machine Learning
- **[RUN_MACHINE_LEARNING.md](./RUN_MACHINE_LEARNING.md)** - Guide ML complet
- **[MLFLOW_REGISTRY_GUIDE.md](./MLFLOW_REGISTRY_GUIDE.md)** - Model Registry usage
- **[MLFLOW_INTEGRATION.md](./MLFLOW_INTEGRATION.md)** - Tracking MLflow

### Monitoring
- **[MONITORING_README.md](./MONITORING_README.md)** - Setup Prometheus/Grafana
- **[MONITORING_GUIDE.md](./MONITORING_GUIDE.md)** - Guide complet monitoring

### Architecture
- **[E1_DOCUMENTATION.md](./E1_DOCUMENTATION.md)** - Documentation E1 complète
- **[E1_ARCHITECTURE_DIAGRAM.md](./E1_ARCHITECTURE_DIAGRAM.md)** - Diagrammes
- **[CI_CD_SETUP.md](./CI_CD_SETUP.md)** - GitHub Actions workflows

### Tests
- **[tests/README.md](./tests/README.md)** - Organisation 252 tests

---

## 🗂️ Architecture Projet

```
Pipeline:
  ETL → PostgreSQL → ML Training → MLflow Registry → API REST → Streamlit

Services Docker:
  ├── postgres (PostgreSQL 15)
  ├── ml_builder (XGBoost training)
  ├── mlflow (Tracking + Registry)
  ├── api (FastAPI REST)
  ├── streamlit (Interface)
  └── monitoring (Prometheus + Grafana)
```

---

## 🧪 Tests & Qualité

```bash
# Tous les tests
pytest tests/ -v  # 252 tests | Coverage 82%

# Par catégorie
pytest tests/api/ -v          # 64 tests - Routes + Services
pytest tests/ml/ -v           # 50 tests - ML Pipeline
pytest tests/mlflow/ -v       # 17 tests - Model Registry
pytest tests/integration/ -v  # 9 tests - E2E MLflow→API

# Coverage
pytest tests/ --cov=. --cov-report=html
```

**CI/CD:** 4 workflows GitHub Actions (tests, docker, lint, ml-pipeline)

---

## 🏗️ Structure Code

```
lets-go-predictiondex/
├── api_pokemon/         # 🌐 API REST FastAPI
│   ├── routes/          # Endpoints
│   ├── services/        # Business logic
│   └── monitoring/      # Prometheus
├── core/                # 🗄️ Database
│   ├── models/          # SQLAlchemy
│   └── schemas/         # Pydantic
├── machine_learning/    # 🤖 ML Pipeline
├── interface/           # 🎨 Streamlit
├── tests/               # 🧪 252 tests
└── docker/              # 🐳 Containers
```

---

## 🔄 Workflow ML Production

```
1. Training
   └─ python run_machine_learning.py --mode all

2. MLflow Tracking
   └─ Params, metrics, artifacts logged

3. Model Registry
   └─ register_model("battle_winner_predictor")

4. Auto-Promotion
   └─ If accuracy >= 85% → stage "Production"

5. API Load
   └─ Load from Registry (stage="Production")

6. Monitoring
   └─ Prometheus metrics + Grafana dashboards
```

---

## 📞 Commandes Utiles

```bash
# Docker
docker compose up          # Start all services
docker compose logs -f api # View API logs
docker compose down -v     # Clean all

# ML Local
python -m machine_learning.run_machine_learning --mode all
python -m machine_learning.train_model --help

# Tests
pytest tests/ -v
pytest tests/mlflow/ -v --cov=machine_learning

# Lint
ruff check .
mypy api_pokemon/ machine_learning/
```

---

## 📖 En Savoir Plus

**👉 Documentation complète:** [PROJECT_SYNTHESIS.md](./PROJECT_SYNTHESIS.md)

**Guides:**
- [QUICK_START.md](./QUICK_START.md) - Démarrage 5min
- [RUN_MACHINE_LEARNING.md](./RUN_MACHINE_LEARNING.md) - ML détaillé
- [MLFLOW_REGISTRY_GUIDE.md](./MLFLOW_REGISTRY_GUIDE.md) - Model Registry

**Architecture:**
- [E1_DOCUMENTATION.md](./E1_DOCUMENTATION.md) - E1 complet
- [E3_COMPETENCES_STATUS.md](./E3_COMPETENCES_STATUS.md) - E3 validé

---

**Version:** 2.0 | **Status:** ✅ Production Ready | **Dernière MAJ:** 26 janvier 2026
├── models/
├── schemas/
├── scripts/
│   ├── init_db.py
│   ├── load_all_csv.py
│   ├── load_pokeapi.py
│   └── inherit_mega_moves.py
├── pokepedia_scraper/
└── run_all_in_one.py
```

---

## 🔄 Pipeline ETL

### 1️⃣ Initialisation de la base

* Création des tables
* Insertion des tables de référence (types, learn methods, etc.)

### 2️⃣ Chargement CSV

* Pokémon (espèces et formes)
* Capacités
* Relations Pokémon ↔ capacités

### 3️⃣ Enrichissement PokéAPI

* Statistiques
* Taille / poids
* Sprites

### 4️⃣ Scraping Poképédia

* Capacités spécifiques Let’s Go
* Méthodes d’apprentissage

### 5️⃣ Post-traitement

* Héritage des capacités Méga

L’ensemble est orchestré via :

```bash
python run_all_in_one.py
```

---

## 🌐 API REST

### Endpoints principaux

#### Pokémon

* `GET /pokemon/` → liste des Pokémon
* `GET /pokemon/{id}` → détail d’un Pokémon

#### Capacités

* `GET /moves/` → liste des capacités
* `GET /moves/{id}` → détail d’une capacité

#### Types

* `GET /types/`

---

## 🧩 Modèles & Schémas

* **SQLAlchemy** : gestion de la persistance
* **Pydantic** : validation et sérialisation des réponses API
* Séparation stricte entre **modèles DB** et **schémas API**

---

## 🐳 Lancement avec Docker

```bash
docker-compose up --build
```

Accès à l’API :

* [http://localhost:8000](http://localhost:8000)
* Swagger : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Tests (à venir)

Des tests unitaires seront ajoutés pour :

* les guards DB
* les services API
* les scripts ETL critiques

---

## 🚀 Améliorations possibles

* Passage partiel en asynchrone
* Pagination des endpoints
* Monitoring (Prometheus / Grafana)
* Modèles de prédiction de combats

---

## 👤 Auteur

Benjamin — Projet pédagogique Pokémon Let’s Go
