# 📚 Documentation PredictionDex

> Index de la documentation technique du projet

## 📁 Structure

| Document | Description |
|----------|-------------|
| [CERTIFICATION_E1_E3.md](CERTIFICATION_E1_E3.md) | Référentiel des compétences RNCP E1/E3 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Schémas d'architecture technique |
| [GUIDE_RAPPORT_E1_E3.md](GUIDE_RAPPORT_E1_E3.md) | 📝 Guide de rédaction du rapport de certification |
| [RAPPORT_E1_E3_TEMPLATE.md](RAPPORT_E1_E3_TEMPLATE.md) | 📄 **Template pré-rempli du rapport E1+E3** (PDF-ready) |

## 🔗 Documentation par Module

| Module | README | Description |
|--------|--------|-------------|
| **API** | [api_pokemon/README.md](../api_pokemon/README.md) | API REST FastAPI, endpoints, authentification |
| **ETL** | [etl_pokemon/README.md](../etl_pokemon/README.md) | Pipeline de collecte de données |
| **ML** | [machine_learning/README.md](../machine_learning/README.md) | Entraînement modèle XGBoost |
| **Interface** | [interface/README.md](../interface/README.md) | Application Streamlit |
| **Core** | [core/README.md](../core/README.md) | Modèles BDD SQLAlchemy |
| **Tests** | [tests/README.md](../tests/README.md) | Tests unitaires et intégration |
| **Scripts** | [scripts/README.md](../scripts/README.md) | Scripts utilitaires |
| **Docker** | [docker/README.md](../docker/README.md) | Configuration Docker |
| **Models** | [models/README.md](../models/README.md) | Artifacts ML exportés |

## 🎓 Certification RNCP

Ce projet valide les compétences des blocs **E1** et **E3** :

### Bloc E1 - Collecte et Traitement des Données
- **C1** : Automatiser l'extraction de données (CSV, API, Scraping, BDD)
- **C2** : Développer des requêtes SQL d'extraction
- **C3** : Développer des règles d'agrégation et nettoyage
- **C4** : Créer une base de données conforme RGPD
- **C5** : Développer une API REST pour exposer les données

### Bloc E3 - Intégration IA en Production
- **C9** : Développer une API exposant un modèle IA
- **C10** : Intégrer l'API dans une application
- **C11** : Monitorer un modèle IA (Prometheus, Grafana)
- **C12** : Programmer les tests automatisés
- **C13** : Créer une chaîne de livraison continue (CI/CD, MLOps)

➡️ Voir [CERTIFICATION_E1_E3.md](CERTIFICATION_E1_E3.md) pour le détail complet.
