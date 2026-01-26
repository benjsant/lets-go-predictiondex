# Scripts utilitaires

Ce dossier contient des scripts Python pour faciliter le développement et les tests.

## 📁 Contenu

### `generate_monitoring_data.py`
Génère des métriques de test pour remplir Grafana/Prometheus.

**Usage:**
```bash
# Mode réaliste (défaut) - 5 minutes
python scripts/generate_monitoring_data.py

# Mode burst (beaucoup de requêtes) - 10 minutes
python scripts/generate_monitoring_data.py --mode burst --duration 10

# Mode spike (pics de trafic) - 15 minutes
python scripts/generate_monitoring_data.py --mode spike --duration 15
```

**Modes disponibles:**
- `realistic`: Simule des utilisateurs réels (pauses 0.5-3s)
- `burst`: Maximum de requêtes rapidement (100+ req/min)
- `spike`: Pics de trafic aléatoires (charge variable)

### `validate_docker_stack.py`
Valide que tous les services Docker sont opérationnels.

**Usage:**
```bash
# Validation basique
python scripts/validate_docker_stack.py

# Mode verbeux
python scripts/validate_docker_stack.py --verbose
```

**Services vérifiés:**
- ✅ PostgreSQL (5432)
- ✅ API FastAPI (8000)
- ✅ Streamlit (8501)
- ✅ Prometheus (9090)
- ✅ Grafana (3000)
- ✅ MLflow (5000)
- ✅ Node Exporter (9100)

## 🚀 Workflow typique

### 1. Vérification rapide
```bash
python quick_check.py
```

### 2. Démarrer la stack
```bash
# Option 1: Script automatique
python scripts/start_docker_stack.py

# Option 2: Manuel
docker-compose up -d
```

### 3. Valider les services
```bash
python scripts/validate_docker_stack.py
```

### 3. Générer des métriques de test
```bash
# Génération 10 minutes en mode réaliste
python scripts/generate_monitoring_data.py --duration 10
```

### 4. Consulter les dashboards
- **Grafana**: http://localhost:3000 (dashboards ML + API)
- **Prometheus**: http://localhost:9090 (métriques brutes)
- **API Swagger**: http://localhost:8000/docs

## 📊 Métriques générées

Les scripts génèrent automatiquement:

**Métriques ML:**
- `model_predictions_total`: Nombre de prédictions
- `model_prediction_latency_seconds`: Latence prédictions (P50, P95, P99)
- `model_prediction_confidence`: Confiance du modèle

**Métriques API:**
- `api_requests_total`: Total requêtes par endpoint
- `api_request_duration_seconds`: Durée requêtes
- `api_errors_total`: Erreurs par type (404, 422, 500)

**Métriques système:**
- `node_cpu_seconds_total`: CPU usage
- `node_memory_MemTotal_bytes`: Mémoire totale
- `node_disk_io_time_seconds_total`: I/O disque

## 🧪 Tests

Les tests de monitoring sont dans `tests/monitoring/`:

```bash
# Exécuter tous les tests monitoring
pytest tests/monitoring/ -v

# Test spécifique
pytest tests/monitoring/test_generate_metrics.py::TestMetricsGeneration::test_generate_prediction_metrics -v

# Génération standalone (sans pytest)
python tests/monitoring/test_generate_metrics.py generate 5
```

## 💡 Troubleshooting

### Services non accessibles
```bash
# Vérifier les logs
docker-compose logs api
docker-compose logs prometheus
docker-compose logs grafana

# Redémarrer un service
docker-compose restart api
```

### Métriques non visibles dans Grafana
1. Vérifier Prometheus: http://localhost:9090/targets
2. Vérifier endpoint API: http://localhost:8000/metrics
3. Générer des données: `python scripts/generate_monitoring_data.py`

### Erreurs de connexion
```bash
# Vérifier que tous les services sont UP
docker-compose ps

# Vérifier les réseaux Docker
docker network ls | grep letsgo
```

## 🔗 Liens utiles

- [Documentation Prometheus](https://prometheus.io/docs/)
- [Documentation Grafana](https://grafana.com/docs/)
- [Prometheus Client Python](https://github.com/prometheus/client_python)
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/middleware/)
