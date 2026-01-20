# Docker Setup - PredictionDex Pokémon Let's Go

## 🎉 Status: 100% Fonctionnel

Tous les services démarrent correctement et les tests passent.

---

## 🚀 Démarrage Rapide

### 1. Prérequis

- Docker Engine 20+
- Docker Compose v2+
- 4 GB RAM minimum
- 5 GB espace disque

### 2. Lancer tous les services

```bash
docker compose up --build
```

### 3. Accéder aux interfaces

- **Streamlit UI**: http://localhost:8501
- **API Swagger**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

---

## 📊 Architecture

```
PostgreSQL (DB)
    │
    ├──> ETL Pipeline (one-shot)
    │     └─> CSV + PokéAPI + Scraping → 188 Pokémon, 226 moves
    │
    ├──> ML Builder (one-shot)
    │     └─> Dataset: 578,100 lignes (1.5 MB)
    │
    ├──> API FastAPI (daemon)
    │     └─> REST endpoints + Swagger
    │
    └──> Streamlit (daemon)
          └─> Interface web
```

---

## 🧪 Vérifier l'installation

```bash
python test_all.py
```

**Résultat attendu**:
```
✅ Docker Compose OK
✅ PostgreSQL OK (188 Pokémon)
✅ API OK ({"status":"ok"})
✅ Endpoint /pokemon/ OK (Bulbizarre)
✅ Streamlit OK
✅ Dataset ML OK (1.51 MB)
✅ ETL complété
```

---

## 📁 Services

| Service | Type | Port | Description |
|---------|------|------|-------------|
| **db** | Daemon | 5432 | PostgreSQL 15 |
| **etl** | One-shot | - | Pipeline ETL (CSV + API + Scraping) |
| **ml_builder** | One-shot | - | Génération dataset ML |
| **api** | Daemon | 8000 | API REST FastAPI |
| **streamlit** | Daemon | 8501 | Interface web |

---

## 🔧 Commandes Utiles

### Logs

```bash
# Tous les services
docker compose logs -f

# Un service spécifique
docker compose logs -f api
docker compose logs -f streamlit
```

### Redémarrer un service

```bash
docker compose restart api
docker compose restart streamlit
```

### Relancer ETL ou ML

```bash
# Relancer ETL (recharge les données)
docker compose run --rm etl

# Relancer ML Builder (régénère le dataset)
docker compose run --rm ml_builder
```

### Stopper

```bash
# Stopper sans supprimer les données
docker compose down

# Stopper et supprimer les volumes (⚠️ perte de données)
docker compose down -v
```

---

## 📊 Données Chargées

### Base PostgreSQL

```sql
SELECT COUNT(*) FROM pokemon;           -- 188 formes
SELECT COUNT(*) FROM move;              -- 226 capacités
SELECT COUNT(*) FROM type_effectiveness; -- 324 (18×18)
```

### Dataset ML

```
Fichier: data/datasets/pokemon_damage_ml.parquet
Lignes: 578,100
Taille: 1.5 MB
Format: Parquet (pandas)
Niveau: 50 uniquement (optimisé)
```

**Colonnes**:
- `attacker_id`, `defender_id`
- `attacker_level`, `defender_level` (50)
- `move_name`, `move_type`, `move_category`
- `move_power`, `move_accuracy`
- `damage_type`, `stab`, `type_multiplier`
- `expected_damage`

---

## 🔄 Mode Développement

### Hot Reload Activé

- **API**: Uvicorn --reload (changements Python détectés)
- **Streamlit**: runOnSave (refresh automatique)

### Modifier le code

Éditez simplement les fichiers locaux :
- `api_pokemon/` → API se reload automatiquement
- `interface/` → Streamlit se refresh automatiquement
- `core/` → Partagé par tous les services

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **README_DOCKER.md** | Ce fichier - Vue d'ensemble |
| [QUICK_START.md](QUICK_START.md) | Démarrage en 3 commandes |
| [DOCKER_SETUP.md](DOCKER_SETUP.md) | Configuration détaillée + Troubleshooting |
| [CORRECTIONS_DOCKER.md](CORRECTIONS_DOCKER.md) | Corrections appliquées (série 1) |
| [CORRECTIONS_ETL_LOOPS.md](CORRECTIONS_ETL_LOOPS.md) | Corrections ETL/ML (série 2) |
| [SUCCES_DOCKER.md](SUCCES_DOCKER.md) | Récapitulatif succès + recommandations |
| `test_all.py` | Script de test automatique |

---

## 🐛 Troubleshooting

### "Port 8000 already in use"

```bash
# Trouver le processus
lsof -i :8000

# Ou changer le port dans docker-compose.yml
ports:
  - "8001:8000"  # Utiliser 8001 au lieu de 8000
```

### "Database connection error"

```bash
# Vérifier que PostgreSQL est healthy
docker compose ps

# Attendre que db soit ready
docker compose logs db | grep "ready to accept connections"
```

### "Module import error"

```bash
# Rebuild les images
docker compose build --no-cache

# Vérifier PYTHONPATH
docker compose exec api env | grep PYTHONPATH
```

### Dataset ML trop volumineux

Le dataset est déjà optimisé (niveau 50 uniquement).

Si besoin de réduire davantage, éditer [machine_learning/build_dataset_ml_v1.py](machine_learning/build_dataset_ml_v1.py:25):

```python
# Ligne 25-26
ATTACKER_LEVELS = [50]  # Déjà optimisé
DEFENDER_LEVELS = [50]  # Déjà optimisé
```

---

## ✅ Validation

Tous les services ont été testés et fonctionnent:

- [x] PostgreSQL démarre et est healthy
- [x] ETL se termine avec succès (5,130 items scraped)
- [x] ML builder génère le dataset (578,100 lignes)
- [x] API répond aux requêtes
- [x] Streamlit est accessible
- [x] Healthchecks fonctionnent
- [x] Hot reload fonctionne

**Dernière validation**: 2026-01-20

---

## 📖 Endpoints API Disponibles

### Pokémon

```bash
# Liste tous les Pokémon
GET /pokemon/

# Détails d'un Pokémon
GET /pokemon/{id}
```

### Moves

```bash
# Liste toutes les capacités
GET /moves/

# Détails d'une capacité
GET /moves/{id}
```

### Types

```bash
# Liste tous les types
GET /types/
```

### Health

```bash
# Status de l'API
GET /health
```

---

## 🎯 Prochaines Étapes

1. Tester l'interface Streamlit : http://localhost:8501
2. Explorer l'API Swagger : http://localhost:8000/docs
3. Développer de nouvelles fonctionnalités
4. Ajouter des tests unitaires (pytest)
5. Configurer CI/CD (GitHub Actions)

---

**Configuration validée**: Docker Compose v2+ / Docker Engine 20+
**Mode**: Development (DEV_MODE=true)
**Date**: 2026-01-20
