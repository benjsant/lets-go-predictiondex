# Docker Setup - PredictionDex

## Architecture Docker

Le projet est conteneurisé en **5 services** orchestrés par Docker Compose :

```
┌──────────────┐
│      DB      │  PostgreSQL 15
│  (postgres)  │
└──────┬───────┘
       │
       ├─────> ETL        (etl_pokemon/)
       │        └─> Charge les données CSV + PokéAPI + Scraping
       │
       ├─────> ML Builder (machine_learning/)
       │        └─> Génère le dataset ML après ETL
       │
       ├─────> API        (api_pokemon/)
       │        └─> FastAPI REST API (port 8000)
       │
       └─────> Streamlit  (interface/)
                └─> Interface web (port 8501)
```

## Services

| Service | Dockerfile | Port | Dépend de | Description |
|---------|-----------|------|-----------|-------------|
| `db` | postgres:15 | 5432 | - | Base PostgreSQL |
| `etl` | Dockerfile.etl | - | db (healthy) | Pipeline ETL complet |
| `ml_builder` | Dockerfile.ml | - | etl (completed) | Génération dataset ML |
| `api` | Dockerfile.api | 8000 | db (healthy) | API REST FastAPI |
| `streamlit` | Dockerfile.streamlit | 8501 | api (healthy) | Interface web |

## Ordre de démarrage

```
1. db          → Attend pg_isready
2. etl         → Attend db healthy, exécute ETL complet
3. ml_builder  → Attend etl completed, génère dataset ML
4. api         → Attend db healthy, démarre FastAPI
5. streamlit   → Attend api healthy, lance interface
```

## Mode Développement

### Variables d'environnement (.env)

```bash
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password
POSTGRES_DB=letsgo_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEV_MODE=true
```

### Volumes montés (hot reload)

En mode dev, tous les services montent leurs sources en volumes :

```yaml
volumes:
  - ./etl_pokemon:/app/etl_pokemon       # ETL
  - ./machine_learning:/app/machine_learning  # ML
  - ./api_pokemon:/app/api_pokemon       # API (--reload activé)
  - ./interface:/app/interface           # Streamlit (runOnSave)
  - ./core:/app/core                     # Shared models
```

Tout changement de code est **immédiatement reflété** sans rebuild.

## Commandes

### Démarrage complet

```bash
docker-compose up --build
```

### Démarrage en arrière-plan

```bash
docker-compose up -d --build
```

### Voir les logs

```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f api
docker-compose logs -f etl
docker-compose logs -f streamlit
```

### Redémarrer un service

```bash
docker-compose restart api
docker-compose restart streamlit
```

### Stopper tout

```bash
docker-compose down
```

### Nettoyer (⚠️ supprime les volumes)

```bash
docker-compose down -v
```

### Rebuild un service spécifique

```bash
docker-compose up --build api
```

## Ordre de build recommandé

Pour éviter les erreurs de dépendances lors du premier build :

```bash
# 1. Builder les images sans démarrer
docker-compose build

# 2. Démarrer la DB seule
docker-compose up -d db

# 3. Attendre que la DB soit prête
docker-compose logs db | grep "ready to accept connections"

# 4. Démarrer les autres services
docker-compose up --build
```

## Healthchecks

### PostgreSQL (db)

```bash
pg_isready -U letsgo_user -d letsgo_db
```

Vérifié toutes les 5s, timeout 5s, 5 retries.

### API (api)

```bash
curl -f http://localhost:8000/health
```

Vérifié toutes les 10s, timeout 5s, 5 retries, start_period 30s.

## Troubleshooting

### L'API ne démarre pas

```bash
# Vérifier les logs
docker-compose logs api

# Vérifier que la DB est accessible
docker-compose exec api ping db

# Tester la connexion DB depuis l'API
docker-compose exec api python -c "import psycopg2; psycopg2.connect(host='db', user='letsgo_user', password='letsgo_password', dbname='letsgo_db')"
```

### L'ETL échoue

```bash
# Voir les logs détaillés
docker-compose logs etl

# Relancer l'ETL avec --force
docker-compose run --rm etl python etl_pokemon/run_all_in_one.py --force
```

### Le ML Builder ne trouve pas les données

```bash
# Vérifier que l'ETL a créé le flag
docker-compose exec etl ls -la /app/etl_pokemon/.etl_done

# Vérifier les tables de la DB
docker-compose exec db psql -U letsgo_user -d letsgo_db -c "\dt"
```

### Streamlit ne se connecte pas à l'API

```bash
# Vérifier que l'API est accessible
docker-compose exec streamlit curl http://api:8000/health

# Vérifier la variable d'env
docker-compose exec streamlit env | grep API_BASE_URL
```

### Hot reload ne fonctionne pas

Vérifier que `DEV_MODE=true` dans les variables d'environnement :

```bash
docker-compose exec api env | grep DEV_MODE
docker-compose exec streamlit env | grep DEV_MODE
```

## Ports exposés

| Service | Port hôte | Port container | URL |
|---------|-----------|----------------|-----|
| db | 5432 | 5432 | postgresql://localhost:5432 |
| api | 8000 | 8000 | http://localhost:8000 |
| streamlit | 8501 | 8501 | http://localhost:8501 |

### Accès

- **API Swagger** : http://localhost:8000/docs
- **API Health** : http://localhost:8000/health
- **Streamlit UI** : http://localhost:8501

## Structure des Dockerfiles

### Dockerfile.etl

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app

# Install dependencies
COPY etl_pokemon/requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY etl_pokemon ./etl_pokemon
COPY core ./core

CMD ["python", "etl_pokemon/run_all_in_one.py"]
```

### Dockerfile.api

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app

# Install dependencies
COPY api_pokemon/requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY api_pokemon ./api_pokemon
COPY core ./core
COPY docker/entrypoint.py ./docker/entrypoint.py

ENTRYPOINT ["python", "docker/entrypoint.py"]
```

Le fichier `entrypoint.py` gère :
- Attente de la DB avec retry
- Démarrage d'uvicorn avec `--reload` si `DEV_MODE=true`

## Dépendances Python

### etl_pokemon/requirements.txt

```
python-dotenv
fastapi
uvicorn[standard]
pydantic
sqlalchemy
psycopg2-binary
asyncpg
requests
aiohttp
pandas
scrapy
parsel
lxml
tqdm
```

### api_pokemon/requirements.txt

```
python-dotenv
fastapi
uvicorn[standard]
pydantic
pydantic-settings
sqlalchemy
psycopg2-binary
asyncpg
requests
```

### machine_learning/requirements.txt

```
python-dotenv
pandas
numpy
scikit-learn
pyarrow
sqlalchemy
psycopg2-binary
```

### interface/requirements_streamlit.txt

```
streamlit
requests
pandas
matplotlib
plotly
pydantic
```

## Optimisations Dev

### Cache des dépendances

Les Dockerfiles copient d'abord uniquement `requirements.txt`, puis installent les dépendances, puis copient le code.

Cela permet de **cacher la couche d'installation** si les requirements n'ont pas changé.

### .dockerignore

Exclut :
- `.venv/`, `__pycache__/`
- `.git/`, `.gitignore`
- `*.pyc`, `*.log`
- Documentation

Cela accélère le contexte de build.

## Production

Pour un déploiement en production, modifier :

1. **Retirer les volumes de code** (utiliser uniquement les COPY des Dockerfiles)
2. **Désactiver DEV_MODE** (`DEV_MODE=false`)
3. **Sécuriser les credentials** (utiliser Docker secrets ou variables d'env externes)
4. **Ajouter un reverse proxy** (Nginx, Traefik) devant l'API
5. **Utiliser gunicorn** au lieu d'uvicorn pour l'API
6. **Configurer les logs** (Loki, Elasticsearch)

## Conclusion

Le setup Docker est configuré pour le **développement rapide** avec :
- ✅ Hot reload API (uvicorn --reload)
- ✅ Hot reload Streamlit (runOnSave)
- ✅ Volumes montés pour modification immédiate
- ✅ Healthchecks pour orchestration fiable
- ✅ Restart policies adaptées
- ✅ Séparation claire des responsabilités

Pour toute question : voir [README.md](README.md)
