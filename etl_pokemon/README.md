# 🔄 ETL Pipeline - Pokémon Let's Go

> Pipeline de collecte, transformation et chargement des données Pokémon

## 📋 Vue d'ensemble

Ce module implémente un pipeline ETL complet qui :
1. **Extract** : Collecte depuis 3 sources (CSV, PokéAPI, Pokepedia)
2. **Transform** : Nettoie, normalise et agrège les données
3. **Load** : Charge dans PostgreSQL (11 tables normalisées)

## 📁 Structure

```
etl_pokemon/
├── pipeline.py              # 🚀 Orchestrateur principal
├── scripts/
│   ├── etl_init_db.py       # Initialisation schéma BDD
│   ├── etl_load_csv.py      # Chargement CSV (151 Pokémon)
│   ├── etl_enrich_pokeapi.py # Enrichissement via PokéAPI
│   ├── etl_post_process.py  # Transformations Méga
│   └── etl_previous_evolution.py # Héritage moves évolutions
├── pokepedia_scraper/       # 🕷️ Spider Scrapy
│   └── pokepedia_scraper/
│       └── spiders/
│           └── letsgo_moves_sql.py
├── data/
│   └── csv/                 # Fichiers CSV source
└── utils/                   # Utilitaires
```

## 🚀 Utilisation

### Exécution complète (recommandé)

```bash
# Via Docker (automatique au démarrage)
docker compose up etl

# En local
source .venv/bin/activate
POSTGRES_HOST=localhost python etl_pokemon/pipeline.py

# Forcer la ré-exécution
python etl_pokemon/pipeline.py --force
```

### Exécution étape par étape

```bash
# 1. Initialisation BDD
python etl_pokemon/scripts/etl_init_db.py

# 2. Chargement CSV
python etl_pokemon/scripts/etl_load_csv.py

# 3. Enrichissement PokéAPI
python etl_pokemon/scripts/etl_enrich_pokeapi.py

# 4. Scraping Pokepedia
cd etl_pokemon/pokepedia_scraper
scrapy crawl letsgo_moves_sql

# 5. Post-processing
python etl_pokemon/scripts/etl_post_process.py
python etl_pokemon/scripts/etl_previous_evolution.py
```

## 📊 Sources de Données

| Source | Type | Données | Compétence |
|--------|------|---------|------------|
| `data/csv/` | Fichier CSV | 151 Pokémon Gen 1 (base) | C1 |
| PokéAPI | API REST | Stats, types, moves (détails) | C1 |
| Pokepedia | Web Scraping | Moves Let's Go spécifiques | C1 |
| PostgreSQL | Base de données | Requêtes SQL complexes | C2 |

## 🗄️ Schéma Base de Données

```
pokemon (188)
├── pokemon_type (dual types)
├── pokemon_stats (HP, Atk, Def, SpA, SpD, Spe)
├── pokemon_move (capacités apprises)
└── pokemon_species (évolutions)

type (18)
└── type_effectiveness (324 = 18×18)

move (226)
├── move_category (physical, special, status)
└── learn_method (level-up, TM, tutor)

form (Alola, Mega)
```

## ⚙️ Variables d'Environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `POSTGRES_HOST` | localhost | Hôte PostgreSQL |
| `POSTGRES_PORT` | 5432 | Port PostgreSQL |
| `POSTGRES_DB` | letsgo_db | Nom de la base |
| `POSTGRES_USER` | letsgo_user | Utilisateur |
| `POSTGRES_PASSWORD` | letsgo_password | Mot de passe |

## 🧪 Tests

```bash
pytest tests/etl/ -v
```

## 📈 Métriques

| Métrique | Valeur |
|----------|--------|
| Pokémon chargés | 188 |
| Moves chargés | 226 |
| Types | 18 |
| Affinités de types | 324 |
| Durée ETL complète | ~5-10 min |
