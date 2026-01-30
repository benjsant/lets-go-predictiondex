# 📊 Explication du Monitoring - Let's Go PredictionDex

**Date**: 2026-01-29
**Status**: ✅ Monitoring Opérationnel

---

## 🎯 Vue d'Ensemble

Votre projet utilise **3 systèmes de monitoring complémentaires**:

1. **Grafana + Prometheus** → Monitoring temps réel (métriques, performance, erreurs)
2. **MLflow** → Tracking des expériences ML et registry de modèles
3. **Evidently AI** → Détection de drift des données (Data Drift)

---

## 📈 1. GRAFANA - Dashboards en Temps Réel

Grafana collecte des métriques depuis Prometheus toutes les 15 secondes.

### Dashboard 1: **Model Performance** 🤖

**URL**: http://localhost:3001/d/letsgo-model

Ce dashboard surveille **les performances du modèle ML** en production.

#### Panneaux (8 au total):

##### Row 1 - Vue d'Ensemble (Stats)

1. **Predictions per Minute**
   - **Quoi**: Nombre de prédictions faites par minute
   - **Métrique**: `model_predictions_total` (rate sur 1 min)
   - **Utilité**: Surveiller le throughput du modèle
   - **Alerte si**: Chute brutale = problème API/modèle

2. **Model Confidence (Avg)**
   - **Quoi**: Confiance moyenne du modèle dans ses prédictions
   - **Métrique**: `model_confidence_score_sum / model_confidence_score_count`
   - **Plage**: 0.0 à 1.0 (0 = pas confiant, 1 = très confiant)
   - **Couleurs**:
     - 🔴 Rouge: < 0.6 (confiance faible)
     - 🟡 Jaune: 0.6 - 0.8 (confiance moyenne)
     - 🟢 Vert: > 0.8 (confiance élevée)
   - **Utilité**: Détecter si le modèle devient incertain (possible drift)

3. **P95 Prediction Latency**
   - **Quoi**: 95% des prédictions sont effectuées en moins de X secondes
   - **Métrique**: `histogram_quantile(0.95, model_prediction_duration_seconds_bucket)`
   - **Unité**: Secondes
   - **Couleurs**:
     - 🟢 Vert: < 0.05s (rapide)
     - 🟡 Jaune: 0.05s - 0.1s (acceptable)
     - 🔴 Rouge: > 0.1s (lent)
   - **Utilité**: Garantir des temps de réponse acceptables
   - **Valeur actuelle**: ~0.45s (à optimiser si critique)

4. **Total Predictions**
   - **Quoi**: Nombre total de prédictions depuis le démarrage
   - **Métrique**: `model_predictions_total` (cumulative)
   - **Utilité**: Tracker l'utilisation globale du modèle

##### Row 2 - Latence et Confiance (Graphs Temporels)

5. **Prediction Latency Percentiles**
   - **Quoi**: Évolution de la latence dans le temps (P50, P95, P99)
   - **Métriques**:
     - P50 (médiane): 50% des requêtes plus rapides
     - P95: 95% des requêtes plus rapides
     - P99: 99% des requêtes plus rapides
   - **Utilité**: Détecter les pics de latence et problèmes de performance
   - **Légende**: Affiche mean et max

6. **Model Confidence Over Time**
   - **Quoi**: Évolution de la confiance moyenne au fil du temps
   - **Métrique**: Rate de `model_confidence_score` sur l'intervalle
   - **Utilité**: Détecter une dégradation progressive du modèle
   - **Alerte si**: Tendance à la baisse = possible data drift

##### Row 3 - Distribution et Versions (Pie Chart + Graph)

7. **Win Probability Distribution**
   - **Quoi**: Répartition des prédictions par probabilité de victoire
   - **Type**: Pie chart (camembert)
   - **Métrique**: `model_win_probability_bucket` (histogram)
   - **Buckets**: Probabilités groupées (≤ 0.1, ≤ 0.3, ≤ 0.5, etc.)
   - **Utilité**: Vérifier que le modèle prédit une distribution réaliste
   - **Exemple sain**: Distribution équilibrée (pas 100% dans un seul bucket)

8. **Predictions Rate by Model Version**
   - **Quoi**: Taux de prédictions par version de modèle (si A/B testing)
   - **Métrique**: `model_predictions_total` groupé par `model_version`
   - **Utilité**: Comparer plusieurs versions de modèle en parallèle
   - **Usage**: Utile pour rollout progressif (v1 vs v2)

---

### Dashboard 2: **API Performance** 🚀

**URL**: http://localhost:3001/d/letsgo-api

Ce dashboard surveille **la santé de l'API FastAPI** en production.

#### Panneaux (probablement 6-8):

##### Métriques Typiques:

1. **Request Rate**
   - Nombre de requêtes HTTP par seconde
   - Métrique: `api_requests_total` (rate)

2. **Error Rate**
   - Pourcentage d'erreurs HTTP (4xx, 5xx)
   - Métrique: `(api_errors_total or vector(0)) / (api_requests_total or vector(1))`
   - **Fixé**: Affiche 0% au lieu de "no data" quand pas d'erreurs

3. **Response Time**
   - Latence des endpoints API (P50, P95, P99)
   - Métrique: `histogram_quantile()` sur `api_request_duration_seconds`

4. **Requests by Endpoint**
   - Répartition du trafic par endpoint (/predict, /health, /docs, etc.)
   - Métrique: `api_requests_total` groupé par `path`

5. **Status Codes Distribution**
   - Répartition des codes HTTP (200, 400, 500, etc.)
   - Métrique: `api_requests_total` groupé par `status_code`

6. **API Uptime**
   - Disponibilité de l'API (0-100%)
   - Métrique: Basé sur health checks

---

## 🧪 2. MLFLOW - Tracking & Model Registry

**URL**: http://localhost:5001

### Qu'est-ce que MLflow fait actuellement?

MLflow remplit **3 rôles majeurs** dans votre projet:

#### A) 📊 **Tracking des Expériences**

**Objectif**: Enregistrer tous les détails de chaque entraînement de modèle.

**Ce qui est tracké**:

```python
# À chaque entraînement, MLflow enregistre:
mlflow.log_params({
    "model_type": "XGBoost",
    "n_estimators": 200,
    "max_depth": 7,
    "learning_rate": 0.05,
    # ... tous les hyperparamètres
})

mlflow.log_metrics({
    "accuracy": 0.94,
    "precision": 0.92,
    "recall": 0.95,
    "f1_score": 0.935,
    "roc_auc": 0.98
})

mlflow.log_artifact("confusion_matrix.png")
mlflow.log_artifact("feature_importance.csv")
```

**Utilité**:
- Comparer différentes versions du modèle
- Retrouver les meilleurs hyperparamètres
- Reproduire un entraînement exact
- Auditer l'évolution du modèle

**Dans l'UI MLflow**:
- Onglet **Experiments**: Liste toutes vos expériences
- Onglet **Runs**: Détails de chaque entraînement
- Tableau comparatif avec tri/filtre sur les métriques

#### B) 📦 **Model Registry**

**Objectif**: Versionner et déployer les modèles ML comme des packages.

**Workflow**:

1. **Enregistrement du modèle**:
   ```python
   mlflow.sklearn.log_model(model, "xgboost_model")
   # Crée automatiquement le modèle dans le registry
   ```

2. **Versioning automatique**:
   - Version 1: Premier modèle (2026-01-15)
   - Version 2: Modèle amélioré (2026-01-20)
   - Version 3: Modèle avec nouvelles features (2026-01-29)

3. **Stages de déploiement**:
   - `None`: Modèle en développement
   - `Staging`: Modèle en test
   - `Production`: Modèle actif en prod
   - `Archived`: Ancien modèle archivé

**Utilité**:
- Rollback facile en cas de problème (revenir à v2)
- Comparer v2 (staging) vs v3 (production)
- Traçabilité: savoir quel modèle est où

**Dans l'UI MLflow**:
- Onglet **Models**: Liste des modèles enregistrés
- Détails: Versions, stages, artifacts, lineage

#### C) 🔗 **Intégration avec l'API**

**Objectif**: Charger automatiquement le modèle depuis MLflow.

**Code actuel** (dans `machine_learning/mlflow_integration.py`):

```python
def load_production_model():
    """
    Charge le modèle en production depuis MLflow.

    Recherche le modèle avec stage='Production' dans le registry.
    Fallback sur la dernière version si pas de modèle en production.
    """
    client = MlflowClient()

    # Cherche le modèle en production
    versions = client.search_model_versions(
        filter_string="name='pokemon_battle_model' AND status='Production'"
    )

    if versions:
        model_uri = f"models:/{MODEL_NAME}/Production"
        model = mlflow.sklearn.load_model(model_uri)
        return model
    else:
        # Fallback sur la dernière version
        model_uri = f"models:/{MODEL_NAME}/latest"
        model = mlflow.sklearn.load_model(model_uri)
        return model
```

**Avantages**:
- API charge toujours le bon modèle automatiquement
- Mise à jour du modèle sans redéployer l'API
- Rollback instantané en cas de régression

---

## 🔍 3. EVIDENTLY AI - Data Drift Detection

**URL**: Rapports HTML générés localement
**Fichier**: `api_pokemon/monitoring/drift_detection.py`

### Qu'est-ce qu'Evidently fait?

**Objectif**: Détecter si les données en production **dérivent** par rapport aux données d'entraînement.

#### Concept de "Data Drift"

**Définition**: Les distributions statistiques changent entre train et production.

**Exemple concret**:

```
📊 Données d'entraînement (2025):
- Pokémon Type 1: Eau (30%), Feu (25%), Plante (20%), autres (25%)
- Niveau moyen: 50
- Stats moyennes: Attack=80, Defense=75

📊 Données en production (2026):
- Pokémon Type 1: Eau (60%), Feu (10%), Plante (5%), autres (25%)  ← DRIFT!
- Niveau moyen: 65  ← DRIFT!
- Stats moyennes: Attack=95, Defense=70  ← DRIFT!
```

**Conséquence**: Le modèle a été entraîné sur une distribution, mais voit une autre en prod → **performances dégradées**.

#### Comment ça fonctionne dans votre projet?

##### 1. **Chargement des Données de Référence**

Au démarrage de l'API:

```python
# Charge X_train.parquet (données d'entraînement)
reference_data = pd.read_parquet("data/datasets/X_train.parquet")
sampled_reference = reference_data.sample(n=10000, random_state=42)

# Crée un Dataset Evidently
reference_dataset = Dataset.from_pandas(sampled_reference)
```

##### 2. **Buffer des Prédictions en Production**

À chaque prédiction via l'API:

```python
# Enregistre les features + prédiction
drift_detector.add_prediction(
    features={
        'pokemon_a_type_1': 'Water',
        'pokemon_a_attack': 95,
        'pokemon_b_defense': 80,
        # ... toutes les features
    },
    prediction=1,  # Pokémon A gagne
    probability=0.87
)

# Stocke dans un buffer (max 1000 prédictions)
```

##### 3. **Génération Automatique de Rapports**

**Triggers**:
- Buffer plein (1000 prédictions)
- OU toutes les 1h

**Actions**:

```python
# Compare production vs référence
report = Report([DataDriftPreset()])
report.run(production_dataset, reference_dataset)

# Génère 2 fichiers:
# 1. drift_dashboard_20260129_153045.html  ← Dashboard interactif
# 2. drift_report_20260129_153045.json     ← Métriques JSON
```

##### 4. **Alertes et Métriques**

**Rapport JSON contient**:

```json
{
  "timestamp": "20260129_153045",
  "n_features": 45,
  "n_drifted_features": 8,
  "share_drifted_features": 0.178,  // 17.8% des features ont drifté
  "dataset_drift": true  // ⚠️ ALERTE DRIFT DÉTECTÉ
}
```

**Tableau HTML montre**:
- ✅ Features stables (pas de drift)
- ⚠️ Features avec drift léger
- 🔴 Features avec drift sévère

**Actions correctives**:
- Si drift < 20%: Surveiller
- Si drift > 30%: Re-entraîner le modèle
- Si drift > 50%: Re-collecter des données

#### Où trouver les rapports?

```bash
# Rapports HTML (ouvrir dans navigateur)
api_pokemon/monitoring/drift_reports/drift_dashboard_*.html

# Métriques JSON (pour automatisation)
api_pokemon/monitoring/drift_reports/drift_summary_*.json

# Données de production sauvegardées
api_pokemon/monitoring/drift_data/production_data_*.parquet
```

---

## 🔄 Comment les 3 Systèmes Travaillent Ensemble

### Scénario: Détection d'un Problème de Modèle

#### Timeline:

**J+0 - Déploiement Initial**:
1. MLflow: Modèle v2 en production (accuracy=94%)
2. Grafana: Model Confidence = 0.92 (bon)
3. Evidently: Drift = 0% (normal)

**J+7 - Premiers Signes**:
1. Grafana: Model Confidence baisse à 0.75 ⚠️
2. Grafana: Win Probability Distribution devient déséquilibrée
3. Aucune alerte encore

**J+14 - Alerte Drift**:
1. Evidently génère un rapport: **Drift détecté sur 35% des features** 🔴
2. Grafana: Model Confidence = 0.68 (rouge)
3. MLflow: Compare v2 (prod) vs v1 (archive) → metrics similaires
4. **Action**: Besoin de re-entraînement avec nouvelles données

**J+15 - Re-entraînement**:
1. MLflow: Nouveau run d'entraînement avec données récentes
2. MLflow: Enregistre modèle v3 (accuracy=95%, prend en compte le drift)
3. MLflow: v3 en Staging pour tests

**J+16 - Tests A/B**:
1. Grafana: "Predictions by Model Version" montre v2 (80%) vs v3 (20%)
2. Grafana: v3 a meilleure confidence (0.91 vs 0.68)
3. Evidently: Drift de v3 = 5% (acceptable)

**J+17 - Rollout v3**:
1. MLflow: Promouvoir v3 en Production
2. API: Charge automatiquement v3 depuis MLflow
3. Grafana: Model Confidence remonte à 0.92 ✅
4. Evidently: Drift stabilisé à 8%

---

## 📋 Récapitulatif des Rôles

| Système | Rôle | Fréquence | Alertes |
|---------|------|-----------|---------|
| **Grafana** | Monitoring temps réel | 15 secondes | Latence, erreurs, throughput |
| **MLflow** | Gestion des modèles | Par entraînement | Aucune (registry passif) |
| **Evidently** | Détection de drift | 1 heure | Drift > seuil (30%) |

### Grafana
- ✅ **Quand l'utiliser**: Surveillance continue (24/7)
- ✅ **Pour détecter**: Problèmes de performance, erreurs, anomalies
- ✅ **Réaction**: Immédiate (alertes en temps réel)

### MLflow
- ✅ **Quand l'utiliser**: Développement de modèles, déploiement
- ✅ **Pour gérer**: Versions de modèles, expériences ML
- ✅ **Réaction**: Manuelle (data scientist décide)

### Evidently
- ✅ **Quand l'utiliser**: Validation périodique des données
- ✅ **Pour détecter**: Changements de distribution, data drift
- ✅ **Réaction**: Planifiée (re-entraînement si nécessaire)

---

## 🎯 Utilisation Pratique

### Pour la Démonstration

1. **Générer des données de test**:
   ```bash
   python3 scripts/populate_monitoring.py
   ```
   → Crée 50 prédictions + 3 runs MLflow

2. **Ouvrir Grafana**:
   ```bash
   open http://localhost:3001
   # admin / admin
   ```
   → Montrer les dashboards avec données réelles

3. **Ouvrir MLflow**:
   ```bash
   open http://localhost:5001
   ```
   → Montrer les expériences et le registry

4. **Générer un rapport Evidently**:
   ```bash
   # Faire 1000 prédictions via l'API
   # Evidently génère automatiquement un rapport
   open api_pokemon/monitoring/drift_reports/drift_dashboard_*.html
   ```

### Pour le Monitoring en Production

**Checklist quotidienne** (5 min):

1. ✅ Grafana Model Performance:
   - Model Confidence > 0.8
   - P95 Latency < 0.1s
   - Pas de pics d'erreurs

2. ✅ Grafana API Performance:
   - Error Rate < 1%
   - Request Rate normal
   - Status codes majoritairement 200

3. ✅ Evidently (1x/semaine):
   - Vérifier dernier rapport drift
   - Drift < 30%

4. ✅ MLflow (1x/mois):
   - Comparer performances des versions
   - Archiver vieux modèles

---

## 📚 Ressources

- **Prometheus Queries**: http://localhost:9091
- **Grafana Dashboards**: http://localhost:3001
- **MLflow UI**: http://localhost:5001
- **API Docs**: http://localhost:8080/docs
- **Evidently Docs**: https://docs.evidentlyai.com/

---

**Auteur**: Claude Sonnet 4.5
**Dernière mise à jour**: 2026-01-29
