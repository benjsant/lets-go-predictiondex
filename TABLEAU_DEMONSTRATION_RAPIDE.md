# 🎯 Tableau Démonstration Rapide - Certification E1/E3

## 📊 Vue d'Ensemble (Imprimer ce document)

| # | Composant | Outil Visuel | URL / Commande | Durée | Compétence | Preuves à Montrer |
|---|-----------|--------------|----------------|-------|------------|-------------------|
| **1** | **Interface Streamlit** | Navigateur Web | `http://localhost:8502` | 4 min | **C10** | ✅ 8 pages fonctionnelles<br>✅ Prédiction ML interactive<br>✅ Visualisations (stats, types) |
| **2** | **API REST Swagger** | Navigateur Web | `http://localhost:8080/docs` | 3 min | **C9** | ✅ 8 endpoints documentés<br>✅ Test `/predict/best-move`<br>✅ Réponse < 500ms |
| **3** | **Grafana Dashboards** | Navigateur Web | `http://localhost:3001` | 3 min | **C11** | ✅ 2 dashboards (API + Model)<br>✅ Métriques temps réel<br>✅ P95 latency, error rate |
| **4** | **MLflow Registry** | Navigateur Web | `http://localhost:5001` | 2 min | **C13** | ✅ Experiment tracking<br>✅ Model versioning<br>✅ Métriques: accuracy 94.46% |
| **5** | **Prometheus** | Navigateur Web | `http://localhost:9091` | 1 min | **C11** | ✅ Targets UP<br>✅ Métriques collectées |
| **6** | **Base PostgreSQL** | Via Swagger API | `/pokemon`, `/types`, `/moves` | 3 min | **E1.3** | ✅ 11 tables (normalisées 3NF)<br>✅ 188 Pokémon, 226 moves<br>✅ Relations FK |
| **7** | **ETL Pipeline** | Logs Docker | `docker logs letsgo_etl` | 3 min | **E1.1, E1.2** | ✅ 3 sources (CSV, API, scraping)<br>✅ Nettoyage et validation<br>✅ 5 étapes automatisées |
| **8** | **ML Training** | Logs + Notebooks | `docker logs letsgo_ml` | 4 min | **C12** | ✅ 898k combats simulés<br>✅ XGBoost optimisé<br>✅ GridSearch hyperparams |
| **9** | **Drift Detection** | Rapports HTML | `api_pokemon/monitoring/reports/` | 2 min | **C11** | ✅ Evidently AI<br>✅ Data drift analysis<br>✅ Statistical tests |
| **10** | **CI/CD GitHub** | GitHub Actions | `github.com/.../actions` | 3 min | **C13** | ✅ 4 workflows<br>✅ 252 tests, 82% coverage<br>✅ Auto-deployment |
| **11** | **Notebooks Jupyter** | VSCode / Jupyter | `notebooks/*.ipynb` | 2 min | **E1.4** | ✅ Exploration données<br>✅ Feature engineering<br>✅ Visualisations |
| **12** | **Documentation** | Markdown | `README.md`, `docs/` | 3 min | **E1.5** | ✅ Guide complet<br>✅ Diagrammes architecture<br>✅ API documentation |

**TOTAL: 33 minutes** (idéal pour 30-45 min avec Q&A)

---

## 🚀 Quick Start Demo (1 commande)

```bash
# Lance automatiquement toute la démo (ouvre 5 onglets navigateur)
python scripts/demo_certification.py --generate-metrics
```

**Résultat:**
- ✅ Vérifie que tous les services sont UP
- ✅ Ouvre 5 onglets navigateur (Streamlit, Swagger, Grafana, MLflow, Prometheus)
- ✅ Lance génération métriques en arrière-plan
- ✅ Affiche guide de démonstration complet
- ✅ Checklist avant démo

---

## 📋 Checklist Pré-Démonstration (5 min)

### 1. Démarrer la Stack

```bash
# Démarrer tous les services Docker (5 min première fois, 30s ensuite)
python scripts/start_docker_stack.py
```

**Vérifier:**
- [ ] ✅ PostgreSQL UP (port 5432)
- [ ] ✅ API UP (port 8080)
- [ ] ✅ Streamlit UP (port 8502)
- [ ] ✅ Grafana UP (port 3001)
- [ ] ✅ Prometheus UP (port 9091)
- [ ] ✅ MLflow UP (port 5001)

### 2. Valider les Services

```bash
# Valider tous les health checks (30s)
python scripts/validate_docker_stack.py --verbose
```

**Résultat attendu:**
```
✅ Tous les services sont opérationnels!
6/6 endpoints fonctionnels
2/2 targets UP
```

### 3. Générer Métriques (Optionnel)

```bash
# Générer trafic pour dashboards Grafana (5 min en arrière-plan)
python scripts/generate_monitoring_data.py --mode realistic --duration 5 &
```

**Effet:**
- Grafana dashboards remplis avec métriques réalistes
- Latences, throughput, error rates visibles

### 4. Préparer Navigateur

**Ouvrir 5 onglets:**
1. http://localhost:8502 (Streamlit)
2. http://localhost:8080/docs (Swagger)
3. http://localhost:3001 (Grafana)
4. http://localhost:5001 (MLflow)
5. http://localhost:9091 (Prometheus)

**OU utiliser le script automatique:**
```bash
python scripts/demo_certification.py
```

### 5. Préparer Code Editor

```bash
# Ouvrir notebooks dans VSCode
code notebooks/
```

**Notebooks à avoir ouverts:**
- `03_training_evaluation.ipynb` (graphiques ML)
- `01_exploration.ipynb` (analyse données)

---

## 🎬 Scénario de Démonstration (30 min)

### PHASE 1: Interfaces Web (12 min)

#### 1.1 Streamlit - Application Finale (4 min)

**Onglet:** http://localhost:8502

**Script:**
> "Je vais vous montrer l'application finale utilisable par un dresseur Pokémon."

**Actions:**
1. **Page Accueil** (30s)
   - Montrer vue d'ensemble
   - Statistiques: 188 Pokémon, 94.46% accuracy

2. **Page "Combat et Prédiction"** (2 min) ⭐ **STAR DEMO**
   - Sélectionner Pikachu (#25)
   - Sélectionner Bulbizarre (#1)
   - Choisir 4 capacités
   - Cliquer "Prédire"
   - **Montrer:** Recommandation ML + probabilités

3. **Page "Détails Pokémon"** (1 min)
   - Rechercher Dracaufeu
   - Afficher stats, types, faiblesses

4. **Page "Types et Affinités"** (30s)
   - Matrice 18x18

**Phrase clé:**
> "Cette interface valide la **compétence C10** (intégration applicative frontend/backend) et consomme l'API REST avec ML intégré."

---

#### 1.2 Swagger API - Tests Interactifs (3 min)

**Onglet:** http://localhost:8080/docs

**Script:**
> "Voici l'API REST production-ready qui expose le modèle ML."

**Actions:**
1. **Documentation** (30s)
   - Montrer 5 groupes endpoints
   - OpenAPI 3.0 complet

2. **Test `/predict/best-move`** (2 min) ⭐ **CORE ML**
   - Try it out
   - Body JSON:
   ```json
   {
     "pokemon_a_id": 25,
     "pokemon_b_id": 1,
     "available_moves": ["Fatal-Foudre", "Vive-Attaque"]
   }
   ```
   - Execute
   - **Montrer:** Réponse < 500ms, probabilités

3. **Test `/pokemon`** (30s)
   - GET /pokemon?limit=5
   - Montrer pagination, filtres

**Phrase clé:**
> "Cette API valide la **compétence C9** (API REST avec intégration IA) et **C12** (optimisation < 500ms)."

---

#### 1.3 Grafana - Monitoring Temps Réel (3 min)

**Onglet:** http://localhost:3001

**Script:**
> "Le monitoring temps réel est essentiel pour la production."

**Actions:**
1. **Dashboard "API Performance"** (2 min) ⭐ **DASHBOARD PRINCIPAL**
   - Navigate: Dashboards → API Performance
   - **Montrer:**
     - API Status: UP
     - Request Rate by Endpoint
     - P95 Latency: < 500ms
     - Error Rate: < 1%

2. **Dashboard "Model Performance"** (1 min)
   - Predictions per Minute
   - Model Accuracy graph
   - Feature Importance

**Phrase clé:**
> "Ce monitoring valide la **compétence C11** (monitoring IA en production) avec Prometheus et Grafana."

---

#### 1.4 MLflow - Model Registry (2 min)

**Onglet:** http://localhost:5001

**Script:**
> "MLflow assure le versioning et le tracking des modèles."

**Actions:**
1. **Experiments** (1 min)
   - Navigate: Experiments → battle_winner_v2
   - Montrer runs avec métriques
   - Comparer 2 runs

2. **Models** (1 min)
   - Navigate: Models
   - Montrer versions (v1, v2, v3)
   - Stage: Production

**Phrase clé:**
> "Ce registry valide la **compétence C13** (MLOps avec versioning et tracking)."

---

#### 1.5 Prometheus - Métriques Brutes (1 min)

**Onglet:** http://localhost:9091

**Actions:**
- Navigate: Status → Targets
- Montrer `api` target: UP
- Scrape interval: 15s

**Phrase clé:**
> "Prometheus collecte automatiquement les métriques toutes les 15 secondes."

---

### PHASE 2: Composants Backend (10 min)

#### 2.1 PostgreSQL via API (3 min)

**Retour Swagger:** http://localhost:8080/docs

**Script:**
> "La base de données est accessible via l'API. Montrons la structure."

**Actions:**
1. `GET /pokemon?limit=5` (1 min)
   - Montrer: id, name, stats, types

2. `GET /types` (30s)
   - 18 types avec couleurs

3. `GET /pokemon/25/moves` (1 min)
   - Capacités de Pikachu

4. `GET /pokemon/25/types` (30s)
   - Types + faiblesses calculées

**Phrase clé:**
> "Cette base valide **E1.3** (structuration BDD 11 tables normalisées 3NF) et **E1.2** (données nettoyées)."

---

#### 2.2 ETL Pipeline - Logs (3 min)

**Terminal:**
```bash
docker logs letsgo_etl --tail 200
```

**Script:**
> "L'ETL collecte et nettoie les données de 3 sources."

**Points à montrer:**
- [1/5] Init DB: 11 tables créées
- [2/5] CSV: 151 Pokémon chargés
- [3/5] PokéAPI: 188 Pokémon (formes Alola)
- [4/5] Pokepedia: 324 règles de types
- [5/5] Validation: 0 données manquantes

**Phrase clé:**
> "Ce pipeline valide **E1.1** (collecte multi-sources) et **E1.2** (nettoyage et validation)."

---

#### 2.3 ML Training - Logs + Notebooks (4 min)

**Terminal:**
```bash
docker logs letsgo_ml --tail 300
```

**Points à montrer:**
- [1/4] Dataset: 898,472 combats, 133 features
- [2/4] Training: GridSearch 12 combinations
- [3/4] Evaluation: 94.46% accuracy
- [4/4] Export: model.pkl + metadata

**Puis VSCode:**
```bash
code notebooks/03_training_evaluation.ipynb
```

**Montrer graphiques:**
- Confusion matrix
- ROC curves
- Feature importance

**Phrase clé:**
> "Ce pipeline valide **C12** (optimisation IA avec GridSearch) et **E1.4** (exploitation données avec notebooks)."

---

### PHASE 3: Technique Avancée (8 min)

#### 3.1 Drift Detection (2 min)

**Terminal:**
```bash
ls -lh api_pokemon/monitoring/reports/
```

**Ouvrir rapport HTML:**
```bash
xdg-open api_pokemon/monitoring/reports/drift_dashboard_*.html
```

**Montrer:**
- Data Drift Dashboard
- Feature drift details
- Statistical tests

**Phrase clé:**
> "Evidently AI détecte le drift des données en production (**C11**)."

---

#### 3.2 GitHub Actions (3 min)

**Navigateur:** https://github.com/YOUR_REPO/actions

**Montrer workflows:**
1. **Run Tests** (1 min)
   - 252 tests passed
   - 82% coverage

2. **Build Docker** (1 min)
   - 5 images buildées
   - Multi-stage optimisé

3. **ML Training** (1 min)
   - Dataset → Train → Register MLflow

**Phrase clé:**
> "Le CI/CD valide **C13** (MLOps avec tests automatisés et déploiement)."

---

#### 3.3 Documentation (3 min)

**VSCode:**
```bash
code README.md
```

**Montrer sections:**
- Architecture diagram (ASCII art)
- Quick Start
- API documentation
- Monitoring stack

**Phrase clé:**
> "La documentation complète valide **E1.5** (documenter le processus)."

---

## 📊 Mapping Compétences → Preuves Visuelles

| Compétence | Preuve Visuelle | Outil | Temps |
|------------|-----------------|-------|-------|
| **E1.1 - Collecte** | 3 sources (CSV, PokéAPI, Pokepedia) | `docker logs letsgo_etl` | 1 min |
| **E1.2 - Nettoyage** | Validation, normalisation | Logs ETL + Swagger API | 2 min |
| **E1.3 - BDD** | 11 tables 3NF, relations FK | Swagger `/pokemon`, `/types` | 3 min |
| **E1.4 - Exploitation** | 133 features, visualisations | Notebooks Jupyter | 2 min |
| **E1.5 - Documentation** | README complet, diagrammes | VSCode Markdown | 3 min |
| **C9 - API + IA** | Swagger UI, test endpoints | http://localhost:8080/docs | 3 min |
| **C10 - Interface** | Streamlit 8 pages fonctionnelles | http://localhost:8502 | 4 min |
| **C11 - Monitoring** | Grafana dashboards + Evidently | http://localhost:3001 | 5 min |
| **C12 - Optimisation** | < 500ms, 94.46% accuracy | Logs ML + Notebooks | 4 min |
| **C13 - MLOps** | MLflow + GitHub Actions | http://localhost:5001 | 5 min |

---

## 🎯 Points Forts à Insister

### Top 5 Features à Montrer

1. **Prédiction ML Interactive** (Streamlit)
   - Temps réel < 500ms
   - Recommandation meilleure capacité
   - Probabilités de victoire

2. **API REST Production-Ready** (Swagger)
   - Documentation OpenAPI complète
   - Tests interactifs
   - Authentification API Key

3. **Monitoring Temps Réel** (Grafana)
   - 2 dashboards personnalisés
   - Métriques métier (latency, accuracy)
   - Alerting automatique

4. **MLOps Complet** (MLflow + GitHub Actions)
   - Experiment tracking
   - Model Registry avec versioning
   - CI/CD automatisé (252 tests)

5. **Pipeline ETL Automatisé** (Logs Docker)
   - 3 sources de données
   - Validation et nettoyage
   - 898k combats simulés

---

## 💡 Astuces Présentation

### Phrases d'Accroche

**Début:**
> "Je vais vous présenter PredictionDex, une plateforme MLOps complète qui prédit les combats Pokémon avec 94.46% de précision. Ce projet valide l'intégralité des compétences E1 et E3."

**Transitions:**
- "Maintenant, voyons comment cette interface consomme l'API..."
- "Passons au monitoring temps réel avec Grafana..."
- "Voici le pipeline ETL qui collecte les données..."

**Fin:**
> "En résumé, ce projet démontre une maîtrise complète du cycle MLOps: de la collecte de données (E1) jusqu'à la production avec monitoring (E3)."

### Gestion du Temps

- **Si en avance:** Montrer notebooks Jupyter en détail
- **Si en retard:** Fusionner Prometheus avec Grafana (4 min → 3 min)
- **Si crash:** Avoir screenshots de backup prêts

### Questions Anticipées

**Q: "Pourquoi 94.46% et pas 99%?"**
> "Le modèle est volontairement sous-fitté pour éviter l'overfitting. 94.46% est excellent pour un problème avec 188×188 matchups possibles et incertitude des capacités adverses."

**Q: "Comment gérez-vous le drift?"**
> "Evidently AI compare les prédictions production aux données de référence toutes les heures et génère des rapports HTML avec tests statistiques."

**Q: "Scalabilité?"**
> "L'architecture Docker Compose peut migrer vers Kubernetes. L'API FastAPI supporte 100+ req/s en production. PostgreSQL peut être remplacé par RDS pour haute disponibilité."

---

## ✅ Checklist Post-Démonstration

- [ ] Tous les composants montrés (12/12)
- [ ] Toutes les compétences E1/E3 couvertes (10/10)
- [ ] Temps respecté (30-35 min)
- [ ] Questions jury répondues
- [ ] Documentation disponible (README, docs/)

---

**Dernière mise à jour:** 27 janvier 2026
**Durée totale:** 30-35 minutes + 10 min Q&A
**Taux de réussite:** ✅ 100% validation E1/E3

**🚀 Prêt pour la certification !**
