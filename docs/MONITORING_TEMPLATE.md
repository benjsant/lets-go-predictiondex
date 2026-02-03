# Guide de Monitoring - Let's Go PredictionDex

## 1. Vue d'ensemble

Le système de monitoring du modèle ML repose sur une stack moderne :
- **Prometheus** : Collecte et stockage des métriques time-series
- **Grafana** : Visualisation temps réel avec dashboards
- **DriftDetector** : Collecte des données de production pour analyse

## 2. Architecture

```
API FastAPI (port 8080)
  ↓ expose /metrics endpoint
Prometheus (port 9090)
  ↓ scrape toutes les 15s
  ↓ stockage 15 jours
Grafana (port 3001)
  ↓ visualisation + alertes
Dashboard temps réel
```

## 3. Métriques Collectées

### Métriques API
- `api_requests_total` : Nombre total de requêtes par endpoint/status
- `api_request_duration_seconds` : Latence des requêtes (histogram)
- `api_errors_total` : Erreurs par type

### Métriques Modèle ML
- `model_predictions_total` : Nombre de prédictions effectuées
- `model_prediction_duration_seconds` : Temps d'inférence (histogram)
- `model_confidence_score` : Distribution des scores de confiance
- `model_win_probability` : Distribution des probabilités prédites

### Métriques Système
- `system_cpu_usage_percent` : Usage CPU
- `system_memory_usage_bytes` : Mémoire utilisée
- `system_memory_available_bytes` : Mémoire disponible

## 4. Installation et Configuration

### Démarrage des services
```bash
# Démarrer toute la stack monitoring
docker compose up -d db api prometheus grafana

# Vérifier l'état
docker compose ps
```

### URLs d'accès
- **API** : http://localhost:8080
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3001 (admin/admin)
- **Endpoint métriques** : http://localhost:8080/metrics

### Vérification
```bash
# Test endpoint métriques
curl http://localhost:8080/metrics

# Vérifier que Prometheus scrape l'API
# → Ouvrir http://localhost:9090/targets
# → L'état doit être "UP" (vert)

# Vérifier Grafana
# → Ouvrir http://localhost:3001
# → Aller dans Dashboards > Model Performance
```

## 5. Utilisation des Dashboards

### Dashboard "Model Performance"
- **Predictions per Minute** : Volume de prédictions
- **Model Confidence Score** : Qualité des prédictions
  - Rouge (< 0.6) : Confiance faible
  - Jaune (0.6-0.8) : Confiance moyenne
  - Vert (> 0.8) : Confiance élevée

### Dashboard "API Performance"
- **API Status** : État de l'API (up/down)
- **Request Duration** : Latence moyenne des requêtes
- **Error Rate** : Taux d'erreurs
- **System Resources** : CPU/Memory

## 6. Alertes Configurées

8 règles d'alertes dans `docker/prometheus/alerts.yml` :

| Alerte | Seuil | Durée | Action |
|--------|-------|-------|--------|
| HighAPILatency | > 0.5s (p95) | 5 min | Vérifier charge API |
| HighErrorRate | > 5% | 2 min | Vérifier logs erreurs |
| APIDown | Indisponible | 1 min | Redémarrer service |
| HighModelLatency | > 0.1s (p95) | 5 min | Optimiser modèle |
| LowModelConfidence | < 0.6 | 10 min | Retraining nécessaire |
| HighCPUUsage | > 80% | 5 min | Scale up ressources |
| HighMemoryUsage | > 85% | 5 min | Vérifier memory leaks |
| LowMemoryAvailable | < 512MB | 2 min | Libérer mémoire |

## 7. Drift Detection

### Fonctionnement
Le système collecte automatiquement les features de chaque prédiction dans un buffer. Lorsque le buffer atteint 100 prédictions, les données sont sauvegardées en parquet.

### Localisation des données
```bash
api_pokemon/monitoring/drift_data/
├── production_data_20260201_163846.parquet
└── production_data_20260201_170548.parquet
```

### Lecture des données
```python
import pandas as pd
from pathlib import Path

# Lire tous les fichiers de drift
drift_dir = Path("api_pokemon/monitoring/drift_data")
files = sorted(drift_dir.glob("*.parquet"))

for file in files:
    df = pd.read_parquet(file)
    print(f"\nFichier : {file.name}")
    print(f"Nombre de prédictions : {len(df)}")
    print(f"Features : {df.columns.tolist()}")
    print(f"Stats :\n{df.describe()}")
```

### Cas d'usage
1. **Détection de dérive** : Comparer les distributions avec les données d'entraînement
2. **Retraining** : Utiliser ces données pour réentraîner le modèle
3. **Analyse de performance** : Identifier les cas où le modèle performe mal

## 8. Requêtes PromQL Utiles

### Taux de requêtes par minute
```promql
rate(api_requests_total[5m])
```

### Latence p95 de l'API
```promql
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))
```

### Taux d'erreurs
```promql
rate(api_errors_total[5m])
```

### Confiance moyenne du modèle
```promql
rate(model_confidence_score_sum[5m]) / rate(model_confidence_score_count[5m])
```

## 9. Troubleshooting

### Prometheus ne scrape pas l'API
```bash
# 1. Vérifier que l'API est accessible
curl http://localhost:8080/metrics

# 2. Vérifier les logs Prometheus
docker compose logs prometheus

# 3. Vérifier la config Prometheus
cat docker/prometheus/prometheus.yml

# 4. Redémarrer Prometheus
docker compose restart prometheus
```

### Grafana n'affiche pas de données
```bash
# 1. Vérifier la datasource Prometheus
# → Grafana > Configuration > Data Sources > Prometheus
# → Test & Save doit être vert

# 2. Vérifier que Prometheus contient des données
# → Ouvrir http://localhost:9090/graph
# → Exécuter : api_requests_total

# 3. Vérifier les dashboards
# → Re-importer les dashboards depuis docker/grafana/dashboards/
```

### Métriques manquantes
```bash
# 1. Vérifier que l'API enregistre les métriques
# → Dans api_pokemon/routes/prediction_route.py
# → La fonction track_prediction() doit être appelée

# 2. Vérifier les logs de l'API
docker compose logs api | grep -i metric
```

## 10. Tests du Monitoring

### Exécuter les tests
```bash
# Tests unitaires des métriques
pytest tests/monitoring/test_metrics.py -v

# Tests d'intégration
pytest tests/integration/test_monitoring_validation.py -v

# Tous les tests de monitoring
pytest tests/monitoring/ tests/integration/test_monitoring*.py -v
```

### Couverture attendue
- 46 tests unitaires de métriques
- Tests de performance (< 1s pour 1000 enregistrements)
- Tests de thread-safety
- Tests d'intégration end-to-end

## 11. Accessibilité

### Pour les utilisateurs Grafana
- **Navigation clavier** : Tous les dashboards sont navigables au clavier (Tab, Entrée)
- **Lecteurs d'écran** : Grafana supporte NVDA et JAWS
- **Contraste** : Les couleurs utilisées respectent WCAG 2.1 AA (ratio 4.5:1)
- **Zoom** : Les dashboards sont utilisables jusqu'à 200% de zoom

### Pour les parties prenantes non techniques
- **Export CSV** : Toutes les métriques sont exportables en CSV depuis Grafana
- **Alertes email** : Configuration possible dans Alertmanager
- **Rapports automatiques** : Snapshots de dashboards disponibles

### Recommandations
- Utiliser Firefox ou Chrome pour meilleure accessibilité
- Activer le mode High Contrast si besoin
- Les dashboards sont testés avec WAVE (Web Accessibility Evaluation Tool)

## 12. Maintenance

### Rétention des données
- **Prometheus** : 15 jours (configurable dans `prometheus.yml`)
- **Drift data** : Nettoyage manuel recommandé tous les 30 jours

### Sauvegarde
```bash
# Backup des données Prometheus
docker compose exec prometheus promtool tsdb snapshot

# Backup des dashboards Grafana
cp -r docker/grafana/dashboards/ backup/dashboards_$(date +%Y%m%d)/
```

### Mise à jour
```bash
# Mettre à jour les images Docker
docker compose pull prometheus grafana

# Redémarrer avec nouvelles versions
docker compose up -d prometheus grafana
```

## 13. Références

- **Prometheus** : https://prometheus.io/docs/
- **Grafana** : https://grafana.com/docs/
- **PromQL** : https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Accessibilité WCAG** : https://www.w3.org/WAI/WCAG21/quickref/
- **Recommandations Valentin Haüy** : https://www.avh.asso.fr/fr/favoriser-laccessibilite

---

**Version** : 2.0
**Dernière mise à jour** : 2 février 2026
**Contact** : Équipe Let's Go PredictionDex
