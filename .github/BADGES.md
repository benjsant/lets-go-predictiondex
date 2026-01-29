# Badges GitHub Actions pour README

Ajoutez ces badges au début de votre README.md pour montrer l'état du CI/CD :

```markdown
## Status CI/CD

![Tests](https://github.com/benjsant/lets-go-predictiondex/workflows/Tests/badge.svg)
![Docker Build](https://github.com/benjsant/lets-go-predictiondex/workflows/Docker%20Build/badge.svg)
![Lint and Format](https://github.com/benjsant/lets-go-predictiondex/workflows/Lint%20and%20Format/badge.svg)
![ML Pipeline](https://github.com/benjsant/lets-go-predictiondex/workflows/ML%20Pipeline/badge.svg)
![Monitoring Validation](https://github.com/benjsant/lets-go-predictiondex/workflows/Monitoring%20Validation/badge.svg)
[![codecov](https://codecov.io/gh/benjsant/lets-go-predictiondex/branch/main/graph/badge.svg)](https://codecov.io/gh/benjsant/lets-go-predictiondex)

## Métriques de Qualité

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B?logo=streamlit)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-337AB7)
![MLflow](https://img.shields.io/badge/MLflow-2.9-0194E2?logo=mlflow)
![Prometheus](https://img.shields.io/badge/Prometheus-2.47-E6522C?logo=prometheus)
![Grafana](https://img.shields.io/badge/Grafana-10.1-F46800?logo=grafana)

## Sécurité & Qualité

![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow)
![Linting: Flake8](https://img.shields.io/badge/linting-flake8-blue)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000)
![Typing: MyPy](https://img.shields.io/badge/typing-mypy-blue)
```

---

## Badges Personnalisés (Shields.io)

Vous pouvez aussi créer des badges personnalisés sur https://shields.io :

### Monitoring Score (100/100)
```markdown
![Monitoring](https://img.shields.io/badge/Monitoring-100%25-success)
```

### Model Accuracy
```markdown
![Model Accuracy](https://img.shields.io/badge/Accuracy-96.24%25-brightgreen)
```

### Dataset Size
```markdown
![Dataset](https://img.shields.io/badge/Dataset-898K%20combats-blue)
```

### Pokémon Count
```markdown
![Pokémon](https://img.shields.io/badge/Pok%C3%A9mon-187-red)
```

---

## Exemple de Section README

```markdown
# 🎮 PredictionDex - Pokémon Battle Predictor

> Prédicteur de combats Pokémon Let's Go avec Machine Learning et monitoring production-ready

![Tests](https://github.com/benjsant/lets-go-predictiondex/workflows/Tests/badge.svg)
![Docker Build](https://github.com/benjsant/lets-go-predictiondex/workflows/Docker%20Build/badge.svg)
![Monitoring](https://img.shields.io/badge/Monitoring-100%25-success)
![Model Accuracy](https://img.shields.io/badge/Accuracy-96.24%25-brightgreen)
[![codecov](https://codecov.io/gh/benjsant/lets-go-predictiondex/branch/main/graph/badge.svg)](https://codecov.io/gh/benjsant/lets-go-predictiondex)

## 🚀 Features

- ✅ **API REST** avec FastAPI (96.24% de précision)
- ✅ **Machine Learning** XGBoost sur 898K combats
- ✅ **Monitoring** Prometheus + Grafana (Score 100/100)
- ✅ **MLOps** avec MLflow pour le tracking
- ✅ **CI/CD** complet avec GitHub Actions
- ✅ **Docker** full-stack (8 services)
- ✅ **Tests** automatisés avec 80+ tests
```

---

## Comment voir les badges en action

1. **Après le premier push** sur `main`, les workflows vont se lancer
2. **Les badges deviennent verts** quand les workflows réussissent
3. **Le badge de monitoring** affichera "100/100 - Excellent" 🏆

## Commandes utiles

```bash
# Déclencher manuellement le workflow de validation
gh workflow run monitoring-validation.yml

# Voir l'état des workflows
gh workflow list

# Voir les runs récents
gh run list --workflow=monitoring-validation.yml
```
