# 🐳 Démarrage Docker - Guide Rapide

## ✅ Tout est prêt !

Votre projet est **100% orchestré** et peut se lancer avec une seule commande.

---

## 🚀 Démarrage en UNE commande

### Option 1 : Docker Compose v2 (recommandé)
```bash
docker compose up --build
```

### Option 2 : Docker Compose v1 (legacy)
```bash
docker-compose up --build
```

### Option 3 : Mode background (détaché)
```bash
docker compose up --build -d
```

---

## 📊 Ce qui se passe automatiquement

```
1. PostgreSQL démarre (healthcheck: 5s)
   ↓
2. ETL s'exécute et se termine (2-3 min)
   • Scrapy Spider (Pokepedia)
   • CSV Loader
   • PokéAPI enrichment
   ↓
3. ML Builder s'exécute et se termine (5-15 min)
   • Génère datasets de bataille
   • Entraîne XGBoost
   • GridSearchCV (si activé)
   • Exporte modèle vers /models/
   ↓
4. Services permanents démarrent
   • API FastAPI (port 8000)
   • Streamlit (port 8501)
   • MLflow (port 5000)
   • Prometheus (port 9090)
   • Grafana (port 3000)
   • Node Exporter (port 9100)
```

**Temps total** : ~10-20 minutes pour le premier démarrage

---

## 🌐 Accès aux services

Après le démarrage, accédez à :

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | FastAPI + Documentation Swagger |
| **Streamlit** | http://localhost:8501 | Interface utilisateur interactive |
| **MLflow** | http://localhost:5000 | Tracking ML + Model Registry |
| **Grafana** | http://localhost:3000 | Dashboards de monitoring |
| **Prometheus** | http://localhost:9090 | Métriques système |

---

## 🔍 Vérifier le démarrage

### Voir les logs en temps réel
```bash
docker compose logs -f
```

### Logs d'un service spécifique
```bash
docker compose logs -f api           # API FastAPI
docker compose logs -f ml_builder    # ML Training
docker compose logs -f etl           # ETL Pipeline
```

### Status des services
```bash
docker compose ps
```

**Output attendu** :
```
NAME                    STATUS                  PORTS
letsgo_postgres         Up (healthy)            5432
letsgo_etl              Exited (0)              -
letsgo_ml               Exited (0)              -
letsgo_api              Up (healthy)            8000
letsgo_streamlit        Up                      8501
letsgo_mlflow           Up (healthy)            5000
letsgo_prometheus       Up                      9090
letsgo_grafana          Up                      3000
letsgo_node_exporter    Up                      9100
```

---

## ⚡ Redémarrage rapide (skip ML training)

Si le modèle existe déjà (`models/battle_winner_model_v2.pkl`), le ML training est automatiquement sauté.

**Configuration par défaut** :
```yaml
ml_builder:
  environment:
    ML_SKIP_IF_EXISTS: "true"  # ✅ Activé
```

**Temps de redémarrage** : ~30 secondes (au lieu de 10-20 minutes)

---

## 🛠️ Commandes utiles

### Arrêter tous les services
```bash
docker compose down
```

### Redémarrer un service
```bash
docker compose restart api
```

### Forcer rebuild d'un service
```bash
docker compose build --no-cache api
docker compose up -d api
```

### Nettoyer tout (⚠️ perte des données)
```bash
docker compose down -v  # Supprime aussi les volumes
```

---

## 🐛 Problèmes courants

### Port 5432 déjà utilisé (PostgreSQL local)
```bash
# Solution 1: Arrêter PostgreSQL local
sudo systemctl stop postgresql

# Solution 2: Changer le port dans docker-compose.yml
ports:
  - "5433:5432"  # Utiliser 5433 au lieu de 5432
```

### Docker Compose non trouvé
```bash
# Utiliser docker compose (v2, intégré à Docker)
docker compose up --build

# Ou installer docker-compose standalone
sudo apt install docker-compose
```

### ML training trop long
```bash
# Éditer docker-compose.yml
ml_builder:
  environment:
    ML_TUNE_HYPERPARAMS: "false"      # Désactiver GridSearch
    ML_SCENARIO_TYPE: "best_move"     # Un seul scénario
```

### Espace disque insuffisant
```bash
# Nettoyer Docker
docker system prune -a --volumes

# Vérifier l'espace
docker system df
```

---

## 🎯 Tests de validation

Vérifier que tout est configuré :
```bash
python test_docker_orchestration.py
```

---

## 📖 Documentation complète

Voir [DOCKER_ORCHESTRATION.md](DOCKER_ORCHESTRATION.md) pour :
- Architecture détaillée
- Configuration avancée
- Optimisations
- Troubleshooting complet
- Checklist production

---

## ✅ Checklist de démarrage

- [x] Docker installé (`docker --version`)
- [x] Fichier `.env` présent
- [x] docker-compose.yml validé
- [x] 9 services configurés
- [x] Health checks activés
- [x] Dépendances orchestrées
- [x] Volumes persistants configurés
- [x] Entrypoints automatisés

**Statut** : ✅ Prêt à lancer !

---

**Commande finale** :
```bash
docker compose up --build
```

🎉 **C'est tout !** Le projet démarre automatiquement.
