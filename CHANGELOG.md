# Changelog - PredictionDex

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [2.0.0] - 2026-01-26

### 🔐 Sécurité - Architecture réseau sécurisée

#### Ajouté
- **API Key authentication** : Middleware FastAPI avec header `X-API-Key`
  - Génération cryptographique de clés (SHA-256)
  - Support multi-clés (séparées par virgules)
  - Mode DEV bypass optionnel
  - Endpoints publics : `/health`, `/metrics`
- **Réseaux Docker isolés** :
  - Réseau `backend` privé : PostgreSQL + API + ETL + ML + MLflow
  - Réseau `monitoring` : Prometheus + Grafana + Node Exporter
  - PostgreSQL NON exposé sur l'hôte (port 5432 interne uniquement)
  - API NON exposée directement (port 8080 interne)
- **Ports modifiés** pour éviter conflits :
  - API : 8000 → 8080 (interne)
  - Streamlit : 8501 → 8502
  - MLflow : 5000 → 5001
  - Prometheus : 9090 → 9091
  - Grafana : 3000 → 3001
  - Node Exporter : 9100 → 9101

#### Fichiers
- `api_pokemon/middleware/security.py` - Middleware d'authentification
- `docs/security/SECURITY.md` - Guide complet de sécurité
- `docs/security/API_KEYS_PRIVATE.md` - Clés générées (gitignored)
- `.env.example` - Template de configuration

#### Documentation
- [SECURITY.md](docs/security/SECURITY.md) - Architecture de sécurité complète
- [ARBORESCENCE_AMELIORATIONS.md](docs/development/ARBORESCENCE_AMELIORATIONS.md) - Propositions d'améliorations

---

## [1.1.0] - 2026-01-25

### 📊 Orchestration Docker complète

#### Ajouté
- **Orchestration automatique** : 9 services avec dépendances gérées
  - PostgreSQL → ETL → ML Builder → API + Services
  - Health checks pour db, api, mlflow
  - Skip ML training si modèle existe (`ML_SKIP_IF_EXISTS=true`)
  - GridSearchCV rapide par défaut (8 combinaisons)
- **Monitoring stack** :
  - Prometheus (scraping 15s, rétention 15j)
  - Grafana (dashboards pré-configurés, auto-login)
  - Node Exporter (métriques système)
- **MLflow tracking** : Server avec backend PostgreSQL

#### Fichiers
- `docker-compose.yml` - Orchestration complète (9 services)
- `docker/*_entrypoint.py` - Scripts de démarrage automatisés
- `docker/grafana/provisioning/` - Configuration Grafana
- `docker/prometheus/prometheus.yml` - Configuration Prometheus

#### Documentation
- [ORCHESTRATION_SUMMARY.md](docs/deployment/ORCHESTRATION_SUMMARY.md) - Guide complet d'orchestration
- [README_DOCKER.md](docs/deployment/README_DOCKER.md) - Quickstart Docker
- [DOCKER_ORCHESTRATION.md](docs/deployment/DOCKER_ORCHESTRATION.md) - Documentation technique

---

## [1.0.0] - 2026-01-20

### 🎉 Version initiale - Certification E1/E3

#### Ajouté
- **ETL Pipeline** (E1 - C1 à C4) :
  - Scrapy spider pour Pokepedia (306 lignes)
  - CSV loader + PokéAPI enrichment
  - 13 modèles SQLAlchemy ORM
  - PostgreSQL 15 avec foreign keys
- **Machine Learning** (E3 - C11, C13) :
  - XGBoost battle winner prediction
  - Feature engineering (44 features)
  - GridSearchCV hyperparameter tuning
  - StandardScaler + encoding
  - Model evaluation (accuracy, precision, recall, F1)
- **API REST** :
  - FastAPI avec Uvicorn
  - Endpoints : `/pokemon`, `/moves`, `/types`, `/predict`
  - Prometheus metrics intégré
  - Health check endpoint
- **Interface Streamlit** :
  - Sélection Pokémon interactive
  - Prédiction de combat en temps réel
  - Visualisation des statistiques
- **MLOps** :
  - MLflow tracking + Model Registry
  - Experiment tracking
  - Artifact storage
- **Tests** :
  - Tests unitaires (API, ETL, ML)
  - Tests d'intégration
  - Coverage > 70%

#### Fichiers principaux
- `etl_pokemon/pokepedia_scraper/` - Spider Scrapy
- `machine_learning/train_model.py` - Entraînement XGBoost
- `machine_learning/mlflow_integration.py` - Intégration MLflow
- `api_pokemon/` - API FastAPI
- `interface/` - Interface Streamlit
- `core/models/` - Modèles SQLAlchemy

#### Documentation
- [E1_E3_VALIDATION_FINALE.md](docs/certification/E1_E3_VALIDATION_FINALE.md) - Validation complète E1/E3
- [E1_DOCUMENTATION.md](docs/certification/E1_DOCUMENTATION.md) - Documentation E1
- [E3_COMPETENCES_STATUS.md](docs/certification/E3_COMPETENCES_STATUS.md) - Status E3

---

## Structure du projet

```
lets-go-predictiondex/
├── api_pokemon/          # API FastAPI
├── core/                 # Modèles DB + Schemas
├── etl_pokemon/          # ETL Scrapy
├── machine_learning/     # ML Pipeline + MLflow
├── interface/            # Streamlit UI
├── docker/               # Dockerfiles + configs
├── docs/                 # Documentation
│   ├── certification/    # E1/E3 validation
│   ├── deployment/       # Docker + CI/CD
│   ├── development/      # Dev guides
│   ├── ml/               # ML docs
│   ├── monitoring/       # Monitoring docs
│   └── security/         # Security docs
├── scripts/              # Scripts utilitaires
├── tests/                # Tests
└── models/               # Modèles entraînés
```

---

## Liens utiles

- **README** : [README.md](README.md)
- **Quickstart** : [QUICK_START.md](docs/deployment/QUICK_START.md)
- **Sécurité** : [SECURITY.md](docs/security/SECURITY.md)
- **Orchestration** : [ORCHESTRATION_SUMMARY.md](docs/deployment/ORCHESTRATION_SUMMARY.md)

---

**Maintenu par** : PredictionDex Team  
**Licence** : MIT
