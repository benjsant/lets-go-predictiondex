# Guide de Certification E1/E3 - Let's Go PredictionDex

## 🎯 Vue d'ensemble

Ce document récapitule **tous les outils et scripts** disponibles pour préparer et réussir ta certification.

---

## 📂 Structure des Scripts d'Orchestration

### **Scripts Principaux**

| Script | Taille | Usage | Compétence |
|--------|--------|-------|------------|
| **demo_certification.py** | 13 KB | 🎯 **Démo complète certification** | E1 + E3 |
| **quick_start_docker.py** | 11 KB | 🚀 Démarrage interactif stack | Setup |
| **validate_docker_stack.py** | 9.5 KB | ✅ Validation services | Vérification |
| **generate_monitoring_data.py** | 13 KB | 📊 Génération métriques Grafana | C11 |
| **populate_monitoring_v2.py** | 11 KB | 📈 Remplir dashboards | C11 |
| **test_certification_workflow.py** | 13 KB | 🧪 Test workflow CI/CD | C13 |
| **run_all_tests.py** | 11 KB | 🧪 Exécution tests complets | C12 |
| **generate_report_figures.py** | 31 KB | 📊 Génération figures rapport | Documentation |

### **Scripts MLflow**

| Script | Usage |
|--------|-------|
| **mlflow/check_mlflow_status.py** | ✅ Vérifier état MLflow |
| **mlflow/enable_mlflow.py** | 🔄 Activer MLflow tracking |
| **mlflow/register_existing_model.py** | 📦 Enregistrer modèle dans Registry |

---

## 🚀 Workflow de Préparation (30 min)

### **1. Démarrer la Stack Docker** (5 min)

```bash
# Démarrage guidé interactif
python scripts/quick_start_docker.py

# OU démarrage automatique
python scripts/quick_start_docker.py --auto
```

**Services démarrés :**
- PostgreSQL (port 5432)
- API FastAPI (port 8080)
- Streamlit (port 8502)
- Prometheus (port 9091)
- Grafana (port 3001)
- MLflow (port 5001)

---

### **2. Valider la Stack** (3 min)

```bash
# Validation complète avec détails
python scripts/validate_docker_stack.py --verbose
```

**Vérifications effectuées :**
- ✅ Tous les containers UP
- ✅ Healthchecks OK
- ✅ Endpoints accessibles
- ✅ Base de données connectée

---

### **3. Générer des Métriques pour Grafana** (10 min)

```bash
# Génération 10 minutes de métriques réalistes
python scripts/generate_monitoring_data.py --mode realistic --duration 10

# OU génération rapide (burst)
python scripts/generate_monitoring_data.py --mode burst --duration 5
```

**Métriques générées :**
- Prédictions ML (200-500 requêtes)
- Latence API (50-200ms)
- Taux d'erreurs (< 1%)
- Confiance modèle (0.85-0.95)
- CPU/Memory usage

---

### **4. Vérifier MLflow** (2 min)

```bash
# Vérifier état MLflow
python scripts/mlflow/check_mlflow_status.py

# Si modèle non enregistré, l'enregistrer
python scripts/mlflow/register_existing_model.py
```

**Résultat attendu :**
- ✅ Serveur MLflow UP
- ✅ 3 expérimentations
- ✅ 1 modèle en Production (battle_winner_predictor v1)
- ✅ Métriques : 96.26% accuracy, 99.54% ROC-AUC

---

### **5. Lancer la Démo Certification** (10 min)

```bash
# Démo complète automatique
python scripts/demo_certification.py

# Ouvrir seulement les interfaces web
python scripts/demo_certification.py --web-only

# Avec génération de métriques
python scripts/demo_certification.py --generate-metrics
```

**Ce script ouvre automatiquement :**
- Streamlit → http://localhost:8502
- Swagger API → http://localhost:8080/docs
- Grafana → http://localhost:3001
- Prometheus → http://localhost:9091
- MLflow → http://localhost:5001

---

## 🎯 Plan de Démonstration (30 min)

### **Phase 1 : Interfaces Web Interactives** (12 min)

#### **1. Streamlit** (4 min) - **C10**
**URL :** http://localhost:8502

**À montrer :**
- ✅ **Page "Combat et Prédiction"** : Prédiction en temps réel
- ✅ Sélection Pokémon A vs Pokémon B
- ✅ API call + résultat (meilleur move + win probability)
- ✅ Interface responsive et accessible
- ✅ 8 pages au total

**Script à dire :**
> "Voici l'interface Streamlit qui intègre l'API ML. L'utilisateur sélectionne deux Pokémon, l'application appelle mon API de prédiction, et affiche le meilleur move avec la probabilité de victoire. L'interface est responsive et accessible (WCAG 2.1 AA)."

---

#### **2. Swagger API** (3 min) - **C9**
**URL :** http://localhost:8080/docs

**À montrer :**
- ✅ **Endpoint POST /predict/best-move** : Tester avec JSON
- ✅ Request body : `{"pokemon_a_id": 1, "pokemon_b_id": 4, "available_moves": [1, 2, 3]}`
- ✅ Response : `{"recommended_move": {...}, "win_probability": 0.87}`
- ✅ Documentation auto-générée
- ✅ Authentification API Key (X-API-Key header)

**JSON exemple :**
```json
{
  "pokemon_a_id": 1,
  "pokemon_b_id": 4,
  "available_moves": [33, 45, 99]
}
```

**Script à dire :**
> "L'API REST expose le modèle XGBoost avec 96.26% accuracy. Elle prend en entrée deux Pokémon et les moves disponibles, et retourne le meilleur move avec la probabilité de victoire. L'API est sécurisée avec API Key et documentée avec Swagger."

---

#### **3. Grafana** (3 min) - **C11**
**URL :** http://localhost:3001 (admin/admin)

**À montrer :**
- ✅ **Dashboard "Model Performance"** :
  - Predictions per Minute
  - Model Confidence Score (gauge)
  - Win Probability distribution
- ✅ **Dashboard "API Performance"** :
  - API Status (UP/DOWN)
  - Request Duration (latency)
  - Error Rate
  - CPU/Memory Usage

**Script à dire :**
> "Pour le monitoring en production, j'utilise Grafana qui affiche les métriques en temps réel. On voit ici le nombre de prédictions par minute, la confiance du modèle, et les performances de l'API. Les dashboards sont accessibles (navigation clavier, WCAG 2.1 AA)."

---

#### **4. Prometheus** (1 min) - **C11**
**URL :** http://localhost:9091

**À montrer :**
- ✅ **Onglet "Targets"** : Tous les targets UP (vert)
- ✅ API scrape toutes les 15s
- ✅ 9 métriques collectées

**Script à dire :**
> "Prometheus collecte les métriques toutes les 15 secondes. On voit ici que tous les targets sont UP, et les données sont stockées avec 15 jours de rétention."

---

#### **5. MLflow** (2 min) - **C13**
**URL :** http://localhost:5001

**À montrer :**
- ✅ **Onglet "Experiments"** : 3 expérimentations
  - pokemon_battle_winner
  - demo_monitoring
  - Default
- ✅ **Onglet "Models"** : battle_winner_predictor v1 (Production)
- ✅ **Métriques** : 96.26% accuracy, 99.54% ROC-AUC

**Script à dire :**
> "MLflow gère le Model Registry et l'experiment tracking. Ici on voit mon modèle battle_winner_predictor en version 1, promu en Production car l'accuracy dépasse 95%. Les métriques et artifacts sont versionnés."

---

### **Phase 2 : Composants Backend** (10 min)

#### **6. PostgreSQL** (3 min) - **E1.3**
**Via Swagger API :**
- GET /pokemon → Liste 151 Pokémon
- GET /types → 18 types
- GET /moves → 600+ moves

**À montrer dans Swagger :**
```bash
# Via terminal (alternatif)
docker exec letsgo_db psql -U letsgo_user -d letsgo_db -c "\dt"
```

**Tables (11) :**
- pokemon_species, pokemon, form
- type, pokemon_type, type_effectiveness
- move, move_category, pokemon_move, learn_method
- pokemon_stat

**Script à dire :**
> "La base de données PostgreSQL contient 11 tables normalisées 3NF avec contraintes d'intégrité référentielle. Les données proviennent de 3 sources : PokéAPI, CSV, et scraping Poképédia."

---

#### **7. ETL Pipeline** (3 min) - **E1.1, E1.2**

```bash
# Voir logs formatés
docker logs letsgo_etl --tail 100
```

**Étapes ETL (5) :**
1. **Init DB** : Création schéma + tables
2. **Load CSV** : 3 fichiers (Pokemon, Moves, Types)
3. **Enrich PokéAPI** : Stats + sprites (threading 10 workers)
4. **Scraping** : Pokepedia moves (Scrapy)
5. **Post-processing** : Héritage moves + évolutions

**Script à dire :**
> "Le pipeline ETL automatise la collecte depuis 3 sources : fichiers CSV, API REST (PokéAPI), et web scraping (Pokepedia). Les données sont nettoyées, normalisées et agrégées dans PostgreSQL. Le pipeline est idempotent et versioned dans Git."

---

#### **8. ML Training** (4 min) - **C12**

```bash
# Voir logs entraînement
docker logs letsgo_ml --tail 100

# Ouvrir notebook
code notebooks/03_training_evaluation.ipynb
```

**Pipeline ML :**
1. Dataset : 718,889 combats (3 scénarios)
2. Features : 133 features engineered
3. Model : XGBoost Classifier
4. Training : GridSearchCV (8 combos)
5. Evaluation : 96.26% accuracy, 99.54% ROC-AUC

**Script à dire :**
> "Le pipeline ML génère 718k combats depuis la base de données, calcule 133 features (stats, types, STAB, effectiveness), entraîne un XGBoost avec GridSearchCV, et évalue sur un test set. L'accuracy finale est 96.26%."

---

### **Phase 3 : Technique Avancé** (8 min)

#### **9. Drift Detection** (2 min) - **C11**

```bash
# Lister fichiers drift
ls -lh api_pokemon/monitoring/drift_data/

# Lire un fichier parquet
python -c "import pandas as pd; df = pd.read_parquet('api_pokemon/monitoring/drift_data/production_data_20260201_163846.parquet'); print(df.describe())"
```

**À montrer :**
- ✅ Fichiers parquet datés (93 KB chacun)
- ✅ 100 prédictions par fichier
- ✅ Features collectées pour analyse future

**Script à dire :**
> "Le DriftDetector collecte automatiquement les features de chaque prédiction en production et les sauvegarde en parquet. Ces données permettent de détecter des dérives de distribution et de déclencher un retraining si nécessaire."

---

#### **10. GitHub Actions** (3 min) - **C13**

**URL :** https://github.com/USERNAME/lets-go-predictiondex/actions

**Workflows (7) :**
1. **certification-e1-e3.yml** : Workflow complet certification
2. **1-lint-and-format.yml** : Lint + format
3. **2-tests-unit.yml** : Tests unitaires
4. **3-docker-build.yml** : Build images Docker
5. **4-integration-tests.yml** : Tests intégration
6. **monitoring-validation.yml** : Tests monitoring
7. **(autres workflows...)**

**À montrer :**
- ✅ **Déclencheurs** : push, PR, workflow_dispatch
- ✅ **Jobs** : E1 data validation, E3 API/monitoring/MLOps
- ✅ **Artifacts** : Coverage reports, test results

**Script à dire :**
> "La chaîne CI/CD GitHub Actions comprend 7 workflows qui testent automatiquement le code, buildent les images Docker, et valident les compétences E1 et E3. Les workflows sont déclenchés sur chaque push et pull request."

---

#### **11. Documentation** (3 min) - **E1.5**

```bash
# Lister documentation
ls -lh docs/
tree docs/ -L 2
```

**Documents (20+) :**
- **README.md** : Guide complet projet
- **docs/ARCHITECTURE.md** : Architecture technique
- **docs/MONITORING.md** : Guide monitoring complet
- **docs/ACCESSIBILITE_MONITORING.md** : Tests accessibilité
- **docs/figures/** : Diagrammes MCD, architecture
- **machine_learning/README.md** : Guide ML
- **api_pokemon/README.md** : Guide API

**Script à dire :**
> "La documentation est complète et accessible (markdown, WCAG 2.1 AA). Elle couvre l'architecture, le monitoring, l'accessibilité, et tous les composants du projet. Les diagrammes MCD et d'architecture sont inclus."

---

## 🎓 Mapping Compétences → Composants

### **BLOC E1 - DONNÉES**

| Compétence | Composant | Preuve |
|------------|-----------|--------|
| **C1** - Collecte données | ETL Pipeline | [etl_pokemon/pipeline.py](../etl_pokemon/pipeline.py) |
| **C2** - Requêtes SQL | SQLAlchemy ORM | [core/db/guards/](../core/db/guards/) |
| **C3** - Nettoyage données | Normalizers | [etl_pokemon/utils/normalizers.py](../etl_pokemon/utils/normalizers.py) |
| **C4** - Structurer BDD | PostgreSQL 11 tables | [core/models/](../core/models/) |
| **C5** - API données | FastAPI REST | [api_pokemon/routes/](../api_pokemon/routes/) |

### **BLOC E3 - IA PRODUCTION**

| Compétence | Composant | Preuve |
|------------|-----------|--------|
| **C9** - API REST + IA | FastAPI + XGBoost | [api_pokemon/routes/prediction_route.py](../api_pokemon/routes/prediction_route.py) |
| **C10** - Intégration app | Streamlit 8 pages | [interface/app.py](../interface/app.py) |
| **C11** - Monitoring IA | Prometheus + Grafana + MLflow | [api_pokemon/monitoring/](../api_pokemon/monitoring/) |
| **C12** - Tests ML | Pytest 407 tests | [tests/ml/](../tests/ml/) |
| **C13** - MLOps CI/CD | GitHub Actions + MLflow | [.github/workflows/](../.github/workflows/) |

---

## 📊 Métriques du Projet

| Métrique | Valeur |
|----------|--------|
| **Python Files** | 150+ |
| **Test Files** | 23 |
| **Test Functions** | 407 |
| **Code Coverage** | 82%+ |
| **Database Tables** | 11 |
| **API Endpoints** | 15+ |
| **GitHub Workflows** | 7 |
| **Docker Services** | 10 |
| **ML Features** | 133+ |
| **Model Accuracy** | 96.26% |
| **Model ROC-AUC** | 99.54% |
| **Training Dataset** | 718,889 combats |
| **Documentation Files** | 20+ |

---

## 🔧 Commandes Utiles

### **Logs**
```bash
# ETL Pipeline
docker logs letsgo_etl --tail 200

# ML Training
docker logs letsgo_ml --tail 200

# API FastAPI
docker logs letsgo_api --tail 200

# Tous les logs
docker compose logs -f
```

### **Base de Données**
```bash
# Connexion PostgreSQL
docker exec -it letsgo_db psql -U letsgo_user -d letsgo_db

# Lister tables
docker exec letsgo_db psql -U letsgo_user -d letsgo_db -c "\dt"

# Compter Pokémon
docker exec letsgo_db psql -U letsgo_user -d letsgo_db -c "SELECT COUNT(*) FROM pokemon;"
```

### **Tests**
```bash
# Tous les tests
python scripts/run_all_tests.py

# Tests ML seulement
pytest tests/ml/ -v

# Tests monitoring
pytest tests/monitoring/ -v

# Coverage
pytest --cov=api_pokemon --cov=machine_learning --cov-report=html
```

### **Docker**
```bash
# État des services
docker compose ps

# Redémarrer un service
docker compose restart api

# Voir ressources
docker stats

# Nettoyer
docker compose down -v
docker system prune -a
```

---

## ✅ Checklist Pré-Certification

### **1 Semaine Avant**
- [ ] Tester le workflow complet (`python scripts/demo_certification.py`)
- [ ] Vérifier tous les services UP (`python scripts/validate_docker_stack.py`)
- [ ] Générer captures d'écran (Grafana, MLflow, Streamlit)
- [ ] Relire documentation (README.md, MONITORING.md)
- [ ] Tester en condition réelle (30 min chrono)

### **La Veille**
- [ ] Activer MLflow (`python scripts/mlflow/register_existing_model.py`)
- [ ] Générer métriques Grafana (`python scripts/generate_monitoring_data.py --duration 10`)
- [ ] Vérifier MLflow status (`python scripts/mlflow/check_mlflow_status.py`)
- [ ] Tester tous les endpoints API
- [ ] Préparer notes de présentation

### **Le Jour J**
- [ ] Démarrer stack Docker (`python scripts/quick_start_docker.py`)
- [ ] Valider services (`python scripts/validate_docker_stack.py --verbose`)
- [ ] Ouvrir tous les onglets (`python scripts/demo_certification.py --web-only`)
- [ ] Respirer profondément 😊
- [ ] Présenter avec confiance !

---

## 🚨 Troubleshooting

### **Problème : Services ne démarrent pas**
```bash
# Vérifier Docker
docker ps

# Vérifier logs
docker compose logs

# Redémarrer
docker compose down
docker compose up -d
```

### **Problème : Ports déjà utilisés**
```bash
# Identifier processus
lsof -i :8080
lsof -i :5432

# Tuer processus
kill -9 <PID>
```

### **Problème : Base de données vide**
```bash
# Relancer ETL
docker compose up -d db
python etl_pokemon/pipeline.py --force
```

### **Problème : MLflow ne démarre pas**
```bash
# Logs MLflow
docker logs letsgo_mlflow

# Redémarrer MLflow
docker compose restart mlflow

# Vérifier health
curl http://localhost:5001/health
```

---

## 📞 Support

- **Documentation** : [README.md](../README.md)
- **Architecture** : [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Monitoring** : [docs/MONITORING.md](MONITORING.md)
- **Accessibilité** : [docs/ACCESSIBILITE_MONITORING.md](ACCESSIBILITE_MONITORING.md)

---

## 🎉 Conclusion

**Tu as tous les outils pour réussir ta certification !**

**Score attendu :**
- **E1** : 100% (5/5 compétences)
- **E3** : 98% (5/5 compétences)

**Points forts à mettre en avant :**
- Architecture complète et professionnelle
- Pipeline ML performant (96.26% accuracy)
- Monitoring production-ready (Prometheus + Grafana + MLflow)
- Tests exhaustifs (407 tests, 82% coverage)
- CI/CD automatisée (7 workflows GitHub Actions)
- Documentation accessible et complète

**Bonne chance ! 🍀**

---

**Version** : 2.0
**Dernière mise à jour** : 2 février 2026
**Auteur** : Let's Go PredictionDex Team
