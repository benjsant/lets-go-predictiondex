# 🎓 CI/CD pour Certification E1/E3

**Date:** 30 janvier 2026  
**Objectif:** Automatiser la validation des compétences E1 et E3 pour la certification RNCP  
**Workflow:** `.github/workflows/certification-e1-e3.yml`

---

## 📋 Vue d'ensemble

Ce workflow CI/CD a été spécialement conçu pour **démontrer et valider automatiquement** toutes les compétences requises pour les épreuves E1 (Collecte et Traitement des Données) et E3 (Intégration IA en Production) de la certification RNCP "Concepteur Développeur d'Applications".

### 🎯 Objectifs du workflow

1. **Automatiser la validation** de chaque compétence E1/E3
2. **Générer un rapport** de certification automatique
3. **Prouver la maîtrise** des technologies et méthodologies
4. **Faciliter la démonstration** lors de la soutenance

---

## 🏗️ Architecture du Workflow

```
certification-e1-e3.yml
│
├── 📦 E1: Data Validation (20 min)
│   ├── E1.1: Collecter les données
│   ├── E1.2: Nettoyer les données
│   ├── E1.3: Structurer la BDD
│   ├── E1.4: Exploiter les données
│   └── E1.5: Documenter le processus
│
├── 🤖 E3: IA Production (70 min)
│   ├── C9: API REST avec IA (15 min)
│   ├── C10: Intégration app (15 min)
│   ├── C11: Monitoring IA (20 min)
│   ├── C12: Optimisation IA (20 min)
│   └── C13: MLOps CI/CD (25 min)
│
├── 🐳 Docker Deployment (30 min) [Optionnel]
│   └── Déploiement complet des services
│
└── 📊 Certification Report
    └── Génération rapport final
```

**Durée totale:** ~90 minutes (sans déploiement Docker)

---

## 🚀 Utilisation

### 1️⃣ Déclenchement Automatique

Le workflow se déclenche automatiquement lors de :

```yaml
# Push sur les branches principales
git push origin main
git push origin develop
git push origin certification

# Pull Request vers main
```

### 2️⃣ Déclenchement Manuel

Depuis GitHub Actions, vous pouvez déclencher manuellement avec options :

1. Aller sur **Actions** → **Certification E1/E3 - Validation Complète**
2. Cliquer sur **Run workflow**
3. Choisir les options :
   - ✅ `run_full_pipeline`: Exécuter le pipeline ML complet
   - ✅ `deploy_services`: Déployer tous les services Docker

```bash
# Depuis la ligne de commande (avec GitHub CLI)
gh workflow run certification-e1-e3.yml \
  --ref main \
  -f run_full_pipeline=true \
  -f deploy_services=false
```

### 3️⃣ Test Local (avant push)

Tester le workflow localement avant de pousser sur GitHub :

```bash
# Installer act (GitHub Actions local runner)
brew install act  # macOS
# ou
sudo apt install act  # Linux

# Exécuter le workflow localement
act -j e1-data-validation

# Exécuter job spécifique
act -j e3-c9-api-rest
act -j e3-c13-mlops
```

---

## 📊 Détail des Jobs

### 🗂️ Job 1: E1 - Data Validation

**Durée:** ~20 minutes  
**Objectif:** Valider les 5 compétences de collecte et traitement des données

#### Compétences validées

| ID | Compétence | Tests exécutés | Preuve |
|----|-----------|----------------|--------|
| **E1.1** | Collecter les données | `test_pokemon_fetcher`, `test_pokepedia_scraper` | 3 sources de données |
| **E1.2** | Nettoyer les données | `test_data_cleaning`, `test_normalization` | Normalisation 3NF |
| **E1.3** | Structurer BDD | `tests/core/db/` | 11 tables PostgreSQL |
| **E1.4** | Exploiter les données | `test_features.py` | 133 features calculées |
| **E1.5** | Documenter | Vérification fichiers docs | README + diagrammes |

#### Outputs
- ✅ Rapport de validation E1
- 📄 Coverage XML
- 📦 Artifacts conservés 30 jours

---

### 🤖 Job 2: E3-C9 - API REST avec IA

**Durée:** ~15 minutes  
**Objectif:** Valider l'exposition d'un modèle IA via API REST

#### Compétences validées

✅ **FastAPI** framework moderne et performant  
✅ **Endpoint `/predict/battle`** avec XGBoost  
✅ **Validation Pydantic** des entrées/sorties  
✅ **Documentation Swagger** automatique (`/docs`)  
✅ **Error handling** avec HTTPException  
✅ **Logging structuré** pour monitoring  

#### Tests exécutés
```bash
pytest tests/api/test_prediction_api.py -v
pytest tests/api/ --cov=api_pokemon
```

#### Résultat attendu
- ✅ Tous les tests API passent
- ✅ Coverage API ≥ 75%
- ✅ Model chargé avec succès
- ✅ Prédictions cohérentes

---

### 📱 Job 3: E3-C10 - Intégration Application

**Durée:** ~15 minutes  
**Objectif:** Valider l'intégration de l'API dans une interface utilisateur

#### Compétences validées

✅ **Interface Streamlit** 8 pages fonctionnelles  
✅ **Client API HTTP** (`services/api_client.py`)  
✅ **Pages interactives** : Compare, Combat, Quiz, etc.  
✅ **Gestion d'erreurs** côté client  
✅ **Accessibilité** features Streamlit built-in  

#### Structure validée
```
interface/
├── app.py                 # Homepage
├── pages/
│   ├── 2_Compare.py       # Prédiction bataille
│   ├── 5_Combat_Classique.py
│   └── 4_Quiz_Types.py
├── services/
│   ├── api_client.py      # HTTP client
│   └── prediction_service.py
└── utils/
```

---

### 📊 Job 4: E3-C11 - Monitoring du Modèle

**Durée:** ~20 minutes  
**Objectif:** Valider le monitoring complet du modèle en production

#### Stack de monitoring

| Outil | Usage | Métriques |
|-------|-------|-----------|
| **Prometheus** | Collecte métriques temps réel | `prediction_requests_total`, `prediction_duration_seconds` |
| **Grafana** | Visualisation dashboards | Dashboards (API, Model, System) |
| **Production Data Collector** | Collecte features production | Sauvegarde parquet pour analyse future |

✅ **Métriques custom Prometheus**  
✅ **Dashboards Grafana** avec alertes  
✅ **Production data collector** pour analyse future  
✅ **Sauvegarde parquet** des features production  
✅ **MLflow tracking** des expériences  

#### Code vérifié
```python
# api_pokemon/monitoring/drift_detection.py
class DriftDetector:
    """Production data collector for future analysis"""
    def add_prediction(...)  # Buffer predictions
    def save_production_data(...)  # Save to parquet

# api_pokemon/monitoring/metrics.py  
# Prometheus metrics
model_predictions_total = Counter(...)
model_prediction_duration_seconds = Histogram(...)
model_confidence_score = Histogram(...)
```

---

### ⚡ Job 5: E3-C12 - Optimisation du Modèle

**Durée:** ~20 minutes  
**Objectif:** Valider les optimisations de performance du modèle

#### Optimisations validées

| Aspect | Technique | Gain |
|--------|-----------|------|
| **Algorithme** | XGBoost (CPU optimisé) | 88.23% accuracy |
| **Paramètres** | `tree_method='hist'` | -60% temps training |
| **Compression** | Pickle protocol 5 | Modèle 30MB (vs 50MB) |
| **Inférence** | Batch processing | ~50ms/prédiction |
| **Features** | 133 features sélectionnées | Balance accuracy/speed |

#### Tests de performance
```bash
pytest tests/ml/test_model_inference.py -v
# Valide:
# - Temps inférence < 100ms
# - Accuracy ≥ 88%
# - Taille modèle < 50MB
```

#### Métriques cibles
- ✅ **Accuracy:** ≥ 88%
- ✅ **Inférence:** < 100ms
- ✅ **Taille:** < 50MB
- ✅ **Training:** < 10min

---

### 🔄 Job 6: E3-C13 - MLOps et CI/CD

**Durée:** ~25 minutes  
**Objectif:** Valider la chaîne complète MLOps et CI/CD

#### Composants MLOps

**1. Pipeline ML Automatisé**
```bash
python machine_learning/run_machine_learning.py --mode=all
```
- ✅ Dataset preparation
- ✅ Feature engineering
- ✅ Model training
- ✅ Model evaluation
- ✅ Model export
- ✅ Versioning automatique

**2. CI/CD GitHub Actions**

7 workflows configurés :
1. `certification-e1-e3.yml` ← **Ce workflow**
2. `tests.yml` - Tests unitaires
3. `docker-build.yml` - Build images
4. `ml-pipeline.yml` - Pipeline ML
5. `lint.yml` - Qualité code
6. `complete-tests.yml` - Tests intégration
7. `monitoring-validation.yml` - Validation monitoring

**3. MLflow (Optionnel)**
- Model Registry
- Experiment tracking
- Metrics logging
- Auto-promotion models

**4. Docker Multi-Services**
```yaml
services:
  - db (PostgreSQL)
  - api (FastAPI)
  - ml (ML service)
  - mlflow (Tracking server)
  - streamlit (Interface)
  - prometheus (Monitoring)
  - grafana (Dashboards)
```

#### Tests MLOps
```bash
pytest tests/ml/ -v --cov=machine_learning
# Valide:
# - Pipeline ML complet
# - Versioning models
# - Metadata tracking
# - Artifacts générés
```

---

### 🐳 Job 7: Docker Deployment (Optionnel)

**Durée:** ~30 minutes  
**Condition:** Manuel (`deploy_services=true`) ou branch `main`

#### Services déployés

1. **PostgreSQL** - Base de données
2. **API FastAPI** - Service prédiction
3. **MLflow** - Tracking server
4. **Streamlit** - Interface utilisateur
5. **Prometheus** - Collecte métriques
6. **Grafana** - Dashboards
7. **pgAdmin** - Admin DB

#### Health checks automatiques
```bash
# PostgreSQL
docker compose exec -T db pg_isready

# API
curl -f http://localhost:8080/health

# MLflow
curl -f http://localhost:5001/health

# Prometheus
curl -f http://localhost:9091/-/healthy

# Grafana
curl -f http://localhost:3001/api/health
```

---

### 📋 Job 8: Certification Report

**Durée:** ~2 minutes  
**Objectif:** Générer un rapport final de certification

#### Contenu du rapport

```markdown
# 🎓 RAPPORT DE CERTIFICATION E1/E3

## 📊 BLOC E1: Collecte et Traitement des Données
| Compétence | Statut | Preuves |
| E1.1 - Collecter données | ✅ VALIDÉ | 3 sources |
| E1.2 - Nettoyer données | ✅ VALIDÉ | Normalisation 3NF |
| E1.3 - Structurer BDD | ✅ VALIDÉ | PostgreSQL 11 tables |
| E1.4 - Exploiter données | ✅ VALIDÉ | 133 features |
| E1.5 - Documenter processus | ✅ VALIDÉ | README complet |

## 🤖 BLOC E3: Intégration IA en Production
| Compétence | Statut | Preuves |
| C9 - API REST avec IA | ✅ VALIDÉ | FastAPI + XGBoost |
| C10 - Intégration app | ✅ VALIDÉ | Streamlit 8 pages |
| C11 - Monitoring IA | ✅ VALIDÉ | Prometheus + Grafana + Data Collector |
| C12 - Optimiser IA | ✅ VALIDÉ | XGBoost optimisé |
| C13 - MLOps CI/CD | ✅ VALIDÉ | 7 workflows GitHub |

## 🎯 Résumé Global
- E1: 5/5 compétences validées ✅
- E3: 5/5 compétences validées ✅
- Score: 10/10 = 100% ✅

**Verdict:** ✅ PROJET VALIDÉ POUR CERTIFICATION E1/E3
```

#### Outputs
- 📄 `certification_report.md` (conservé 90 jours)
- 💬 Commentaire automatique sur PR
- 📊 Résumé dans GitHub Actions

---

## 📈 Métriques de Succès

### Critères de validation

| Critère | Cible | Actuel | Statut |
|---------|-------|--------|--------|
| **Tests unitaires** | ≥ 200 | 252+ | ✅ |
| **Coverage** | ≥ 80% | 82% | ✅ |
| **Model accuracy** | ≥ 85% | 88.23% | ✅ |
| **Temps inférence** | < 100ms | ~50ms | ✅ |
| **Workflows CI/CD** | ≥ 5 | 7 | ✅ |
| **Services Docker** | ≥ 4 | 7 | ✅ |
| **Documentation** | Complète | 10+ docs | ✅ |

### Temps d'exécution

```
┌─────────────────────────────┬──────────┐
│ Job                         │ Durée    │
├─────────────────────────────┼──────────┤
│ E1 Data Validation          │ ~20 min  │
│ E3-C9 API REST              │ ~15 min  │
│ E3-C10 Integration          │ ~15 min  │
│ E3-C11 Monitoring           │ ~20 min  │
│ E3-C12 Optimization         │ ~20 min  │
│ E3-C13 MLOps                │ ~25 min  │
│ Docker Deployment (opt.)    │ ~30 min  │
│ Certification Report        │ ~2 min   │
├─────────────────────────────┼──────────┤
│ TOTAL (sans Docker)         │ ~117 min │
│ TOTAL (avec Docker)         │ ~147 min │
└─────────────────────────────┴──────────┘
```

**Note:** Les jobs E3 s'exécutent en séquence car ils dépendent les uns des autres.

---

## 🎯 Utilisation pour la Soutenance

### 1. Avant la soutenance

```bash
# 1. Pousser sur la branche certification
git checkout -b certification
git add .
git commit -m "feat: validation certification E1/E3"
git push origin certification

# 2. Vérifier que le workflow passe
# → Aller sur GitHub Actions
# → Vérifier tous les jobs verts ✅

# 3. Télécharger le rapport de certification
# → Actions → Dernier run → Artifacts → certification-report
```

### 2. Pendant la soutenance

**Démonstration en direct:**

1. **Montrer le workflow GitHub Actions**
   - Naviguer vers **Actions** → **Certification E1/E3**
   - Montrer l'exécution récente (tous jobs verts ✅)
   - Expliquer l'architecture des jobs

2. **Présenter le rapport de certification**
   - Ouvrir `certification_report.md`
   - Montrer les 10/10 compétences validées
   - Détailler les métriques techniques

3. **Démontrer chaque compétence**
   - **E1:** Montrer le code ETL, la BDD, les features
   - **E3-C9:** Tester l'API en direct
   - **E3-C10:** Montrer l'interface Streamlit
   - **E3-C11:** Ouvrir Grafana dashboards
   - **E3-C12:** Montrer les métriques de performance
   - **E3-C13:** Expliquer le pipeline MLOps

4. **Lancer un workflow en direct** (si temps)
   ```bash
   # Déclencher manuellement
   gh workflow run certification-e1-e3.yml \
     --ref certification \
     -f run_full_pipeline=false
   
   # Montrer l'exécution en temps réel
   ```

### 3. Questions fréquentes du jury

**Q: Pourquoi 7 workflows au lieu d'un seul ?**
> R: Séparation des responsabilités (SoC). Chaque workflow a un objectif spécifique :
> - Tests rapides sur chaque push (`tests.yml`)
> - Build Docker optimisé avec cache (`docker-build.yml`)
> - Validation complète pour certification (`certification-e1-e3.yml`)

**Q: Comment garantissez-vous la reproductibilité ?**
> R: 
> - Versions Python/packages fixées dans `requirements.txt`
> - Services PostgreSQL via containers (versions fixes)
> - Cache pip/Docker pour cohérence
> - Seeds aléatoires fixés dans le code ML

**Q: Que se passe-t-il si un test échoue ?**
> R:
> - Le workflow s'arrête au premier job échoué
> - Les logs détaillés sont disponibles dans GitHub Actions
> - Les artifacts sont conservés pour analyse
> - Le rapport de certification indique l'échec

**Q: Comment gérez-vous les secrets (API keys, passwords) ?**
> R:
> - GitHub Secrets pour les credentials sensibles
> - Variables d'environnement pour configuration
> - Fichier `.env.example` pour documentation
> - Jamais de secrets hardcodés dans le code

---

## 🔒 Sécurité et Bonnes Pratiques

### Secrets GitHub

Configurer dans **Settings** → **Secrets** → **Actions** :

```bash
POSTGRES_PASSWORD=***
API_KEYS=***
MLFLOW_TRACKING_URI=***
CODECOV_TOKEN=***  # Optionnel
```

### Variables d'environnement

```yaml
env:
  POSTGRES_HOST: localhost
  POSTGRES_PORT: 5432
  POSTGRES_DB: letsgo_test
  PYTHONPATH: ${{ github.workspace }}
  DISABLE_MLFLOW_TRACKING: true
```

### Permissions minimales

```yaml
permissions:
  contents: read
  pull-requests: write  # Pour commenter
  actions: read
```

---

## 🐛 Dépannage

### Problème: Job timeout

**Symptôme:** Job dépasse 30 minutes

**Solution:**
```yaml
# Augmenter le timeout
timeout-minutes: 45
```

### Problème: PostgreSQL ne démarre pas

**Symptôme:** `pg_isready` échoue

**Solution:**
```yaml
# Augmenter health check retries
options: >-
  --health-retries 10
  --health-interval 5s
```

### Problème: Dépendances pip échouent

**Symptôme:** `pip install` error

**Solution:**
```bash
# Mettre à jour requirements.txt
pip freeze > requirements.txt

# Ou spécifier versions compatibles
pip install "package>=1.0,<2.0"
```

### Problème: Tests flaky (instables)

**Symptôme:** Tests passent/échouent aléatoirement

**Solution:**
```python
# Fixer les seeds aléatoires
import random
import numpy as np

random.seed(42)
np.random.seed(42)
```

---

## 📚 Ressources Complémentaires

### Documentation interne

- [CERTIFICATION_E1_E3_VALIDATION.md](../CERTIFICATION_E1_E3_VALIDATION.md) - Validation finale
- [E1_DOCUMENTATION.md](E1_DOCUMENTATION.md) - Documentation E1 complète
- [E3_COMPETENCES_STATUS.md](E3_COMPETENCES_STATUS.md) - Statut compétences E3
- [CI_CD_SETUP.md](../deployment/CI_CD_SETUP.md) - Configuration CI/CD détaillée

### Documentation externe

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

## ✅ Checklist Certification

Avant la soutenance, vérifier :

### Code et Tests
- [ ] Tous les tests passent localement (`pytest`)
- [ ] Coverage ≥ 80% (`pytest --cov`)
- [ ] Linting OK (`black`, `flake8`, `pylint`)
- [ ] Pas de secrets hardcodés
- [ ] Documentation à jour

### CI/CD
- [ ] Workflow `certification-e1-e3.yml` passe ✅
- [ ] Tous les jobs verts dans GitHub Actions
- [ ] Rapport de certification généré
- [ ] Artifacts disponibles

### Infrastructure
- [ ] Docker Compose démarre sans erreur
- [ ] Tous les services accessible (health checks OK)
- [ ] Grafana dashboards fonctionnels
- [ ] API répond correctement

### Documentation
- [ ] README.md complet
- [ ] Diagrammes à jour (MCD, MLD, architecture)
- [ ] Guides d'utilisation clairs
- [ ] Commentaires code compréhensibles

### Présentation
- [ ] Slides préparés
- [ ] Démo locale testée
- [ ] Workflow GitHub Actions visible
- [ ] Rapport de certification imprimé
- [ ] Questions du jury anticipées

---

## 🎓 Conclusion

Ce workflow CI/CD **certification-e1-e3.yml** est conçu pour :

1. ✅ **Valider automatiquement** les 10 compétences E1/E3
2. ✅ **Générer un rapport** de certification complet
3. ✅ **Faciliter la démonstration** lors de la soutenance
4. ✅ **Garantir la qualité** du code et de l'infrastructure

**Résultat:** Un projet professionnel, testé, documenté et prêt pour la certification RNCP.

---

**Auteur:** Équipe PredictionDex  
**Date:** 30 janvier 2026  
**Version:** 1.0  
**Status:** ✅ Production Ready
