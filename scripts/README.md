# Scripts Utilitaires

> Scripts pour faciliter le développement, les tests et les démonstrations

## Structure

```
scripts/
├── demo_certification.py # Démonstration E1/E3
├── quick_start_docker.py # Guide interactif Docker
├── start_docker_stack.py # Démarrage Docker simplifié
├── validate_docker_stack.py # Validation des services
├── run_all_tests.py # Orchestration des tests
├── test_certification_workflow.py # Simulation CI/CD local
├── test_ci_cd_locally.py # Tests CI/CD avant push
├── generate_monitoring_data.py # Génération métriques Grafana
├── populate_monitoring_v2.py # Prédictions réalistes
└── mlflow/ # MLOps
 ├── enable_mlflow.py # Activation MLflow
 └── register_existing_model.py # Enregistrement Model Registry
```

## Scripts de Démarrage

### `quick_start_docker.py`
Guide interactif pour démarrer la stack Docker complète.

```bash
# Démarrage guidé
python scripts/quick_start_docker.py

# Mode automatique (sans prompts)
python scripts/quick_start_docker.py --auto
```

### `start_docker_stack.py`
Démarrage rapide Docker en Python pur.

```bash
python scripts/start_docker_stack.py
```

### `validate_docker_stack.py`
Vérifie que tous les services Docker sont opérationnels.

```bash
# Validation standard
python scripts/validate_docker_stack.py

# Mode verbeux
python scripts/validate_docker_stack.py --verbose
```

**Services vérifiés** : PostgreSQL, API, Streamlit, Prometheus, Grafana, MLflow

## Scripts de Certification

### `demo_certification.py`
Ouvre automatiquement toutes les interfaces pour la démonstration E1/E3.

```bash
# Démonstration complète
python scripts/demo_certification.py

# Interfaces web uniquement
python scripts/demo_certification.py --web-only

# Avec génération de métriques
python scripts/demo_certification.py --generate-metrics
```

**URLs ouvertes** :
- Streamlit (8502)
- Swagger API (8080/docs)
- Grafana (3001)
- Prometheus (9091)
- MLflow (5001)

### `test_certification_workflow.py`
Simule le workflow GitHub Actions E1/E3 en local.

```bash
# Tous les jobs
python scripts/test_certification_workflow.py --all

# Job spécifique
python scripts/test_certification_workflow.py --job e1-data-validation
python scripts/test_certification_workflow.py --job e3-c13-mlops
```

## Scripts de Test

### `run_all_tests.py`
Orchestration complète des tests via Docker.

```bash
# Tous les tests
python scripts/run_all_tests.py

# Tests locaux (sans Docker)
python scripts/run_all_tests.py --local

# Avec rebuild des images
python scripts/run_all_tests.py --build
```

### `test_ci_cd_locally.py`
Teste le CI/CD localement avant de pousser sur GitHub.

```bash
python scripts/test_ci_cd_locally.py
```

## Scripts de Monitoring

### `generate_monitoring_data.py`
Génère des métriques pour remplir Grafana/Prometheus.

```bash
# Mode réaliste (défaut) - 5 minutes
python scripts/generate_monitoring_data.py

# Mode burst (beaucoup de requêtes) - 10 minutes
python scripts/generate_monitoring_data.py --mode burst --duration 10

# Mode spike (pics de trafic)
python scripts/generate_monitoring_data.py --mode spike --duration 15
```

**Modes disponibles** :
- `realistic` : Simule des utilisateurs réels (pauses 0.5-3s)
- `burst` : Maximum de requêtes (100+ req/min)
- `spike` : Pics de trafic aléatoires

### `populate_monitoring_v2.py`
Génère des prédictions réalistes avec les vrais moves des Pokémon.

```bash
# 50 prédictions (défaut)
python scripts/populate_monitoring_v2.py

# 100 prédictions
python scripts/populate_monitoring_v2.py --count 100

# Sans MLflow
python scripts/populate_monitoring_v2.py --count 50 --skip-mlflow
```

## Scripts MLflow

### `mlflow/enable_mlflow.py`
Active MLflow et configure le tracking.

```bash
python scripts/mlflow/enable_mlflow.py
```

### `mlflow/register_existing_model.py`
Enregistre le modèle existant (v2, 88.23% accuracy) dans MLflow Registry.

```bash
python scripts/mlflow/register_existing_model.py
```

## Prérequis

- Python 3.11+
- Docker et Docker Compose
- Stack Docker démarrée (`docker compose up`)

## Workflow Typique

```bash
# 1. Démarrer la stack
python scripts/quick_start_docker.py

# 2. Valider les services
python scripts/validate_docker_stack.py

# 3. Générer des métriques (optionnel)
python scripts/generate_monitoring_data.py --duration 5

# 4. Lancer la démonstration
python scripts/demo_certification.py
```

---

**Dernière mise à jour** : 31 janvier 2026
