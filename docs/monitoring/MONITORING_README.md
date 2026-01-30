# 🚀 Monitoring Stack - Guide de Démarrage Rapide

## ✅ Ce qui est implémenté

### Stack Complète (v1.0)
- ✅ **Prometheus** : Collecte de métriques (API, Modèle, Système)
- ✅ **Grafana** : 2 dashboards (API Performance + Model Performance)
- ✅ **MLflow** : Tracking des expériences ML et registry de modèles
- ✅ **Production Data Collection** : Collecte automatique des features ML pour future analyse
- ✅ **Node Exporter** : Métriques système (CPU, RAM, etc.)
- ✅ **Alerting** : 8 règles d'alerte configurées

---

## 🎯 Lancement

### Option 1 : Stack Complète
```bash
docker compose up --build
```

### Option 2 : Monitoring Seul (après DB+API)
```bash
# Démarrer DB + ETL + API d'abord
docker compose up db etl api -d

# Puis le monitoring
docker compose up prometheus grafana node-exporter -d
```

---

## 🌐 URLs d'Accès

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Swagger** | http://localhost:8000/docs | - |
| **API Metrics** | http://localhost:8000/metrics | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Streamlit UI** | http://localhost:8501 | - |

---

## 📊 Dashboards Grafana

Après connexion sur http://localhost:3000 (admin/admin) :

### Dashboard 1 : API Performance
- URL: http://localhost:3000/d/api-performance
- **Métriques** : Requêtes/s, Latence P95, Taux d'erreurs, Status HTTP

### Dashboard 2 : Model Performance  
- URL: http://localhost:3000/d/model-performance
- **Métriques** : Prédictions/min, Confiance, Latence modèle, Distribution win probability

---

## 🧪 Tester le Monitoring

### 1. Vérifier que les métriques sont exposées

```bash
curl http://localhost:8000/metrics
```

Vous devriez voir des métriques Prometheus :
```
# HELP api_requests_total Total API requests
# TYPE api_requests_total counter
api_requests_total{endpoint="/docs",method="GET",status="200"} 5.0
model_predictions_total{model_version="v2"} 42.0
```

### 2. Générer des prédictions

```bash
curl -X POST http://localhost:8000/predict/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 1,
    "pokemon_b_id": 25,
    "available_moves": ["Surf", "Ice Beam", "Earthquake"]
  }'
```

### 3. Vérifier Prometheus

1. Ouvrir http://localhost:9090
2. Query : `rate(api_requests_total[1m])`
3. Cliquer sur "Execute" → Graphique des requêtes/s

### 4. Ouvrir Grafana

1. http://localhost:3000 (admin / admin)
2. Menu gauche → Dashboards
3. Cliquer sur "API Performance" ou "Model Performance"

---

## 💾 Collecte de Données de Production

### Fonctionnement Automatique

Le système collecte automatiquement les features ML de chaque prédiction :
- Buffer : 100 prédictions max
- Référence : 10k exemples d'entraînement (X_train.parquet) chargés au démarrage
- Output : Fichiers parquet avec 133 features ML

### Localisation des Données

```bash
ls -lh api_pokemon/monitoring/drift_data/
```

Fichiers générés :
```
production_data_20260130_124717.parquet  # 100 prédictions × 133 features
```

### Utilisation des Données

Ces données peuvent être utilisées pour :
- Analyse manuelle de drift des données
- Réentraînement du modèle avec données réelles
- Validation de la qualité des prédictions
- Debugging et amélioration du modèle

---

## 📈 Requêtes Prometheus Utiles

### API Performance

```promql
# Requêtes par seconde
rate(api_requests_total[5m])

# Latence P95 globale
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Taux d'erreurs
rate(api_errors_total[5m]) / rate(api_requests_total[5m])
```

### Model Performance

```promql
# Prédictions par minute
rate(model_predictions_total[1m]) * 60

# Latence P95 du modèle  
histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))

# Confiance moyenne
avg(model_confidence_score)
```

---

## 🚨 Alertes Configurées

### Alertes API (3)
- **HighAPILatency** : Latence > 0.5s pendant 5min
- **HighErrorRate** : Erreurs > 5% pendant 5min  
- **APIDown** : API ne répond pas pendant 1min

### Alertes Modèle (2)
- **HighModelLatency** : Latence > 0.1s pendant 5min
- **LowModelConfidence** : Confiance < 0.6 pendant 10min

### Alertes Système (3)
- **HighCPUUsage** : CPU > 80% pendant 5min
- **HighMemoryUsage** : RAM > 85% pendant 5min
- **LowMemoryAvailable** : RAM disponible < 512MB pendant 2min

Voir les alertes : http://localhost:9090/alerts

---

## 🛠️ Troubleshooting

### Prometheus ne collecte pas les métriques

```bash
# Vérifier que l'API est accessible
curl http://localhost:8000/health

# Vérifier que /metrics répond
curl http://localhost:8000/metrics

# Vérifier les logs Prometheus
docker compose logs prometheus

# Vérifier les targets dans Prometheus
# http://localhost:9090/targets
```

### Grafana n'affiche pas de données

```bash
# Vérifier que Prometheus collecte les données
# http://localhost:9090/graph

# Vérifier la datasource Grafana
# http://localhost:3000/datasources

# Recharger les dashboards
docker compose restart grafana
```

### Collecte de données de production

```bash
# Vérifier que X_train.parquet existe (référence)
ls -lh data/datasets/X_train.parquet

# Vérifier les logs de collecte
docker compose logs -f api | grep -i "production"

# Vérifier les fichiers de données collectées
ls -lh api_pokemon/monitoring/drift_data/
```

---

## 📚 Documentation Complète

- **Prometheus** : https://prometheus.io/docs/
- **Grafana** : https://grafana.com/docs/
- **MLflow** : https://mlflow.org/docs/latest/index.html

---

## 🎯 Prochaines Étapes (C13 - MLOps)

- [ ] MLflow pour le tracking d'expériences
- [ ] CI/CD avec GitHub Actions
- [ ] Architecture monitoring modulaire (Redis + Worker)
- [ ] Alerting Slack/Discord
- [ ] Auto-retraining sur drift détecté

---

**Version** : 1.1
**Stack** : Prometheus + Grafana + MLflow + Production Data Collection + Node Exporter
**Dernière MAJ** : 30 janvier 2026
