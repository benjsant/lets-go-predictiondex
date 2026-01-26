# 📁 Améliorations de l'arborescence - Proposition

**Date** : 26 janvier 2026

---

## 📊 Structure actuelle (simplifiée)

```
lets-go-predictiondex/
├── api_pokemon/          # ✅ API FastAPI
│   ├── middleware/       # ✨ NOUVEAU : Sécurité
│   ├── monitoring/       # ✅ Metrics + drift
│   ├── routes/           # ✅ Endpoints
│   └── services/         # ✅ Logique métier
├── core/                 # ✅ Modèles DB + Schemas
│   ├── db/
│   ├── models/
│   └── schemas/
├── etl_pokemon/          # ✅ ETL Scrapy
│   ├── pokepedia_scraper/
│   └── scripts/
├── machine_learning/     # ✅ ML Pipeline
├── interface/            # ✅ Streamlit
├── docker/               # ✅ Dockerfiles + configs
│   ├── grafana/
│   └── prometheus/
├── models/               # ✅ Modèles entraînés
├── data/                 # ✅ Datasets
├── notebooks/            # ✅ Jupyter
├── docs/                 # ✅ Documentation
├── scripts/              # ✅ Scripts utilitaires
└── tests/                # ⚠️ Tests (à compléter)
```

---

## ✨ Améliorations proposées

### 1. Structure de sécurité (✅ Déjà implémenté)

```
api_pokemon/
├── middleware/
│   ├── __init__.py
│   └── security.py       # ✨ API Key authentication
```

**Avantages** :
- Séparation claire des préoccupations
- Réutilisable pour d'autres middlewares (rate limiting, CORS, etc.)
- Facile à tester

---

### 2. Secrets et configuration (🎯 À améliorer)

**Actuel** :
```
.env                      # Variables sensibles
API_KEYS_PRIVATE.md      # Clés API (gitignored)
```

**Proposition** :
```
config/
├── .env.example          # Template sans secrets
├── .env.development      # Dev (valeurs par défaut)
├── .env.production       # Production (à créer)
└── secrets/              # Secrets (gitignored)
    ├── api_keys.txt
    ├── db_passwords.txt
    └── ssl_certs/
```

**Avantages** :
- Séparation environnements dev/prod
- Gestion centralisée des secrets
- Template `.env.example` pour nouveaux développeurs

---

### 3. Tests structurés (🎯 À améliorer)

**Actuel** :
```
tests/                    # Vide ou minimal
```

**Proposition** :
```
tests/
├── unit/                 # Tests unitaires
│   ├── test_api/
│   │   ├── test_routes/
│   │   ├── test_services/
│   │   └── test_middleware/
│   │       └── test_security.py  # ✨ Tester API Key
│   ├── test_etl/
│   ├── test_ml/
│   └── test_core/
├── integration/          # Tests d'intégration
│   ├── test_api_db.py
│   ├── test_etl_db.py
│   └── test_ml_pipeline.py
├── e2e/                  # Tests end-to-end
│   └── test_full_workflow.py
├── fixtures/             # Données de test
│   ├── pokemon_sample.json
│   └── moves_sample.csv
└── conftest.py           # Configuration pytest
```

**Avantages** :
- Tests organisés par type
- Couverture complète (unit → e2e)
- Fixtures réutilisables

---

### 4. Documentation améliorée (🎯 À améliorer)

**Actuel** :
```
docs/
├── sql/
└── archive_jan_2026/
*.md (root)               # Nombreux fichiers MD
```

**Proposition** :
```
docs/
├── architecture/         # Architecture technique
│   ├── diagrams/
│   ├── decisions/        # ADR (Architecture Decision Records)
│   └── security.md       # ✨ SECURITY.md déplacé ici
├── api/                  # Documentation API
│   ├── openapi.json
│   └── authentication.md
├── deployment/           # Guides de déploiement
│   ├── docker.md
│   ├── production.md
│   └── security_checklist.md
├── development/          # Guides pour développeurs
│   ├── setup.md
│   ├── contributing.md
│   └── testing.md
├── sql/                  # Scripts SQL
└── archive/              # Archives
    └── 2026_01/

# Root (uniquement essentiels)
README.md                 # Vue d'ensemble
QUICKSTART.md            # Démarrage rapide
CHANGELOG.md             # Historique des versions
```

**Avantages** :
- Documentation organisée par thème
- Root épuré (moins de clutter)
- Facile à naviguer

---

### 5. Scripts organisés (🎯 À améliorer)

**Actuel** :
```
scripts/
├── generate_monitoring_data.py
├── quick_start_docker.py
├── start_docker_stack.py
└── test_mlflow_integration.py
```

**Proposition** :
```
scripts/
├── setup/                # Scripts d'initialisation
│   ├── init_db.py
│   ├── generate_api_keys.py  # ✨ Déplacer security.py ici
│   └── check_requirements.py
├── deployment/           # Scripts de déploiement
│   ├── docker_stack.py
│   └── healthcheck.py
├── monitoring/           # Scripts de monitoring
│   ├── generate_monitoring_data.py
│   └── check_drift.py
├── ml/                   # Scripts ML
│   ├── train_model.py
│   └── evaluate_model.py
└── utils/                # Utilitaires
    └── backup_db.py
```

**Avantages** :
- Scripts organisés par fonction
- Facile à trouver
- Réutilisables

---

### 6. CI/CD (🆕 Nouveau)

**Proposition** :
```
.github/
├── workflows/
│   ├── ci.yml            # Tests + lint
│   ├── security.yml      # Scan sécurité
│   ├── docker-build.yml  # Build images
│   └── deploy.yml        # Déploiement prod
└── dependabot.yml        # Mises à jour auto

.gitlab-ci.yml            # Alternative GitLab
```

**Avantages** :
- Automatisation CI/CD
- Tests automatiques
- Scan de sécurité
- Build Docker automatique

---

### 7. Logs centralisés (🆕 Nouveau)

**Proposition** :
```
logs/                     # Logs locaux (gitignored)
├── api/
├── etl/
├── ml/
└── monitoring/

docker/
└── logging/
    ├── loki-config.yml   # Grafana Loki
    └── promtail-config.yml
```

**Avantages** :
- Logs centralisés
- Facilite le debugging
- Intégration Grafana

---

## 🎯 Arborescence cible (complète)

```
lets-go-predictiondex/
├── 📁 api_pokemon/           # API FastAPI
│   ├── middleware/           # ✨ Sécurité, CORS, etc.
│   ├── monitoring/
│   ├── routes/
│   └── services/
├── 📁 core/                  # Modèles + Schemas
├── 📁 etl_pokemon/           # ETL Scrapy
├── 📁 machine_learning/      # ML Pipeline
├── 📁 interface/             # Streamlit
├── 📁 docker/                # Docker configs
│   ├── grafana/
│   ├── prometheus/
│   └── logging/              # 🆕 Loki/Promtail
├── 📁 config/                # 🆕 Configuration
│   ├── .env.example
│   └── secrets/ (gitignored)
├── 📁 models/                # Modèles entraînés
├── 📁 data/                  # Datasets
├── 📁 notebooks/             # Jupyter
├── 📁 docs/                  # 🎯 Documentation structurée
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   └── development/
├── 📁 scripts/               # 🎯 Scripts organisés
│   ├── setup/
│   ├── deployment/
│   ├── monitoring/
│   └── ml/
├── 📁 tests/                 # 🎯 Tests structurés
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── 📁 .github/               # 🆕 CI/CD GitHub
│   └── workflows/
├── 📁 logs/ (gitignored)     # 🆕 Logs locaux
├── 📄 README.md              # Vue d'ensemble
├── 📄 QUICKSTART.md          # Démarrage rapide
├── 📄 CHANGELOG.md           # Historique
├── 📄 .env                   # Config locale (gitignored)
├── 📄 .gitignore
├── 📄 docker-compose.yml
└── 📄 pytest.ini
```

---

## 🚀 Plan de migration

### Phase 1 : Sécurité (✅ Fait)
- [x] Créer `api_pokemon/middleware/security.py`
- [x] Intégrer API Key dans FastAPI
- [x] Configurer réseaux Docker privés
- [x] Modifier les ports

### Phase 2 : Configuration (🎯 Recommandé)
- [ ] Créer `config/`
- [ ] Template `.env.example`
- [ ] Séparer dev/prod

### Phase 3 : Tests (🎯 Recommandé)
- [ ] Créer structure `tests/`
- [ ] Tests API (routes + middleware)
- [ ] Tests ETL
- [ ] Tests ML

### Phase 4 : Documentation (🎯 Recommandé)
- [ ] Réorganiser `docs/`
- [ ] Déplacer fichiers MD root → docs/
- [ ] Créer CHANGELOG.md

### Phase 5 : CI/CD (🔮 Futur)
- [ ] GitHub Actions
- [ ] Tests automatiques
- [ ] Scan sécurité
- [ ] Deploy automatique

### Phase 6 : Logs (🔮 Futur)
- [ ] Intégrer Loki
- [ ] Configurer Promtail
- [ ] Dashboards Grafana

---

## ✅ Recommandations immédiates

### 1. Créer .env.example (haute priorité)
```bash
# config/.env.example
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=letsgo_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEV_MODE=true

# API Security
API_KEY_REQUIRED=true
API_KEYS="GENERATE_WITH: python api_pokemon/middleware/security.py"
```

### 2. Créer tests de sécurité (haute priorité)
```bash
# tests/unit/test_api/test_middleware/test_security.py
```

### 3. Documenter les changements (haute priorité)
```bash
# docs/deployment/security.md (déplacer SECURITY.md)
# CHANGELOG.md (créer)
```

---

## 📝 Conclusion

**Améliorations implémentées** :
- ✅ Middleware de sécurité structuré
- ✅ Réseaux Docker isolés
- ✅ Documentation SECURITY.md

**Prochaines étapes recommandées** :
1. Créer `.env.example` pour nouveaux développeurs
2. Ajouter tests de sécurité (`test_security.py`)
3. Réorganiser documentation (`docs/`)
4. Créer `CHANGELOG.md`

**Impact** :
- Meilleure maintenabilité
- Onboarding facilité
- Sécurité renforcée
- CI/CD prêt

---

**Créé le** : 26 janvier 2026  
**Statut** : Proposition (Phase 1 ✅ implémentée)
