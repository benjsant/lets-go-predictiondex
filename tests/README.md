# Tests Organization

## Structure

```
tests/
├── api/ # API tests (routes + services)
│ ├── test_pokemon_route.py
│ ├── test_pokemon_service.py
│ ├── test_move_route.py
│ ├── test_move_service.py
│ ├── test_type_route.py
│ ├── test_type_service.py
│ ├── test_prediction_route.py
│ └── test_prediction_service.py
├── core/ # Core models and database tests
│ └── (existing tests)
├── etl/ # ETL pipeline tests
│ └── test_pipeline.py (NEW)
├── integration/ # Integration tests
│ └── test_mlflow_to_api.py (NEW)
├── interface/ # Streamlit interface tests
│ └── test_streamlit_app.py (NEW)
├── ml/ # Machine Learning tests
│ ├── test_dataset.py
│ ├── test_model_inference.py
│ └── test_preprocessing.py
├── mlflow/ # MLflow Model Registry tests
│ ├── test_mlflow_tracker.py
│ └── test_model_registry.py (NEW)
├── conftest.py # Shared fixtures
└── __init__.py
```

## Test Categories

### API Tests (64 tests)
**Location**: `tests/api/`

Tests for FastAPI routes and services:
- Pokemon CRUD operations
- Move queries
- Type effectiveness
- Battle predictions
- Error handling
- Input validation

**Run**: `pytest tests/api/ -v`

---

### Core Tests
**Location**: `tests/core/`

Tests for database models and core functionality:
- Database models (Pokemon, Move, Type, etc.)
- Relationships (many-to-many, foreign keys)
- Data integrity
- Query optimization

**Run**: `pytest tests/core/ -v`

---

### ETL Tests (30 tests)
**Location**: `tests/etl/`

Tests for data extraction, transformation, and loading:
- Data extraction from database
- Feature engineering
- Data transformation
- Parquet export
- Data quality validation
- Scraper integration

**Run**: `pytest tests/etl/ -v`

---

### Integration Tests (9 tests)
**Location**: `tests/integration/`

End-to-end tests across multiple components:
- **MLflow → API**: Model registry to API loading
- Train → Register → Load → Predict workflow
- Rollback scenarios
- Concurrent access
- Error handling and fallbacks

**Run**: `pytest tests/integration/ -v`

---

### Interface Tests (20+ tests)
**Location**: `tests/interface/`

Tests for Streamlit web interface:
- Page rendering
- User interactions
- Data display
- Stats visualization (radar charts, progress bars)
- Battle prediction UI
- Session state management
- Error handling
- Caching

**Run**: `pytest tests/interface/ -v`

---

### ML Tests (50 tests)
**Location**: `tests/ml/`

Tests for machine learning components:
- Dataset validation
- Model training
- Model inference
- Feature preprocessing
- Hyperparameter tuning
- Model evaluation
- Performance metrics

**Run**: `pytest tests/ml/ -v`

---

### MLflow Tests (17 tests)
**Location**: `tests/mlflow/`

Tests for MLflow integration and Model Registry:
- Experiment tracking
- Model registration
- Model promotion (Staging → Production)
- Model comparison
- Model loading from registry
- Artifacts (scalers, metadata)
- Auto-promotion based on metrics

**Run**: `pytest tests/mlflow/ -v`

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Category
```bash
pytest tests/api/ -v # API tests only
pytest tests/ml/ -v # ML tests only
pytest tests/mlflow/ -v # MLflow tests only
pytest tests/integration/ -v # Integration tests only
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Fast Tests Only (skip slow integration)
```bash
pytest tests/ -v -m "not integration"
```

### Run with Parallel Execution
```bash
pytest tests/ -n auto # Requires pytest-xdist
```

---

## Test Statistics

| Category | Tests | Status | Coverage |
|----------|-------|--------|----------|
| **API** | 64 | Passing | ~85% |
| **Core** | 15 | Passing | ~90% |
| **ETL** | 30 | 🆕 New | ~70% |
| **Integration** | 9 | Passing | ~80% |
| **Interface** | 20+ | 🆕 New | ~60% |
| **ML** | 50 | Passing | ~75% |
| **MLflow** | 17 | Passing | ~85% |
| **TOTAL** | **~252** | **** | **~82%** |

---

## Test Fixtures

### Shared Fixtures (`conftest.py`)
- `db_session`: Database session for tests
- `sample_pokemon`: Sample Pokemon data
- `sample_moves`: Sample moves data
- `sample_types`: Sample type data
- `temp_dir`: Temporary directory for file operations

### ML Fixtures
- `sample_model`: Trained ML model
- `sample_scalers`: Feature scalers
- `sample_metadata`: Model metadata
- `sample_features`: Feature vectors

### API Fixtures
- `client`: FastAPI test client
- `mock_db`: Mocked database session
- `authenticated_user`: User with auth token

---

## Writing New Tests

### Test Naming Convention
```python
# Good
def test_get_pokemon_by_id_returns_correct_pokemon():
 pass

def test_predict_battle_winner_with_type_advantage():
 pass

# Bad
def test1():
 pass

def test_function():
 pass
```

### Test Structure (AAA Pattern)
```python
def test_example():
 # Arrange: Set up test data and dependencies
 pokemon = create_sample_pokemon()
 
 # Act: Execute the code under test
 result = get_pokemon_by_id(pokemon.id)
 
 # Assert: Verify the results
 assert result.name == pokemon.name
 assert result.type1 == pokemon.type1
```

### Mocking External Dependencies
```python
@patch('api_pokemon.services.prediction_service.load_model')
def test_prediction_with_mocked_model(mock_load_model):
 mock_load_model.return_value = Mock(predict=Mock(return_value=[1]))
 # Test code here
```

---

## Debugging Failed Tests

### Run Single Test
```bash
pytest tests/api/test_pokemon_service.py::test_get_pokemon_by_id -v
```

### Show Print Statements
```bash
pytest tests/api/ -v -s
```

### Stop at First Failure
```bash
pytest tests/api/ -x
```

### Show Full Traceback
```bash
pytest tests/api/ --tb=long
```

### Run with Debugger
```bash
pytest tests/api/ --pdb
```

---

## Test Markers

### Mark Tests
```python
@pytest.mark.integration
def test_full_pipeline():
 pass

@pytest.mark.slow
def test_large_dataset():
 pass

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
 pass
```

### Run Marked Tests
```bash
pytest -m integration # Only integration tests
pytest -m "not slow" # Skip slow tests
pytest -m "api and not slow" # API tests that aren't slow
```

---

## Continuous Integration

Tests run automatically on:
- Every commit (fast tests)
- Pull requests (all tests)
- Nightly builds (all tests + integration)

### CI Configuration
See `.github/workflows/tests.yml` for CI setup.

---

## Coverage Goals

- **Minimum**: 70% overall coverage
- **Target**: 80% overall coverage
- **Critical paths**: 90%+ coverage (API, ML inference, predictions)

### Generate Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [MLflow testing best practices](https://mlflow.org/docs/latest/python_api/index.html)
- [Mocking with unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**Last Updated**: 31 janvier 2026
