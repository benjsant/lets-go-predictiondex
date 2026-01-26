# ⏱️ Estimation Temps de Développement - Projet PredictionDex

**Date d'analyse:** 26 janvier 2026  
**Projet:** Pokémon Let's Go PredictionDex (Version 2.0 - MLflow Registry)

---

## 📊 Temps Total Estimé

### 🎯 En Solo (Développeur Confirmé)

**Total:** ~**180-220 heures** (4.5 - 5.5 mois à mi-temps)

---

## 📅 Décomposition Détaillée

### Phase 1: ETL & Base de Données (35-45h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Design BDD** | 8-10h | Schéma relationnel, normalisation 3NF, contraintes |
| **Scraper Pokepedia** | 6-8h | Parsing HTML, gestion erreurs, retry logic |
| **PokéAPI Integration** | 4-6h | Appels API, rate limiting, cache |
| **Scripts ETL** | 10-12h | Load CSV, orchestration, validation |
| **Tests ETL** | 4-6h | Tests unitaires + intégration |
| **Documentation** | 3-5h | README, diagrammes |

**Difficulté:** ⭐⭐⭐☆☆ (Moyenne)

---

### Phase 2: API REST (30-40h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Setup FastAPI** | 4-6h | Structure projet, config, middleware |
| **Models SQLAlchemy** | 6-8h | ORM, relations, indexes |
| **Schemas Pydantic** | 4-6h | Validation, serialization |
| **Routes & Services** | 10-12h | Endpoints, business logic |
| **Tests API** | 8-10h | 64 tests routes + services |
| **Documentation Swagger** | 2-3h | Docstrings, examples |

**Difficulté:** ⭐⭐⭐☆☆ (Moyenne)

---

### Phase 3: Machine Learning (40-50h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Dataset Building** | 8-10h | Feature engineering, validation |
| **Notebooks Exploration** | 6-8h | EDA, visualisations, insights |
| **Training Pipeline** | 10-12h | XGBoost, Random Forest, GridSearch |
| **Optimisation CPU** | 6-8h | Multi-threading, histogramme, benchmarks |
| **Compression Modèles** | 2-3h | Joblib, compression, tests |
| **Tests ML** | 6-8h | 50 tests preprocessing + dataset |
| **Documentation** | 2-3h | Notebooks, README ML |

**Difficulté:** ⭐⭐⭐⭐☆ (Élevée)

---

### Phase 4: MLflow Model Registry (25-35h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Setup MLflow** | 4-6h | Tracking server, backend config |
| **Integration Tracking** | 6-8h | Log params/metrics/artifacts |
| **Model Registry** | 8-10h | Register, promote, compare, load |
| **API Integration** | 4-6h | Load from registry, fallback |
| **Tests MLflow** | 6-8h | 17 tests registry + 9 tests E2E |
| **Documentation** | 2-3h | Guide registry, changelog |

**Difficulté:** ⭐⭐⭐⭐☆ (Élevée - nouveau domaine)

---

### Phase 5: Monitoring (20-25h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Prometheus Setup** | 4-6h | Métriques custom, middleware |
| **Grafana Dashboards** | 6-8h | 2 dashboards (API + Model) |
| **Evidently Data Drift** | 4-6h | Reports, validation, automation |
| **Tests Monitoring** | 3-4h | Validation métriques |
| **Documentation** | 3-4h | README monitoring, screenshots |

**Difficulté:** ⭐⭐⭐☆☆ (Moyenne)

---

### Phase 6: Interface Streamlit (15-20h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Pages UI** | 8-10h | 7 pages (Home, Compare, Quiz, etc.) |
| **Services API** | 3-4h | Client HTTP, error handling |
| **Formatters** | 2-3h | Stats, types, visualisations |
| **Tests Interface** | 0h | (Skippés - non implémentés) |
| **Documentation** | 2-3h | README interface |

**Difficulté:** ⭐⭐☆☆☆ (Facile - si Streamlit connu)

---

### Phase 7: DevOps & CI/CD (20-30h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Docker Compose** | 6-8h | 6 services, health checks, volumes |
| **Dockerfiles** | 4-6h | Multi-stage builds, optimisation |
| **GitHub Actions** | 6-8h | 4 workflows (tests, docker, lint, ML) |
| **Tests E2E** | 4-6h | 9 tests integration MLflow→API |
| **Documentation** | 2-4h | CI/CD setup, deployment guide |

**Difficulté:** ⭐⭐⭐⭐☆ (Élevée - si peu d'expérience Docker)

---

### Phase 8: Documentation & Finition (15-20h)

| Tâche | Heures | Détails |
|-------|--------|---------|
| **Documentation E1** | 6-8h | Architecture, choix techniques |
| **Documentation E3** | 4-6h | Compétences, preuves |
| **README Synthèse** | 2-3h | PROJECT_SYNTHESIS, guides |
| **Refactoring** | 2-3h | Cleanup, organisation |
| **Validation Finale** | 1-2h | Tests, coverage, validation |

**Difficulté:** ⭐⭐☆☆☆ (Facile mais chronophage)

---

## 📊 Répartition par Domaine

```
ML/MLOps:        65-85h (36%)  ████████████
ETL/Database:    35-45h (20%)  ███████
API REST:        30-40h (17%)  ██████
DevOps:          20-30h (11%)  ████
Monitoring:      20-25h (11%)  ████
Interface:       15-20h (9%)   ███
Documentation:   15-20h (9%)   ███
```

---

## ⏰ Scénarios Réalistes

### Scénario 1: Développeur Junior (250-300h)
**Profil:** Peu d'expérience ML/Docker
- ETL: 50-60h (+40%)
- ML: 60-75h (+50%)
- MLflow: 40-50h (+60%)
- Docker: 35-45h (+50%)
- Reste: +20-30h

**Total:** ~6-7 mois à mi-temps

---

### Scénario 2: Développeur Confirmé (180-220h)
**Profil:** Expérience Python, base ML, Docker
- ETL: 35-45h
- ML: 40-50h
- MLflow: 25-35h (apprentissage)
- Docker: 20-30h
- Reste: normal

**Total:** ~4.5-5.5 mois à mi-temps

---

### Scénario 3: Senior ML Engineer (140-170h)
**Profil:** Expert ML, MLOps, Docker
- ETL: 25-30h (-30%)
- ML: 30-35h (-25%)
- MLflow: 15-20h (-40%)
- Docker: 12-18h (-40%)
- Reste: -20-30h

**Total:** ~3.5-4 mois à mi-temps

---

## 📅 Planning Type (Développeur Confirmé)

### Semaine 1-2 (30-40h)
- ETL Pipeline complet
- Base PostgreSQL normalisée

### Semaine 3-4 (30-40h)
- API REST complète
- Tests API

### Semaine 5-7 (40-50h)
- ML Training Pipeline
- Notebooks + Optimisations

### Semaine 8-9 (25-35h)
- MLflow Model Registry
- Tests MLflow

### Semaine 10-11 (20-25h)
- Monitoring Prometheus/Grafana
- Evidently

### Semaine 12 (15-20h)
- Interface Streamlit

### Semaine 13-14 (20-30h)
- Docker Compose
- CI/CD GitHub Actions

### Semaine 15-16 (15-20h)
- Documentation finale
- Validation E1/E3

**Total:** ~16 semaines (4 mois) à mi-temps ✅

---

## 🎯 Temps par Compétence E3

| Compétence | Temps | % Total |
|------------|-------|---------|
| **C9** - API REST avec IA | 40-50h | 22% |
| **C10** - Intégration app | 15-20h | 9% |
| **C11** - Monitoring | 20-25h | 11% |
| **C12** - Optimisation ML | 25-35h | 15% |
| **C13** - MLOps CI/CD | 45-60h | 26% |
| Autres (ETL, Doc) | 35-50h | 17% |

---

## 💡 Facteurs d'Accélération

**Ce qui fait gagner du temps:**
- ✅ Connaissance préalable de FastAPI/SQLAlchemy
- ✅ Expérience scikit-learn/XGBoost
- ✅ Maîtrise Docker Compose
- ✅ Templates/boilerplates réutilisables
- ✅ Documentation claire (PokéAPI, MLflow)

**Ce qui prend plus de temps:**
- ❌ Apprentissage MLflow Model Registry (nouveau)
- ❌ Debugging scraper (HTML change)
- ❌ Tuning hyperparamètres ML
- ❌ Configuration Prometheus/Grafana
- ❌ Rédaction documentation E1/E3

---

## 🏆 Comparaison Temps Réel vs Estimé

**Temps réel développement (avec iterations):** ~200-250h
- Includes: bugfixes, refactoring, iterations, tests multiples

**Temps estimé clean (sans détour):** 180-220h

**Différence:** ~20-30h de "waste" (bugs, fausses pistes, rewrites)

**Ratio:** ~10-15% overhead normal en développement solo

---

## 📊 Conclusion

### En Solo - Développeur Confirmé
```
Temps minimal:    180h (4.5 mois mi-temps)
Temps réaliste:   200h (5 mois mi-temps)
Temps maximal:    220h (5.5 mois mi-temps)
```

### Avec Binôme
```
Temps:            110-130h/personne (2.5-3 mois mi-temps)
Gain:             ~40% (grâce à parallélisation + review)
```

### Full-Time (40h/semaine)
```
Solo:             5-6 semaines
Binôme:           3-4 semaines
```

---

## 🎓 Recommandation Pédagogique

**Pour E1/E3:** Ce projet est **parfait en solo** pour démontrer:
- Autonomie complète ✅
- Maîtrise technique transverse ✅
- Gestion projet A→Z ✅
- Documentation pro ✅

**Temps investissement:** ~200h (5 mois mi-temps) = **Très raisonnable**

**ROI:** Compétences acquises valent **×10** le temps investi

---

**Créé le:** 26 janvier 2026  
**Basé sur:** Analyse post-mortem du projet PredictionDex  
**Fiabilité:** ±15% (facteurs individuels)
