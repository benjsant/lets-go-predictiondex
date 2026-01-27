# 🎥 Guide de Démonstration Visuelle - PredictionDex
## Certification E1/E3 - Présentation Professionnelle

**Objectif:** Montrer visuellement TOUS les composants du projet pour la certification RNCP

**Date:** 27 janvier 2026
**Durée démo:** 30-45 minutes
**Public:** Jury de certification E1/E3

---

## 📋 Tableau Récapitulatif - Composant → Outil Visuel

| # | Composant | Type | Outil Visuel | URL / Commande | Preuves E1/E3 |
|---|-----------|------|--------------|----------------|---------------|
| 1 | **Interface Streamlit** | Web UI | Navigateur | http://localhost:8502 | C10 - Intégration app |
| 2 | **API REST (Swagger)** | Web UI | Navigateur | http://localhost:8080/docs | C9 - API REST avec IA |
| 3 | **Grafana Dashboards** | Web UI | Navigateur | http://localhost:3001 | C11 - Monitoring IA |
| 4 | **Prometheus Metrics** | Web UI | Navigateur | http://localhost:9091 | C11 - Métriques temps réel |
| 5 | **MLflow UI** | Web UI | Navigateur | http://localhost:5001 | C13 - MLOps CI/CD |
| 6 | **Base PostgreSQL** | Database | Visualisation par API + Requêtes | http://localhost:8080/docs | E1.3 - Structurer BDD |
| 7 | **ETL Pipeline** | Backend | Logs Docker formatés | `docker logs letsgo_etl` | E1.1, E1.2 - Collecte/Nettoyage |
| 8 | **ML Training** | Backend | Logs + Notebooks | `docker logs letsgo_ml` | C12 - Optimiser IA |
| 9 | **Drift Detection** | Backend | Rapports HTML Evidently | `api_pokemon/monitoring/reports/` | C11 - Monitoring IA |
| 10 | **Tests Automatisés** | CI/CD | GitHub Actions | https://github.com/.../actions | C13 - MLOps CI/CD |
| 11 | **Notebooks Jupyter** | Data Science | Jupyter Lab / VSCode | `notebooks/` | E1.4 - Exploiter données |
| 12 | **Documentation** | Documentation | Markdown (GitHub/VSCode) | `README.md`, `docs/` | E1.5 - Documenter processus |

---

## 🎯 Plan de Démonstration (30 minutes)

### Phase 1: Interfaces Web Interactives (12 min)

#### 1.1 Interface Streamlit - Application Utilisateur (4 min)
**URL:** http://localhost:8502
**Objectif:** Montrer l'application finale fonctionnelle (C10)

**Parcours de démonstration:**

1. **Page Accueil** (30s)
   - Vue d'ensemble du projet
   - Statistiques clés (188 Pokémon, 226 capacités, 94.46% accuracy)
   - Navigation vers fonctionnalités

2. **Page "Combat et Prédiction"** (2 min) ⭐ **FEATURE PRINCIPALE**
   - Sélectionner Pokémon A (ex: Pikachu #25)
   - Sélectionner Pokémon B (ex: Bulbizarre #1)
   - Choisir 4 capacités pré-suggérées
   - Cliquer "Prédire le vainqueur"
   - **Montrer:** Prédiction ML avec probabilités + recommandation meilleure capacité
   - **Temps de réponse:** < 500ms

3. **Page "Détails Pokémon"** (1 min)
   - Rechercher un Pokémon (ex: Dracaufeu)
   - Afficher stats, types, capacités apprises, faiblesses
   - **Montrer:** Feature engineering (multiplicateurs de types)

4. **Page "Capacités"** (30s)
   - Filtrer par type (ex: Électrik)
   - Trier par puissance
   - **Montrer:** Catalogue complet des 226 moves

5. **Page "Types et Affinités"** (30s)
   - Matrice 18x18 des affinités
   - **Montrer:** Règles métier complexes (324 règles)

**Preuves démontrées:**
- ✅ C10: Intégration applicative frontend/backend
- ✅ C9: API REST consommée par Streamlit
- ✅ E1.4: Exploitation des données via features

---

#### 1.2 API REST - Swagger UI (3 min)
**URL:** http://localhost:8080/docs
**Objectif:** Montrer l'API RESTful production-ready (C9)

**Parcours de démonstration:**

1. **Documentation interactive** (30s)
   - Présenter les 5 groupes d'endpoints
   - Montrer descriptions OpenAPI complètes

2. **Endpoint `/pokemon`** (1 min)
   - Cliquer "Try it out"
   - Exécuter `GET /pokemon?limit=10`
   - **Montrer:** Response JSON structuré (pagination, filtres)

3. **Endpoint `/predict/best-move`** (1 min 30s) ⭐ **CORE ML API**
   - Cliquer "Try it out"
   - Body JSON:
   ```json
   {
     "pokemon_a_id": 25,
     "pokemon_b_id": 1,
     "available_moves": ["Fatal-Foudre", "Vive-Attaque", "Tonnerre", "Cage-Éclair"]
   }
   ```
   - Exécuter la requête
   - **Montrer:**
     - Prédictions pour chaque move
     - Recommandation meilleure capacité
     - Temps de réponse < 500ms
     - Probabilités de victoire

4. **Endpoint `/health`** (30s)
   - Montrer health check
   - **Montrer:** API operationnelle, metrics disponibles

**Preuves démontrées:**
- ✅ C9: API REST avec intégration IA
- ✅ C12: Optimisation inférence (<500ms)
- ✅ Documentation API complète (OpenAPI 3.0)

---

#### 1.3 Grafana - Dashboards Monitoring (3 min)
**URL:** http://localhost:3001
**Objectif:** Monitoring temps réel de l'API et du modèle (C11)

**Parcours de démonstration:**

1. **Accès Grafana** (30s)
   - Ouvrir http://localhost:3001
   - Login automatique (anonymous auth enabled)

2. **Dashboard "API Performance"** (1 min 30s) ⭐ **DASHBOARD PRINCIPAL**
   - Navigate: Dashboards → Let's Go PredictionDex - API Performance
   - **Montrer:**
     - ✅ API Status (UP/DOWN)
     - ✅ Request Rate by Endpoint (req/s)
     - ✅ P95 Latency (< 500ms)
     - ✅ Error Rate (%)
     - ✅ Response Status Codes (200, 404, 500)
   - **Action:** Lancer `generate_monitoring_data.py` en parallèle pour voir métriques live

3. **Dashboard "Model Performance"** (1 min)
   - Navigate: Dashboards → Let's Go PredictionDex - Model Performance
   - **Montrer:**
     - ✅ Predictions per Minute
     - ✅ Model Accuracy (%)
     - ✅ Prediction Confidence Distribution
     - ✅ Feature Importance (top 10 features)

**Script pour générer métriques live:**
```bash
# Terminal séparé
python scripts/generate_monitoring_data.py --mode realistic --duration 5
```

**Preuves démontrées:**
- ✅ C11: Monitoring IA en production
- ✅ Prometheus + Grafana stack complète
- ✅ Métriques métier (accuracy, latency, throughput)

---

#### 1.4 Prometheus - Métriques Brutes (1 min)
**URL:** http://localhost:9091
**Objectif:** Montrer collecte métriques sous-jacente (C11)

**Parcours de démonstration:**

1. **Accès Prometheus** (30s)
   - Ouvrir http://localhost:9091
   - Navigate: Status → Targets

2. **Vérifier targets** (30s)
   - **Montrer:**
     - ✅ `api` target: UP (http://api:8080/metrics)
     - ✅ `node-exporter` target: UP
     - ✅ Scrape interval: 15s
   - **Expliquer:** Prometheus scrape API `/metrics` endpoint automatiquement

**Preuves démontrées:**
- ✅ C11: Infrastructure monitoring
- ✅ Auto-discovery des services via Docker labels

---

#### 1.5 MLflow UI - Model Registry (2 min)
**URL:** http://localhost:5001
**Objectif:** MLOps - Versioning et registry des modèles (C13)

**Parcours de démonstration:**

1. **Accès MLflow** (30s)
   - Ouvrir http://localhost:5001

2. **Experiments** (1 min)
   - Navigate: Experiments → battle_winner_v2
   - **Montrer:**
     - ✅ Liste des runs avec métriques (accuracy, f1, precision)
     - ✅ Comparaison entre runs
     - ✅ Hyperparamètres trackés automatiquement
     - ✅ Artifacts (model.pkl, confusion_matrix.png)

3. **Models Registry** (30s)
   - Navigate: Models → battle_winner_model
   - **Montrer:**
     - ✅ Versions du modèle (v1, v2, v3...)
     - ✅ Stage: Production / Staging / Archived
     - ✅ Métadonnées: accuracy, dataset version, training date

**Preuves démontrées:**
- ✅ C13: MLOps - Experiment tracking
- ✅ C13: Model Registry avec versioning
- ✅ C13: Auto-promotion modèles (meilleur accuracy → Production)

---

### Phase 2: Composants Backend Visuels (10 min)

#### 2.1 Base de Données PostgreSQL - Via API (3 min)
**Objectif:** Montrer structure BDD sans pgAdmin (E1.3)

**Méthode 1: Via Swagger UI** ⭐ **RECOMMANDÉ**

1. **Ouvrir** http://localhost:8080/docs

2. **Explorer tables via endpoints:**

**A. Table `pokemon`**
```bash
GET /pokemon?limit=5
# Montrer: id, name, national_number, height, weight, stats
```

**B. Table `types`**
```bash
GET /types
# Montrer: 18 types avec couleurs
```

**C. Table `moves`**
```bash
GET /moves?limit=5
# Montrer: name, power, accuracy, type, category (Physical/Special)
```

**D. Relations `pokemon_moves`**
```bash
GET /pokemon/25/moves
# Montrer: Capacités apprises par Pikachu avec learn_method
```

**E. Relations `pokemon_types` + `type_effectiveness`**
```bash
GET /pokemon/25/types
# Montrer: Types + faiblesses/résistances calculées
```

**Méthode 2: Via Requêtes SQL directes (optionnel)**
```bash
# Connexion PostgreSQL
docker exec -it letsgo_postgres psql -U letsgo_user -d letsgo_db

# Commandes à montrer
\dt                          # Liste des 11 tables
\d pokemon                   # Structure table pokemon
SELECT COUNT(*) FROM pokemon; # 188 Pokémon
SELECT * FROM type_effectiveness LIMIT 10; # 324 règles
```

**Diagramme à montrer:** (optionnel - si préparé)
- Schéma relationnel des 11 tables
- Clés étrangères
- Normalisation 3NF

**Preuves démontrées:**
- ✅ E1.3: Base de données structurée (11 tables, 3NF)
- ✅ E1.3: Relations (FK, many-to-many via junction tables)
- ✅ E1.2: Données nettoyées et normalisées
- ✅ E1.1: 188 Pokémon + 226 moves + 324 type rules

---

#### 2.2 ETL Pipeline - Logs Formatés (3 min)
**Objectif:** Montrer collecte et nettoyage données (E1.1, E1.2)

**Méthode: Docker Logs avec formatage coloré**

```bash
# Afficher logs ETL complets
docker logs letsgo_etl --tail 200
```

**Points clés à montrer dans les logs:**

1. **Étape 1: Initialisation DB** (30s)
```
🔧 [1/5] Initialisation des tables PostgreSQL...
   ✅ Table pokemon créée
   ✅ Table types créée
   ✅ Table moves créée
   ✅ Contraintes FK appliquées
```

2. **Étape 2: Chargement CSV** (1 min)
```
📦 [2/5] Chargement données CSV (151 Pokémon Gen1)...
   ✅ 151 Pokémon chargés depuis CSV
   ⚠️  Nettoyage: 3 doublons supprimés
   ⚠️  Validation: 2 stats manquantes interpolées
```

3. **Étape 3: Enrichissement PokéAPI** (1 min)
```
🌐 [3/5] Enrichissement via PokéAPI (188 Pokémon)...
   ✅ Formes Alola ajoutées (37 Pokémon)
   ✅ Statistiques complétées
   ✅ Capacités apprises: 4,248 associations
```

4. **Étape 4: Scraping Pokepedia** (30s)
```
🕷️ [4/5] Scraping évolutions et affinités (Pokepedia)...
   ✅ Chaînes d'évolution: 78 liens
   ✅ Affinités de types: 324 règles
```

5. **Étape 5: Validation finale** (30s)
```
✅ [5/5] Validation des données...
   ✅ 188 Pokémon valides
   ✅ 226 capacités valides
   ✅ 324 règles de types complètes
   ✅ 0 données manquantes
```

**Méthode alternative: Script validation**
```bash
# Script Python pour valider ETL
python scripts/validate_docker_stack.py --verbose
```

**Preuves démontrées:**
- ✅ E1.1: Collecte de données (3 sources)
- ✅ E1.2: Nettoyage (doublons, valeurs manquantes)
- ✅ E1.2: Validation (contraintes, types)
- ✅ Pipeline automatisé et reproductible

---

#### 2.3 ML Training - Logs + Notebooks (4 min)
**Objectif:** Montrer entraînement modèle et optimisations (C12, C13)

**Méthode 1: Logs Docker** (2 min)

```bash
# Afficher logs ML training
docker logs letsgo_ml --tail 300
```

**Points clés à montrer:**

1. **Dataset Generation** (30s)
```
📊 [1/4] Génération dataset de combats...
   Mode: all_scenarios (best_move + random_move + all_combinations)
   ✅ 898,472 combats simulés
   ✅ Train: 718,889 samples (80%)
   ✅ Test: 179,583 samples (20%)
   ✅ Features: 133 (stats + types + STAB + effectiveness)
```

2. **Model Training** (1 min)
```
🤖 [2/4] Entraînement XGBoost Classifier...
   Hyperparams tuning: GridSearchCV (12 combinations)
   ⏱️  Training time: 180s
   ✅ Best params: n_estimators=200, max_depth=8, lr=0.1
   ✅ Train accuracy: 96.24%
```

3. **Model Evaluation** (30s)
```
📈 [3/4] Évaluation sur test set...
   ✅ Test accuracy: 94.46%
   ✅ Precision: 94.21%
   ✅ Recall: 94.11%
   ✅ F1-score: 94.16%
   ✅ AUC-ROC: 0.9876
```

4. **Model Export** (30s)
```
💾 [4/4] Export du modèle...
   ✅ Modèle sauvegardé: models/battle_winner_model_v2.pkl
   ✅ Métadonnées: models/battle_winner_model_v2_metadata.json
   ✅ Taille: 2.3 MB (compressed)
   ✅ MLflow: Enregistré avec run_id abc123
```

**Méthode 2: Jupyter Notebooks** (2 min) ⭐ **PLUS VISUEL**

```bash
# Ouvrir notebooks dans VSCode ou Jupyter
code notebooks/03_training_evaluation.ipynb
```

**Notebooks à montrer:**

1. **`01_exploration.ipynb`** (30s)
   - Distribution des stats Pokémon
   - Analyse des types (bar charts)
   - Corrélations entre features

2. **`02_feature_engineering.ipynb`** (30s)
   - Création des 133 features
   - Feature importance (bar chart)
   - STAB et multiplicateurs de types

3. **`03_training_evaluation.ipynb`** (1 min) ⭐ **PRINCIPAL**
   - Training curves (loss vs epochs)
   - Confusion matrix (heatmap)
   - ROC curves (3 scenarios)
   - Feature importance (top 20)
   - **Montrer:** Graphiques interactifs avec matplotlib

**Preuves démontrées:**
- ✅ C12: Optimisation IA (GridSearch, hyperparams)
- ✅ C12: Feature engineering (133 features)
- ✅ E1.4: Exploitation données (notebooks)
- ✅ C13: MLOps pipeline automatisé
- ✅ Accuracy: 94.46% (validation métier)

---

### Phase 3: Composants Techniques Avancés (8 min)

#### 3.1 Drift Detection - Rapports Evidently (2 min)
**Objectif:** Monitoring qualité prédictions en production (C11)

**Méthode: Rapports HTML Evidently**

1. **Générer du trafic pour drift** (1 min)
```bash
# Générer 1000 prédictions
python scripts/generate_monitoring_data.py --mode burst --duration 2
```

2. **Vérifier génération rapport** (30s)
```bash
# Lister rapports générés
ls -lh api_pokemon/monitoring/reports/
# Montrer: drift_dashboard_2026-01-27_15-30-00.html
```

3. **Ouvrir rapport HTML** (30s)
```bash
# Ouvrir dans navigateur
xdg-open api_pokemon/monitoring/reports/drift_dashboard_*.html
# Ou: double-clic dans l'explorateur de fichiers
```

**Éléments à montrer dans le rapport:**

- ✅ **Data Drift Dashboard** (page 1)
  - Nombre de features avec drift détecté
  - Distribution features (histogrammes)
  - Statistical tests (Kolmogorov-Smirnov)

- ✅ **Feature Drift Details** (page 2)
  - Drift score par feature
  - P-values des tests statistiques
  - Graphiques "Reference vs Current"

- ✅ **Summary** (page 3)
  - Alertes (features en drift)
  - Recommandations (retraining needed?)

**Preuves démontrées:**
- ✅ C11: Drift detection avec Evidently AI
- ✅ C11: Rapports automatiques (HTML + JSON)
- ✅ C11: Statistical tests professionnels

---

#### 3.2 Tests Automatisés - GitHub Actions (3 min)
**Objectif:** CI/CD et qualité code (C13)

**Méthode: GitHub Actions UI**

1. **Accès GitHub Actions** (30s)
```
https://github.com/YOUR_USERNAME/lets-go-predictiondex/actions
```

2. **Workflows à montrer:** (2 min 30s)

**A. Workflow "Run Tests"** (1 min)
- Navigate: Actions → Run Tests → Latest run
- **Montrer:**
  - ✅ 252 tests passed
  - ✅ Coverage: 82%
  - ✅ Test matrix: Python 3.11, 3.12
  - ✅ Durée: ~5 minutes
  - ✅ Artifacts: coverage report

**B. Workflow "Build Docker Images"** (1 min)
- Navigate: Actions → Build Docker Images → Latest run
- **Montrer:**
  - ✅ 5 images buildées (api, streamlit, etl, ml, mlflow)
  - ✅ Multi-stage builds optimisés
  - ✅ Cache layers
  - ✅ Security scan (pas de vulnérabilités critiques)

**C. Workflow "Deploy to Staging"** (optionnel)
- **Montrer:**
  - Auto-trigger après merge sur `main`
  - Déploiement automatique
  - Health checks post-déploiement

**D. Workflow "ML Training Pipeline"** (30s)
- Navigate: Actions → ML Training Pipeline
- **Montrer:**
  - ✅ Dataset generation
  - ✅ Model training
  - ✅ Model evaluation
  - ✅ Auto-registration MLflow
  - ✅ Artifacts: model.pkl, metrics.json

**Méthode alternative: Badges README**
```bash
# Montrer badges dans README.md
cat README.md | grep -A 5 "badges"
```

**Preuves démontrées:**
- ✅ C13: CI/CD complet (4 workflows)
- ✅ C13: Tests automatisés (252 tests)
- ✅ C13: Quality gates (coverage, linting)
- ✅ C13: MLOps pipeline automatisé

---

#### 3.3 Documentation - Markdown & Diagrammes (3 min)
**Objectif:** Documentation complète du processus (E1.5)

**Fichiers à montrer:**

1. **README.md principal** (1 min)
```bash
# Ouvrir dans VSCode avec preview
code README.md
```
**Points clés:**
- ✅ Badges (Python, Docker, Tests, Coverage)
- ✅ Quick Start (5 min)
- ✅ Architecture diagram (ASCII art)
- ✅ Table of Contents complète
- ✅ Documentation API, monitoring, déploiement

2. **Documentation technique ETL** (1 min)
```bash
# Ouvrir docs ETL
code docs/CERTIFICATION_E1_E3_VALIDATION.md
```
**Points clés:**
- ✅ Validation compétences E1/E3
- ✅ Preuves concrètes (code snippets)
- ✅ Scores par compétence
- ✅ Architecture détaillée

3. **Diagrammes architecturaux** (1 min)

**A. Diagramme global (ASCII art dans README.md)**
```
┌─────────────────────────────────────────────┐
│           SOURCES DE DONNÉES                 │
├─────────────────────────────────────────────┤
│  📦 CSV   🌐 PokéAPI   🕷️ Pokepedia         │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│        ETL PIPELINE (E1.1, E1.2)            │
├─────────────────────────────────────────────┤
│  • Extraction multi-sources                  │
│  • Transformation (nettoyage, validation)    │
│  • Load PostgreSQL (11 tables, 3NF)         │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│      BASE POSTGRESQL (E1.3)                 │
├─────────────────────────────────────────────┤
│  188 Pokémon • 226 Moves • 18 Types         │
│  11 tables • Relations FK • Normalisation    │
└─────────────┬───────────────────────────────┘
              │
      ┌───────┴────────┐
      ▼                ▼
┌───────────┐    ┌───────────────────┐
│  ML       │    │  API REST (C9)    │
│  PIPELINE │    │  FastAPI + IA     │
│  (C12)    │    │  8 endpoints      │
└─────┬─────┘    └─────┬─────────────┘
      │                │
      ▼                ▼
┌───────────┐    ┌───────────────────┐
│  MLflow   │    │  Streamlit (C10)  │
│  Registry │    │  8 pages          │
│  (C13)    │    │  Interface User   │
└───────────┘    └───────────────────┘
      │                │
      └────────┬───────┘
               ▼
┌─────────────────────────────────────────────┐
│     MONITORING (C11)                        │
├─────────────────────────────────────────────┤
│  Prometheus • Grafana • Evidently Drift     │
└─────────────────────────────────────────────┘
```

**B. Diagramme CI/CD**
- GitHub Actions workflows
- Tests → Build → Deploy pipeline
- MLflow integration

**Preuves démontrées:**
- ✅ E1.5: Documentation complète et structurée
- ✅ E1.5: Diagrammes architecturaux
- ✅ E1.5: Guide d'installation et déploiement
- ✅ E1.5: Documentation API (OpenAPI/Swagger)

---

## 🚀 Scripts de Démonstration Automatisés

### Script 1: Démarrage Stack Complète
**Fichier:** `/mnt/Data/Dev/projet_python_ia_v1/lets-go-predictiondex/scripts/start_docker_stack.py`

```bash
# Démarre tous les services Docker en une commande
python scripts/start_docker_stack.py

# Sortie formatée:
# ==================================================
# 🚀 Démarrage PredictionDex - Full Stack
# ==================================================
# ✅ Docker et Docker Compose détectés
# ✅ Fichier .env créé
# 📦 Construction des images... (3 min)
# 🚀 Démarrage des services... (30s)
# 🔍 Vérification des services...
#    ✅ PostgreSQL (5432)
#    ✅ API FastAPI (8080)
#    ✅ Streamlit (8502)
#    ✅ Prometheus (9091)
#    ✅ Grafana (3001)
#    ✅ MLflow (5001)
# ==================================================
# ✅ Tous les services sont opérationnels!
# ==================================================
# 🌐 URLs disponibles:
#    API (Swagger):    http://localhost:8080/docs
#    Streamlit:        http://localhost:8502
#    Grafana:          http://localhost:3001
#    Prometheus:       http://localhost:9091
#    MLflow:           http://localhost:5001
```

---

### Script 2: Validation Stack
**Fichier:** `/mnt/Data/Dev/projet_python_ia_v1/lets-go-predictiondex/scripts/validate_docker_stack.py`

```bash
# Valide tous les services (health checks)
python scripts/validate_docker_stack.py --verbose

# Sortie formatée:
# ==================================================
# 🔍 Validation de la stack Docker
# ==================================================
# 1️⃣ Services Docker
# ✅ postgres          [5432]  - PostgreSQL
# ✅ api               [8080]  - API FastAPI
# ✅ streamlit         [8502]  - Interface Streamlit
# ✅ prometheus        [9091]  - Prometheus
# ✅ grafana           [3001]  - Grafana
# ✅ mlflow            [5001]  - MLflow
#
# 2️⃣ Endpoints API
#    6/6 endpoints fonctionnels
#
# 3️⃣ Prometheus Targets
#    2/2 targets UP
#
# 4️⃣ Grafana Datasources
#    1 datasource(s) configurée(s)
#
# ==================================================
# ✅ Tous les services sont opérationnels!
# ==================================================
```

---

### Script 3: Génération Métriques de Monitoring
**Fichier:** `/mnt/Data/Dev/projet_python_ia_v1/lets-go-predictiondex/scripts/generate_monitoring_data.py`

```bash
# Génère trafic réaliste pour dashboards Grafana
python scripts/generate_monitoring_data.py --mode realistic --duration 5

# Sortie formatée en temps réel:
# ==================================================
# 🎯 Générateur de métriques Prometheus/Grafana
# ==================================================
# 🔧 Initialisation...
#    ✅ API accessible
#    ✅ 188 Pokémon chargés
#    ✅ Prometheus accessible
#    ✅ Grafana accessible
#
# 👥 Mode REALISTIC - 5 minutes
# ==================================================
# Simulation: 5-10 utilisateurs avec patterns réalistes
#
# [  30s] Prédictions:    15 | Lectures:   8 | Erreurs:  1 | Latence: P50=245ms P95=387ms P99=456ms
# [  60s] Prédictions:    32 | Lectures:  17 | Erreurs:  3 | Latence: P50=238ms P95=401ms P99=478ms
# [  90s] Prédictions:    49 | Lectures:  25 | Erreurs:  5 | Latence: P50=241ms P95=395ms P99=467ms
# [ 120s] Prédictions:    67 | Lectures:  34 | Erreurs:  7 | Latence: P50=247ms P95=408ms P99=489ms
# [ 150s] Prédictions:    84 | Lectures:  42 | Erreurs:  9 | Latence: P50=239ms P95=392ms P99=471ms
#
# ==================================================
# ✅ Mode realistic terminé!
# ==================================================
# 📊 Statistiques finales:
#    Durée totale: 5.0 minutes
#    Total requêtes: 135
#    Prédictions: 84 (62.2%)
#    Lectures: 42 (31.1%)
#    Erreurs: 9 (6.7%)
#    Débit moyen: 27.0 req/min
#
#    Latences prédictions:
#       Moyenne: 243.2ms
#       P50: 241.0ms
#       P95: 395.0ms
#       P99: 478.0ms
#
# 💡 Consultez Grafana: http://localhost:3001
# 💡 Consultez Prometheus: http://localhost:9091
```

**Options du script:**
```bash
# Mode burst (trafic intense)
python scripts/generate_monitoring_data.py --mode burst --duration 10

# Mode spike (pics aléatoires)
python scripts/generate_monitoring_data.py --mode spike --duration 15
```

---

## 📊 Checklist Démonstration

### Avant la Démonstration

- [ ] Démarrer stack Docker: `python scripts/start_docker_stack.py`
- [ ] Valider services: `python scripts/validate_docker_stack.py`
- [ ] Pré-charger notebooks dans VSCode
- [ ] Ouvrir 5 onglets navigateur:
  - [ ] http://localhost:8502 (Streamlit)
  - [ ] http://localhost:8080/docs (Swagger)
  - [ ] http://localhost:3001 (Grafana)
  - [ ] http://localhost:5001 (MLflow)
  - [ ] https://github.com/YOUR_REPO/actions (GitHub Actions)
- [ ] Lancer génération métriques en arrière-plan:
  ```bash
  python scripts/generate_monitoring_data.py --mode realistic --duration 30 &
  ```

### Pendant la Démonstration

**Phase 1: Interfaces Web (12 min)**
- [ ] Streamlit: 4 min
- [ ] Swagger API: 3 min
- [ ] Grafana: 3 min
- [ ] Prometheus: 1 min
- [ ] MLflow: 2 min

**Phase 2: Backend (10 min)**
- [ ] PostgreSQL via API: 3 min
- [ ] ETL logs: 3 min
- [ ] ML training (logs + notebooks): 4 min

**Phase 3: Technique (8 min)**
- [ ] Drift detection: 2 min
- [ ] GitHub Actions: 3 min
- [ ] Documentation: 3 min

### Après la Démonstration

- [ ] Montrer README.md complet
- [ ] Présenter architecture globale
- [ ] Questions/Réponses

---

## 🎯 Points Forts à Insister

### Pour E1 (Collecte et Traitement Données)

1. **3 sources de données** (CSV, PokéAPI, Pokepedia)
2. **Pipeline ETL automatisé** avec validation
3. **898,472 combats simulés** pour dataset ML
4. **Base normalisée 3NF** (11 tables, FK, contraintes)
5. **Feature engineering** (133 features)

### Pour E3 (Intégration IA Production)

1. **API REST production-ready** (FastAPI + OpenAPI)
2. **Interface utilisateur fonctionnelle** (Streamlit 8 pages)
3. **Monitoring complet** (Prometheus + Grafana + Evidently)
4. **MLOps pipeline** (MLflow + GitHub Actions)
5. **Performance optimisée** (< 500ms, 94.46% accuracy)

---

## 💡 Astuces Présentation

### Timing

- **30 min minimum** (essentiel)
- **45 min idéal** (complet)
- **15 min Q&A** (questions jury)

### Préparation Technique

1. **Tester la démo 2 fois avant**
2. **Avoir plan B si services down:**
   - Screenshots pré-préparés
   - Vidéo screencast backup
3. **Vérifier résolution écran** (1920x1080 minimum)
4. **Fermer applications inutiles** (performances)

### Communication

1. **Commencer par vue d'ensemble** (architecture globale)
2. **Montrer d'abord l'application finale** (Streamlit)
3. **Puis descendre vers technique** (API, DB, ML)
4. **Finir par CI/CD et qualité** (tests, monitoring)
5. **Toujours lier à compétences E1/E3** (mentionner codes)

### Phrases Clés

- "Ce composant valide la compétence **E1.1** (collecte de données)"
- "Ici on voit **C9** (API REST avec IA intégrée)"
- "Ce dashboard démontre **C11** (monitoring IA en production)"
- "Ce pipeline illustre **C13** (MLOps automatisé)"

---

## 🔧 Dépannage Démo

### Si un service ne démarre pas

```bash
# Vérifier logs
docker logs letsgo_<service_name>

# Redémarrer service spécifique
docker-compose restart <service_name>

# Rebuild si nécessaire
docker-compose up -d --build <service_name>
```

### Si Grafana ne montre pas de données

```bash
# Générer trafic
python scripts/generate_monitoring_data.py --mode burst --duration 2

# Vérifier Prometheus targets
curl http://localhost:9091/api/v1/targets
```

### Si notebooks ne s'affichent pas

```bash
# Ouvrir avec VSCode
code notebooks/

# Ou démarrer Jupyter
jupyter lab notebooks/
```

---

## 📁 Fichiers Clés à Connaître

### Scripts Démonstration

- `/scripts/start_docker_stack.py` - Démarrage complet
- `/scripts/validate_docker_stack.py` - Validation services
- `/scripts/generate_monitoring_data.py` - Génération métriques

### Documentation

- `/README.md` - Documentation principale
- `/docs/CERTIFICATION_E1_E3_VALIDATION.md` - Validation compétences
- `/docs/EXPLICATIONS_TECHNIQUES_ML_MONITORING.md` - Détails techniques

### Code Principal

- `/api_pokemon/main.py` - API FastAPI (C9)
- `/interface/app.py` - Streamlit (C10)
- `/machine_learning/run_machine_learning.py` - ML pipeline (C12)
- `/etl_pokemon/pipeline.py` - ETL pipeline (E1.1, E1.2)

### Configuration

- `/docker-compose.yml` - Orchestration complète (9 services)
- `/.github/workflows/` - CI/CD GitHub Actions (C13)
- `/docker/grafana/dashboards/` - Dashboards Grafana (C11)

---

## 📚 Ressources Complémentaires

### Documentation Externe

- **FastAPI:** https://fastapi.tiangolo.com/
- **Streamlit:** https://docs.streamlit.io/
- **XGBoost:** https://xgboost.readthedocs.io/
- **MLflow:** https://mlflow.org/docs/latest/
- **Prometheus:** https://prometheus.io/docs/
- **Grafana:** https://grafana.com/docs/
- **Evidently AI:** https://docs.evidentlyai.com/

### Documentation Projet

- [README principal](README.md)
- [Guide déploiement](docs/deployment/QUICK_START.md)
- [Documentation API](http://localhost:8080/docs)
- [Explications ML](docs/EXPLICATIONS_TECHNIQUES_ML_MONITORING.md)

---

## ✅ Validation Finale

### Avant de Présenter

**Vérifier que TOUS ces éléments sont démontrables:**

#### E1 - Collecte et Traitement Données
- [x] E1.1: 3 sources de données (CSV, PokéAPI, Pokepedia)
- [x] E1.2: Nettoyage et validation (logs ETL)
- [x] E1.3: Base PostgreSQL (11 tables via API)
- [x] E1.4: Feature engineering (133 features, notebooks)
- [x] E1.5: Documentation complète (README, diagrammes)

#### E3 - Intégration IA Production
- [x] C9: API REST avec IA (Swagger UI fonctionnel)
- [x] C10: Interface applicative (Streamlit 8 pages)
- [x] C11: Monitoring IA (Grafana + Prometheus + Evidently)
- [x] C12: Optimisation IA (< 500ms, 94.46% accuracy)
- [x] C13: MLOps CI/CD (MLflow + GitHub Actions)

---

**Dernière mise à jour:** 27 janvier 2026
**Version:** 1.0
**Auteur:** PredictionDex Team
**Objectif:** Certification RNCP Niveau 6 - E1/E3

---

**🎯 Bon courage pour la démonstration ! 🚀**
