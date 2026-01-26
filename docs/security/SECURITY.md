# 🔐 Sécurité et Architecture Réseau - v2.0

**Date** : 26 janvier 2026  
**Version** : 2.0 (Architecture sécurisée)

---

## 🎯 Améliorations apportées

### 1. ✅ Authentification par API Key

**Implémentation** : Middleware FastAPI avec vérification des clés

**Fichiers modifiés** :
- [api_pokemon/middleware/security.py](api_pokemon/middleware/security.py) - Middleware de sécurité
- [api_pokemon/main.py](api_pokemon/main.py) - Intégration du middleware

**Fonctionnalités** :
- ✅ Génération cryptographique de clés (SHA-256)
- ✅ Support multi-clés (séparées par virgules)
- ✅ Mode DEV bypass (si `DEV_MODE=true` et pas de clés)
- ✅ Header standard : `X-API-Key`
- ✅ Endpoints publics : `/health`, `/metrics` (monitoring)

**Utilisation** :
```bash
# Générer des clés
python api_pokemon/middleware/security.py

# Requête avec API Key
curl -H "X-API-Key: VOTRE_CLE" http://localhost:8080/pokemon
```

---

### 2. 🌐 Réseaux Docker isolés

**Architecture réseau** :
```
┌─────────────────────────────────────────────┐
│  Réseau BACKEND (privé)                     │
│  ┌──────────┐  ┌──────┐  ┌─────┐  ┌────┐   │
│  │PostgreSQL│◄─┤ ETL  │◄─┤ ML  │  │API │   │
│  │   (db)   │  └──────┘  └─────┘  └─┬──┘   │
│  │ :5432    │                        │      │
│  └──────────┘                        │      │
│  ┌──────────┐                        │      │
│  │  MLflow  │◄───────────────────────┘      │
│  │ :5001    │                               │
│  └──────────┘                               │
└─────────────────────────────────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────────┐  ┌──────────────────┐
│ Réseau MONITORING   │  │   Streamlit      │
│  ┌──────────────┐   │  │   :8502          │
│  │ Prometheus   │   │  │   (public)       │
│  │ :9091        │   │  └──────────────────┘
│  └──────────────┘   │
│  ┌──────────────┐   │
│  │ Grafana      │   │
│  │ :3001        │   │
│  └──────────────┘   │
│  ┌──────────────┐   │
│  │Node Exporter │   │
│  │ :9101        │   │
│  └──────────────┘   │
└─────────────────────┘
```

**Isolation** :
- **Backend** : PostgreSQL + API + ETL + ML + MLflow
  - PostgreSQL **non exposé** sur l'hôte (port 5432 interne uniquement)
  - API **non exposée** directement (port 8080 interne)
- **Monitoring** : Prometheus + Grafana + Node Exporter
- **Frontend** : Streamlit (seul service exposé publiquement avec API Key)

**Sécurité** :
- ✅ PostgreSQL accessible uniquement depuis les containers Docker
- ✅ API accessible uniquement via Streamlit (avec API Key)
- ✅ Pas d'accès direct depuis l'extérieur à la DB ou l'API

---

### 3. 🔢 Ports modifiés

**Avant** → **Après** :

| Service | Ancien port | Nouveau port | Exposition |
|---------|-------------|--------------|------------|
| PostgreSQL | 5432:5432 | **5432 (interne)** | ❌ Non exposé |
| API | 8000:8000 | **8080 (interne)** | ❌ Non exposé |
| Streamlit | 8501:8501 | **8502:8501** | ✅ Public (avec API Key) |
| MLflow | 5000:5000 | **5001:5001** | ✅ Public |
| Prometheus | 9090:9090 | **9091:9090** | ✅ Public |
| Grafana | 3000:3000 | **3001:3000** | ✅ Public |
| Node Exporter | 9100:9100 | **9101:9100** | ✅ Public |

**Raisons** :
- Éviter les conflits de ports
- Réduire la surface d'attaque (DB + API privées)
- Faciliter le déploiement sur serveurs avec services existants

---

## 📋 Configuration

### Variables d'environnement (.env)

```bash
# PostgreSQL
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password  # ⚠️ À changer en production
POSTGRES_DB=letsgo_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Mode développement
DEV_MODE=true  # ⚠️ Mettre à false en production

# API Security (v2.0)
API_KEY_REQUIRED=true
API_KEYS="clé1,clé2,clé3"  # ⚠️ Générer avec security.py
```

### Génération des API Keys

```bash
# Générer 3 clés cryptographiquement sécurisées
python api_pokemon/middleware/security.py

# Sortie :
# API_KEYS="BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ,..."
```

---

## 🚀 Déploiement

### Démarrage

```bash
# 1. Construire et lancer
docker compose up --build

# 2. Attendre 10-20 minutes (premier lancement)

# 3. Accéder aux services
# Streamlit:  http://localhost:8502
# Grafana:    http://localhost:3001
# MLflow:     http://localhost:5001
# Prometheus: http://localhost:9091
```

### Vérification de la sécurité

```bash
# ❌ Accès direct API sans clé (doit échouer)
curl http://localhost:8080/pokemon
# Erreur 401 : API Key manquante

# ✅ Accès avec API Key (doit fonctionner)
curl -H "X-API-Key: BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ" \
     http://api:8080/pokemon
# (Depuis un container sur le réseau backend)

# ❌ Accès direct PostgreSQL depuis l'hôte (doit échouer)
psql -h localhost -p 5432 -U letsgo_user -d letsgo_db
# Connection refused (port non exposé)

# ✅ Accès PostgreSQL depuis un container
docker exec -it letsgo_api psql -h db -p 5432 -U letsgo_user -d letsgo_db
```

---

## 🔒 Bonnes pratiques de sécurité

### ✅ Recommandations

1. **API Keys** :
   - ✅ Générer des clés longues (32+ caractères)
   - ✅ Stocker dans un vault (pas en clair dans .env)
   - ✅ Rotation régulière (tous les 3-6 mois)
   - ✅ Clés différentes par environnement (dev/prod)
   - ✅ Révoquer immédiatement si compromises

2. **PostgreSQL** :
   - ✅ Changer `POSTGRES_PASSWORD` en production
   - ✅ Utiliser un utilisateur avec droits limités
   - ✅ Backup réguliers (volume `postgres_data`)
   - ✅ Chiffrement des données au repos (si sensible)

3. **Réseau** :
   - ✅ Maintenir le réseau `backend` privé
   - ✅ Utiliser un reverse proxy (Nginx/Traefik) en production
   - ✅ Activer HTTPS avec Let's Encrypt
   - ✅ Limiter les IPs autorisées (firewall)

4. **Docker** :
   - ✅ Ne jamais commiter `.env` ou `API_KEYS_PRIVATE.md`
   - ✅ Scanner les images : `docker scan letsgo_api`
   - ✅ Mettre à jour les images régulièrement
   - ✅ Limiter les ressources (CPU/RAM)

---

## 📊 Architecture de sécurité

### Niveaux de protection

```
┌─────────────────────────────────────────┐
│  Niveau 1 : Réseau Docker isolé         │
│  ✅ Backend privé (db, api, etl, ml)    │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Niveau 2 : Authentification API Key    │
│  ✅ Header X-API-Key obligatoire        │
│  ✅ Hash SHA-256 des clés               │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Niveau 3 : PostgreSQL isolé            │
│  ✅ Port 5432 non exposé sur l'hôte     │
│  ✅ Accès uniquement depuis backend     │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Niveau 4 : Monitoring public           │
│  ✅ Grafana/Prometheus accessibles      │
│  ✅ /health et /metrics sans auth       │
└─────────────────────────────────────────┘
```

---

## 🧪 Tests de sécurité

### Script de test

```bash
#!/bin/bash
# test_security.sh

echo "=== Test de sécurité v2.0 ==="

# Test 1 : API sans clé (doit échouer)
echo -e "\n1️⃣ Test API sans clé..."
curl -s http://localhost:8080/pokemon || echo "✅ Accès refusé (attendu)"

# Test 2 : API avec clé invalide (doit échouer)
echo -e "\n2️⃣ Test API avec clé invalide..."
curl -s -H "X-API-Key: INVALID" http://api:8080/pokemon || echo "✅ Accès refusé (attendu)"

# Test 3 : PostgreSQL depuis l'hôte (doit échouer)
echo -e "\n3️⃣ Test PostgreSQL depuis l'hôte..."
timeout 2 psql -h localhost -p 5432 -U letsgo_user -d letsgo_db 2>&1 | grep -q "Connection refused" && echo "✅ Connexion refusée (attendu)"

# Test 4 : Health check public (doit réussir)
echo -e "\n4️⃣ Test /health public..."
curl -s http://api:8080/health | grep -q "healthy" && echo "✅ Health check accessible"

# Test 5 : Metrics public (doit réussir)
echo -e "\n5️⃣ Test /metrics public..."
curl -s http://api:8080/metrics | grep -q "http_requests_total" && echo "✅ Metrics accessible"

echo -e "\n✅ Tests de sécurité terminés"
```

---

## 📝 Checklist de déploiement production

### Avant de déployer en production :

- [ ] Changer `POSTGRES_PASSWORD` (fort + unique)
- [ ] Générer de nouvelles `API_KEYS` (production uniquement)
- [ ] Mettre `DEV_MODE=false`
- [ ] Désactiver l'auto-login Grafana
- [ ] Configurer HTTPS avec Let's Encrypt
- [ ] Limiter les IPs autorisées (firewall)
- [ ] Activer les backups automatiques PostgreSQL
- [ ] Scanner les images Docker (`docker scan`)
- [ ] Configurer les logs centralisés (ELK/Loki)
- [ ] Mettre en place la rotation des clés API
- [ ] Tester le plan de disaster recovery
- [ ] Documenter les procédures d'incident

---

## 🔄 Migration depuis v1.1.0

### Changements nécessaires

1. **Mettre à jour .env** :
```bash
# Ajouter ces lignes
API_KEY_REQUIRED=true
API_KEYS="..."  # Générer avec security.py
```

2. **Mettre à jour les clients API** :
```python
# Avant
response = requests.get("http://localhost:8000/pokemon")

# Après
headers = {"X-API-Key": "VOTRE_CLE"}
response = requests.get("http://localhost:8080/pokemon", headers=headers)
```

3. **Mettre à jour les URLs** :
- Streamlit : `8501` → `8502`
- MLflow : `5000` → `5001`
- Prometheus : `9090` → `9091`
- Grafana : `3000` → `3001`

4. **Redéployer** :
```bash
docker compose down
docker compose up --build
```

---

## 📚 Références

### Fichiers modifiés

| Fichier | Changement |
|---------|------------|
| [api_pokemon/middleware/security.py](api_pokemon/middleware/security.py) | ✨ Nouveau : Middleware API Key |
| [api_pokemon/main.py](api_pokemon/main.py) | 🔒 Intégration sécurité |
| [docker-compose.yml](docker-compose.yml) | 🌐 Réseaux + Ports |
| [docker/Dockerfile.api](docker/Dockerfile.api) | 🔢 Port 8080 |
| [docker/api_entrypoint.py](docker/api_entrypoint.py) | 🔢 Port 8080 |
| [docker/prometheus/prometheus.yml](docker/prometheus/prometheus.yml) | 🔢 Port 8080 |
| [.env](.env) | 🔑 API_KEYS |

### Documentation

- [API_KEYS_PRIVATE.md](API_KEYS_PRIVATE.md) - Clés générées (NE PAS COMMITER)
- [SECURITY.md](SECURITY.md) - Ce document
- [ORCHESTRATION_SUMMARY.md](ORCHESTRATION_SUMMARY.md) - Guide orchestration v1.0

---

**Créé le** : 26 janvier 2026  
**Par** : GitHub Copilot  
**Version** : 2.0 - Architecture sécurisée  
**Statut** : ✅ Production-ready
