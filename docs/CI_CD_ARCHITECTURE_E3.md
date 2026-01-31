# Architecture CI/CD - Alignée Certification E3 RNCP

## 📋 Vue d'ensemble

La chaîne CI/CD a été restructurée en **4 workflows spécialisés** pour répondre aux exigences de la certification **RNCP Niveau 6 - Compétences E3 (MLOps)**.

### 🎯 Objectifs de la restructuration

1. **Réduire le temps d'exécution** : 60min+ → ~30min max
2. **Paralléliser les tâches** : Workflows indépendants exécutables simultanément
3. **Clarifier les responsabilités** : Chaque workflow = 1 compétence E3
4. **Éliminer la redondance** : Plus de duplication de build/tests
5. **Aligner avec E3** : Mapping explicite vers C12, C13, C18, C19

---

## 🏗️ Architecture des 4 Workflows

```
┌─────────────────────────────────────────────────────────────┐
│                    Push / Pull Request                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├──────────┬──────────┬──────────┐
                   │          │          │          │
                   ▼          ▼          ▼          ▼
         ┌─────────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
         │ 1️⃣ Lint    │ │ 2️⃣ Unit │ │ 3️⃣ Docker│ │ ML      │
         │  & Format  │ │  Tests  │ │  Build   │ │ Pipeline │
         │   (C18)    │ │(C12+C18)│ │(C13+C19) │ │(C12+C13)│
         │   ~10min   │ │  ~15min │ │  ~20min  │ │ ~25min  │
         └─────────────┘ └─────────┘ └────┬─────┘ └─────────┘
                                          │
                                          │ Artifacts
                                          │ (Images)
                                          ▼
                                 ┌─────────────────┐
                                 │ 4️⃣ Integration │
                                 │     Tests      │
                                 │   (C13+C19)    │
                                 │    ~30min      │
                                 └─────────────────┘
```

---

## 🔢 Workflows détaillés

### 1️⃣ Lint & Format (`1-lint-and-format.yml`)

**Compétence E3** : **C18** - Automatiser les phases de tests lors de la mise en production

**Durée** : ~10 minutes

**Responsabilités** :
- ✅ Vérification formatage Black
- ✅ Tri des imports (isort)
- ✅ Linting (Flake8, Pylint, Mypy)
- ✅ Scan sécurité (Bandit, Safety)

**Triggers** :
- Push sur `main`, `develop`, `monitoring_grafana_evidently`, `nettoyage_clean_code_final`
- Pull requests vers `main`, `monitoring_grafana_evidently`

**Artifacts** :
- Rapports de sécurité (JSON)

---

### 2️⃣ Unit Tests (`2-tests-unit.yml`)

**Compétences E3** : **C12** (Tests automatisés) + **C18** (Intégration continue)

**Durée** : ~15 minutes

**Responsabilités** :
- ✅ Tests unitaires rapides (sans Docker)
- ✅ Coverage Python (api_pokemon, core, machine_learning)
- ✅ Tests avec PostgreSQL en service
- ✅ Upload coverage vers Codecov

**Triggers** :
- Push sur `main`, `develop`, `prototype_final_v1`, `nettoyage_clean_code_final`
- Pull requests vers `main`, `monitoring_grafana_evidently`

**Exclusions** :
- Tests lents (`-m "not slow"`)
- Tests d'intégration Docker

**Artifacts** :
- Coverage XML/JSON
- Rapports de tests

---

### 3️⃣ Docker Build (`3-docker-build.yml`)

**Compétences E3** : **C13** (Chaîne MLOps) + **C19** (Fiabilité déploiement)

**Durée** : ~20 minutes (parallélisé)

**Responsabilités** :
- ✅ Build parallèle de 5 images Docker :
  - `api` (FastAPI + modèle ML)
  - `etl` (Pokepedia scraper)
  - `ml` (Machine learning training)
  - `streamlit` (Interface utilisateur)
  - `mlflow` (Tracking & Registry)
- ✅ Cache Docker Buildx pour accélérer
- ✅ Sauvegarde artifacts pour workflow 4️⃣

**Stratégie** :
```yaml
strategy:
  fail-fast: false
  matrix:
    service: [api, etl, ml, streamlit, mlflow]
```

**Triggers** :
- Push sur `main`, `develop`, `monitoring_grafana_evidently`, `nettoyage_clean_code_final`
- Pull requests
- Dispatch manuel

**Artifacts** :
- Images Docker compressées (`.tar.gz`)
- Rétention : 1 jour

---

### 4️⃣ Integration Tests (`4-integration-tests.yml`)

**Compétences E3** : **C13** (Validation chaîne MLOps) + **C19** (Validation système)

**Durée** : ~30 minutes

**Responsabilités** :
- ✅ Démarrage stack Docker Compose complète
- ✅ Tests d'intégration end-to-end
- ✅ Health checks de tous les services :
  - PostgreSQL
  - API FastAPI
  - MLflow
  - Prometheus
  - Grafana
- ✅ Validation connectivité inter-services

**Déclenchement** :
- Automatique après succès de `3️⃣ Docker Build`
- Dispatch manuel

**Condition d'exécution** :
```yaml
if: ${{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}
```

**Artifacts** :
- Logs de tests d'intégration
- Rapports de santé des services

---

## 📊 Comparaison Avant/Après

| Aspect | ❌ Avant | ✅ Après |
|--------|---------|----------|
| **Nombre de workflows** | 7 workflows | 7 workflows (4 principaux + 3 spécialisés) |
| **Workflows principaux** | `complete-tests.yml` (monolithique) | 4 workflows spécialisés |
| **Temps total** | 60min+ (timeout dépassé) | ~30min max |
| **Exécution** | Séquentielle | Parallèle (1️⃣, 2️⃣, 3️⃣ simultanés) |
| **Redondance** | Oui (build dupliqué) | Non (artifacts réutilisés) |
| **Mapping E3** | Implicite | Explicite (nom + commentaires) |
| **Lisibilité** | Faible (monolithique) | Haute (séparation claire) |
| **Débogage** | Difficile (tout ensemble) | Facile (workflows isolés) |

---

## 🎓 Alignement Certification E3

### Compétence C12 : Tests automatisés du modèle IA

✅ **Workflows concernés** :
- `2️⃣ 2-tests-unit.yml` : Tests unitaires avec coverage
- `4️⃣ 4-integration-tests.yml` : Tests d'intégration complets
- `ml-pipeline.yml` : Tests spécifiques ML (training, evaluation)

✅ **Critères validés** :
- Framework de tests cohérent (pytest)
- Coverage définie et mesurée
- Tests versionnés sur Git
- Exécution automatique en CI

---

### Compétence C13 : Chaîne de livraison continue MLOps

✅ **Workflows concernés** :
- `3️⃣ 3-docker-build.yml` : Packaging Docker
- `4️⃣ 4-integration-tests.yml` : Validation chaîne complète
- `ml-pipeline.yml` : Entraînement et validation modèles

✅ **Critères validés** :
- Configuration reconnue par système (GitHub Actions)
- Étape de données de test intégrée
- Étapes train/validate fonctionnelles
- Déclenchement automatique (push, PR)
- Registry MLflow pour versioning modèles

---

### Compétence C18 : Intégration continue

✅ **Workflows concernés** :
- `1️⃣ 1-lint-and-format.yml` : Qualité code
- `2️⃣ 2-tests-unit.yml` : Tests unitaires
- Tous les workflows (déclenchés sur push/PR)

✅ **Critères validés** :
- Automatisation complète
- Déclenchement sur versioning Git
- Feedback rapide (<15min pour lint+unit tests)
- Rapports de qualité et tests

---

### Compétence C19 : Gestion incidents et fiabilité

✅ **Workflows concernés** :
- `3️⃣ 3-docker-build.yml` : Assure builds reproductibles
- `4️⃣ 4-integration-tests.yml` : Validation système complète

✅ **Critères validés** :
- Tests d'intégration couvrant tous les services
- Health checks automatiques
- Logs détaillés en cas d'échec
- Cleanup automatique des ressources

---

## 🚀 Utilisation

### Workflow automatique (recommandé)

```bash
# 1. Développer et tester localement
pytest tests/ -v

# 2. Commit et push
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push

# 3. GitHub Actions exécute automatiquement :
#    - 1️⃣ Lint & Format (parallèle)
#    - 2️⃣ Unit Tests (parallèle)
#    - 3️⃣ Docker Build (parallèle)
#    - 4️⃣ Integration Tests (après 3️⃣)
```

### Workflow manuel

```bash
# Déclencher un workflow spécifique via GitHub UI :
# Actions → Workflow souhaité → "Run workflow"

# Ou via GitHub CLI :
gh workflow run "3️⃣ Docker Build (C13 + C19)"
```

---

## 📈 Monitoring et métriques

### Temps d'exécution cible

| Workflow | Temps cible | Timeout |
|----------|-------------|---------|
| 1️⃣ Lint | 5-10min | 10min |
| 2️⃣ Unit Tests | 10-15min | 15min |
| 3️⃣ Docker Build | 15-20min | 20min |
| 4️⃣ Integration | 20-30min | 30min |

### Métriques de succès

- ✅ Taux de réussite > 95%
- ✅ Temps total < 30min
- ✅ Parallélisation effective (1️⃣, 2️⃣, 3️⃣)
- ✅ Pas de timeout dépassé

---

## 🔧 Maintenance

### Ajouter un nouveau test

1. **Test unitaire** → Ajouter dans `tests/api/`, `tests/ml/`, etc.
   - Exécuté par `2️⃣ Unit Tests`

2. **Test d'intégration** → Ajouter dans `tests/integration/`
   - Exécuté par `4️⃣ Integration Tests`

3. **Test ML spécifique** → Ajouter dans `tests/ml/`
   - Exécuté par `ml-pipeline.yml`

### Modifier un workflow

1. Éditer `.github/workflows/X-nom.yml`
2. Tester localement avec `act` (si possible)
3. Push et vérifier sur GitHub Actions

### Déboguer un échec

```bash
# Voir les logs du workflow
gh run list
gh run view <run_id> --log

# Télécharger les artifacts
gh run download <run_id>

# Relancer un workflow échoué
gh run rerun <run_id>
```

---

## 📚 Ressources

- [Documentation GitHub Actions](https://docs.github.com/en/actions)
- [Certification RNCP - Compétences E3](../A_VALIDER_POUR_CERTIF.md)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MLflow Documentation](https://mlflow.org/)

---

## ✅ Checklist Certification E3

### C12 - Tests automatisés
- [x] Framework de tests cohérent (pytest)
- [x] Tests unitaires automatisés (`2-tests-unit.yml`)
- [x] Tests d'intégration automatisés (`4-integration-tests.yml`)
- [x] Coverage mesurée et reportée
- [x] Tests versionnés sur Git

### C13 - Chaîne MLOps
- [x] Configuration CI/CD reconnue (GitHub Actions)
- [x] Étape de données de test (`4-integration-tests.yml`)
- [x] Étapes train/validate (`ml-pipeline.yml`)
- [x] Packaging automatisé (`3-docker-build.yml`)
- [x] Registry modèles (MLflow)

### C18 - Intégration continue
- [x] Automatisation complète
- [x] Déclenchement sur Git push/PR
- [x] Feedback rapide (lint + unit tests < 20min)
- [x] Qualité code vérifiée (`1-lint-and-format.yml`)

### C19 - Fiabilité
- [x] Tests d'intégration complets
- [x] Health checks automatiques
- [x] Logs détaillés en cas d'échec
- [x] Cleanup automatique ressources

---

**Date de restructuration** : 31 janvier 2026  
**Auteur** : Équipe Lets-Go PredictionDex  
**Version** : 2.0 (Architecture E3)
