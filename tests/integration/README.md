# Tests d'intégration

Tests end-to-end qui vérifient que tous les services fonctionnent ensemble.

## Tests disponibles

**test_complete_system.py** : validation complète du système (7 services Docker, monitoring, MLflow, API, BDD, prédictions). Score attendu : >= 95%.

```bash
python3 tests/integration/test_complete_system.py
```

**test_monitoring_complete.py** : stack monitoring (Prometheus, Grafana, collecte de métriques, percentiles P50/P95/P99). Score attendu : >= 80%.

```bash
python3 tests/integration/test_monitoring_complete.py
```

**test_monitoring_validation.py** : génère un rapport HTML et JSON de validation du monitoring.

```bash
python3 tests/integration/test_monitoring_validation.py
```

**test_mlflow_to_api.py** : intégration MLflow → API (chargement du modèle depuis le Registry, prédictions, cohérence).

```bash
pytest tests/integration/test_mlflow_to_api.py -v
```

## Prérequis

Tous les services Docker doivent tourner (`docker compose up -d`). Pour les tests de monitoring, il faut d'abord générer du trafic :

```bash
python3 scripts/generate_monitoring_data.py
```

## Tout lancer

```bash
python3 scripts/run_all_tests.py              # Tests unitaires + intégration
python3 scripts/run_all_tests.py --skip-unit   # Intégration seulement
docker compose --profile tests up tests        # Via Docker
```

## Dépannage

- **"Connection refused"** : les services ne sont pas démarrés, faire `docker compose up -d` et attendre ~30s
- **Percentiles NaN** : pas assez de trafic, lancer `generate_monitoring_data.py` d'abord
- **MLflow échoue** : modèle pas enregistré, lancer `scripts/mlflow/enable_mlflow.py`
