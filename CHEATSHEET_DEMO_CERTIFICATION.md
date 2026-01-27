# 🎯 Cheatsheet Démonstration Certification E1/E3

**À IMPRIMER - Format 2 pages recto-verso**

---

## 🚀 Démarrage Rapide (1 commande)

```bash
# Démarrer TOUTE la stack + ouvrir navigateurs + afficher guide
python scripts/demo_certification.py --generate-metrics
```

---

## 📊 Tableau Rapide - Composant → Compétence

```
┌────────────────────────────────────────────────────────────────┐
│                    QUICK REFERENCE TABLE                        │
├─────────────────────┬──────────────────────┬───────────────────┤
│ COMPOSANT           │ URL                  │ COMPETENCE        │
├─────────────────────┼──────────────────────┼───────────────────┤
│ 1. Streamlit        │ :8502                │ C10 - Interface   │
│ 2. Swagger API      │ :8080/docs           │ C9 - API + IA     │
│ 3. Grafana          │ :3001                │ C11 - Monitoring  │
│ 4. MLflow           │ :5001                │ C13 - MLOps       │
│ 5. Prometheus       │ :9091                │ C11 - Métriques   │
│ 6. PostgreSQL       │ Via Swagger          │ E1.3 - BDD        │
│ 7. ETL Pipeline     │ docker logs etl      │ E1.1, E1.2        │
│ 8. ML Training      │ docker logs ml       │ C12 - Optim IA    │
│ 9. Notebooks        │ code notebooks/      │ E1.4 - Exploit    │
│ 10. GitHub Actions  │ github.com/.../acts  │ C13 - CI/CD       │
└─────────────────────┴──────────────────────┴───────────────────┘
```

---

## ⏱️ Plan 30 Minutes

```
┌─────────────────────────────────────────────────────────────────┐
│                      TIMELINE 30 MIN                            │
├──────┬──────────────────────────────────────────────┬──────────┤
│ MIN  │ ACTION                                        │ TOOL     │
├──────┼──────────────────────────────────────────────┼──────────┤
│ 0-4  │ Streamlit - Prédiction interactive ⭐        │ :8502    │
│ 4-7  │ Swagger - Test /predict/best-move ⭐         │ :8080    │
│ 7-10 │ Grafana - Dashboards temps réel ⭐           │ :3001    │
│ 10-12│ MLflow - Model Registry                      │ :5001    │
│ 12-15│ PostgreSQL - Via API (/pokemon, /types)      │ :8080    │
│ 15-18│ ETL Logs - 5 étapes                          │ Terminal │
│ 18-22│ ML Logs + Notebooks - Training ⭐            │ Terminal │
│ 22-24│ Drift Detection - Evidently HTML            │ Reports  │
│ 24-27│ GitHub Actions - 4 workflows CI/CD           │ GitHub   │
│ 27-30│ Documentation - README + Diagrammes          │ VSCode   │
└──────┴──────────────────────────────────────────────┴──────────┘

⭐ = Moments clés à ne pas manquer
```

---

## 🎬 Script Phase 1: Interfaces Web (12 min)

### 1. Streamlit (4 min) - :8502

**Page "Combat et Prédiction":**
```
1. Sélectionner Pikachu (#25)
2. Sélectionner Bulbizarre (#1)
3. Choisir 4 capacités
4. Cliquer "Prédire le vainqueur"
5. MONTRER: Probabilités + Meilleure capacité
   Temps: < 500ms
```

**Dire:** "Cette interface valide **C10** (intégration app) et consomme l'API REST."

---

### 2. Swagger API (3 min) - :8080/docs

**Test `/predict/best-move`:**
```json
{
  "pokemon_a_id": 25,
  "pokemon_b_id": 1,
  "available_moves": ["Fatal-Foudre", "Vive-Attaque"]
}
```

**MONTRER:**
- Réponse < 500ms
- Probabilités par move
- Recommandation

**Dire:** "Cette API valide **C9** (API REST + IA) et **C12** (< 500ms)."

---

### 3. Grafana (3 min) - :3001

**Dashboard "API Performance":**
```
✅ API Status: UP
✅ Request Rate: 10-50 req/s
✅ P95 Latency: < 500ms
✅ Error Rate: < 1%
```

**Dire:** "Ce monitoring valide **C11** (monitoring IA production)."

---

### 4. MLflow (2 min) - :5001

**Navigate:**
```
Experiments → battle_winner_v2
Models → battle_winner_model
```

**MONTRER:**
- Comparaison runs
- Versions modèles (v1, v2, v3)
- Stage: Production

**Dire:** "Ce registry valide **C13** (MLOps versioning)."

---

## 🎬 Script Phase 2: Backend (10 min)

### 5. PostgreSQL via API (3 min) - :8080/docs

**Endpoints à tester:**
```
GET /pokemon?limit=5     → 188 Pokémon
GET /types               → 18 types
GET /pokemon/25/moves    → Capacités Pikachu
GET /pokemon/25/types    → Faiblesses
```

**Dire:** "Cette BDD valide **E1.3** (11 tables 3NF) et **E1.2** (données nettoyées)."

---

### 6. ETL Pipeline (3 min) - Terminal

```bash
docker logs letsgo_etl --tail 200
```

**Points clés:**
```
[1/5] Init DB: ✅ 11 tables créées
[2/5] CSV: ✅ 151 Pokémon chargés
[3/5] PokéAPI: ✅ 188 Pokémon (formes Alola)
[4/5] Pokepedia: ✅ 324 règles types
[5/5] Validation: ✅ 0 données manquantes
```

**Dire:** "Ce pipeline valide **E1.1** (collecte 3 sources) et **E1.2** (nettoyage)."

---

### 7. ML Training (4 min) - Terminal + VSCode

**Logs:**
```bash
docker logs letsgo_ml --tail 300
```

```
[1/4] Dataset: ✅ 898,472 combats, 133 features
[2/4] Training: ✅ GridSearch 12 combinations
[3/4] Evaluation: ✅ 94.46% accuracy
[4/4] Export: ✅ model.pkl + metadata
```

**Notebooks:**
```bash
code notebooks/03_training_evaluation.ipynb
```

**MONTRER:** Confusion matrix, ROC curves, Feature importance

**Dire:** "Ce pipeline valide **C12** (optimisation IA) et **E1.4** (exploitation données)."

---

## 🎬 Script Phase 3: Technique (8 min)

### 8. Drift Detection (2 min)

```bash
# Lister rapports
ls -lh api_pokemon/monitoring/reports/

# Ouvrir dernier rapport
xdg-open api_pokemon/monitoring/reports/drift_dashboard_*.html
```

**MONTRER:** Data drift dashboard, Statistical tests

**Dire:** "Evidently AI détecte le drift production (**C11**)."

---

### 9. GitHub Actions (3 min)

**URL:** https://github.com/YOUR_REPO/actions

**Workflows:**
```
1. Run Tests: ✅ 252 tests, 82% coverage
2. Build Docker: ✅ 5 images
3. ML Training: ✅ Auto-register MLflow
4. Deploy: ✅ Staging auto-deploy
```

**Dire:** "Le CI/CD valide **C13** (MLOps tests automatisés)."

---

### 10. Documentation (3 min)

```bash
code README.md
```

**Sections:**
```
✅ Architecture diagram
✅ Quick Start
✅ API documentation
✅ Monitoring stack
```

**Dire:** "La documentation valide **E1.5** (documenter processus)."

---

## 🔥 Top 5 Moments Clés (À NE PAS MANQUER)

```
┌────────────────────────────────────────────────────────────────┐
│                       STAR MOMENTS ⭐                          │
├────────────────────────────────────────────────────────────────┤
│ 1. Streamlit - Prédiction interactive < 500ms                 │
│    → Montrer sélection Pokémon + résultat temps réel          │
│                                                                 │
│ 2. Swagger - Test /predict/best-move avec JSON                │
│    → Try it out + Execute + Montrer response                   │
│                                                                 │
│ 3. Grafana - Dashboard API Performance live                   │
│    → Request rate, P95 latency, Error rate                     │
│                                                                 │
│ 4. ML Logs - 898k combats → 94.46% accuracy                   │
│    → Dataset size + Training time + Metrics                    │
│                                                                 │
│ 5. GitHub Actions - 252 tests passed                          │
│    → Workflow runs + Coverage badge                            │
└────────────────────────────────────────────────────────────────┘
```

---

## 📋 Checklist Avant Démo

### Infrastructure (5 min avant)

```bash
# 1. Démarrer stack
python scripts/start_docker_stack.py

# 2. Valider services
python scripts/validate_docker_stack.py

# 3. Générer métriques (arrière-plan)
python scripts/generate_monitoring_data.py --mode realistic --duration 30 &
```

### Vérifications

- [ ] ✅ 6 services UP (db, api, streamlit, grafana, prometheus, mlflow)
- [ ] ✅ 5 onglets navigateur ouverts
- [ ] ✅ Notebooks ouverts dans VSCode
- [ ] ✅ Terminal prêt (logs)
- [ ] ✅ Grafana dashboards chargés
- [ ] ✅ Métriques générées (courbes visibles)

---

## 💬 Phrases d'Accroche

### Début
> "Je vais présenter PredictionDex, une plateforme MLOps complète qui prédit les combats Pokémon avec **94.46% de précision**. Ce projet valide l'intégralité des **compétences E1 et E3**."

### Transitions
- "Voyons maintenant l'API REST qui expose le modèle..."
- "Passons au monitoring temps réel avec Grafana..."
- "Voici le pipeline ETL qui collecte les données..."

### Fin
> "En résumé: collecte multi-sources (**E1.1**), nettoyage et BDD (**E1.2/E1.3**), exploitation ML (**E1.4**), documentation complète (**E1.5**), API REST + IA (**C9**), interface utilisateur (**C10**), monitoring production (**C11**), optimisation < 500ms (**C12**), et MLOps CI/CD (**C13**). **Toutes les compétences E1/E3 sont validées**."

---

## 🛠️ Commandes Utiles (Mémo)

```bash
# Validation rapide
python scripts/validate_docker_stack.py --verbose

# Générer métriques
python scripts/generate_monitoring_data.py --mode realistic --duration 5

# Logs ETL
docker logs letsgo_etl --tail 200

# Logs ML
docker logs letsgo_ml --tail 300

# Ouvrir notebooks
code notebooks/03_training_evaluation.ipynb

# Lister rapports drift
ls -lh api_pokemon/monitoring/reports/

# Redémarrer service
docker-compose restart <service>
```

---

## 🎯 Mapping Compétences → Preuves

```
╔═══════════════════════════════════════════════════════════════╗
║                   COMPETENCES E1 (DONNEES)                    ║
╠═══════════════════════════════════════════════════════════════╣
║ E1.1 - Collecte      │ ETL 3 sources (CSV, API, scraping)    ║
║ E1.2 - Nettoyage     │ Validation, normalisation, guards     ║
║ E1.3 - BDD           │ PostgreSQL 11 tables 3NF              ║
║ E1.4 - Exploitation  │ 133 features, notebooks, viz          ║
║ E1.5 - Documentation │ README, diagrammes, OpenAPI           ║
╠═══════════════════════════════════════════════════════════════╣
║                   COMPETENCES E3 (IA PRODUCTION)              ║
╠═══════════════════════════════════════════════════════════════╣
║ C9  - API + IA       │ FastAPI + XGBoost 94.46%              ║
║ C10 - Interface      │ Streamlit 8 pages fonctionnelles      ║
║ C11 - Monitoring     │ Prometheus + Grafana + Evidently      ║
║ C12 - Optimisation   │ < 500ms, GridSearch, CPU optimized    ║
║ C13 - MLOps          │ MLflow Registry + GitHub Actions      ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🚨 Dépannage Express

### Service ne démarre pas
```bash
docker-compose restart <service>
docker logs <container_name>
```

### Grafana vide
```bash
python scripts/generate_monitoring_data.py --mode burst --duration 2
```

### Notebooks ne s'affichent pas
```bash
jupyter lab notebooks/
# OU
code notebooks/
```

### Métriques manquantes
```bash
# Vérifier Prometheus targets
curl http://localhost:9091/api/v1/targets
```

---

## 📊 Statistiques Clés (À RETENIR)

```
┌────────────────────────────────────────────────────────────────┐
│                    KEY METRICS                                 │
├────────────────────────────────────────────────────────────────┤
│ 📦 Données:                                                    │
│    • 188 Pokémon (Gen 1 + formes Alola)                       │
│    • 226 capacités                                             │
│    • 18 types (324 règles d'affinité)                         │
│    • 898,472 combats simulés (dataset ML)                     │
│    • 11 tables PostgreSQL (3NF)                               │
│                                                                 │
│ 🤖 Machine Learning:                                           │
│    • 94.46% accuracy (test set)                               │
│    • 133 features engineered                                   │
│    • < 500ms latence prédiction                               │
│    • XGBoost optimisé CPU                                      │
│                                                                 │
│ 🔧 Infrastructure:                                             │
│    • 9 services Docker                                         │
│    • 4 workflows GitHub Actions                                │
│    • 252 tests automatisés                                     │
│    • 82% code coverage                                         │
│    • 2 dashboards Grafana                                      │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Questions Jury Fréquentes

### Q: "Pourquoi 94.46% et pas plus?"

**R:** "Le modèle est volontairement équilibré entre accuracy et généralisation. Avec 188×188 matchups possibles et l'incertitude sur les capacités adverses, 94.46% est excellent. Un modèle à 99% risquerait l'overfitting."

---

### Q: "Comment gérez-vous le drift?"

**R:** "Evidently AI compare les prédictions production aux données de référence (10k samples) toutes les heures. Des rapports HTML avec tests statistiques (Kolmogorov-Smirnov) sont générés automatiquement. Si drift détecté, alerte pour retraining."

---

### Q: "Scalabilité de l'architecture?"

**R:** "L'architecture Docker Compose peut migrer vers Kubernetes (1 pod par service). FastAPI supporte 100+ req/s. PostgreSQL peut être remplacé par AWS RDS pour haute disponibilité. Redis peut être ajouté pour cache prédictions."

---

### Q: "Sécurité de l'API?"

**R:** "API Key authentication via header X-API-Key. Rate limiting (100 req/min par IP). CORS configuré. Endpoints publics: /health, /metrics, /docs uniquement. Production: HTTPS + WAF recommandés."

---

### Q: "CI/CD en détail?"

**R:** "4 workflows GitHub Actions:
1. Tests (252 tests, 82% coverage)
2. Build Docker (multi-stage optimisé)
3. ML Training (auto-register MLflow)
4. Deploy staging (si tests passent)

Trigger: push sur main ou PR."

---

## ✅ Validation Finale

### Checklist Compétences

**E1 - Données:**
- [x] E1.1: 3 sources (CSV, PokéAPI, Pokepedia)
- [x] E1.2: Nettoyage et validation
- [x] E1.3: BDD PostgreSQL 11 tables
- [x] E1.4: 133 features, notebooks
- [x] E1.5: Documentation complète

**E3 - IA Production:**
- [x] C9: API REST + XGBoost
- [x] C10: Streamlit 8 pages
- [x] C11: Prometheus + Grafana + Evidently
- [x] C12: < 500ms, 94.46% accuracy
- [x] C13: MLflow + GitHub Actions

---

**Score Global:** ✅ **10/10 compétences validées**

**Durée:** 30 minutes + 10 min Q&A

**Verdict:** ✅ **PRÊT POUR CERTIFICATION**

---

**Dernière mise à jour:** 27 janvier 2026
**Version:** 1.0

**🚀 BON COURAGE ! 🎯**
