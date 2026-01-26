# 📦 Tests Legacy - Archive

**Date archivage:** 26 janvier 2026  
**Raison:** Tests ad-hoc remplacés par suite organisée dans `tests/`

---

## Fichiers Archivés

Ces fichiers étaient des **tests manuels/temporaires** créés pendant le développement :

| Fichier | Taille | Description | Remplacé par |
|---------|--------|-------------|--------------|
| `test_all.py` | 6.5K | Tests généraux | `tests/` complets |
| `test_api_examples.py` | 11K | Exemples API | `tests/api/` |
| `test_before_evolution.py` | 4.7K | Tests évolution | `tests/core/` |
| `test_manual.py` | 13K | Tests manuels API | `tests/api/test_prediction_route.py` |
| `test_ml_cpu_optimization.py` | 8.8K | Validation optim CPU | Intégré dans code |
| `test_mlflow_integration.py` | 1.6K | Tests MLflow temporaires | `tests/mlflow/` |
| `test_monitoring.py` | 8.1K | Tests monitoring | Déjà dans `tests/api/` |
| `test_monitoring_smart.py` | 7.9K | Tests avancés monitoring | Idem |
| `test_prediction_api.py` | 5.9K | Tests prédictions | `tests/api/test_prediction_route.py` |

**Total:** 9 fichiers (67.5K) → Redondants avec suite organisée

---

## ✅ Nouvelle Organisation Tests

**Suite complète dans `tests/` :** 252 tests organisés en 6 catégories

```
tests/
├── api/ (64 tests)         → Routes + Services
├── core/ (15 tests)        → Models + Schemas
├── integration/ (9 tests)  → E2E MLflow→API
├── ml/ (50 tests)          → ML Pipeline
├── mlflow/ (17 tests)      → Model Registry
└── conftest.py             → Fixtures partagées
```

**Avantages nouvelle organisation:**
- ✅ Structure claire par domaine
- ✅ Fixtures réutilisables
- ✅ Coverage tracking
- ✅ CI/CD intégré
- ✅ Pas de duplication

---

## 🔍 Pourquoi Archivé ?

**Tests legacy:**
- 🔴 Ad-hoc, sans structure
- 🔴 Duplication avec tests organisés
- 🔴 Pas dans CI/CD
- 🔴 Pas de fixtures partagées
- 🔴 Difficile à maintenir

**Nouvelle suite:**
- ✅ Organisation par catégorie
- ✅ Fixtures pytest standardisées
- ✅ Dans GitHub Actions
- ✅ Coverage 82%
- ✅ Maintenable

---

## 📊 Migration

| Anciens Tests | Nouveaux Tests |
|--------------|----------------|
| `test_api_examples.py` | `tests/api/test_*_route.py` |
| `test_prediction_api.py` | `tests/api/test_prediction_route.py` |
| `test_manual.py` | `tests/api/test_prediction_service.py` |
| `test_monitoring*.py` | Métriques dans `tests/api/` |
| `test_mlflow_integration.py` | `tests/mlflow/test_model_registry.py` |
| `test_ml_cpu_optimization.py` | Intégré dans code production |

**Tous les scénarios de test sont couverts** dans la nouvelle suite.

---

## ⚠️ Ne Pas Supprimer

Ces fichiers restent **consultables** pour :
- Historique de développement
- Scénarios de test spécifiques
- Documentation des bugs résolus

Ils ne sont **plus exécutés** (remplacés par `tests/`).

---

**Archivé le:** 26 janvier 2026  
**Tests actuels:** 252 dans `tests/` (voir `tests/README.md`)
