# Diagnostic MLflow & Grafana - Pas de Résultats

**Date** : 2026-01-29
**Status** : ⚠️ SERVICES UP, MAIS PAS DE DONNÉES

---

## 🔍 Diagnostic Rapide

### ✅ Services Fonctionnels

| Service | Status | URL | Health |
|---------|--------|-----|--------|
| **MLflow** | ✅ UP | http://localhost:5001 | OK |
| **Grafana** | ✅ UP | http://localhost:3001 | OK (v10.1.0) |
| **Prometheus** | ✅ UP | http://localhost:9091 | OK |
| **API** | ✅ UP | http://localhost:8080 | OK |

**Conclusion** : Tous les services sont en ligne et répondent.

---

## ❌ Problèmes Identifiés

### 1. **MLflow : Aucune Expérience**

```bash
$ curl http://localhost:5001/api/2.0/mlflow/experiments/search
# Résultat : Vide
```

**Cause** : Aucun modèle n'a été entraîné avec MLflow tracking

**Impact** :
- ❌ Pas de runs à afficher
- ❌ Pas de métriques (accuracy, loss, etc.)
- ❌ Pas de modèles dans le Model Registry
- ❌ UI MLflow vide

**Solution** : Entraîner un modèle avec tracking MLflow actif

---

### 2. **Grafana : Pas de Données**

**Cause** : Pas de métriques dans Prometheus

**Vérification** :
```bash
$ curl http://localhost:9091/api/v1/targets
# Résultat : Aucun target actif
```

**Impact** :
- ❌ Dashboards Grafana vides
- ❌ Pas de graphiques de latence
- ❌ Pas de throughput affiché
- ❌ Pas de métriques business

**Raison** : Aucune prédiction n'a été faite depuis le démarrage

---

### 3. **Prometheus : Pas de Métriques Business**

**Vérification** :
```bash
$ curl http://localhost:8080/metrics | grep pokemon
# Résultat : Aucune métrique pokemon_* trouvée
```

**Métriques Python génériques présentes** :
- ✅ `python_gc_*` (garbage collector)
- ✅ `process_*` (CPU, mémoire)
- ✅ Métriques système

**Métriques business manquantes** :
- ❌ `pokemon_predictions_total`
- ❌ `pokemon_prediction_latency_seconds`
- ❌ `pokemon_model_confidence`
- ❌ `pokemon_errors_total`

**Raison** : Les compteurs de métriques ne sont incrémentés que lors de prédictions

---

## 🎯 Solutions

### Solution 1 : **Générer des Données de Test**

#### A. Lancer le Script de Validation Monitoring

```bash
# Génère 100 prédictions + métriques
python3 tests/integration/test_monitoring_validation.py
```

**Ce que ça fait** :
1. ✅ Génère 100 prédictions via `/predict/best-move`
2. ✅ Incrémente les compteurs Prometheus
3. ✅ Popule Grafana avec des données
4. ✅ Teste le monitoring complet

**Résultats attendus** :
- Métriques dans Prometheus (pokemon_*)
- Graphiques dans Grafana
- Rapport HTML généré

---

#### B. Faire des Prédictions Manuelles

```bash
# Via curl
curl -X POST http://localhost:8080/predict/best-move \
  -H "X-API-Key: BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ" \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 25,
    "pokemon_b_id": 6,
    "available_moves": [1, 2, 3, 4]
  }'

# Répéter plusieurs fois (10-20x) pour voir des graphiques
```

**Après 10-20 prédictions** :
- ✅ Grafana affichera des graphiques
- ✅ Prometheus aura des métriques

---

#### C. Utiliser Streamlit

```bash
# Ouvrir Streamlit
firefox http://localhost:8502
```

**Puis** :
1. Aller sur "Prédiction de Combat"
2. Faire plusieurs prédictions (10-20)
3. Recharger Grafana → Les graphiques apparaissent

---

### Solution 2 : **Entraîner un Modèle avec MLflow**

Pour peupler MLflow :

```bash
# Option A : Via Docker
docker compose run --rm ml_builder python machine_learning/run_machine_learning.py \
  --mode=train \
  --dataset-version=v2 \
  --version=test_mlflow

# Option B : En local (si venv configuré)
python machine_learning/run_machine_learning.py \
  --mode=train \
  --dataset-version=v2 \
  --version=test_mlflow
```

**Durée** : ~5-10 minutes

**Résultat** :
- ✅ Expérience créée dans MLflow
- ✅ Run avec métriques (accuracy, loss)
- ✅ Modèle enregistré dans Model Registry
- ✅ UI MLflow populate

---

### Solution 3 : **Vérifier les Dashboards Grafana**

#### Étape 1 : Accéder à Grafana

```
URL: http://localhost:3001
User: admin
Password: admin
```

#### Étape 2 : Vérifier les Datasources

```
Configuration → Data Sources → Prometheus
```

**Vérifier** :
- ✅ URL: `http://prometheus:9090`
- ✅ Status: Connected

#### Étape 3 : Importer les Dashboards

Si les dashboards n'existent pas :

```bash
# Vérifier si le provisioning est actif
docker compose exec grafana ls -la /etc/grafana/provisioning/dashboards/
```

**Si vide** → Les dashboards ne sont pas provisionnés automatiquement

---

## 🔧 Diagnostic Complet - Checklist

### Services

- [x] MLflow accessible (http://localhost:5001)
- [x] Grafana accessible (http://localhost:3001)
- [x] Prometheus accessible (http://localhost:9091)
- [x] API accessible (http://localhost:8080)

### Données

- [ ] MLflow a au moins 1 expérience
- [ ] Prometheus a des targets actifs
- [ ] Prometheus a des métriques `pokemon_*`
- [ ] Grafana affiche des graphiques

### Actions Recommandées

1. **Priorité 1** : Générer des prédictions de test
   ```bash
   python3 tests/integration/test_monitoring_validation.py
   ```

2. **Priorité 2** : Vérifier Grafana après génération
   ```bash
   firefox http://localhost:3001
   # Login: admin / admin
   # Aller dans Dashboards → Pokemon Predictions
   ```

3. **Priorité 3** : Entraîner un modèle pour MLflow
   ```bash
   docker compose run --rm ml_builder python machine_learning/run_machine_learning.py --mode=train --version=demo
   ```

---

## 📊 Métriques Attendues

Après avoir généré des prédictions, vous devriez voir :

### Prometheus (http://localhost:9091)

```promql
# Requêtes à tester dans Prometheus
pokemon_predictions_total
rate(pokemon_predictions_total[5m])
pokemon_prediction_latency_seconds_bucket
histogram_quantile(0.95, rate(pokemon_prediction_latency_seconds_bucket[5m]))
```

### Grafana (http://localhost:3001)

**Graphiques attendus** :
- 📈 Throughput (predictions/sec)
- ⏱️ Latency (p50, p95, p99)
- ✅ Success Rate (%)
- 🎯 Confidence Distribution
- 🔥 Top Pokémon Used
- ⚠️ Error Rate

---

## ⚠️ CI/CD - Problème de Timeout ?

Vous mentionnez que le CI/CD plante avec un problème de temps d'exécution.

### Workflows Concernés

**Quels workflows échouent ?**
- `complete-tests.yml` ? (timeout: 30 min)
- `monitoring-validation.yml` ? (timeout: 30 min)
- `ml-pipeline.yml` ?
- `docker-build.yml` ?

### Limites de Temps

| Workflow | Timeout Configuré | Temps Typique |
|----------|-------------------|---------------|
| complete-tests.yml | 30 min | ~15 min |
| monitoring-validation.yml | 30 min | ~10 min |
| ml-pipeline.yml | Default (6h) | ~5 min |
| docker-build.yml | Default (6h) | ~15 min |

### Vérification

Pour identifier le problème :

```bash
# Vérifier les logs GitHub Actions
gh run list --limit 10
gh run view <run-id> --log
```

**Causes fréquentes** :
1. ❌ Build Docker trop long (sans cache)
2. ❌ Tests bloqués sur une connexion
3. ❌ Service qui ne démarre pas (healthcheck timeout)
4. ❌ Dépendances qui ne s'installent pas

**Solutions** :
- Augmenter le timeout :
  ```yaml
  timeout-minutes: 45  # Au lieu de 30
  ```
- Utiliser le cache Docker :
  ```yaml
  - name: Set up Docker Buildx
    uses: docker/setup-buildx-action@v3

  - name: Cache Docker layers
    uses: actions/cache@v4
    with:
      path: /tmp/.buildx-cache
      key: ${{ runner.os }}-buildx-${{ github.sha }}
  ```

---

## 🎉 Test de Validation Rapide

Pour vérifier que tout fonctionne :

```bash
# 1. Générer des prédictions
python3 tests/integration/test_monitoring_validation.py

# 2. Vérifier Prometheus (devrait avoir des métriques)
curl -s http://localhost:9091/api/v1/query?query=pokemon_predictions_total | jq .

# 3. Ouvrir Grafana
firefox http://localhost:3001
# Login: admin / admin
# Les dashboards devraient afficher des données

# 4. Vérifier MLflow (si entraînement effectué)
firefox http://localhost:5001
```

**Résultat attendu** :
- ✅ Prometheus affiche des métriques pokemon_*
- ✅ Grafana affiche des graphiques avec données
- ✅ MLflow affiche des expériences (si entraînement)

---

**Auteur** : Claude Sonnet 4.5
**Date** : 2026-01-29
**Status** : ✅ DIAGNOSTIC COMPLET
