# Architecture Technique

> Schémas d'architecture du projet PredictionDex

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│ SOURCES DE DONNÉES │
├─────────────────────────────────────────────────────────────────┤
│ CSV PokéAPI Pokepedia (Scrapy) │
│ (151 Gen1) (Stats + Moves) (Évolutions + Affinités) │
└──────────────┬──────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────┐
│ ETL PIPELINE │
├─────────────────────────────────────────────────────────────────┤
│ 1. etl_init_db.py → Initialisation schéma PostgreSQL │
│ 2. etl_load_csv.py → Chargement CSV (151 Pokémon base) │
│ 3. etl_enrich_pokeapi.py → Enrichissement PokéAPI │
│ 4. scrapy crawl → Scraping Pokepedia (moves LGPE) │
│ 5. etl_post_process.py → Transformations finales │
└──────────────┬──────────────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────┐
│ POSTGRESQL DATABASE │
├─────────────────────────────────────────────────────────────────┤
│ 11 tables normalisées (3NF) │
│ ├── pokemon (188) ├── type (18) │
│ ├── pokemon_type ├── type_effectiveness (324) │
│ ├── pokemon_stats ├── move (226) │
│ ├── pokemon_move ├── move_category (3) │
│ ├── pokemon_species ├── learn_method │
│ └── form │
└──────────────┬──────────────────────────────────────────────────┘
 │
 ┌───────┴───────┬───────────────────┐
 ▼ ▼ ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│ ML PIPELINE │ │ API REST │ │ INTERFACE │
│ (XGBoost) │ │ (FastAPI) │ │ (Streamlit) │
├──────────────┤ ├──────────────┤ ├──────────────────┤
│ • Dataset │ │ • /pokemon │ │ • 7 pages │
│ 898k combats│ │ • /moves │ │ • Prédictions │
│ • 133 features│ │ • /types │ │ • Visualisations │
│ • Accuracy │ │ • /predict │ │ • Quiz types │
│ 96.26% │ │ • /health │ │ │
└──────┬───────┘ └──────┬───────┘ └────────┬─────────┘
 │ │ │
 └────────────────┴───────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────┐
│ MONITORING STACK │
├─────────────────────────────────────────────────────────────────┤
│ Prometheus (9091) → Collecte métriques │
│ Grafana (3001) → 2 dashboards (API + Model) │
│ MLflow (5001) → Experiment tracking + Model Registry │
│ Drift Detection → Collecte données production │
└─────────────────────────────────────────────────────────────────┘
```

## Stack Technique

### Backend
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Language | Python | 3.11 |
| Database | PostgreSQL | 15 |
| ORM | SQLAlchemy | 2.0 |
| API | FastAPI | 0.109 |
| Validation | Pydantic | 2.5 |

### Machine Learning
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Model | XGBoost | 2.0 |
| Preprocessing | scikit-learn | 1.4 |
| Data | pandas | 2.2 |
| Storage | Parquet (PyArrow) | 15.0 |

### MLOps & Monitoring
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Tracking | MLflow | 2.18 |
| Metrics | Prometheus | 2.47 |
| Dashboards | Grafana | 10.1 |
| CI/CD | GitHub Actions | - |

### Frontend & DevOps
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Interface | Streamlit | 1.39 |
| Containers | Docker | 24+ |
| Orchestration | Docker Compose | 2+ |
| Testing | pytest | 8.0 |

## Ports des Services

| Service | Port | URL |
|---------|------|-----|
| API FastAPI | 8080 | http://localhost:8080/docs |
| Streamlit | 8502 | http://localhost:8502 |
| PostgreSQL | 5432 | - |
| Prometheus | 9091 | http://localhost:9091 |
| Grafana | 3001 | http://localhost:3001 |
| MLflow | 5001 | http://localhost:5001 |
| pgAdmin | 5050 | http://localhost:5050 |
