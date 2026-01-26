# Architecture Monitoring Modulaire - PredictionDex

## 🎯 Vision

Séparation des préoccupations (Separation of Concerns) pour le monitoring :
- **API Python** : Génération et exposition des métriques uniquement
- **Prometheus** : Collecte centralisée des métriques
- **Grafana** : Visualisation et dashboards
- **Evidently** : Analyse de drift (intégré à l'API pour l'instant)

---

## 🏗️ Architecture Actuelle (v1.0)

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   API        │      │  PostgreSQL  │                     │
│  │  (FastAPI)   │─────▶│    (DB)      │                     │
│  │              │      │              │                     │
│  │ • Métriques  │      └──────────────┘                     │
│  │ • Evidently  │                                            │
│  │ • /metrics   │                                            │
│  └──────┬───────┘                                            │
│         │                                                     │
│         │ scrape                                              │
│         ▼                                                     │
│  ┌──────────────┐                                            │
│  │  Prometheus  │                                            │
│  │              │                                            │
│  │ • Scraping   │                                            │
│  │ • Alerting   │                                            │
│  │ • Storage    │                                            │
│  └──────┬───────┘                                            │
│         │                                                     │
│         │ query                                               │
│         ▼                                                     │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Grafana    │      │Node Exporter │                     │
│  │              │      │              │                     │
│  │ • Dashboards │      │ • System     │                     │
│  │ • Alerting   │      │   Metrics    │                     │
│  └──────────────┘      └──────────────┘                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Problèmes

1. **Evidently intégré à l'API** : Alourdit le container API
2. **Pas de service dédié** pour la génération de rapports de drift
3. **Drift detection synchrone** : Peut ralentir les prédictions
4. **Scalabilité limitée** : Tout dans un seul service

---

## 🚀 Architecture Proposée (v2.0 - Modulaire)

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   API        │      │  PostgreSQL  │                     │
│  │  (FastAPI)   │─────▶│    (DB)      │                     │
│  │              │      │              │                     │
│  │ • Lightweight│      └──────────────┘                     │
│  │ • /metrics   │                                            │
│  │ • Queue jobs │                                            │
│  └──────┬───────┘                                            │
│         │                │                                    │
│         │ scrape         │ predictions                        │
│         ▼                ▼                                    │
│  ┌──────────────┐  ┌────────────────┐                       │
│  │  Prometheus  │  │  Drift Service │                       │
│  │              │  │  (Evidently)   │                       │
│  │ • Scraping   │  │                │                       │
│  │ • Alerting   │  │ • Async worker │                       │
│  │ • Storage    │  │ • Batch reports│                       │
│  └──────┬───────┘  │ • HTML/JSON    │                       │
│         │          └────────┬───────┘                        │
│         │                   │                                 │
│         │ query             │ reports                         │
│         ▼                   ▼                                 │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Grafana    │      │  Report UI   │                     │
│  │              │      │  (Nginx)     │                     │
│  │ • Dashboards │      │              │                     │
│  │ • Alerting   │      │ • Serve HTML │                     │
│  └──────────────┘      └──────────────┘                     │
│                                                               │
│  ┌──────────────┐                                            │
│  │Node Exporter │                                            │
│  │              │                                            │
│  │ • System     │                                            │
│  │   Metrics    │                                            │
│  └──────────────┘                                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Avantages

1. **Séparation des services** : Chaque composant a une responsabilité unique
2. **Scalabilité** : Chaque service peut scaler indépendamment
3. **Performance** : L'API ne fait que des prédictions, pas d'analyse de drift
4. **Asynchrone** : Le drift service traite en arrière-plan
5. **Maintenance** : Plus facile de débugger et mettre à jour

---

## 📦 Services Détaillés

### 1. API Service (api)

**Responsabilités** :
- Exposer les endpoints de prédiction
- Exposer `/metrics` pour Prometheus
- Envoyer les prédictions à une queue/topic (Redis ou RabbitMQ)

**Stack** :
- FastAPI
- prometheus-client
- SQLAlchemy

**Volumes** :
- `./api_pokemon:/app/api_pokemon`
- `./models:/app/models`

### 2. Drift Service (drift_detector)

**Responsabilités** :
- Consommer les prédictions depuis la queue
- Générer des rapports Evidently périodiques
- Sauvegarder HTML/JSON dans un volume partagé

**Stack** :
- Python 3.11
- Evidently 0.7.x
- Redis client / RabbitMQ client
- pandas, numpy

**Volumes** :
- `drift_reports:/app/reports` (partagé avec nginx)
- `./data/datasets:/app/data` (référence data)

**Variables d'env** :
- `REPORT_FREQUENCY=3600` (secondes)
- `BUFFER_SIZE=1000`
- `REFERENCE_DATA_PATH=/app/data/X_train.parquet`

### 3. Prometheus (prometheus)

**Responsabilités** :
- Scraper l'API `/metrics` toutes les 10s
- Stocker les time-series
- Évaluer les alerting rules

**Configuration** :
- `./docker/prometheus/prometheus.yml`
- `./docker/prometheus/alerts.yml`

**Volumes** :
- `prometheus_data:/prometheus`

### 4. Grafana (grafana)

**Responsabilités** :
- Afficher les dashboards
- Alerting avancé (optionnel)
- Annotations

**Configuration** :
- `./docker/grafana/provisioning/`
- `./docker/grafana/dashboards/`

**Volumes** :
- `grafana_data:/var/lib/grafana`

### 5. Node Exporter (node-exporter)

**Responsabilités** :
- Exporter les métriques système (CPU, RAM, Disk, Network)

**Ports** :
- `9100:9100`

### 6. Report UI (nginx - optionnel)

**Responsabilités** :
- Servir les rapports HTML d'Evidently
- Listage des rapports disponibles

**Configuration** :
```nginx
server {
    listen 8080;
    root /usr/share/nginx/html/reports;
    autoindex on;
}
```

**Volumes** :
- `drift_reports:/usr/share/nginx/html/reports:ro`

---

## 🔄 Flux de Données

### Flux de Prédiction

```
User Request → API → Model → Prediction
                │
                └──→ Prometheus metrics (sync)
                └──→ Redis Queue (async)
```

### Flux de Drift Detection

```
Redis Queue → Drift Service → Evidently Analysis
                                     │
                                     ├──→ HTML Report
                                     ├──→ JSON Report
                                     └──→ Parquet Archive
```

### Flux de Visualisation

```
Prometheus ← API /metrics (pull)
     │
     └──→ Grafana Dashboards

Nginx ← Drift HTML Reports (static)
     │
     └──→ Browser (http://localhost:8080/drift_report_xxx.html)
```

---

## 🛠️ Implémentation v2.0

### Étape 1 : Créer le Drift Service

Créer `docker/Dockerfile.drift`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    evidently>=0.7.0,<0.8.0 \
    pandas \
    numpy \
    pyarrow \
    redis

# Copy drift detector code
COPY api_pokemon/monitoring/drift_detection.py /app/
COPY docker/drift_entrypoint.py /app/

CMD ["python", "drift_entrypoint.py"]
```

### Étape 2 : Créer l'Entrypoint

Créer `docker/drift_entrypoint.py`:

```python
import time
import redis
import json
from drift_detection import drift_detector

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

while True:
    # Read from Redis queue
    data = redis_client.blpop('predictions', timeout=10)
    
    if data:
        _, prediction_json = data
        prediction = json.loads(prediction_json)
        
        # Add to drift detector
        drift_detector.add_prediction(
            features=prediction['features'],
            prediction=prediction['prediction'],
            probability=prediction['probability']
        )
    
    # Periodic report generation (every hour)
    if time.time() % 3600 < 10:
        drift_detector.generate_drift_report()
```

### Étape 3 : Ajouter Redis

```yaml
redis:
  image: redis:7-alpine
  container_name: letsgo_redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  restart: unless-stopped
```

### Étape 4 : Ajouter le Drift Service

```yaml
drift_detector:
  build:
    context: .
    dockerfile: docker/Dockerfile.drift
  container_name: letsgo_drift
  depends_on:
    - redis
  environment:
    REDIS_HOST: redis
    REDIS_PORT: 6379
    REPORT_FREQUENCY: 3600
    BUFFER_SIZE: 1000
  volumes:
    - drift_reports:/app/reports
    - ./data/datasets:/app/data:ro
  restart: unless-stopped
```

### Étape 5 : Ajouter Nginx pour les Rapports

```yaml
drift_ui:
  image: nginx:alpine
  container_name: letsgo_drift_ui
  ports:
    - "8080:80"
  volumes:
    - drift_reports:/usr/share/nginx/html:ro
    - ./docker/nginx/nginx.conf:/etc/nginx/conf.d/default.conf
  restart: unless-stopped
```

### Étape 6 : Modifier l'API

Dans `prediction_route.py`, au lieu de :

```python
drift_detector.add_prediction(...)  # Synchrone
```

Utiliser :

```python
# Publier dans Redis
redis_client.rpush('predictions', json.dumps({
    'features': features,
    'prediction': prediction,
    'probability': probability,
    'timestamp': datetime.now().isoformat()
}))
```

---

## 📊 Comparaison

| Feature | v1.0 (Actuel) | v2.0 (Modulaire) |
|---------|---------------|------------------|
| **Services** | 5 (API, DB, Prometheus, Grafana, Node) | 8 (+Redis, Drift, Nginx) |
| **Drift Detection** | Synchrone dans API | Asynchrone worker |
| **Performance API** | -10ms overhead | Pas d'overhead |
| **Scalabilité** | Limitée | Excellente |
| **Maintenance** | Complexe | Modulaire |
| **Rapports Evidently** | Difficile d'accès | UI dédiée (8080) |
| **Queue** | None | Redis |
| **Isolation** | Faible | Forte |

---

## 🎯 Recommandation

Pour le **MVP actuel (C11)**, garder la **v1.0 simplifiée** :
- ✅ Moins de services à gérer
- ✅ Setup plus rapide
- ✅ Suffisant pour la validation
- ✅ Evidently 0.7 déjà intégré

Pour la **production (C13 - MLOps)**, migrer vers la **v2.0 modulaire** :
- ✅ Meilleure performance
- ✅ Scalabilité horizontale
- ✅ Monitoring dédié
- ✅ Async drift detection

---

## 📝 Notes

- L'architecture v1.0 est **suffisante pour le développement** et la validation des compétences
- L'architecture v2.0 est **recommandée pour la production** à grande échelle
- La migration v1.0 → v2.0 est **progressive** (ajouter Redis, puis Drift Service)
- Les dashboards Grafana et Prometheus restent **identiques** dans les deux versions

---

**Status**: 📋 Proposition d'architecture  
**Version actuelle**: v1.0 (implémentée)  
**Version cible**: v2.0 (pour C13)
