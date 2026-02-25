# ETL Pipeline

Pipeline de collecte, transformation et chargement des données Pokémon Let's Go.

## Ce que ça fait

1. **Extract** : collecte depuis 3 sources (CSV locaux, PokeAPI, scraping Pokepedia)
2. **Transform** : nettoyage, normalisation, agrégation
3. **Load** : insertion dans PostgreSQL (11 tables normalisées 3NF)

## Structure

```
etl_pokemon/
├── pipeline.py                    # Orchestrateur principal
├── scripts/
│   ├── etl_init_db.py             # Init schéma BDD
│   ├── etl_load_csv.py            # Chargement CSV (151 Pokémon)
│   ├── etl_enrich_pokeapi.py      # Enrichissement via PokeAPI
│   ├── etl_post_process.py        # Transformations Méga
│   └── etl_previous_evolution.py  # Héritage moves évolutions
├── pokepedia_scraper/             # Spider Scrapy pour les moves Let's Go
├── data/csv/                      # Fichiers CSV source
└── utils/
```

## Lancer

```bash
# Via Docker (s'exécute automatiquement au démarrage)
docker compose up etl

# En local
source .venv/bin/activate
POSTGRES_HOST=localhost python etl_pokemon/pipeline.py

# Forcer la ré-exécution
python etl_pokemon/pipeline.py --force
```

On peut aussi lancer chaque étape séparément :

```bash
python etl_pokemon/scripts/etl_init_db.py
python etl_pokemon/scripts/etl_load_csv.py
python etl_pokemon/scripts/etl_enrich_pokeapi.py
cd etl_pokemon/pokepedia_scraper && scrapy crawl letsgo_moves_sql
python etl_pokemon/scripts/etl_post_process.py
python etl_pokemon/scripts/etl_previous_evolution.py
```

## Sources de données

- **CSV** (`data/csv/`) : 151 Pokémon Gen 1 de base
- **PokeAPI** : stats, types, détails des moves
- **Pokepedia** (Scrapy) : moves spécifiques à Let's Go

## Résultat

188 Pokémon, 226 moves, 18 types, 324 affinités de types. Le pipeline complet prend environ 5-10 min.

## Troubleshooting

**"Connection refused" sur PostgreSQL** : vérifier que le service `db` est lancé et que `POSTGRES_HOST` est correct (`localhost` en local, `db` dans Docker).

**Le scraping Pokepedia échoue** : le site peut être temporairement indisponible ou avoir changé de structure HTML. Les données déjà insérées en BDD ne sont pas re-scrapées.

**"Table already exists"** : le pipeline est idempotent. Relancer avec `--force` pour tout recréer depuis zéro.

**L'ETL est très lent** : l'enrichissement PokeAPI fait ~188 requêtes HTTP et le scraping Pokepedia ~153 pages. Avec les délais de politesse, 5-10 min est normal au premier lancement.

## Variables d'environnement

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password
```
