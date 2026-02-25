# Scripts

Scripts utilitaires pour le développement, les tests et les démos.

## Démarrage et validation Docker

```bash
python scripts/quick_start_docker.py          # Guide interactif de démarrage
python scripts/quick_start_docker.py --auto   # Mode automatique
python scripts/start_docker_stack.py          # Démarrage rapide
python scripts/validate_docker_stack.py       # Vérifie que tous les services tournent
```

## Certification / Démo

```bash
# Script shell complet (recommandé pour la soutenance)
./scripts/demo_full.sh              # Lance tout de A à Z (Docker, ETL, MLflow, tests, navigateur)
./scripts/demo_full.sh --skip-tests # Sans les tests (plus rapide)
./scripts/demo_full.sh --skip-etl   # Sans relancer l'ETL
./scripts/demo_full.sh --stop       # Arrêter tous les services

# Script Python (ouvre les interfaces uniquement)
python scripts/demo_certification.py              # Ouvre toutes les interfaces (Streamlit, Swagger, Grafana, etc.)
python scripts/demo_certification.py --web-only    # Interfaces web uniquement
python scripts/demo_certification.py --generate-metrics  # Avec génération de métriques

python scripts/test_certification_workflow.py --all           # Simule le workflow GitHub Actions en local
python scripts/test_certification_workflow.py --job e1-data-validation  # Job spécifique
```

## Tests

```bash
python scripts/run_all_tests.py           # Tous les tests
python scripts/run_all_tests.py --local   # Sans Docker
python scripts/run_all_tests.py --build   # Avec rebuild des images

python scripts/test_ci_cd_locally.py      # Teste le CI/CD avant de push
```

## Monitoring

```bash
# Génère du trafic pour remplir Grafana/Prometheus
python scripts/generate_monitoring_data.py                        # Mode réaliste, 5 min
python scripts/generate_monitoring_data.py --mode burst --duration 10  # Beaucoup de requêtes

# Prédictions réalistes avec les vrais moves
python scripts/populate_monitoring_v2.py --count 50
```

## MLflow

```bash
python scripts/mlflow/enable_mlflow.py               # Active MLflow
python scripts/mlflow/register_existing_model.py      # Enregistre le modèle dans le Registry
```

## Workflow typique

```bash
# Option A : tout-en-un (recommandé)
./scripts/demo_full.sh

# Option B : étape par étape
python scripts/quick_start_docker.py       # 1. Démarrer
python scripts/validate_docker_stack.py    # 2. Vérifier
python scripts/generate_monitoring_data.py # 3. Générer des métriques
python scripts/demo_certification.py       # 4. Démo
```
