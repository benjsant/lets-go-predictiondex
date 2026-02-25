# Docker

Configuration Docker Compose pour les 9 services du projet.

## Structure

```
docker/
├── Dockerfile.api         # API FastAPI
├── Dockerfile.etl         # Pipeline ETL
├── Dockerfile.ml          # ML Builder
├── Dockerfile.mlflow      # MLflow Server
├── Dockerfile.streamlit   # Interface Streamlit
├── Dockerfile.tests       # Tests pytest
├── api_entrypoint.py      # Entrypoint API
├── etl_entrypoint.py      # Entrypoint ETL
├── ml_entrypoint.py       # Entrypoint ML
├── wait_for_db.py         # Attente BDD
├── grafana/               # Dashboards + provisioning
├── prometheus/            # prometheus.yml
└── pgadmin4/              # Serveurs pré-configurés
```

## Commandes

```bash
docker compose up --build       # Tout construire et lancer
docker compose up -d            # En arrière-plan
docker compose up api           # Un service en particulier
docker compose build --no-cache # Rebuild sans cache
docker compose run --rm tests   # Lancer les tests
```

## Services

| Service | Port | URL |
|---------|------|-----|
| db (PostgreSQL 15) | 5432 | - |
| api (FastAPI) | 8080 | http://localhost:8080/docs |
| streamlit | 8502 | http://localhost:8502 |
| prometheus | 9091 | http://localhost:9091 |
| grafana | 3001 | http://localhost:3001 (admin/admin) |
| mlflow | 5001 | http://localhost:5001 |
| pgadmin | 5050 | http://localhost:5050 |
| etl | - | One-shot |
| ml_builder | - | One-shot |

## Ordre de démarrage

La BDD démarre en premier. L'ETL attend la BDD, puis le ML builder attend l'ETL. L'API et Streamlit démarrent une fois la BDD prête. Prometheus, Grafana et MLflow sont indépendants.

## Configuration

Les variables d'environnement sont dans `.env` (voir `.env.example`). Les volumes persistants stockent les données PostgreSQL, pgAdmin, Grafana et MLflow.

## Commandes utiles

```bash
docker compose logs -f api                             # Suivre les logs
docker compose exec db psql -U letsgo_user -d letsgo_db # Accès PostgreSQL
docker compose down -v --rmi all                        # Tout nettoyer
```
