# Tests

## Structure

```
tests/
├── api/          # Routes + services FastAPI (64 tests)
├── core/         # Modèles BDD (15 tests)
├── etl/          # Pipeline ETL (30 tests)
├── integration/  # Tests end-to-end (9 tests)
├── interface/    # Streamlit (20+ tests)
├── ml/           # Machine learning (50 tests)
├── mlflow/       # MLflow + Model Registry (17 tests)
└── conftest.py   # Fixtures partagées
```

Total : ~250 tests, couverture ~82%.

## Lancer les tests

```bash
pytest tests/ -v                          # Tout
pytest tests/api/ -v                      # Par catégorie
pytest tests/ --cov=. --cov-report=html   # Avec couverture
pytest tests/ -v -m "not integration"     # Sans les tests d'intégration (plus rapide)
pytest tests/ -n auto                     # En parallèle (nécessite pytest-xdist)
```

## Par catégorie

- **API** (`tests/api/`) : CRUD Pokémon, moves, types, prédictions de combat, validation d'entrée, gestion d'erreurs
- **Core** (`tests/core/`) : modèles BDD, relations, intégrité des données
- **ETL** (`tests/etl/`) : extraction, feature engineering, export parquet, qualité des données
- **Integration** (`tests/integration/`) : workflow complet MLflow → API, rollback, accès concurrent
- **Interface** (`tests/interface/`) : rendu des pages, interactions, graphiques, gestion de session
- **ML** (`tests/ml/`) : dataset, entraînement, inférence, preprocessing, évaluation
- **MLflow** (`tests/mlflow/`) : tracking, registration, promotion Staging → Production

## Fixtures principales

- `db_session` : session BDD de test
- `sample_pokemon`, `sample_moves`, `sample_types` : données d'exemple
- `client` : client FastAPI de test
- `sample_model`, `sample_scalers` : modèle ML de test

## Debug

```bash
pytest tests/api/test_pokemon_service.py::test_get_pokemon_by_id -v  # Un seul test
pytest tests/api/ -v -s   # Avec les prints
pytest tests/api/ -x       # S'arrêter au premier échec
pytest tests/api/ --pdb    # Debugger interactif
```
