# 📓 Guide d'Utilisation Jupyter (Local)

## 🎯 Principe Simple

**Jupyter s'exécute sur votre machine**, les services Docker sont accessibles via `localhost`.

---

## 🚀 Installation (Une seule fois)

### 1. Créer un environnement virtuel

```bash
# Dans le dossier du projet
cd /path/to/lets-go-predictiondex

# Créer venv
python3 -m venv .venv_notebooks

# Activer
source .venv_notebooks/bin/activate  # Linux/Mac
# OU
.venv_notebooks\Scripts\activate  # Windows
```

### 2. Installer les dépendances

```bash
pip install -r notebooks/requirements_jupyter.txt
```

---

## 🎬 Démarrage

### 1. Démarrer les services Docker

```bash
docker compose up -d
```

**Services démarrés**:
- PostgreSQL → `localhost:5432`
- API FastAPI → `localhost:8080`
- MLflow → `localhost:5001`
- Prometheus → `localhost:9091`
- Grafana → `localhost:3001`
- Streamlit → `localhost:8502`

### 2. Activer l'environnement virtuel

```bash
source .venv_notebooks/bin/activate
```

### 3. Lancer Jupyter Lab

```bash
cd notebooks/
jupyter lab
```

Jupyter s'ouvre automatiquement dans votre navigateur → `http://localhost:8888`

---

## 🔌 Connexions aux Services

Tous les services Docker sont accessibles via **localhost** depuis vos notebooks.

### PostgreSQL

```python
from sqlalchemy import create_engine
import pandas as pd

# Connection string (localhost car hors Docker)
DATABASE_URL = "postgresql://letsgo_user:letsgo_password@localhost:5432/letsgo_db"
engine = create_engine(DATABASE_URL)

# Query
df = pd.read_sql("SELECT * FROM pokemon LIMIT 10", engine)
print(df)
```

### API FastAPI

```python
import requests

API_URL = "http://localhost:8080"

# GET Pokemon
response = requests.get(f"{API_URL}/pokemons/25")
pikachu = response.json()
print(pikachu['name'])

# POST Prediction
payload = {
    "pokemon_a_id": 25,
    "pokemon_b_id": 6,
    "available_moves": ["thunderbolt", "quick-attack", "iron-tail", "thunder"]
}
response = requests.post(f"{API_URL}/predict/best-move", json=payload)
print(response.json())
```

### MLflow

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5001")

# Lister expériences
experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"- {exp.name}")

# Charger modèle
model = mlflow.sklearn.load_model("models:/pokemon_battle_model/Production")
```

### Prometheus

```python
import requests

PROMETHEUS_URL = "http://localhost:9091"

# Query
query = "model_predictions_total"
response = requests.get(
    f"{PROMETHEUS_URL}/api/v1/query",
    params={"query": query}
)
print(response.json())
```

---

## 📊 Récapitulatif des URLs

| Service | URL Notebook | Navigateur |
|---------|--------------|------------|
| **PostgreSQL** | `localhost:5432` | - |
| **API** | `http://localhost:8080` | http://localhost:8080/docs |
| **MLflow** | `http://localhost:5001` | http://localhost:5001 |
| **Prometheus** | `http://localhost:9091` | http://localhost:9091 |
| **Grafana** | `http://localhost:3001` | http://localhost:3001 |
| **Streamlit** | - | http://localhost:8502 |

---

## 📚 Notebooks Disponibles

```
notebooks/
├── 00_SETUP_GUIDE.md              → Ce guide
├── 00_test_connections.ipynb      → Test connexions (à exécuter en premier)
├── 01_exploration.ipynb           → Exploration données Pokemon
├── 02_feature_engineering.ipynb   → Feature engineering
├── 03_training_evaluation.ipynb   → Entraînement modèle
└── 04_scenario_comparison.ipynb   → Comparaison scénarios
```

---

## 🔍 Troubleshooting

### PostgreSQL refuse la connexion

```bash
# Vérifier que Docker tourne
docker compose ps

# Vérifier que le port 5432 est exposé
docker compose port db 5432
# Devrait afficher: 0.0.0.0:5432
```

### Module non trouvé (ImportError)

```bash
# Vérifier que le venv est activé
which python  # Doit pointer vers .venv_notebooks/bin/python

# Réinstaller les dépendances
pip install -r notebooks/requirements_jupyter.txt
```

### API injoignable

```bash
# Tester avec curl
curl http://localhost:8080/health

# Si erreur, vérifier que l'API tourne
docker compose logs api
```

---

## 🛑 Arrêt

### Arrêter Jupyter

Dans le terminal Jupyter: **Ctrl+C** deux fois

### Arrêter les services Docker

```bash
docker compose down
```

---

## ✅ Avantages de cette Approche

1. ✅ **Simple**: Jupyter s'exécute normalement sur votre machine
2. ✅ **Rapide**: Pas de rebuild Docker à chaque changement
3. ✅ **Familier**: Environnement Python classique
4. ✅ **Flexible**: Vous contrôlez les versions de packages
5. ✅ **Léger**: Pas de container Jupyter supplémentaire
6. ✅ **Debug facile**: Accès direct aux fichiers et debugger Python

---

## 📖 Ressources

- **Jupyter Lab**: https://jupyterlab.readthedocs.io/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **MLflow**: https://mlflow.org/docs/latest/python_api/
- **Pandas**: https://pandas.pydata.org/docs/

---

**Créé le**: 2026-01-30
**Auteur**: Claude Sonnet 4.5
