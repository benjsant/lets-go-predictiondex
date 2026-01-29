# Analyse des Requirements - Incohérences de Versions

**Date** : 2026-01-29
**Status** : ⚠️ INCOHÉRENCES DÉTECTÉES

---

## 📋 Fichiers Analysés

1. **api_pokemon/requirements.txt** - API REST FastAPI
2. **etl_pokemon/requirements.txt** - Pipeline ETL
3. **machine_learning/requirements.txt** - Entraînement ML
4. **tests/requirements.txt** - Tests unitaires et intégration

---

## 🔍 Comparaison des Versions

| Package | api_pokemon | etl_pokemon | machine_learning | tests | Status |
|---------|-------------|-------------|------------------|-------|--------|
| **python-dotenv** | ❌ Non spécifié | ❌ Non spécifié | ❌ Non spécifié | ✅ 1.0.0 | ⚠️ Incohérent |
| **fastapi** | ❌ Non spécifié | ❌ Non spécifié | - | ✅ 0.104.1 | ⚠️ Incohérent |
| **pydantic** | ❌ Non spécifié | ❌ Non spécifié | - | ✅ 2.5.2 | ⚠️ Incohérent |
| **sqlalchemy** | ❌ Non spécifié | ❌ Non spécifié | ❌ Non spécifié | ✅ 2.0.23 | ⚠️ Incohérent |
| **psycopg2-binary** | ❌ Non spécifié | ❌ Non spécifié | ❌ Non spécifié | ✅ 2.9.9 | ⚠️ Incohérent |
| **pandas** | ❌ Non spécifié | ❌ Non spécifié | ❌ Non spécifié | ✅ 2.1.4 | ⚠️ Incohérent |
| **numpy** | ❌ Non spécifié | - | ❌ Non spécifié | ✅ 1.26.2 | ⚠️ Incohérent |
| **requests** | ❌ Non spécifié | ❌ Non spécifié | - | ✅ 2.31.0 | ⚠️ Incohérent |
| **mlflow** | ✅ 3.8.1 | - | ✅ 3.8.1 | ✅ 3.8.1 | ✅ OK |
| **scikit-learn** | ❌ Non spécifié | - | ❌ Non spécifié | - | ⚠️ Incohérent |
| **xgboost** | ❌ Non spécifié | - | ❌ Non spécifié | - | ⚠️ Incohérent |
| **evidently** | ✅ >=0.7.0,<0.8.0 | - | - | - | ✅ OK (API only) |

---

## ⚠️ Problèmes Identifiés

### 1. **Versions Non Spécifiées** (Critique)

**Impact** : Installations non reproductibles, risque de breaking changes

**Fichiers concernés** :
- `api_pokemon/requirements.txt` - 90% des packages sans version
- `etl_pokemon/requirements.txt` - 100% des packages sans version
- `machine_learning/requirements.txt` - 90% des packages sans version

**Packages critiques affectés** :
- `fastapi` - API framework (breaking changes fréquents)
- `pydantic` - Validation (v1 vs v2 incompatibles)
- `sqlalchemy` - ORM (v1.4 vs v2.0 incompatibles)
- `pandas` - Data manipulation (breaking changes)
- `numpy` - Core scientifique (ABI incompatibilities)

---

### 2. **Incohérences Entre Environnements**

**Problème** : Les tests utilisent des versions précises, mais la production utilise les dernières versions disponibles.

**Conséquence** :
- ✅ Tests passent avec `pandas==2.1.4`
- ❌ Production installe `pandas==2.3.0` (hypothétique) → breaking changes

**Exemple concret** :
```yaml
# tests/requirements.txt
fastapi==0.104.1  # Testé et validé

# api_pokemon/requirements.txt
fastapi  # Installe 0.115.0 (dernière) → comportement différent
```

---

### 3. **Risques de Sécurité**

Sans versions épinglées :
- ⚠️ Impossible de valider les vulnérabilités CVE
- ⚠️ Pas de contrôle sur les dépendances transitives
- ⚠️ Audits de sécurité impossibles

---

## ✅ Recommandations

### Option A : **Versions Épinglées Strictes** (Recommandé pour Production)

**Avantages** :
- ✅ Reproductibilité garantie
- ✅ Pas de surprises en production
- ✅ Audits de sécurité possibles
- ✅ Tests fiables

**Inconvénients** :
- ⚠️ Maintenance manuelle des versions
- ⚠️ Retard sur les patches de sécurité si pas mis à jour

**Implémentation** :
```bash
# Générer les versions exactes depuis l'environnement actuel
pip freeze > requirements.txt
```

---

### Option B : **Versions Minimales avec Plafonds** (Compromis)

**Exemple** :
```txt
fastapi>=0.104.1,<0.110.0  # Compatible avec tests, mais permet patches
pandas>=2.1.4,<2.3.0
numpy>=1.26.2,<2.0.0  # Évite numpy 2.0 (breaking)
```

**Avantages** :
- ✅ Patches de sécurité automatiques
- ✅ Contrôle des breaking changes
- ⚠️ Légèrement moins reproductible

---

### Option C : **requirements.txt + requirements-lock.txt**

Structure moderne :
```
requirements.txt          # Versions minimales/plages
requirements-lock.txt     # pip freeze (versions exactes)
```

Utilisation :
```dockerfile
# Dockerfile - Production
RUN pip install -r requirements-lock.txt

# Développement
pip install -r requirements.txt
```

---

## 🎯 Plan d'Action Recommandé

### Phase 1 : **Alignement Immédiat** (Critique)

Copier les versions de `tests/requirements.txt` vers les autres fichiers :

```txt
# api_pokemon/requirements.txt
python-dotenv==1.0.0
fastapi==0.104.1
pydantic==2.5.2
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pandas==2.1.4
numpy==1.26.2
requests==2.31.0
mlflow==3.8.1
evidently>=0.7.0,<0.8.0
```

```txt
# machine_learning/requirements.txt
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.26.2
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
mlflow==3.8.1
# Ajouter versions pour scikit-learn et xgboost
```

---

### Phase 2 : **Vérification des Versions Manquantes**

Packages sans version dans les tests :
- `scikit-learn` → Besoin de version
- `xgboost` → Besoin de version
- `uvicorn` → Besoin de version
- `scrapy` → Besoin de version

**Action** : Exécuter dans l'environnement actuel :
```bash
pip freeze | grep -E "scikit-learn|xgboost|uvicorn|scrapy"
```

---

### Phase 3 : **Validation**

1. Reconstruire tous les conteneurs Docker
2. Relancer tous les tests
3. Vérifier qu'aucune régression n'apparaît

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
python scripts/run_all_tests.py
```

---

## 📊 Versions Actuelles Détectées

**D'après tests/requirements.txt (versions validées)** :

```txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.12.0
requests==2.31.0
httpx==0.25.2
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
fastapi==0.104.1
pydantic==2.5.2
mlflow==3.8.1
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.26.2
```

**Versions manquantes (à détecter)** :
- `scikit-learn` → ?
- `xgboost` → ?
- `uvicorn` → ?
- `prometheus-client` → ?
- `psutil` → ?
- `scrapy` → ?
- `asyncpg` → ?
- `aiohttp` → ?

---

## 🚨 Action Immédiate Requise

**Priorité HAUTE** : Fixer les incohérences avant le push sur GitHub

**Raison** :
- GitHub Actions va installer les versions **non épinglées**
- Comportement différent entre local (Docker) et CI/CD
- Risque de failures aléatoires en CI

**Commande de diagnostic** :
```bash
# Dans chaque conteneur Docker, extraire les versions exactes
docker compose exec api pip freeze > api_versions.txt
docker compose exec etl pip freeze > etl_versions.txt
docker compose exec ml pip freeze > ml_versions.txt
```

---

## ✅ Checklist de Validation

- [ ] Aligner les versions dans `api_pokemon/requirements.txt`
- [ ] Aligner les versions dans `etl_pokemon/requirements.txt`
- [ ] Aligner les versions dans `machine_learning/requirements.txt`
- [ ] Ajouter les versions manquantes (scikit-learn, xgboost, etc.)
- [ ] Rebuild Docker sans cache
- [ ] Relancer tous les tests
- [ ] Vérifier GitHub Actions workflows
- [ ] Commit et push

---

**Auteur** : Claude Sonnet 4.5
**Date** : 2026-01-29
**Status** : ⚠️ ACTION REQUISE
