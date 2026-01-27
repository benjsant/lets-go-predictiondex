# 🚀 CI/CD GitHub Actions - Explication Détaillée

**Date:** 27 janvier 2026
**Objectif:** Comprendre en profondeur les 4 workflows GitHub Actions et leur fonctionnement

---

## 📋 Table des Matières

1. [Vue d'Ensemble CI/CD](#1-vue-densemble-cicd)
2. [Workflow 1: Tests](#2-workflow-1-tests)
3. [Workflow 2: Docker Build](#3-workflow-2-docker-build)
4. [Workflow 3: ML Pipeline](#4-workflow-3-ml-pipeline)
5. [Workflow 4: Lint & Security](#5-workflow-4-lint--security)
6. [Intégration Complète](#6-intégration-complète)

---

## 1. Vue d'Ensemble CI/CD

### 🎯 Architecture Globale

```
┌──────────────────────────────────────────────────────────┐
│              GITHUB ACTIONS CI/CD PIPELINE               │
└──────────────────────────────────────────────────────────┘

TRIGGER (Push/Pull Request)
    │
    │  git push origin main
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  GitHub Repository                                        │
│  └─ .github/workflows/                                   │
│     ├─ tests.yml          → Workflow 1: Tests            │
│     ├─ docker-build.yml   → Workflow 2: Docker Build     │
│     ├─ ml-pipeline.yml    → Workflow 3: ML Pipeline      │
│     └─ lint.yml           → Workflow 4: Lint & Security  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │  Parallel Execution (4 workflows)
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │               │              │
        ▼              ▼               ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐
│ Workflow 1   │ │ Workflow 2   │ │Workflow 3│ │Workflow 4│
│ Tests        │ │ Docker Build │ │ML Pipeline│ │Lint      │
│ (2-3 min)    │ │ (8-10 min)   │ │(3-4 min) │ │(2-3 min) │
└──────┬───────┘ └──────┬───────┘ └────┬─────┘ └────┬─────┘
       │                │               │             │
       │  ✅ Pass       │  ✅ Pass      │  ✅ Pass    │  ✅ Pass
       │                │               │             │
       └────────────────┴───────────────┴─────────────┘
                       │
                       │  ALL CHECKS PASSED ✅
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│  Pull Request (PR)                                        │
│  ✅ All checks have passed                               │
│  ✅ Code is ready to merge                               │
│                                                           │
│  [Merge Pull Request]                                    │
└──────────────────────────────────────────────────────────┘
                       │
                       │  Merge to main
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│  Production Deployment                                    │
│  - Docker images built and tested                        │
│  - All tests passed (252 tests)                          │
│  - Code quality validated                                │
│  - Security checks passed                                │
│  - ML model validated                                    │
│  → Ready for docker-compose up -d                        │
└──────────────────────────────────────────────────────────┘
```

---

### 📊 Résumé 4 Workflows

| Workflow | Fichier | Triggers | Durée | Objectif |
|----------|---------|----------|-------|----------|
| **1. Tests** | tests.yml | Push/PR sur main, develop | 2-3 min | Run 252 tests, coverage 82% |
| **2. Docker Build** | docker-build.yml | Push/PR sur main, develop | 8-10 min | Build 5 images Docker + tests intégration |
| **3. ML Pipeline** | ml-pipeline.yml | Push ML files, manual trigger | 3-4 min | Tests ML + training optionnel |
| **4. Lint & Security** | lint.yml | Push/PR sur main, develop | 2-3 min | Code quality + security scan |

**Temps total:** 15-20 minutes (en parallèle, pas séquentiel)

---

## 2. Workflow 1: Tests

**Fichier:** `.github/workflows/tests.yml`

### 🎯 Objectif

Exécuter automatiquement les 252 tests unitaires + intégration à chaque commit/PR pour garantir la qualité du code.

### 📝 Code Complet Annoté

```yaml
name: Tests

# TRIGGERS: Quand ce workflow s'exécute
on:
  push:
    branches: [ main, monitoring_grafana_evidently, develop ]
    # → S'exécute sur push vers ces branches
  pull_request:
    branches: [ main, monitoring_grafana_evidently ]
    # → S'exécute sur ouverture/update PR vers ces branches

jobs:
  test:
    # Runner: Machine virtuelle Ubuntu 22.04
    runs-on: ubuntu-latest

    # SERVICE CONTAINERS: PostgreSQL lancé automatiquement
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: letsgo_test
          POSTGRES_USER: letsgo_user
          POSTGRES_PASSWORD: letsgo_password
        ports:
          - 5432:5432
        # Health checks: attendre que Postgres soit prêt avant de continuer
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        # → Postgres sera accessible sur localhost:5432

    # MATRIX STRATEGY: Test sur plusieurs versions Python (ici juste 3.11)
    strategy:
      matrix:
        python-version: ['3.11']

    steps:
      # ÉTAPE 1: Checkout code
      - name: Checkout code
        uses: actions/checkout@v4
        # → Clone le repository GitHub dans le runner

      # ÉTAPE 2: Setup Python
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
        # → Installe Python 3.11

      # ÉTAPE 3: Cache dependencies (optimisation)
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          # Cache key basé sur hash requirements.txt
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
        # → Si requirements.txt n'a pas changé, restaure cache
        # → Gain: 30-60s par run

      # ÉTAPE 4: Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov pytest-asyncio
          pip install -r api_pokemon/requirements.txt
          pip install -r machine_learning/requirements.txt
        # → Installe pytest + toutes les dépendances du projet

      # ÉTAPE 5: Set environment variables
      - name: Set environment variables
        run: |
          echo "POSTGRES_HOST=localhost" >> $GITHUB_ENV
          echo "POSTGRES_PORT=5432" >> $GITHUB_ENV
          echo "POSTGRES_DB=letsgo_test" >> $GITHUB_ENV
          echo "POSTGRES_USER=letsgo_user" >> $GITHUB_ENV
          echo "POSTGRES_PASSWORD=letsgo_password" >> $GITHUB_ENV
          echo "PYTHONPATH=$PWD" >> $GITHUB_ENV
        # → Variables d'environnement pour connexion PostgreSQL

      # ÉTAPE 6: Run tests ⭐ CŒUR DU WORKFLOW
      - name: Run unit tests
        run: |
          pytest tests/ -v \
            --tb=short \
            --cov=api_pokemon \
            --cov=core \
            --cov=machine_learning \
            --cov-report=xml \
            --cov-report=term-missing
        # Options pytest:
        # -v: verbose (détails tests)
        # --tb=short: traceback court si erreur
        # --cov=XXX: coverage pour ces modules
        # --cov-report=xml: génère coverage.xml (pour Codecov)
        # --cov-report=term-missing: affiche lignes non couvertes

      # ÉTAPE 7: Upload coverage to Codecov
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false
        # → Upload coverage vers Codecov.io pour visualisation

      # ÉTAPE 8: Generate coverage badge
      - name: Generate coverage badge
        if: github.ref == 'refs/heads/main'
        run: |
          pip install coverage-badge
          coverage-badge -o coverage.svg -f
        # → Génère badge SVG "Coverage 82%" (seulement sur main)

      # ÉTAPE 9: Archive test results
      - name: Archive test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            coverage.xml
            .coverage
          retention-days: 30
        # → Sauvegarde coverage.xml pendant 30 jours
        # → if: always() = exécute même si tests échouent
```

---

### 🔍 Détails Techniques

#### Service Containers (PostgreSQL)

```yaml
services:
  postgres:
    image: postgres:15
    # ...
```

**Comment ça marche ?**

1. GitHub Actions lance un container Docker PostgreSQL **avant** les steps
2. Container accessible via `localhost:5432` (mapping automatique)
3. Health checks garantissent que Postgres est prêt avant les tests
4. Container est automatiquement arrêté/supprimé après le workflow

**Équivalent Docker local:**

```bash
docker run -d \
  --name postgres-test \
  -e POSTGRES_DB=letsgo_test \
  -e POSTGRES_USER=letsgo_user \
  -e POSTGRES_PASSWORD=letsgo_password \
  -p 5432:5432 \
  postgres:15

# Health check
docker exec postgres-test pg_isready

# Run tests
pytest tests/

# Cleanup
docker stop postgres-test && docker rm postgres-test
```

---

#### Coverage Report

**Output exemple:**

```
========================= test session starts ==========================
platform linux -- Python 3.11.7, pytest-7.4.3, pluggy-1.3.0
rootdir: /home/runner/work/lets-go-predictiondex
plugins: cov-4.1.0, asyncio-0.21.1

collected 252 items

tests/api/test_pokemon_route.py::test_get_pokemon_list PASSED    [  1%]
tests/api/test_pokemon_route.py::test_get_pokemon_by_id PASSED   [  2%]
tests/api/test_prediction_route.py::test_predict_best_move PASSED[  3%]
...
tests/ml/test_feature_engineering.py::test_engineer_features PASSED [99%]
tests/mlflow/test_registry.py::test_load_model_from_registry PASSED[100%]

========================= 252 passed in 14.52s ==========================

---------- coverage: platform linux, python 3.11.7 -----------
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
api_pokemon/__init__.py                       0      0   100%
api_pokemon/main.py                          48      5    90%   78-82
api_pokemon/routes/prediction_route.py       65      8    88%   95-102
api_pokemon/services/prediction_service.py  127     18    86%   234-251
core/db/session.py                           23      2    91%   45-46
core/models/pokemon.py                       45      0   100%
machine_learning/run_machine_learning.py    312     42    87%   567-608
-----------------------------------------------------------------------
TOTAL                                       2847    512    82%

10 files skipped due to complete coverage.
```

---

## 3. Workflow 2: Docker Build

**Fichier:** `.github/workflows/docker-build.yml`

### 🎯 Objectif

Build et tester les 5 images Docker du projet en parallèle, puis exécuter des tests d'intégration avec `docker-compose`.

### 📝 Code Complet Annoté

```yaml
name: Docker Build

on:
  push:
    branches: [ main, monitoring_grafana_evidently, develop ]
  pull_request:
    branches: [ main, monitoring_grafana_evidently ]

jobs:
  # JOB 1: Build images en parallèle (matrix strategy)
  build-and-test:
    runs-on: ubuntu-latest

    # MATRIX STRATEGY: Build 5 services en parallèle
    strategy:
      matrix:
        service: [api, etl, ml, streamlit, mlflow]
        # → GitHub Actions lancera 5 jobs en parallèle (1 par service)
        # → Gain: 8-10 min au lieu de 40-50 min séquentiel

    steps:
      # ÉTAPE 1: Checkout code
      - name: Checkout code
        uses: actions/checkout@v4

      # ÉTAPE 2: Setup Docker Buildx (builder avancé)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        # → Buildx = builder Docker moderne avec cache layers

      # ÉTAPE 3: Cache Docker layers (OPTIMISATION CLÉE)
      - name: Cache Docker layers
        uses: actions/cache@v3
        with:
          path: /tmp/.buildx-cache
          key: ${{ runner.os }}-buildx-${{ matrix.service }}-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-buildx-${{ matrix.service }}-
        # → Cache layers Docker par service
        # → Si Dockerfile/code pas changé, restore cache
        # → Gain: 5-7 min par build

      # ÉTAPE 4: Build image Docker
      - name: Build ${{ matrix.service }} image
        run: |
          docker compose build ${{ matrix.service }}
        # → Équivalent: docker build -t lets-go-predictiondex-api -f docker/api/Dockerfile .
        # → Utilise docker-compose.yml pour config

      # ÉTAPE 5: Save image en tar.gz (artifact)
      - name: Save image
        run: |
          docker save lets-go-predictiondex-${{ matrix.service }} | gzip > ${{ matrix.service }}.tar.gz
        # → Exporte image Docker en fichier .tar.gz
        # → Pourquoi ? Pour partager entre jobs (GitHub Actions)

      # ÉTAPE 6: Upload artifact
      - name: Upload image artifact
        uses: actions/upload-artifact@v3
        with:
          name: docker-${{ matrix.service }}
          path: ${{ matrix.service }}.tar.gz
          retention-days: 1
        # → Upload .tar.gz vers GitHub Artifacts
        # → Accessible par job suivant (integration-test)
        # → retention-days: 1 = supprimé après 24h (économie stockage)

  # JOB 2: Tests d'intégration (dépend de build-and-test)
  integration-test:
    runs-on: ubuntu-latest
    needs: build-and-test
    # → needs: attend que build-and-test soit terminé avec succès

    steps:
      # ÉTAPE 1: Checkout code
      - name: Checkout code
        uses: actions/checkout@v4

      # ÉTAPE 2: Download ALL artifacts (5 images Docker)
      - name: Download all artifacts
        uses: actions/download-artifact@v3
        # → Télécharge docker-api, docker-etl, docker-ml, docker-streamlit, docker-mlflow

      # ÉTAPE 3: Load Docker images
      - name: Load Docker images
        run: |
          for service in api etl ml streamlit mlflow; do
            if [ -f docker-$service/$service.tar.gz ]; then
              gunzip -c docker-$service/$service.tar.gz | docker load
            fi
          done
        # → Importe les 5 images .tar.gz dans Docker local

      # ÉTAPE 4: Create .env file
      - name: Create .env file
        run: |
          cat > .env << EOF
          POSTGRES_HOST=db
          POSTGRES_PORT=5432
          POSTGRES_DB=letsgo_db
          POSTGRES_USER=letsgo_user
          POSTGRES_PASSWORD=letsgo_password
          DEV_MODE=true
          API_KEY_REQUIRED=false
          API_KEYS=test_key_for_ci_cd
          EOF
        # → Config environnement pour docker-compose

      # ÉTAPE 5: Start services ⭐ CŒUR DU WORKFLOW
      - name: Start services
        run: |
          docker compose up -d
          sleep 60  # Wait for services to be ready
        # → Lance les 9 services Docker en détaché (-d)
        # → sleep 60 = attente startup (API, MLflow, Prometheus, etc.)

      # ÉTAPE 6: Check service health
      - name: Check service health
        run: |
          echo "Checking API health..."
          curl -f http://localhost:8080/health || exit 1

          echo "Checking MLflow health..."
          curl -f http://localhost:5001/health || exit 1

          echo "Checking Prometheus health..."
          curl -f http://localhost:9091/-/healthy || exit 1
        # → Health checks: si 1 service down, workflow échoue
        # → -f flag curl = fail si HTTP error (4xx, 5xx)

      # ÉTAPE 7: Run integration tests
      - name: Run integration tests
        run: |
          docker compose exec -T api pytest tests/ -v -m integration
        # → Exécute tests intégration INSIDE container API
        # → -T flag = no TTY (requis pour CI/CD)
        # → -m integration = seulement tests marqués @pytest.mark.integration

      # ÉTAPE 8: Show logs on failure
      - name: Show logs on failure
        if: failure()
        run: |
          docker compose logs
        # → Si un step échoue, affiche logs de TOUS les services
        # → Utile pour debugging

      # ÉTAPE 9: Stop services (cleanup)
      - name: Stop services
        if: always()
        run: |
          docker compose down -v
        # → Arrête et supprime containers + volumes
        # → if: always() = exécute même si tests échouent
        # → -v flag = supprime volumes (cleanup complet)
```

---

### 🔍 Détails Techniques

#### Matrix Strategy (Parallélisation)

**Sans matrix:**

```yaml
steps:
  - build api      # 8 min
  - build etl      # 8 min
  - build ml       # 8 min
  - build streamlit # 8 min
  - build mlflow   # 8 min
# Total: 40 min séquentiel ❌
```

**Avec matrix:**

```yaml
strategy:
  matrix:
    service: [api, etl, ml, streamlit, mlflow]
# → GitHub Actions lance 5 jobs en PARALLÈLE
# → Chaque job build 1 service
# Total: 8 min (le plus lent) ✅
```

**Visualisation GitHub Actions:**

```
build-and-test (api)       ████████ 8 min ✅
build-and-test (etl)       ████████ 8 min ✅
build-and-test (ml)        ████████ 8 min ✅
build-and-test (streamlit) ████████ 8 min ✅
build-and-test (mlflow)    ████████ 8 min ✅

integration-test           ████ 2 min ✅

Total: 10 min (au lieu de 42 min)
```

---

#### Artifacts (Partage entre Jobs)

**Problème:** Job 1 build images, Job 2 besoin de ces images

**Solution:** Artifacts

1. **Job 1:** Build image → Save tar.gz → Upload artifact
2. **Job 2:** Download artifact → Load tar.gz → Use image

**Equivalent local:**

```bash
# Job 1 (build-and-test)
docker compose build api
docker save lets-go-predictiondex-api | gzip > api.tar.gz

# Transfer to Job 2 (upload/download artifact)
# ...

# Job 2 (integration-test)
gunzip -c api.tar.gz | docker load
docker compose up -d
```

---

## 4. Workflow 3: ML Pipeline

**Fichier:** `.github/workflows/ml-pipeline.yml`

### 🎯 Objectif

- **Auto:** Tester le code ML à chaque modification
- **Manuel:** Entraîner un nouveau modèle via `workflow_dispatch`

### 📝 Code Complet Annoté

```yaml
name: ML Pipeline

on:
  # TRIGGER 1: Push sur fichiers ML
  push:
    branches: [ main, monitoring_grafana_evidently ]
    paths:
      - 'machine_learning/**'
      - 'data/ml/**'
      - 'models/**'
    # → S'exécute SEULEMENT si fichiers ML modifiés

  # TRIGGER 2: Manuel (workflow_dispatch)
  workflow_dispatch:
    inputs:
      dataset_version:
        description: 'Dataset version (v1 or v2)'
        required: true
        default: 'v2'
        type: choice
        options:
          - v1
          - v2
      model_version:
        description: 'Model version suffix'
        required: true
        default: 'ci'
    # → Utilisateur peut déclencher manuellement via GitHub UI
    # → Paramètres: dataset version + model version

jobs:
  test-ml:
    runs-on: ubuntu-latest

    # SERVICE CONTAINERS: PostgreSQL + MLflow
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: letsgo_db
          POSTGRES_USER: letsgo_user
          POSTGRES_PASSWORD: letsgo_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      mlflow:
        image: ghcr.io/mlflow/mlflow:v2.9.2
        env:
          MLFLOW_BACKEND_STORE_URI: sqlite:///mlflow.db
        ports:
          - 5000:5000
        # → MLflow Tracking Server accessible sur localhost:5000

    steps:
      # ÉTAPE 1-2: Checkout + Setup Python
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # ÉTAPE 3: Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r machine_learning/requirements.txt
          pip install pytest pytest-cov

      # ÉTAPE 4: Set environment variables
      - name: Set environment variables
        run: |
          echo "POSTGRES_HOST=localhost" >> $GITHUB_ENV
          echo "POSTGRES_PORT=5432" >> $GITHUB_ENV
          echo "MLFLOW_TRACKING_URI=http://localhost:5000" >> $GITHUB_ENV
          echo "PYTHONPATH=$PWD" >> $GITHUB_ENV

      # ÉTAPE 5: Run ML tests ⭐
      - name: Run ML tests
        run: |
          pytest tests/ml/ -v --cov=machine_learning --cov-report=xml
        # → Exécute 50 tests ML (feature engineering, dataset, training)

      # ÉTAPE 6: Train model (SEULEMENT si manuel trigger)
      - name: Train model (if manual trigger)
        if: github.event_name == 'workflow_dispatch'
        run: |
          python machine_learning/run_machine_learning.py \
            --mode=train \
            --dataset-version=${{ github.event.inputs.dataset_version }} \
            --version=${{ github.event.inputs.model_version }}
        # → if: seulement si déclenché manuellement
        # → Utilise paramètres fournis par utilisateur

      # ÉTAPE 7: Validate model metrics
      - name: Validate model metrics
        if: github.event_name == 'workflow_dispatch'
        run: |
          python -c "
          import json
          from pathlib import Path
          metadata_path = Path('models/battle_winner_metadata_${{ github.event.inputs.model_version }}.json')
          with open(metadata_path) as f:
              meta = json.load(f)
          acc = meta['metrics']['test_accuracy']
          print(f'Test Accuracy: {acc:.4f}')
          assert acc > 0.80, f'Accuracy too low: {acc}'
          print('✅ Model validation passed')
          "
        # → Validation: accuracy DOIT être > 80%
        # → Si < 80%, workflow échoue (assert)

      # ÉTAPE 8: Upload model artifacts
      - name: Upload model artifacts
        if: github.event_name == 'workflow_dispatch'
        uses: actions/upload-artifact@v3
        with:
          name: model-${{ github.event.inputs.model_version }}
          path: |
            models/battle_winner_model_${{ github.event.inputs.model_version }}.pkl
            models/battle_winner_metadata_${{ github.event.inputs.model_version }}.json
            models/battle_winner_scalers_${{ github.event.inputs.model_version }}.pkl
          retention-days: 90
        # → Sauvegarde modèle pendant 90 jours
        # → Téléchargeable depuis GitHub Actions UI

      # ÉTAPE 9: Comment PR avec métriques
      - name: Comment PR with metrics
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ ML tests passed! Model metrics will be available after training.'
            })
        # → Si c'est une PR, poste un commentaire automatique
```

---

### 🔍 Détails Techniques

#### Workflow Dispatch (Trigger Manuel)

**Dans GitHub UI:**

1. Aller dans **Actions**
2. Sélectionner **ML Pipeline**
3. Cliquer **Run workflow**
4. Remplir inputs:
   - Dataset version: `v2`
   - Model version: `ci_test_2026`
5. **Run workflow**

**GitHub Actions exécute:**

```bash
python machine_learning/run_machine_learning.py \
  --mode=train \
  --dataset-version=v2 \
  --version=ci_test_2026

# Training... (8 minutes)

# Output:
# ✅ Model trained successfully
# Test Accuracy: 0.8823 (88.23%)
# Model saved: models/battle_winner_model_ci_test_2026.pkl

# Validation:
assert 0.8823 > 0.80  # ✅ Pass

# Upload artifacts (90 jours)
```

---

#### MLflow Service Container

```yaml
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.2
    env:
      MLFLOW_BACKEND_STORE_URI: sqlite:///mlflow.db
    ports:
      - 5000:5000
```

**Pourquoi ?**

- MLflow Tracking Server nécessaire pour `mlflow.log_model()`, `mlflow.log_metrics()`, etc.
- Service container = lancé automatiquement avant le job
- Accessible via `http://localhost:5000` pendant le workflow

**Code ML qui utilise MLflow:**

```python
# machine_learning/run_machine_learning.py
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")  # → Service container

with mlflow.start_run(run_name="ci_training"):
    mlflow.log_params(hyperparams)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, "model")
```

---

## 5. Workflow 4: Lint & Security

**Fichier:** `.github/workflows/lint.yml`

### 🎯 Objectif

- **Lint:** Vérifier code quality (formatage, style, types)
- **Security:** Scanner vulnérabilités code + dépendances

### 📝 Code Complet Annoté

```yaml
name: Lint and Format

on:
  push:
    branches: [ main, monitoring_grafana_evidently, develop ]
  pull_request:
    branches: [ main, monitoring_grafana_evidently ]

jobs:
  # JOB 1: Linting
  lint:
    runs-on: ubuntu-latest

    steps:
      # ÉTAPE 1-2: Checkout + Setup Python
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # ÉTAPE 3: Cache pip
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-lint-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-lint-

      # ÉTAPE 4: Install linting tools
      - name: Install linting tools
        run: |
          python -m pip install --upgrade pip
          pip install black flake8 isort mypy pylint
          pip install -r api_pokemon/requirements.txt
        # → Installe 5 linters

      # ÉTAPE 5: Black (code formatting check)
      - name: Run black (check only)
        run: |
          black --check --diff api_pokemon core machine_learning interface
        # → Black = formatteur Python automatique
        # → --check = vérifie formatage sans modifier
        # → --diff = affiche différences si non-conforme
        # → ÉCHOUE si code pas formatté selon Black

      # ÉTAPE 6: isort (imports sorting check)
      - name: Run isort (check only)
        run: |
          isort --check-only --diff api_pokemon core machine_learning interface
        # → isort = tri imports alphabétique
        # → ÉCHOUE si imports pas triés

      # ÉTAPE 7: Flake8 (PEP8 style guide)
      - name: Run flake8
        run: |
          flake8 api_pokemon core machine_learning interface \
            --max-line-length=120 \
            --exclude=__pycache__,.venv,.git,migrations \
            --ignore=E203,W503,E501
        # → Flake8 = linter PEP8 (style guide Python officiel)
        # → max-line-length=120 (au lieu de 79 par défaut)
        # → ignore E203, W503, E501 (conflits Black)

      # ÉTAPE 8: Pylint (code quality)
      - name: Run pylint
        continue-on-error: true
        run: |
          pylint api_pokemon core machine_learning \
            --disable=C0111,C0103,R0913,R0914,W0511 \
            --max-line-length=120
        # → Pylint = linter strict code quality
        # → continue-on-error: true = WARNING seulement (pas bloquant)
        # → disable codes: docstrings, naming, trop d'arguments

      # ÉTAPE 9: Mypy (type checking)
      - name: Run mypy
        continue-on-error: true
        run: |
          mypy api_pokemon core --ignore-missing-imports
        # → Mypy = vérification types statiques
        # → continue-on-error: true = WARNING (pas bloquant)

  # JOB 2: Security Scanning
  security:
    runs-on: ubuntu-latest

    steps:
      # ÉTAPE 1-2: Checkout + Setup Python
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # ÉTAPE 3: Install security tools
      - name: Install security tools
        run: |
          python -m pip install --upgrade pip
          pip install bandit safety
        # → Bandit = scanner sécurité code Python
        # → Safety = scanner vulnérabilités dépendances

      # ÉTAPE 4: Bandit (security linter)
      - name: Run bandit (security linter)
        run: |
          bandit -r api_pokemon core machine_learning -f json -o bandit-report.json
        # → Scanne code pour vulnérabilités:
        #   - Injections SQL
        #   - Hardcoded passwords
        #   - Eval/exec insecure
        #   - etc.
        # → Output: JSON report

      # ÉTAPE 5: Safety (dependency vulnerabilities)
      - name: Run safety (dependency check)
        continue-on-error: true
        run: |
          safety check --json --output safety-report.json
        # → Scanne requirements.txt pour CVEs connus
        # → Exemple: requests==2.25.0 a CVE-2023-XYZ
        # → continue-on-error: warnings seulement

      # ÉTAPE 6: Upload security reports
      - name: Upload security reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
          retention-days: 30
        # → Sauvegarde reports 30 jours
        # → Téléchargeables depuis GitHub Actions UI
```

---

### 🔍 Détails Techniques

#### Linters Expliqués

**1. Black (Formatage Automatique)**

```python
# Code NON-conforme:
def my_function(a,b,c):
    return a+b+c

# Code Black-conforme:
def my_function(a, b, c):
    return a + b + c
```

**2. isort (Tri Imports)**

```python
# NON-conforme:
import sys
import pandas as pd
import os
from fastapi import FastAPI

# Conforme isort:
import os
import sys

import pandas as pd
from fastapi import FastAPI
```

**3. Flake8 (PEP8 Style Guide)**

```python
# Erreur Flake8:
def myFunction():  # E999: CamelCase (doit être snake_case)
    x=1+2  # E225: missing whitespace around operator
    return x

# Conforme:
def my_function():
    x = 1 + 2
    return x
```

**4. Pylint (Code Quality)**

```python
# Warning Pylint:
def process_data(a, b, c, d, e, f, g, h):  # R0913: Too many arguments (8/6)
    pass

# Amélioration:
def process_data(config: DataConfig):  # 1 argument (dict/object)
    pass
```

**5. Mypy (Type Checking)**

```python
# Erreur Mypy:
def add(a, b):
    return a + b

result = add("hello", 5)  # Error: str + int impossible

# Conforme:
def add(a: int, b: int) -> int:
    return a + b

result = add(3, 5)  # ✅ OK
```

---

#### Bandit (Security Scanner)

**Exemple vulnérabilités détectées:**

```python
# 1. Hardcoded password (HIGH SEVERITY)
PASSWORD = "admin123"  # ❌ Bandit: B105

# Fix:
PASSWORD = os.getenv("PASSWORD")  # ✅

# 2. SQL Injection (HIGH SEVERITY)
query = f"SELECT * FROM users WHERE id = {user_id}"  # ❌ Bandit: B608

# Fix:
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))  # ✅ Parameterized query

# 3. Eval usage (MEDIUM SEVERITY)
eval(user_input)  # ❌ Bandit: B307

# Fix:
ast.literal_eval(user_input)  # ✅ Safe evaluation

# 4. Assert in production (LOW SEVERITY)
assert user.is_admin, "Not admin"  # ❌ Bandit: B101 (assert removed with -O flag)

# Fix:
if not user.is_admin:
    raise PermissionError("Not admin")  # ✅
```

---

## 6. Intégration Complète

### 🔗 Flow Complet: Push → CI/CD → Merge

```
DEVELOPER
    │
    │  git checkout -b feature/add-new-pokemon
    │  (modifie code)
    │  git commit -m "feat: Add Mew to dataset"
    │  git push origin feature/add-new-pokemon
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  GITHUB REPOSITORY                                        │
│  Branch: feature/add-new-pokemon                         │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │  Push event triggered
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS CI/CD                                     │
│  4 workflows lancés en PARALLÈLE                         │
└──────────────────────────────────────────────────────────┘
        │
        ├─────────────────┬──────────────────┬──────────────┐
        │                 │                  │              │
        ▼                 ▼                  ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌────────────┐
│ Tests        │  │ Docker Build │  │ ML Pipeline│  │ Lint       │
│ (2 min)      │  │ (8 min)      │  │ (3 min)    │  │ (2 min)    │
│              │  │              │  │            │  │            │
│ Run 252 tests│  │ Build 5      │  │ Test ML    │  │ Black      │
│ Coverage 82% │  │ images       │  │ code       │  │ Flake8     │
│              │  │ Integration  │  │            │  │ Bandit     │
│ ✅ PASS      │  │ tests        │  │ ✅ PASS    │  │ Safety     │
│              │  │ ✅ PASS      │  │            │  │ ✅ PASS    │
└──────┬───────┘  └──────┬───────┘  └────┬───────┘  └────┬───────┘
       │                 │               │              │
       └─────────────────┴───────────────┴──────────────┘
                       │
                       │  ALL CHECKS PASSED ✅
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│  PULL REQUEST                                             │
│  feature/add-new-pokemon → main                          │
│                                                           │
│  ✅ Tests (252 passed)                                   │
│  ✅ Docker Build (5 images OK)                           │
│  ✅ ML Pipeline (50 tests passed)                        │
│  ✅ Lint & Security (No issues)                          │
│                                                           │
│  [Merge Pull Request] ← Enabled (checks passed)          │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │  Merge button clicked
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│  MAIN BRANCH                                              │
│  feature/add-new-pokemon merged ✅                       │
│                                                           │
│  Triggers CI/CD again (on main branch)                   │
│  → Generate coverage badge                               │
│  → Build Docker images (production)                      │
│  → Ready for deployment                                  │
└──────────────────────────────────────────────────────────┘
                       │
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│  PRODUCTION DEPLOYMENT                                    │
│  docker-compose pull                                     │
│  docker-compose up -d                                    │
│  ✅ New version deployed                                 │
└──────────────────────────────────────────────────────────┘
```

---

### 📊 Timeline Exemple

```
Minute 0:  Developer push code
           │
           ├─ Tests workflow started
           ├─ Docker Build workflow started
           ├─ ML Pipeline workflow started
           └─ Lint workflow started

Minute 2:  Tests ✅ (252 passed, coverage 82%)
           Lint ✅ (Black, Flake8, Bandit OK)

Minute 3:  ML Pipeline ✅ (50 tests passed)

Minute 8:  Docker Build ✅ (5 images built, integration tests passed)

Minute 8:  ALL CHECKS PASSED ✅
           → Pull Request "ready to merge" (green checkmark)

Minute 9:  Developer clicks "Merge Pull Request"
           → Code merged to main

Minute 10: Main branch CI/CD triggered
           → Coverage badge generated
           → Docker images tagged "latest"

Minute 15: Production deployment
           → docker-compose up -d
           → New version live ✅
```

---

### 🎯 Avantages CI/CD

**Sans CI/CD:**

```
Developer → Push code → Manual testing (30 min) → Hope it works → Production 🤞
```

**Avec CI/CD:**

```
Developer → Push code → Auto tests (252 tests, 8 min) → Guaranteed quality ✅ → Production 🚀
```

**Bénéfices:**

1. ✅ **Détection bugs immédiate** - Tests auto à chaque commit
2. ✅ **Code quality garanti** - Linters obligatoires
3. ✅ **Sécurité vérifiée** - Bandit + Safety scans
4. ✅ **Intégration validée** - Docker compose tests
5. ✅ **ML quality** - Accuracy > 80% requis
6. ✅ **Feedback rapide** - 8 minutes au lieu de heures
7. ✅ **Confiance déploiement** - Si CI/CD vert, production OK
8. ✅ **Documentation vivante** - Coverage badge, test reports

---

**Voilà ! Vous avez une compréhension complète du CI/CD GitHub Actions.**

**Créé le:** 27 janvier 2026
**Pour:** Certification RNCP E1/E3
**Compétence:** C13 - MLOps CI/CD ✅
