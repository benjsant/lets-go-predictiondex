# Tests d'Intégration - Let's Go PredictionDex

Ce dossier contient tous les tests d'intégration pour valider le fonctionnement complet du système.

## 📋 Tests Disponibles

### 1. **test_complete_system.py**
Validation complète du système end-to-end.

**Ce qui est testé**:
- ✅ 7 services Docker (PostgreSQL, API, Streamlit, MLflow, Prometheus, Grafana, pgAdmin)
- ✅ Stack monitoring (Prometheus targets, métriques, Grafana dashboards)
- ✅ MLflow (expériences, Model Registry, runs)
- ✅ API endpoints (health, Pokemon, moves, types, predictions)
- ✅ Base de données (188 Pokemon, 226 moves, 18 types)

**Usage**:
```bash
# Depuis l'hôte
python3 tests/integration/test_complete_system.py

# Via Docker
docker compose --profile tests up tests
```

**Résultat attendu**: Score ≥ 95% (51/52 tests)

---

### 2. **test_monitoring_complete.py**
Test d'intégration complet de la stack monitoring.

**Ce qui est testé**:
- ✅ Services (Prometheus, Grafana, API, MLflow)
- ✅ Collecte de métriques (via génération de trafic API)
- ✅ Requêtes Prometheus (métriques, percentiles, alertes)
- ✅ Dashboards Grafana (datasource, panels, variables)
- ✅ Calcul des percentiles (P50, P95, P99) - sans NaN

**Usage**:
```bash
python3 tests/integration/test_monitoring_complete.py
```

**Résultat attendu**: Score ≥ 80% (17/18 tests)

---

### 3. **test_monitoring_validation.py**
Validation du monitoring avec génération de rapport HTML.

**Ce qui est testé**:
- ✅ Collecte de métriques Prometheus
- ✅ Requêtes PromQL fonctionnelles
- ✅ Percentiles sans NaN
- ✅ Génération de rapport HTML et JSON

**Usage**:
```bash
python3 tests/integration/test_monitoring_validation.py
```

**Rapports générés**:
- `reports/monitoring/validation_report.json`
- `reports/monitoring/validation_report.html`

---

### 4. **test_mlflow_to_api.py**
Test d'intégration entre MLflow et l'API.

**Ce qui est testé**:
- ✅ Chargement du modèle depuis MLflow Registry
- ✅ Prédictions via API avec modèle MLflow
- ✅ Cohérence entre modèle local et MLflow

**Usage**:
```bash
pytest tests/integration/test_mlflow_to_api.py -v
```

---

## 🚀 Exécution des Tests

### Option 1: Exécuter tous les tests (recommandé)

```bash
python3 scripts/run_all_tests.py
```

Cette commande exécute:
1. Tests unitaires (6 suites)
2. Tests d'intégration (4 tests)
3. Validation système (1 validation complète)

**Options disponibles**:
```bash
# Sauter les tests unitaires
python3 scripts/run_all_tests.py --skip-unit

# Sauter les tests d'intégration
python3 scripts/run_all_tests.py --skip-integration

# Exécuter via Docker
python3 scripts/run_all_tests.py --docker
```

---

### Option 2: Exécuter un test spécifique

```bash
# Test système complet
python3 tests/integration/test_complete_system.py

# Test monitoring
python3 tests/integration/test_monitoring_complete.py

# Test validation
python3 tests/integration/test_monitoring_validation.py

# Test MLflow (avec pytest)
pytest tests/integration/test_mlflow_to_api.py -v
```

---

### Option 3: Exécuter via Docker

```bash
# Démarrer tous les services + lancer les tests
docker compose --profile tests up --build tests

# Ou en mode détaché puis voir les logs
docker compose --profile tests up -d tests
docker logs -f letsgo_tests
```

---

## 📊 Rapports Générés

Tous les rapports sont sauvegardés dans `reports/`:

```
reports/
├── monitoring/
│   ├── validation_report.html       # Rapport HTML interactif
│   ├── validation_report.json       # Données JSON
│   ├── monitoring_validation_report.html
│   └── integration_test_results.json
└── validation/
    └── system_validation_report.json  # Résultats validation système
```

**Consulter les rapports**:
```bash
# Ouvrir le rapport HTML
xdg-open reports/monitoring/validation_report.html

# Voir le score JSON
cat reports/monitoring/validation_report.json | jq '.validation_score'
```

---

## 🔧 Prérequis

### Services Docker requis

Tous les services doivent être démarrés:
```bash
docker compose up -d
```

Vérifier que les services sont UP:
```bash
docker compose ps
```

Services nécessaires:
- ✅ `letsgo_postgres` - Base de données
- ✅ `letsgo_api` - API FastAPI
- ✅ `letsgo_streamlit` - Interface web
- ✅ `letsgo_mlflow` - Tracking ML
- ✅ `letsgo_prometheus` - Métriques
- ✅ `letsgo_grafana` - Dashboards
- ✅ `letsgo_pgadmin` - Admin PostgreSQL

### Dépendances Python

```bash
# Installer les dépendances de test
pip install -r tests/requirements.txt
```

Dépendances principales:
- `pytest` - Framework de tests
- `requests` - Client HTTP
- `psycopg2-binary` - Client PostgreSQL
- `mlflow` - Client MLflow

---

## 📈 Critères de Succès

### Validation Complète (test_complete_system.py)

| Catégorie | Score Attendu |
|-----------|---------------|
| Infrastructure | 7/7 (100%) |
| Monitoring | 13/13 (100%) |
| MLflow | 8/9 (88.9%) |
| API | 10/10 (100%) |
| Database | 3/3 (100%) |
| Predictions | 10/10 (100%) |
| **TOTAL** | **≥ 95%** |

### Monitoring (test_monitoring_complete.py)

| Critère | Attendu |
|---------|---------|
| Services UP | 4/4 |
| Métriques collectées | ≥ 5 |
| Requêtes Prometheus | ≥ 10 |
| Percentiles (P50, P95, P99) | Pas de NaN |
| Dashboards Grafana | 2 dashboards |

---

## 🐛 Dépannage

### Tests échouent: "Connection refused"

**Problème**: Les services ne sont pas démarrés.

**Solution**:
```bash
docker compose up -d
sleep 30  # Attendre que les services soient prêts
python3 tests/integration/test_complete_system.py
```

### Percentiles retournent NaN

**Problème**: Pas assez de trafic API généré.

**Solution**:
```bash
# Générer du trafic d'abord
python3 scripts/generate_monitoring_data.py

# Puis lancer les tests
python3 tests/integration/test_monitoring_complete.py
```

### MLflow tests échouent

**Problème**: Modèle pas enregistré dans MLflow Registry.

**Solution**:
```bash
# Enregistrer le modèle v2
python3 scripts/mlflow/enable_mlflow.py

# Vérifier dans MLflow UI
curl http://localhost:5001/health
```

### Tests Docker échouent à builder

**Problème**: Dockerfile.tests manquant ou invalide.

**Solution**:
```bash
# Vérifier que le Dockerfile existe
ls -la docker/Dockerfile.tests

# Rebuild l'image
docker compose --profile tests build tests

# Relancer
docker compose --profile tests up tests
```

---

## 📝 Notes

- Les tests d'intégration nécessitent que **tous les services soient UP**
- Générer du trafic API avant de tester le monitoring
- Les rapports HTML sont auto-contenus (CSS inline)
- Les tests sont idempotents (peuvent être relancés sans effets de bord)

---

## 🎯 Prochaines Étapes

1. ✅ Tous les tests passent (≥95%)
2. ✅ Rapports générés et consultables
3. ✅ Déploiement CI/CD fonctionnel (GitHub Actions)
4. 🚀 **Projet prêt pour la certification E1/E3**
