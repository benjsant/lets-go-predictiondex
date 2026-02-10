# PredictionDex - Pokemon Let's Go Battle Predictor

> Plateforme MLOps pour predire les combats Pokemon Let's Go Pikachu/Eevee

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange.svg)](https://xgboost.readthedocs.io/)
[![MLflow](https://img.shields.io/badge/MLflow-2.18-blue.svg)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

---

## Quick Start

```bash
# 1. Cloner et configurer
git clone <repo-url>
cd lets-go-predictiondex
cp .env.example .env
cp interface/.env.example interface/.env
# Editer .env pour configurer API_KEYS et STREAMLIT_API_KEY

# 2. Lancer la stack (10 services)
docker compose up --build

# 3. Acceder aux interfaces
# API Swagger  : http://localhost:8080/docs
# Streamlit    : http://localhost:8502
# Grafana      : http://localhost:3001 (admin/admin)
# Prometheus   : http://localhost:9091
# MLflow       : http://localhost:5001
# pgAdmin      : http://localhost:5050
```

Premiere execution : ~60-90 min (ETL + ML training). Demarrages suivants : 2-3 min.

---

## Vue d'ensemble

**PredictionDex** predit l'issue de combats Pokemon en analysant les stats, types, et capacites via un modele XGBoost entraine sur 898 612 combats simules.

| Donnees | Valeur |
|---------|--------|
| Pokemon | 188 (Gen 1 + Alola + Mega) |
| Capacites | 226 |
| Types | 18 (matrice d'affinites 18x18) |
| Combats d'entrainement | 898 612 |
| Features engineered | 135 |

### Resultats du modele (XGBoost v2)

| Metrique | Train | Test |
|----------|-------|------|
| **Accuracy** | 98.23% | **96.26%** |
| **Precision** | - | 96.54% |
| **Recall** | - | 96.55% |
| **F1-Score** | - | 96.54% |
| **ROC-AUC** | - | 0.995 |
| **Overfitting** | | 1.97% |

---

## Architecture

```
Sources de donnees
  CSV (151 Pokemon)  +  PokeAPI (Stats/Moves)  +  Pokepedia Scrapy (Evolutions/Affinites)
       |                       |                          |
       v                       v                          v
  +-----------------------------------------------------------------+
  |                     ETL Pipeline (5 phases)                     |
  |  init_db -> load_csv -> enrich_pokeapi -> scrapy -> post_process|
  +-----------------------------------------------------------------+
                               |
                               v
  +-----------------------------------------------------------------+
  |                PostgreSQL (11 tables, 3NF)                      |
  +-----------------------------------------------------------------+
          |                    |                    |
          v                    v                    v
  +----------------+  +----------------+  +------------------+
  | ML Pipeline    |  | API REST       |  | Interface        |
  | XGBoost v2     |  | FastAPI        |  | Streamlit        |
  | 135 features   |  | 15 endpoints   |  | 6 pages          |
  | GridSearchCV   |  | API Key auth   |  | Predictions      |
  +----------------+  +----------------+  +------------------+
          |                    |                    |
          v                    v                    v
  +-----------------------------------------------------------------+
  |                    Monitoring Stack                              |
  |  Prometheus + Grafana + MLflow + Drift Detection                |
  +-----------------------------------------------------------------+
```

---

## Structure du projet

```
lets-go-predictiondex/
├── etl_pokemon/           # Pipeline ETL (CSV + PokeAPI + Scrapy)
├── core/                  # Modeles SQLAlchemy (11 tables)
├── machine_learning/      # Pipeline ML (dataset, training, evaluation)
├── api_pokemon/           # API REST FastAPI (15 endpoints)
├── interface/             # Application Streamlit (6 pages)
├── tests/                 # Tests unitaires et integration
├── models/                # Artefacts ML exportes (modele, scalers, metadata)
├── data/                  # Datasets CSV et ML
├── docker/                # Dockerfiles et configuration services
├── scripts/               # Scripts utilitaires et orchestration
├── docs/                  # Documentation technique
├── reports/               # Rapports auto-generes
└── docker-compose.yml     # Orchestration 10 services
```

Chaque dossier contient son propre `README.md` avec la documentation detaillee :

| Module | Documentation |
|--------|--------------|
| ETL Pipeline | [etl_pokemon/README.md](etl_pokemon/README.md) |
| Core (BDD/ORM) | [core/README.md](core/README.md) |
| Machine Learning | [machine_learning/README.md](machine_learning/README.md) |
| API REST | [api_pokemon/README.md](api_pokemon/README.md) |
| Interface Streamlit | [interface/README.md](interface/README.md) |
| Tests | [tests/README.md](tests/README.md) |
| Tests Integration | [tests/integration/README.md](tests/integration/README.md) |
| Docker | [docker/README.md](docker/README.md) |
| Scripts | [scripts/README.md](scripts/README.md) |
| Modeles ML | [models/README.md](models/README.md) |
| Datasets | [data/ml/README.md](data/ml/README.md) |
| Architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |

---

## Stack technique

### Backend & Data

| Technologie | Version | Usage |
|-------------|---------|-------|
| Python | 3.11 | Langage principal |
| PostgreSQL | 15 | Base de donnees relationnelle |
| SQLAlchemy | 2.0 | ORM |
| FastAPI | 0.109 | API REST |
| Pydantic | 2.5 | Validation des schemas |
| Scrapy | 2.11 | Web scraping Pokepedia |

### Machine Learning & MLOps

| Technologie | Version | Usage |
|-------------|---------|-------|
| XGBoost | 2.0 | Modele de classification |
| scikit-learn | 1.4 | Preprocessing, metriques, GridSearchCV |
| pandas | 2.2 | Manipulation de donnees |
| MLflow | 2.18 | Experiment tracking + Model Registry |
| Prometheus | 2.47 | Collecte de metriques |
| Grafana | 10.1 | Dashboards de monitoring |

### Frontend & DevOps

| Technologie | Version | Usage |
|-------------|---------|-------|
| Streamlit | 1.39 | Interface utilisateur |
| Docker Compose | 2+ | Orchestration multi-services |
| GitHub Actions | - | CI/CD |
| pytest | 8.0 | Tests automatises |

---

## Services Docker

| Service | Port | Description |
|---------|------|-------------|
| **db** | 5432 | PostgreSQL 15 |
| **pgadmin** | 5050 | Administration BDD |
| **etl** | - | Pipeline ETL (one-shot) |
| **ml_builder** | - | Entrainement ML (one-shot) |
| **api** | 8080 | API REST FastAPI |
| **streamlit** | 8502 | Interface utilisateur |
| **prometheus** | 9091 | Metriques temps reel |
| **grafana** | 3001 | Dashboards |
| **node-exporter** | 9101 | Metriques systeme |
| **mlflow** | 5001 | Tracking + Model Registry |

---

## API REST - Endpoints

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/pokemon/` | Liste des Pokemon |
| GET | `/pokemon/search` | Recherche par nom |
| GET | `/pokemon/{id}` | Details d'un Pokemon |
| GET | `/pokemon/{id}/weaknesses` | Faiblesses d'un Pokemon |
| GET | `/moves/` | Liste des capacites |
| GET | `/moves/search` | Recherche de capacites |
| GET | `/moves/by-type/{type}` | Capacites par type |
| GET | `/moves/id/{id}` | Details d'une capacite |
| GET | `/types/` | Liste des 18 types |
| GET | `/types/affinities` | Matrice d'affinites |
| GET | `/types/affinities/by-name` | Affinite specifique |
| GET | `/types/{id}/pokemon` | Pokemon par type (ID) |
| GET | `/types/by-name/{name}/pokemon` | Pokemon par type (nom) |
| POST | `/predict/best-move` | Prediction meilleure capacite |
| GET | `/predict/model-info` | Informations du modele ML |

Documentation interactive : http://localhost:8080/docs (Swagger UI)

---

## Certification RNCP

Ce projet valide les competences des blocs **E1** et **E3** du titre RNCP "Concepteur Developpeur d'Applications" (Niveau 6).

### Bloc E1 - Collecte et traitement de donnees

| Competence | Description | Implementation |
|-----------|-------------|----------------|
| **C1** | Extraction de donnees | CSV + PokeAPI REST + Scrapy scraper |
| **C2** | Requetes SQL | SQLAlchemy ORM + requetes complexes |
| **C3** | Agregation et nettoyage | Pipeline ETL 5 phases |
| **C4** | Creation BDD (RGPD) | PostgreSQL 11 tables normalisees (3NF) |
| **C5** | API REST | FastAPI 15 endpoints + Swagger |

### Bloc E3 - Integration IA en production

| Competence | Description | Implementation |
|-----------|-------------|----------------|
| **C9** | API exposant modele IA | `/predict/best-move` + `/predict/model-info` |
| **C10** | Integration application | Streamlit 6 pages consommant l'API |
| **C11** | Monitoring modele | Prometheus + Grafana + Drift Detection |
| **C12** | Tests automatises | pytest (unitaires + integration) |
| **C13** | CI/CD et MLOps | GitHub Actions + Docker + MLflow |

---

## Propriete intellectuelle & Conformite

### Conformite RGPD

- Aucune donnee personnelle collectee ou stockee
- Base de donnees contenant uniquement des donnees de jeu Pokemon
- Metriques techniques anonymes et agregees

### Disclaimer juridique

**Pokemon** et tous les noms de personnages Pokemon sont des marques deposees de **Nintendo**, **Creatures Inc.** et **GAME FREAK Inc.**

Ce projet est un projet pedagogique a but non lucratif developpe dans le cadre d'une certification RNCP. Il beneficie de l'exception pedagogique francaise (article L122-5 du Code de la Propriete Intellectuelle).

### Sources de donnees

| Source | Type | Usage |
|--------|------|-------|
| CSV manuels | 3 fichiers | Pokemon, capacites, affinites de types |
| [PokeAPI](https://pokeapi.co/) | API REST | Stats de combat, sprites |
| [Pokepedia](https://www.pokepedia.fr/) | Scraping (Scrapy) | Capacites Let's Go (CC-BY-SA) |

---

**Version :** 2.0
**Derniere mise a jour :** Fevrier 2026
