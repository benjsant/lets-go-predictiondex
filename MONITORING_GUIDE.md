# Guide de Monitoring - PredictionDex

## 📊 Stack de Monitoring

Le système PredictionDex inclut une stack complète de monitoring avec :

- **Prometheus** : Collecte de métriques temps réel
- **Grafana** : Visualisation et dashboards
- **Evidently AI** : Détection de drift des données
- **Node Exporter** : Métriques système

---

## 🚀 Démarrage Rapide

### 1. Lancer la Stack Complète

```bash
# Lancer tous les services (DB + ETL + API + Streamlit + Monitoring)
docker compose up --build

# Ou lancer uniquement le monitoring après l'API
docker compose up prometheus grafana node-exporter -d
```

### 2. Accéder aux Services

| Service | URL | Identifiants |
|---------|-----|--------------|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **API Metrics** | http://localhost:8000/metrics | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Streamlit** | http://localhost:8501 | - |

---

## 📈 Métriques Collectées

### Métriques API

```python
# Compteurs
api_requests_total{method, endpoint, status}
api_errors_total{method, endpoint, error_type}

# Histogrammes (latence)
api_request_duration_seconds{method, endpoint}
# Buckets: 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0
```

### Métriques Modèle ML

```python
# Prédictions
model_predictions_total{model_version}

# Latence du modèle
model_prediction_duration_seconds{model_version}
# Buckets: 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0

# Confiance du modèle
model_confidence_score{model_version}

# Distribution des probabilités
model_win_probability{model_version}
```

### Métriques Système

```python
# CPU
system_cpu_usage_percent

# Mémoire
system_memory_usage_bytes
system_memory_available_bytes
```

---

## 🎯 Dashboards Grafana

### Dashboard 1: API Performance

**URL**: http://localhost:3000/d/api-performance

**Panels**:
- ✅ Statut de l'API (UP/DOWN)
- 📊 Taux de requêtes par endpoint
- ⏱️ Latence P95 globale
- ❌ Taux d'erreurs
- 📉 Latence P50/P95/P99 par endpoint
- 📈 Codes de statut HTTP

**Use Case**: Monitoring de la santé générale de l'API et détection des problèmes de performance.

### Dashboard 2: Model Performance

**URL**: http://localhost:3000/d/model-performance

**Panels**:
- 🎯 Prédictions par minute
- 💯 Score de confiance moyen
- ⏱️ Latence P95 du modèle
- 📊 Total des prédictions
- 📉 Évolution de la latence
- 📈 Confiance au fil du temps
- 🎲 Distribution des probabilités de victoire
- 🔄 Prédictions par version de modèle

**Use Case**: Monitoring des performances du modèle ML et détection de dégradation.

---

## 🚨 Alertes Prometheus

### Alertes API

#### HighAPILatency
- **Condition**: Latence P95 > 0.5s pendant 5 minutes
- **Gravité**: warning
- **Action**: Vérifier les performances de la base de données et du modèle

#### HighErrorRate
- **Condition**: Taux d'erreurs > 5% pendant 5 minutes
- **Gravité**: critical
- **Action**: Vérifier les logs de l'API et la base de données

#### APIDown
- **Condition**: API ne répond pas pendant 1 minute
- **Gravité**: critical
- **Action**: Redémarrer le conteneur API

### Alertes Modèle

#### HighModelLatency
- **Condition**: Latence P95 du modèle > 0.1s pendant 5 minutes
- **Gravité**: warning
- **Action**: Vérifier les performances du modèle et le CPU

#### LowModelConfidence
- **Condition**: Confiance moyenne < 0.6 pendant 10 minutes
- **Gravité**: warning
- **Action**: Vérifier le drift des données et la qualité du modèle

### Alertes Système

#### HighCPUUsage
- **Condition**: CPU > 80% pendant 5 minutes
- **Gravité**: warning
- **Action**: Augmenter les ressources ou optimiser le code

#### HighMemoryUsage
- **Condition**: Mémoire > 85% pendant 5 minutes
- **Gravité**: warning
- **Action**: Vérifier les fuites mémoire et augmenter les ressources

#### LowMemoryAvailable
- **Condition**: Mémoire disponible < 512MB pendant 2 minutes
- **Gravité**: critical
- **Action**: Augmenter la RAM ou redémarrer les services

---

## 🔍 Détection de Drift (Evidently AI)

### Configuration

- **Version**: Evidently 0.3.3 (stable - les versions 0.4.x ont des problèmes de compatibilité)
- **Données de référence**: 10,000 échantillons d'entraînement
- **Buffer de production**: 1,000 prédictions max
- **Fréquence de rapport**: 1 heure (configurable)

### Fonctionnement

1. **Chargement des données de référence**:
   - Fichier: `data/datasets/X_train.parquet`
   - Colonnes: 133 features (stats, types, moves, etc.)

2. **Collecte des prédictions en production**:
   - Buffer FIFO de 1000 prédictions
   - Sauvegarde automatique tous les 1000 exemples

3. **Génération des rapports**:
   - Automatique: toutes les heures
   - Manuel: via API endpoint (future feature)
   - Formats: JSON + HTML dashboard

### Rapports Générés

#### Localisation
```
api_pokemon/monitoring/drift_reports/
├── drift_report_20250125_143022.json       # Métriques numériques
├── drift_dashboard_20250125_143022.html    # Visualisation interactive
└── ...
```

#### Données de production sauvegardées
```
api_pokemon/monitoring/drift_data/
├── production_data_20250125_143022.parquet
└── ...
```

### Métriques de Drift

- **Data Drift**: Changement de distribution des features
- **Prediction Drift**: Changement de distribution des prédictions
- **Kolmogorov-Smirnov Test**: Test statistique par feature
- **Chi-Square Test**: Pour features catégorielles
- **PSI (Population Stability Index)**: Stabilité globale

### Interprétation

- **PSI < 0.1**: Pas de drift significatif ✅
- **0.1 ≤ PSI < 0.25**: Drift modéré ⚠️ (monitoring)
- **PSI ≥ 0.25**: Drift sévère 🚨 (ré-entraînement recommandé)

---

## 🛠️ Commandes Utiles

### Monitoring

```bash
# Voir les métriques brutes Prometheus
curl http://localhost:8000/metrics

# Tester l'endpoint de prédiction
curl -X POST http://localhost:8000/predict/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 1,
    "pokemon_b_id": 25,
    "available_moves": ["Surf", "Ice Beam", "Earthquake"]
  }'

# Vérifier le statut de Prometheus
curl http://localhost:9090/-/healthy

# Vérifier le statut de Grafana
curl http://localhost:3000/api/health
```

### Logs

```bash
# Logs du service API
docker compose logs -f api

# Logs de Prometheus
docker compose logs -f prometheus

# Logs de Grafana
docker compose logs -f grafana

# Logs du Node Exporter
docker compose logs -f node-exporter
```

### Redémarrage

```bash
# Redémarrer un service spécifique
docker compose restart api

# Redémarrer le monitoring
docker compose restart prometheus grafana

# Redémarrer tout
docker compose restart
```

---

## 📊 Requêtes Prometheus Utiles

### API Performance

```promql
# Taux de requêtes par seconde
rate(api_requests_total[5m])

# Latence P95 globale
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Taux d'erreurs
rate(api_errors_total[5m]) / rate(api_requests_total[5m])

# Top endpoints par requêtes
topk(5, sum by (endpoint) (rate(api_requests_total[5m])))
```

### Model Performance

```promql
# Prédictions par minute
rate(model_predictions_total[1m]) * 60

# Latence P95 du modèle
histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))

# Confiance moyenne
avg(model_confidence_score)

# Distribution des probabilités de victoire
histogram_quantile(0.5, rate(model_win_probability_bucket[5m]))
```

### System Metrics

```promql
# CPU usage
system_cpu_usage_percent

# Mémoire utilisée (%)
(system_memory_usage_bytes / (system_memory_usage_bytes + system_memory_available_bytes)) * 100

# Mémoire disponible (MB)
system_memory_available_bytes / 1024 / 1024
```

---

## 🔧 Configuration Avancée

### Modifier la Fréquence de Scraping

Éditez `docker/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'api'
    scrape_interval: 10s  # Changez ici (défaut: 10s)
    static_configs:
      - targets: ['api:8000']
```

### Modifier la Rétention Prometheus

Éditez `docker-compose.yml`:

```yaml
prometheus:
  command:
    - '--storage.tsdb.retention.time=15d'  # Changez ici (défaut: 15 jours)
```

### Modifier la Fréquence de Drift Detection

Éditez `api_pokemon/monitoring/drift_detection.py`:

```python
self.report_frequency = timedelta(hours=1)  # Changez ici (défaut: 1 heure)
```

### Modifier la Taille du Buffer de Drift

```python
self.max_buffer_size = 1000  # Changez ici (défaut: 1000)
```

---

## 🐛 Troubleshooting

### Prometheus ne scrape pas l'API

**Symptôme**: Aucune métrique dans Prometheus

**Solutions**:
1. Vérifier que l'API est UP: `curl http://localhost:8000/health`
2. Vérifier que `/metrics` est accessible: `curl http://localhost:8000/metrics`
3. Vérifier les logs: `docker compose logs prometheus`
4. Vérifier la config: `docker/prometheus/prometheus.yml`

### Grafana n'affiche pas les données

**Symptôme**: Dashboards vides

**Solutions**:
1. Vérifier que Prometheus collecte les données: http://localhost:9090
2. Vérifier la datasource Grafana: http://localhost:3000/datasources
3. Vérifier que les dashboards sont provisionnés: `docker compose logs grafana`
4. Recharger les dashboards: Grafana UI > Dashboards > Refresh

### Evidently génère des erreurs

**Symptôme**: Erreurs dans les logs API lors de la génération de rapports

**Solutions**:
1. Vérifier que `data/datasets/X_train.parquet` existe
2. Vérifier la version d'Evidently: `pip show evidently` (doit être 0.3.3)
3. Vérifier les colonnes du dataset: doivent matcher les features du modèle
4. Vérifier les logs: `docker compose logs -f api | grep -i drift`

### Node Exporter ne démarre pas

**Symptôme**: Container `letsgo_node_exporter` en erreur

**Solution**: Vérifier les permissions des volumes montés
```bash
# Linux/Mac
sudo chmod -R 755 /proc /sys
```

---

## 📚 Ressources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Evidently AI Documentation](https://docs.evidentlyai.com/)
- [FastAPI Prometheus Instrumentation](https://github.com/trallnag/prometheus-fastapi-instrumentator)

---

## 🎯 Prochaines Étapes (C13 - MLOps)

- [ ] Intégration MLflow pour le tracking d'expériences
- [ ] Pipeline CI/CD avec GitHub Actions
- [ ] Tests automatisés des performances du modèle
- [ ] Alerting avancé avec PagerDuty/Slack
- [ ] Automatisation du ré-entraînement sur drift détecté

---

**Version**: 1.0  
**Dernière mise à jour**: 25 janvier 2025  
**Auteur**: AI-assisted development
