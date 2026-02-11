# Reports Directory

Ce dossier contient les rapports automatiquement générés par les tests d'intégration et de validation.

## Structure

```
reports/
├── monitoring/ # Rapports de validation du monitoring
│ ├── validation_report.json
│ ├── validation_report.html
│ └── integration_test_results.json
└── validation/ # Rapports de validation système complète
 └── system_validation_report.json
```

## Génération automatique

Les rapports sont générés par :

| Fichier | Générateur | Commande |
|---------|-----------|----------|
| `monitoring/validation_report.*` | `test_monitoring_validation.py` | `python scripts/test_ci_cd_locally.py` |
| `monitoring/integration_test_results.json` | `test_monitoring_complete.py` | `pytest tests/integration/test_monitoring_complete.py` |
| `validation/system_validation_report.json` | `test_complete_system.py` | `pytest tests/integration/test_complete_system.py` |

## Contenu des rapports

### Monitoring Validation Report

Validation complète de la stack de monitoring :
- Services status (API, Prometheus, Grafana, MLflow)
- Métriques Prometheus collectées
- Prédictions ML testées
- Détection de drift
- Score de validation /100

**Utilisation** : CI/CD pré-push GitHub Actions

### Integration Test Results

Résultats des tests d'intégration monitoring :
- Collecte métriques temps réel
- Trafic API simulé
- Calcul percentiles (p50, p95, p99)
- Requêtes Prometheus
- Score /100

**Utilisation** : Tests pytest automatiques

### System Validation Report

Validation end-to-end complète du système :
- Base de données PostgreSQL (151 Pokémon, moves, types)
- API FastAPI (endpoints, santé, prédictions)
- MLflow (modèle enregistré, métriques)
- Monitoring (Prometheus, Grafana)
- Streamlit (interface utilisateur)
- Score global /100

**Utilisation** : Validation système avant déploiement

## .gitignore

Ces fichiers sont **gitignorés** car générés automatiquement lors des tests. 
La structure des dossiers est préservée via les fichiers `.gitkeep`.

## Notes

- Les rapports HTML sont consultables dans un navigateur
- Les rapports JSON peuvent être parsés par des outils d'analyse
- Score minimum recommandé : **≥ 60/100** pour CI/CD
- Score minimum recommandé : **≥ 80/100** pour production
