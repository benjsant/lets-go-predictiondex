# E1 - Diagramme d'Architecture
## Flux de Données et Infrastructure

### Vue d'ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SOURCES DE DONNÉES                                  │
└─────────────────────────────────────────────────────────────────────────────┘
     │                          │                         │
     │ CSV                      │ API REST                │ Web Scraping
     │ (Référence)              │ (Enrichissement)        │ (Enrichissement)
     ▼                          ▼                         ▼
┌─────────────┐          ┌──────────────┐          ┌─────────────────┐
│liste_pokemon│          │  PokéAPI     │          │   Poképédia     │
│.csv         │          │pokeapi.co    │          │ (Scrapy Spider) │
│             │          │              │          │                 │
│- 188 espèces│          │- Stats base  │          │- Capacités      │
│- Noms FR/EN │          │- Sprites     │          │- Niveaux        │
│- Numéros    │          │- Types       │          │- Méthodes       │
└─────────────┘          └──────────────┘          └─────────────────┘
     │                          │                         │
     └──────────────┬───────────┴─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PIPELINE ETL                                      │
│                      (etl_pokemon/pipeline.py)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
┌────────────┐ ┌────────────┐ ┌───────────────┐
│etl_load_csv│ │etl_enrich  │ │etl_post       │
│            │ │_pokeapi    │ │_process       │
│            │ │            │ │               │
│- CSV parse │ │- API calls │ │- Nettoyage    │
│- Upsert    │ │- Rate limit│ │- Normalisation│
│- Guards    │ │- Cache     │ │- Validation   │
└────────────┘ └────────────┘ └───────────────┘
       │            │            │
       └────────────┼────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BASE DE DONNÉES PostgreSQL                              │
│                          (letsgo_db)                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                    │
       ┌────────────┼────────────────────┐
       │            │                    │
       ▼            ▼                    ▼
┌────────────┐ ┌────────────┐    ┌──────────────┐
│  pokemon   │ │    move    │    │type_         │
│  (188)     │ │   (226)    │    │effectiveness │
│            │ │            │    │  (324)       │
│- species_id│ │- name      │    │              │
│- form_id   │ │- power     │    │- attack_type │
│- sprite    │ │- accuracy  │    │- defend_type │
└────────────┘ └────────────┘    │- multiplier  │
       │            │             └──────────────┘
       ▼            ▼                    │
┌────────────┐ ┌────────────┐           │
│pokemon_stat│ │pokemon_move│           │
│            │ │            │           │
│- hp        │ │- learn_lvl │           │
│- attack    │ │- method_id │           │
│- defense   │ └────────────┘           │
└────────────┘                          │
                                        │
                    ┌───────────────────┘
                    │
       ┌────────────┼────────────────────┐
       │            │                    │
       ▼            ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COUCHE APPLICATION                                    │
└─────────────────────────────────────────────────────────────────────────────┘
       │            │                    │
       ▼            ▼                    ▼
┌────────────┐ ┌────────────┐    ┌──────────────┐
│  FastAPI   │ │ ML Dataset │    │  Streamlit   │
│    API     │ │  Builder   │    │  Interface   │
│            │ │            │    │              │
│/pokemon    │ │build_      │    │- Home        │
│/moves      │ │classification│  │- Moves       │
│/types      │ │_dataset.py │    │- Compare     │
│            │ │            │    │              │
│Port: 8000  │ │→ Parquet   │    │Port: 8501    │
└────────────┘ └────────────┘    └──────────────┘
       │                                │
       └────────────────┬───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          UTILISATEURS FINAUX                                 │
│                                                                              │
│  - Enfants (interface Streamlit)                                            │
│  - Data Scientists (dataset Parquet)                                        │
│  - Développeurs (API REST)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Flux ETL Détaillé

```
PHASE 1: INITIALISATION
├─ init_db()
│  ├─ CREATE TABLE pokemon_species
│  ├─ CREATE TABLE pokemon
│  ├─ CREATE TABLE move
│  ├─ CREATE TABLE type
│  ├─ INSERT INTO move_category (physique, spécial, statut)
│  ├─ INSERT INTO learn_method (niveau, CT, tuteur, évolution, départ)
│  └─ INSERT INTO form (base, mega, alola, starter)

PHASE 2: LOAD CSV (Données de Référence)
├─ load_pokemon_csv()
│  ├─ READ data/csv/liste_pokemon.csv
│  ├─ FOR EACH row:
│  │  └─ UPSERT pokemon_species (nom_fr, nom_en, numero)
│  └─ COMMIT
│
├─ load_types_csv()
│  ├─ READ data/csv/table_type.csv
│  ├─ FOR EACH row:
│  │  ├─ UPSERT type (nom)
│  │  └─ UPSERT type_effectiveness (attaquant, défenseur, multiplicateur)
│  └─ COMMIT
│
└─ load_moves_csv()
   ├─ READ data/csv/liste_capacite_lets_go.csv
   ├─ FOR EACH row:
   │  └─ UPSERT move (nom, puissance, précision, type)
   └─ COMMIT

PHASE 3: ENRICH FROM POKEAPI (Enrichissement)
├─ FOR EACH pokemon_species:
│  ├─ GET https://pokeapi.co/api/v2/pokemon/{id}
│  ├─ SLEEP 1s (rate limiting)
│  ├─ CREATE pokemon (form=base)
│  ├─ UPSERT pokemon_stat (hp, attack, defense, ...)
│  └─ UPSERT pokemon_type (type1, type2)
│
├─ Handle Mega Evolutions:
│  ├─ GET https://pokeapi.co/api/v2/pokemon/{id}-mega-x
│  ├─ CREATE pokemon (form=mega_x)
│  └─ ...
│
└─ COMMIT

PHASE 4: SCRAPE POKEPEDIA (Enrichissement)
├─ RUN scrapy crawl letsgo_moves_sql
│  ├─ PARSE https://www.pokepedia.fr/Liste_des_capacités...
│  ├─ FOR EACH <table class="tableaustandard">:
│  │  ├─ EXTRACT pokemon_name
│  │  ├─ EXTRACT move_name
│  │  ├─ EXTRACT learn_method (niveau, CT, tuteur)
│  │  ├─ EXTRACT learn_level
│  │  └─ UPSERT pokemon_move
│  └─ COMMIT
│
└─ Log: "2471 items scraped"

PHASE 5: POST-PROCESSING
├─ inherit_mega_moves()
│  └─ FOR EACH mega_pokemon:
│     └─ COPY moves FROM base_form
│
├─ standardize_names()
│  └─ FOR EACH move:
│     ├─ TRIM whitespace
│     └─ CAPITALIZE first letter
│
└─ COMMIT

RÉSULTAT:
✓ 188 Pokémon
✓ 226 Capacités
✓ 18 Types
✓ 324 Règles d'efficacité
✓ ~5000 Relations Pokémon-Capacité
```

---

### Architecture Docker

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOCKER COMPOSE NETWORK                                │
│                     (lets-go-predictiondex_default)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  letsgo_postgres │ (Service 1 - Daemon)
│  ────────────────│
│  Image: postgres:15
│  Port: 5432
│  Volume: postgres_data (persistant)
│  Healthcheck: pg_isready
│  Environment:
│    - POSTGRES_USER=letsgo_user
│    - POSTGRES_PASSWORD=***
│    - POSTGRES_DB=letsgo_db
└──────────────────┘
         │
         │ depends_on: db (healthy)
         ▼
┌──────────────────┐
│   letsgo_etl     │ (Service 2 - One-shot)
│  ────────────────│
│  Build: docker/Dockerfile.etl
│  Command: python docker/etl_entrypoint.py
│  Restart: "no"
│  Volumes:
│    - ./etl_pokemon:/app/etl_pokemon
│    - ./core:/app/core
│    - ./data:/app/data
│  Entrypoint:
│    1. Check DB ready
│    2. Check if ETL already done (SELECT COUNT(*) FROM pokemon)
│    3. Run pipeline.py (if needed)
└──────────────────┘
         │
         │ depends_on: etl (completed_successfully)
         ▼
┌──────────────────┐
│ letsgo_ml_builder│ (Service 3 - One-shot)
│  ────────────────│
│  Build: docker/Dockerfile.ml
│  Command: python machine_learning/build_dataset_ml_v2.py
│  Restart: "no"
│  Volumes:
│    - ./machine_learning:/app/machine_learning
│    - ./data:/app/data
│  Output:
│    - data/datasets/pokemon_damage_ml.parquet (578K rows)
└──────────────────┘
         │
         │ depends_on: db (healthy) + etl (completed)
         ▼
┌──────────────────┐
│   letsgo_api     │ (Service 4 - Daemon)
│  ────────────────│
│  Build: docker/Dockerfile.api
│  Port: 8000 (host) → 8000 (container)
│  Command: uvicorn api_pokemon.main:app --reload
│  Volumes:
│    - ./api_pokemon:/app/api_pokemon
│    - ./core:/app/core
│  Healthcheck: GET http://localhost:8000/health
└──────────────────┘
         │
         │ depends_on: api (healthy)
         ▼
┌──────────────────┐
│letsgo_streamlit  │ (Service 5 - Daemon)
│  ────────────────│
│  Build: docker/Dockerfile.streamlit
│  Port: 8501 (host) → 8501 (container)
│  Command: streamlit run interface/app.py
│  Volumes:
│    - ./interface:/app/interface
│  Environment:
│    - API_BASE_URL=http://api:8000
└──────────────────┘
```

**Ordre de démarrage garanti**:
```
1. letsgo_postgres (démarrage immédiat)
   └─> healthcheck toutes les 5s

2. letsgo_etl (attend db:healthy)
   └─> s'exécute puis exit 0

3. letsgo_ml_builder (attend etl:completed_successfully)
   └─> s'exécute puis exit 0

4. letsgo_api (attend db:healthy + etl:completed)
   └─> reste actif (daemon)
   └─> healthcheck toutes les 10s

5. letsgo_streamlit (attend api:healthy)
   └─> reste actif (daemon)
```

---

### Modèle de Données Détaillé

```sql
-- TABLES DE RÉFÉRENCE (vocabulaire contrôlé)
CREATE TABLE form (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
    -- Valeurs: base, mega, mega_x, mega_y, alola, starter
);

CREATE TABLE move_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
    -- Valeurs: physique, spécial, statut
);

CREATE TABLE learn_method (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
    -- Valeurs: niveau, CT, tuteur, évolution, départ
);

-- TABLES PRINCIPALES
CREATE TABLE pokemon_species (
    id SERIAL PRIMARY KEY,
    pokedex_id INTEGER UNIQUE NOT NULL,
    name_fr VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    name_jp VARCHAR(100)
);

CREATE TABLE pokemon (
    id SERIAL PRIMARY KEY,
    species_id INTEGER REFERENCES pokemon_species(id) ON DELETE CASCADE,
    form_id INTEGER REFERENCES form(id) ON DELETE CASCADE,
    sprite_url VARCHAR(255),
    height_m DECIMAL(4,2),
    weight_kg DECIMAL(5,2),
    UNIQUE(species_id, form_id)
);

CREATE TABLE pokemon_stat (
    pokemon_id INTEGER PRIMARY KEY REFERENCES pokemon(id) ON DELETE CASCADE,
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    sp_attack INTEGER NOT NULL,
    sp_defense INTEGER NOT NULL,
    speed INTEGER NOT NULL
);

CREATE TABLE type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
    -- 18 types: normal, feu, eau, plante, électrik, glace, combat, poison, sol,
    --           vol, psy, insecte, roche, spectre, dragon, ténèbres, acier, fée
);

CREATE TABLE pokemon_type (
    pokemon_id INTEGER REFERENCES pokemon(id) ON DELETE CASCADE,
    type_id INTEGER REFERENCES type(id) ON DELETE CASCADE,
    slot INTEGER NOT NULL CHECK (slot IN (1, 2)),
    PRIMARY KEY (pokemon_id, type_id),
    UNIQUE (pokemon_id, slot)
);

CREATE TABLE type_effectiveness (
    attacking_type_id INTEGER REFERENCES type(id) ON DELETE CASCADE,
    defending_type_id INTEGER REFERENCES type(id) ON DELETE CASCADE,
    multiplier DECIMAL(3,2) NOT NULL,
    PRIMARY KEY (attacking_type_id, defending_type_id)
    -- multiplier: 0.0 (aucun effet), 0.25, 0.5, 1.0, 2.0, 4.0
);

CREATE TABLE move (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type_id INTEGER REFERENCES type(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES move_category(id) ON DELETE CASCADE,
    power INTEGER,
    accuracy INTEGER CHECK (accuracy IS NULL OR (accuracy >= 0 AND accuracy <= 100)),
    description TEXT,
    damage_type VARCHAR(50)
    -- damage_type: offensif, critique_100, multi_coups, degat_aleatoire, etc.
);

CREATE TABLE pokemon_move (
    pokemon_id INTEGER REFERENCES pokemon(id) ON DELETE CASCADE,
    move_id INTEGER REFERENCES move(id) ON DELETE CASCADE,
    learn_method_id INTEGER REFERENCES learn_method(id) ON DELETE CASCADE,
    learn_level INTEGER,
    PRIMARY KEY (pokemon_id, move_id, learn_method_id)
);

-- INDEX POUR PERFORMANCE
CREATE INDEX idx_pokemon_species ON pokemon(species_id);
CREATE INDEX idx_pokemon_move_pokemon ON pokemon_move(pokemon_id);
CREATE INDEX idx_pokemon_move_move ON pokemon_move(move_id);
CREATE INDEX idx_type_effectiveness_attacking ON type_effectiveness(attacking_type_id);
CREATE INDEX idx_type_effectiveness_defending ON type_effectiveness(defending_type_id);
```

---

### Patterns et Bonnes Pratiques

**1. Idempotence (Guards)**
```python
def upsert_pokemon_species(db: Session, **kwargs):
    """Get or create - idempotent."""
    species = db.query(PokemonSpecies).filter_by(
        pokedex_id=kwargs["pokedex_id"]
    ).first()

    if species:
        for key, value in kwargs.items():
            setattr(species, key, value)
    else:
        species = PokemonSpecies(**kwargs)
        db.add(species)

    db.commit()
    return species
```

**2. Validation (Pydantic)**
```python
class PokemonStatsOut(BaseModel):
    hp: int = Field(..., ge=1, le=255)
    attack: int = Field(..., ge=1, le=255)
    defense: int = Field(..., ge=1, le=255)
    sp_attack: int = Field(..., ge=1, le=255)
    sp_defense: int = Field(..., ge=1, le=255)
    speed: int = Field(..., ge=1, le=255)
```

**3. Eager Loading (N+1 Prevention)**
```python
pokemon = (
    db.query(Pokemon)
    .options(
        joinedload(Pokemon.species),
        joinedload(Pokemon.stats),
        joinedload(Pokemon.types).joinedload(PokemonType.type),
        joinedload(Pokemon.moves).joinedload(PokemonMove.move)
    )
    .filter(Pokemon.id == pokemon_id)
    .one_or_none()
)
```

**4. Transaction Safety**
```python
try:
    # Multiple DB operations
    db.add(pokemon)
    db.add(stats)
    db.commit()
except Exception as e:
    db.rollback()
    logger.error(f"Transaction failed: {e}")
    raise
finally:
    db.close()
```

---

## Métriques et Performance

| Métrique | Valeur | Cible | Statut |
|----------|--------|-------|--------|
| Nombre de tables | 11 | - | ✅ |
| Nombre de relations FK | 12 | - | ✅ |
| Temps init DB | ~2s | <5s | ✅ |
| Temps ETL complet | ~3min | <5min | ✅ |
| Temps génération dataset ML | ~10min | <15min | ✅ |
| Latence API (`/pokemon/`) | ~50ms | <100ms | ✅ |
| Latence API (`/pokemon/{id}`) | ~30ms | <50ms | ✅ |
| Taille DB (données) | ~5 MB | <50 MB | ✅ |
| Taille dataset ML (Parquet) | 6-13 MB | <100 MB | ✅ |

---

**Document créé le**: 2026-01-20
**Version**: 1.0
