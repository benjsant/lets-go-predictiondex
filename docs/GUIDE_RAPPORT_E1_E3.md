# 📝 Guide de Rédaction du Rapport Projet E1 + E3

> **Certification RNCP37827 "Développeur en Intelligence Artificielle"**  
> Projet : **PredictionDex - Prédicteur de Combats Pokémon Let's Go**

---

## 📌 Exigences Officielles (Règlement Simplon)

### Structure des évaluations

| Évaluation | Bloc | Compétences | Durée soutenance |
|------------|------|-------------|------------------|
| **E1** | Bloc 1 (RNCP37827BC01) | C1-C5 | 15 min présentation + 10 min Q/R |
| E2 | Bloc 2 (RNCP37827BC02) | C6-C8 | 15 min |
| **E3** | Bloc 2 (RNCP37827BC02) | C9-C13 | 20 min + démonstration |
| E4 | Bloc 3 (RNCP37827BC03) | C14-C19 | 20 min + démo |
| E5 | Bloc 3 (RNCP37827BC03) | C20-C21 | 10 min |

> 💡 **Point important** : *"Un projet unique peut être présenté pour les évaluations E1, E3 et E4, agrégeant ces modalités."* — C'est exactement ce que permet PredictionDex !

### Ce que le jury attend

**Pour E1 (Mise en situation 1)** :
- Présenter le **flux automatisé de collecte** depuis différentes sources
- Présenter les **requêtes de nettoyage et mise en forme**
- Présenter la **création de la base de données**
- Présenter l'**exposition des données via API**

**Pour E3 (Mise en situation 2)** :
- Présenter le développement d'une **API encapsulant un modèle d'IA**
- Présenter les **étapes d'intégration** dans l'application
- Présenter le **monitorage et les tests** du modèle
- Présenter la **chaîne de livraison continue**
- **Effectuer une démonstration** des différents composants

---

## 📋 Structure Recommandée du Rapport Combiné

Le rapport combiné E1+E3 doit démontrer la maîtrise de l'ensemble des compétences des deux blocs tout en présentant un projet cohérent de bout en bout.

---

## 🎯 Page de Garde

```
RAPPORT DE PROJET
Certification RNCP Concepteur Développeur en Intelligence Artificielle

Blocs de compétences : E1 (API & Base de données) + E3 (Mise à disposition de l'IA)

Projet : PredictionDex
Prédicteur de résultats de combats Pokémon Let's Go

Candidat : [Votre nom]
Date : [Date de rendu]
Organisme de formation : Simplon
```

---

## 📖 Table des Matières Suggérée

```
1. Introduction et Contexte du Projet
   1.1 Présentation du projet
   1.2 Objectifs métier
   1.3 Périmètre technique
   1.4 Planning et méthodologie

2. BLOC E1 : Collecte et Gestion des Données
   2.1 Architecture des données (C1)
   2.2 Pipeline ETL et collecte (C2)
   2.3 Modélisation de la base de données (C3)
   2.4 Développement de l'API REST (C4)
   2.5 Intégration et déploiement (C5)

3. BLOC E3 : Mise à Disposition de l'IA
   3.1 Exposition des modèles ML via API (C9)
   3.2 Intégration dans l'application (C10)
   3.3 Monitoring et détection de dérives (C11)
   3.4 Tests et validation (C12)
   3.5 Pipeline CI/CD (C13)

4. Synthèse et Perspectives
   4.1 Bilan technique
   4.2 Difficultés rencontrées et solutions
   4.3 Axes d'amélioration
   4.4 Conclusion

Annexes
```

---

## 📄 Détail des Sections

### 1. Introduction et Contexte du Projet (2-3 pages)

#### 1.1 Présentation du projet
**Contenu pour PredictionDex :**
- Contexte : Prédiction de résultats de combats Pokémon Let's Go Pikachu/Evoli
- Problématique : Comment prédire le vainqueur d'un combat basé sur les statistiques des Pokémon ?
- Solution : Plateforme MLOps complète intégrant collecte de données, ML et interface utilisateur

#### 1.2 Objectifs métier
- Permettre aux joueurs de simuler des combats
- Analyser les forces/faiblesses des Pokémon
- Fournir des recommandations de stratégie

#### 1.3 Périmètre technique
**Stack technologique :**
| Composant | Technologies |
|-----------|-------------|
| Backend | Python 3.11, FastAPI 0.109 |
| Base de données | PostgreSQL 15, SQLAlchemy 2.0 |
| Machine Learning | XGBoost 2.0, scikit-learn 1.4 |
| MLOps | MLflow 2.18, Prometheus, Grafana |
| Frontend | Streamlit 1.39 |
| DevOps | Docker Compose, GitHub Actions |

#### 1.4 Planning et méthodologie
- Méthodologie agile
- Sprints de développement
- Revue de code et tests continus

---

### 2. BLOC E1 : Collecte et Gestion des Données (8-10 pages)

#### 2.1 Architecture des données (C1 - Recueillir les besoins)

**À démontrer :**
- Analyse du besoin métier
- Identification des sources de données
- Volumétrie estimée

**Contenu PredictionDex :**
```
Sources de données identifiées :
├── API PokéAPI (données officielles Pokémon)
├── Fichiers CSV (datasets de combats)
└── Scraping Pokepedia (données françaises)

Volume : ~150 Pokémon, ~165 attaques, milliers de combats simulés
```

**Livrables à inclure :**
- Schéma des flux de données
- Matrice des sources vs besoins
- Screenshot de l'analyse des données brutes

---

#### 2.2 Pipeline ETL et collecte (C2 - Collecter les données)

**À démontrer :**
- Scripts de collecte automatisés
- Transformation des données
- Qualité et validation

**Contenu PredictionDex :**

```python
# Exemple de code ETL à inclure (simplifié)
# etl_pokemon/pipeline.py

class ETLPipeline:
    """Pipeline complet d'extraction, transformation, chargement"""
    
    def extract_from_pokeapi(self) -> List[dict]:
        """Extraction depuis PokéAPI"""
        ...
    
    def transform_pokemon_data(self, raw_data: dict) -> Pokemon:
        """Transformation et normalisation"""
        ...
    
    def load_to_database(self, pokemon: Pokemon) -> None:
        """Chargement en base PostgreSQL"""
        ...
```

**Livrables à inclure :**
- Diagramme du pipeline ETL
- Captures d'écran du scraper
- Logs d'exécution
- Métriques de qualité des données

---

#### 2.3 Modélisation de la base de données (C3 - Modéliser les données)

**À démontrer :**
- Modèle Conceptuel de Données (MCD)
- Modèle Physique de Données (MPD)
- Scripts de création

**Contenu PredictionDex :**

```
Tables principales (11 tables) :
├── pokemons (id, name, hp, attack, defense, ...)
├── moves (id, name, power, accuracy, type_id, ...)
├── types (id, name)
├── pokemon_moves (pokemon_id, move_id)
├── pokemon_types (pokemon_id, type_id)
├── type_effectiveness (attacking_type_id, defending_type_id, multiplier)
├── evolutions (pokemon_id, evolves_to_id, method)
├── battles (id, pokemon1_id, pokemon2_id, winner_id, scenario)
├── ml_predictions (id, battle_id, predicted_winner, confidence)
├── ml_models (id, name, version, accuracy, created_at)
└── monitoring_metrics (id, timestamp, metric_name, value)
```

**Livrables à inclure :**
- Diagramme MCD (outil : dbdiagram.io, draw.io)
- Diagramme MPD avec relations
- Script SQL de création des tables
- Screenshot pgAdmin/DBeaver

---

#### 2.4 Développement de l'API REST (C4 - Développer une API)

**À démontrer :**
- Architecture de l'API
- Endpoints CRUD
- Documentation OpenAPI

**Contenu PredictionDex :**

```yaml
# Endpoints principaux
/api/v1/pokemon:
  GET: Liste des Pokémon
  GET /{id}: Détail d'un Pokémon
  POST: Création (admin)
  PUT /{id}: Mise à jour (admin)
  DELETE /{id}: Suppression (admin)

/api/v1/moves:
  GET: Liste des attaques
  GET /{id}: Détail d'une attaque

/api/v1/types:
  GET: Liste des types
  GET /effectiveness: Matrice d'efficacité

/api/v1/battle/predict:
  POST: Prédiction de combat (appel ML)
```

**Livrables à inclure :**
- Capture Swagger UI (/docs)
- Exemples de requêtes/réponses (Postman/curl)
- Code des routes principales
- Tests unitaires des endpoints

---

#### 2.5 Intégration et déploiement (C5 - Intégrer une solution)

**À démontrer :**
- Conteneurisation
- Orchestration
- Configuration

**Contenu PredictionDex :**

```yaml
# docker-compose.yml - Services E1
services:
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  api:
    build: 
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    
  pgadmin:
    image: dpage/pgadmin4
    ports:
      - "5050:80"
```

**Livrables à inclure :**
- Architecture Docker (schéma)
- Dockerfile commenté
- Captures des services en exécution
- Logs de déploiement

---

### 3. BLOC E3 : Mise à Disposition de l'IA (8-10 pages)

#### 3.1 Exposition des modèles ML via API (C9 - Développer une API ML)

**À démontrer :**
- Endpoints de prédiction
- Sérialisation du modèle
- Gestion des versions

**Contenu PredictionDex :**

```python
# api_pokemon/routes/prediction_route.py

@router.post("/predict")
async def predict_battle(
    battle: BattleRequest,
    model_version: str = "v2"
) -> PredictionResponse:
    """
    Prédit le vainqueur d'un combat Pokémon.
    
    - Charge le modèle XGBoost depuis MLflow
    - Applique le feature engineering
    - Retourne la prédiction avec confiance
    """
    model = load_model(f"battle_winner_{model_version}")
    features = extract_features(battle)
    prediction = model.predict(features)
    probability = model.predict_proba(features)
    
    return PredictionResponse(
        winner=prediction,
        confidence=probability.max(),
        model_version=model_version
    )
```

**Métriques du modèle v2 :**
| Métrique | Valeur |
|----------|--------|
| Accuracy | 88.23% |
| Precision | 87.8% |
| Recall | 88.5% |
| F1-Score | 88.1% |

**Livrables à inclure :**
- Code de l'endpoint de prédiction
- Format des requêtes/réponses
- Screenshot MLflow (modèles versionnés)
- Comparaison des versions de modèles

---

#### 3.2 Intégration dans l'application (C10 - Intégrer l'IA)

**À démontrer :**
- Interface utilisateur
- Appels API depuis le frontend
- Expérience utilisateur

**Contenu PredictionDex :**

```python
# interface/pages/battle_predictor.py

def display_battle_predictor():
    """Page Streamlit de prédiction de combat"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        pokemon1 = st.selectbox("Pokémon 1", pokemon_list)
        moves1 = st.multiselect("Attaques", get_moves(pokemon1))
    
    with col2:
        pokemon2 = st.selectbox("Pokémon 2", pokemon_list)
        moves2 = st.multiselect("Attaques", get_moves(pokemon2))
    
    if st.button("Prédire le vainqueur"):
        result = call_prediction_api(pokemon1, pokemon2, moves1, moves2)
        display_result_with_animation(result)
```

**Livrables à inclure :**
- Captures d'écran de l'interface Streamlit
- Diagramme de séquence (User → Streamlit → API → ML)
- Code d'intégration
- Démonstration (vidéo ou GIF)

---

#### 3.3 Monitoring et détection de dérives (C11 - Surveiller l'IA)

**À démontrer :**
- Métriques collectées
- Dashboards de monitoring
- Alertes configurées

**Contenu PredictionDex :**

```python
# api_pokemon/monitoring/drift_detection.py

class DriftDetector:
    """Détection de dérive des données et du modèle"""
    
    def detect_data_drift(self, current_data: pd.DataFrame) -> DriftReport:
        """Détecte les dérives statistiques des features"""
        reference = self.load_reference_distribution()
        
        drift_results = {}
        for feature in MONITORED_FEATURES:
            ks_stat, p_value = ks_2samp(
                reference[feature], 
                current_data[feature]
            )
            drift_results[feature] = {
                "is_drifted": p_value < 0.05,
                "ks_statistic": ks_stat,
                "p_value": p_value
            }
        
        return DriftReport(results=drift_results)
    
    def detect_prediction_drift(self) -> bool:
        """Détecte les changements dans la distribution des prédictions"""
        ...
```

**Stack de monitoring :**
```
┌─────────────┐     ┌────────────┐     ┌─────────┐
│   FastAPI   │────▶│ Prometheus │────▶│ Grafana │
│  (métriques)│     │  (stockage)│     │ (visu)  │
└─────────────┘     └────────────┘     └─────────┘
```

**Livrables à inclure :**
- Captures dashboards Grafana
- Configuration Prometheus
- Code de détection de drift
- Exemple d'alerte déclenchée

---

#### 3.4 Tests et validation (C12 - Tester la solution)

**À démontrer :**
- Stratégie de tests
- Couverture de code
- Tests ML spécifiques

**Contenu PredictionDex :**

```
Structure des tests (252 tests, 82% couverture) :
tests/
├── api/           # Tests endpoints FastAPI
│   ├── test_pokemon_route.py
│   ├── test_prediction_route.py
│   └── test_moves_route.py
├── ml/            # Tests modèles ML
│   ├── test_model_training.py
│   ├── test_feature_engineering.py
│   └── test_predictions.py
├── integration/   # Tests bout-en-bout
│   ├── test_full_pipeline.py
│   └── test_api_to_ml.py
├── monitoring/    # Tests monitoring
│   └── test_drift_detection.py
└── conftest.py    # Fixtures partagées
```

**Exemple de test ML :**
```python
# tests/ml/test_predictions.py

def test_model_prediction_accuracy():
    """Vérifie que le modèle maintient une accuracy > 85%"""
    model = load_production_model()
    X_test, y_test = load_test_dataset()
    
    accuracy = model.score(X_test, y_test)
    
    assert accuracy >= 0.85, f"Accuracy {accuracy} < seuil 85%"

def test_prediction_consistency():
    """Vérifie la cohérence des prédictions"""
    # Même entrée = même sortie
    result1 = predict(pokemon1_id=25, pokemon2_id=6)
    result2 = predict(pokemon1_id=25, pokemon2_id=6)
    
    assert result1.winner == result2.winner
```

**Livrables à inclure :**
- Rapport pytest avec couverture
- Captures GitHub Actions (tests CI)
- Code des tests clés
- Matrice de tests (unitaires, intégration, E2E)

---

#### 3.5 Pipeline CI/CD (C13 - Déployer en continu)

**À démontrer :**
- Workflows automatisés
- Déploiement continu
- Gestion des environnements

**Contenu PredictionDex :**

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: docker-compose build
      - name: Push to registry
        run: docker-compose push

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: ./scripts/deploy.sh
```

**Workflows GitHub Actions :**
| Workflow | Déclencheur | Actions |
|----------|-------------|---------|
| CI Tests | Push/PR | Tests + Couverture |
| Build | Merge main | Build Docker |
| Security | Quotidien | Scan vulnérabilités |
| MLflow | Push ML/ | Versioning modèles |
| Docs | Push docs/ | MkDocs deploy |
| Release | Tag | Publication GitHub |

**Livrables à inclure :**
- Captures GitHub Actions (runs réussis)
- Fichiers YAML des workflows
- Schéma du pipeline CI/CD
- Logs de déploiement

---

### 4. Synthèse et Perspectives (2-3 pages)

#### 4.1 Bilan technique
**Points forts du projet :**
- Architecture microservices complète
- Pipeline ML reproductible avec MLflow
- Monitoring temps réel
- Couverture de tests élevée (82%)

#### 4.2 Difficultés rencontrées et solutions

| Problème | Solution |
|----------|----------|
| Données manquantes PokéAPI | Ajout scraping Pokepedia |
| Performance modèle v1 | Feature engineering amélioré v2 |
| Temps de réponse API | Cache Redis + optimisation requêtes |
| Dérive données | Système de monitoring automatique |

#### 4.3 Axes d'amélioration
- Ajouter plus de scénarios de combat
- Implémenter un système de A/B testing
- Déployer sur Kubernetes
- Ajouter l'explication des prédictions (SHAP)

#### 4.4 Conclusion
Synthèse des compétences démontrées et perspectives professionnelles.

---

## 📎 Annexes Recommandées

> Les annexes sont essentielles pour appuyer ton rapport avec des preuves concrètes. Voici les annexes à inclure, classées par priorité.

### Annexes E1 — Gestion des Données

| # | Annexe | Contenu | Priorité |
|---|--------|---------|----------|
| A1 | **Schémas BDD (MCD/MPD)** | Diagrammes entité-relation des tables PostgreSQL (pokemon, types, moves, battles) | ⭐⭐⭐ ESSENTIEL |
| A2 | **Pipeline ETL** | Schéma visuel du flux : Sources → Scraping/API → Nettoyage → PostgreSQL | ⭐⭐⭐ ESSENTIEL |
| A3 | **Documentation API Swagger** | Capture complète de `/docs` (OpenAPI) avec tous les endpoints | ⭐⭐⭐ ESSENTIEL |
| A4 | **Requêtes SQL clés** | 3-5 requêtes importantes commentées (jointures, agrégations) | ⭐⭐ RECOMMANDÉ |
| A5 | **Captures pgAdmin** | Vues des tables peuplées avec données | ⭐⭐ RECOMMANDÉ |
| A6 | **Rétro-planning** | Gantt ou timeline des phases du projet | ⭐ OPTIONNEL |

### Annexes E3 — Mise à Disposition de l'IA

| # | Annexe | Contenu | Priorité |
|---|--------|---------|----------|
| B1 | **Architecture technique** | Schéma des 9 services Docker avec flux de données | ⭐⭐⭐ ESSENTIEL |
| B2 | **Métriques du modèle** | Matrice de confusion, courbe ROC, accuracy 88.23% | ⭐⭐⭐ ESSENTIEL |
| B3 | **Dashboard monitoring** | Captures Grafana + métriques Prometheus | ⭐⭐⭐ ESSENTIEL |
| B4 | **Pipelines CI/CD** | Schéma des 6 workflows GitHub Actions | ⭐⭐⭐ ESSENTIEL |
| B5 | **MLflow tracking** | Captures des expériences et du model registry | ⭐⭐ RECOMMANDÉ |
| B6 | **Rapport de tests** | Résumé pytest (252 tests, 82% coverage) | ⭐⭐ RECOMMANDÉ |
| B7 | **Interface Streamlit** | Captures de l'application utilisateur en action | ⭐⭐ RECOMMANDÉ |
| B8 | **Détection de drift** | Graphiques KS-test, PSI, alertes configurées | ⭐⭐ RECOMMANDÉ |

### Annexes Communes

| # | Annexe | Contenu |
|---|--------|----------|
| C1 | **Glossaire technique** | Définitions : ETL, MLOps, CI/CD, Drift, XGBoost, FastAPI, etc. |
| C2 | **Références bibliographiques** | Documentation officielle, articles, tutoriels utilisés |
| C3 | **Lien GitHub** | URL du repository avec instructions de lancement |

### Glossaire type (Annexe C1)

| Terme | Définition |
|-------|------------|
| **ETL** | Extract, Transform, Load — Pipeline de collecte et transformation de données |
| **MLOps** | Machine Learning Operations — Pratiques DevOps appliquées au ML |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **Drift** | Dérive des données ou du modèle dans le temps |
| **XGBoost** | Algorithme de gradient boosting pour la classification/régression |
| **FastAPI** | Framework Python moderne pour créer des APIs REST |
| **MLflow** | Plateforme open-source pour le cycle de vie ML |
| **Prometheus** | Système de monitoring et d'alerting open-source |
| **Grafana** | Outil de visualisation de métriques |
| **Docker Compose** | Outil d'orchestration de conteneurs multi-services |

---

## ✅ Checklist de Validation

### Bloc E1 - API & Base de données
- [ ] C1 : Schéma des besoins et flux de données
- [ ] C2 : Pipeline ETL documenté avec code
- [ ] C3 : MCD/MPD + Scripts SQL
- [ ] C4 : API REST avec Swagger + tests
- [ ] C5 : Docker-compose fonctionnel

### Bloc E3 - Mise à disposition de l'IA
- [ ] C9 : Endpoint `/predict` documenté
- [ ] C10 : Interface Streamlit avec captures
- [ ] C11 : Dashboards monitoring + code drift
- [ ] C12 : 252 tests, 82% couverture
- [ ] C13 : 6 workflows GitHub Actions

---

## 📏 Conseils de Rédaction

### Format et longueur
1. **Longueur recommandée** : 20-30 pages (hors annexes)
2. **Format** : PDF, numéroté, avec table des matières cliquable
3. **Police** : Arial ou Calibri, 11-12pt, interligne 1.15-1.5
4. **Marges** : 2.5 cm minimum

### Contenu
5. **Illustrations** : Privilégier les diagrammes et captures d'écran annotées
6. **Code** : Extraits pertinents et commentés (pas de copier-coller massif)
7. **Références** : Citer tes sources (documentation, articles)
8. **Cohérence** : Présenter E1 et E3 comme un projet unique et fluide

### Erreurs à éviter
- ❌ Trop de code sans explication
- ❌ Captures d'écran illisibles ou non annotées
- ❌ Oublier de mentionner le RGPD (même si pas de données personnelles)
- ❌ Ne pas lier les compétences aux réalisations concrètes
- ❌ Rapport trop long (le jury doit pouvoir le lire en 30 min)

---

## 🎤 Préparation à la Soutenance

### Durées officielles (règlement Simplon)

| Bloc | Présentation | Questions jury | Total |
|------|--------------|----------------|-------|
| **E1** (Bloc 1) | 15 min | 10 min max | **25 min** |
| **E3** (Bloc 2) | 20 min + démo | 10 min max | **30 min** |

> Si rapport combiné E1+E3 : prévoir ~35-45 min de présentation totale

### Déroulement suggéré

**E1 — Gestion des données (15 min)**
1. Contexte et problématique (2 min)
2. Pipeline ETL et sources de données (4 min)
3. Base de données et modélisation (4 min)
4. API REST de données (4 min)
5. Transition vers E3 (1 min)

**E3 — Mise à disposition de l'IA (20 min)**
1. API du modèle ML (4 min)
2. Intégration Streamlit (3 min)
3. **Démonstration live** (5 min) ⚡
4. Monitoring et détection de drift (4 min)
5. Tests et CI/CD (3 min)
6. Conclusion et perspectives (1 min)

### Démonstration live (obligatoire pour E3)

**Scénario de démo suggéré :**
```
1. Ouvrir l'interface Streamlit
2. Sélectionner deux Pokémon (ex: Pikachu vs Dracaufeu)
3. Lancer une prédiction
4. Montrer le résultat avec probabilités
5. Ouvrir Grafana et montrer les métriques temps réel
6. (Optionnel) Montrer MLflow avec les expériences
```

### Questions types du jury

**E1 — Données :**
- "Comment avez-vous géré les données manquantes ?"
- "Pourquoi PostgreSQL plutôt qu'une autre BDD ?"
- "Comment sécurisez-vous l'API de données ?"
- "Quelle est votre politique RGPD ?"

**E3 — IA :**
- "Comment détectez-vous les dérives du modèle ?"
- "Pourquoi avoir choisi XGBoost ?"
- "Comment testez-vous le pipeline ML ?"
- "Quelle est votre stratégie de versioning des modèles ?"
- "Que se passe-t-il si le modèle dérive ?"
- "Comment gérez-vous le rollback d'un modèle ?"

### Points différenciants à mettre en avant
- ✅ Architecture MLOps complète (rare pour un projet de certification)
- ✅ Détection de drift automatisée avec alertes
- ✅ 9 services Docker orchestrés
- ✅ CI/CD avec 6 workflows GitHub Actions
- ✅ 252 tests, 82% de couverture
- ✅ Deux versions de modèle comparées (v1 vs v2)

---

*Guide créé le 31 janvier 2026 pour le projet PredictionDex*
