# E1 - Documentation Complète
## Bloc de Compétences : Développer une Solution de Collecte et de Traitement de Données

**Projet**: Pokémon Let's Go - PredictionDex
**Date**: 2026-01-20
**Candidat**: [Votre Nom]
**Formation**: Concepteur Développeur d'Applications spécialité Intelligence Artificielle

---

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture des Données](#architecture-des-données)
3. [C1 - Automatiser l'Extraction](#c1---automatiser-lextraction)
4. [C2 - Développer des Requêtes SQL](#c2---développer-des-requêtes-sql)
5. [C3 - Agrégation des Données](#c3---agrégation-des-données)
6. [C4 - Créer une Base de Données](#c4---créer-une-base-de-données)
7. [C5 - Partager le Jeu de Données](#c5---partager-le-jeu-de-données)
8. [Limites et Améliorations](#limites-et-améliorations)

---

## Vue d'ensemble

### Contexte Métier

PredictionDex est une application éducative destinée aux enfants pour apprendre les bases des combats Pokémon dans le jeu *Pokémon Let's Go Pikachu/Eevee*. L'application permet de :
- Consulter les Pokémon et leurs capacités
- Comparer l'efficacité des types
- Prédire l'issue de combats (via Machine Learning - E3)

### Objectif E1

Constituer un **jeu de données fiable, normalisé et accessible** pour alimenter à la fois l'interface utilisateur et les modèles de Machine Learning.

### Périmètre des Données

- **188 Pokémon** (formes de base + méga-évolutions)
- **226 capacités** (moves)
- **18 types élémentaires**
- **324 règles d'efficacité de type**
- **Relations** : Pokémon ↔ Capacités, Types, Stats

---

## Architecture des Données

### Schéma Relationnel

```
┌─────────────────┐         ┌──────────────┐
│ pokemon_species │◄────────│   pokemon    │
│  - id           │ 1     * │  - id        │
│  - name_fr      │         │  - species_id│
│  - name_en      │         │  - form_id   │
│  - name_jp      │         │  - sprite_url│
└─────────────────┘         └──────────────┘
                                    │
                                    │ 1
                            ┌───────┴───────┐
                            │               │
                    ┌───────▼──────┐ ┌─────▼────────┐
                    │ pokemon_stat │ │ pokemon_type │
                    │  - pokemon_id│ │  - pokemon_id│
                    │  - hp        │ │  - type_id   │
                    │  - attack    │ │  - slot      │
                    │  - defense   │ └──────────────┘
                    │  - sp_attack │         │
                    │  - sp_defense│         │ *
                    │  - speed     │         │
                    └──────────────┘   ┌─────▼──────┐
                                       │    type    │
                                       │  - id      │
                                       │  - name    │
                                       └────────────┘
                                             │
                                             │ *
                                  ┌──────────┴────────────┐
                                  │ type_effectiveness   │
                                  │  - attacking_type_id │
                                  │  - defending_type_id │
                                  │  - multiplier        │
                                  └──────────────────────┘

┌──────────────┐         ┌──────────────┐
│     move     │         │ pokemon_move │
│  - id        │◄────────│  - pokemon_id│
│  - name      │ 1     * │  - move_id   │
│  - power     │         │  - learn_lvl │
│  - accuracy  │         │  - method_id │
│  - type_id   │         └──────────────┘
│  - category_id│
│  - damage_type│
└──────────────┘
      │
      │ *
┌─────▼──────────┐
│ move_category  │
│  - id          │
│  - name        │
│  (physique,    │
│   spécial,     │
│   statut)      │
└────────────────┘
```

### Séparation des Sources de Données

| Table | Source Principale | Enrichissement | Mode de Gestion |
|-------|------------------|----------------|-----------------|
| `pokemon_species` | CSV (liste_pokemon.csv) | PokéAPI | ETL automatisé |
| `pokemon` | PokéAPI | - | ETL automatisé |
| `pokemon_stat` | PokéAPI | - | ETL automatisé |
| `pokemon_type` | PokéAPI | - | ETL automatisé |
| `type` | CSV (table_type.csv) | - | ETL automatisé |
| `type_effectiveness` | CSV (table_type.csv) | - | ETL automatisé |
| `move` | CSV (liste_capacite.csv) | Poképédia (scraping) | ETL automatisé |
| `pokemon_move` | Poképédia (scraping) | - | ETL automatisé |
| `move_category` | - | - | **init_db** (vocabulaire contrôlé) |
| `learn_method` | - | - | **init_db** (vocabulaire contrôlé) |
| `form` | - | - | **init_db** (vocabulaire contrôlé) |

### Justification init_db vs CSV

**Tables gérées par `init_db`** ([core/db/session.py:46-94](core/db/session.py#L46-L94)):
- `move_category`: 3 valeurs fixes (physique, spécial, statut)
- `learn_method`: 5 valeurs fixes (niveau, CT, évolution, tuteur, départ)
- `form`: ~10 valeurs stables (base, mega, alola, starter)

**Avantages**:
- Vocabulaire contrôlé stable
- Évite la multiplication de fichiers CSV triviaux
- Garantit la cohérence des clés étrangères
- Facilite l'initialisation de la base

---

## C1 - Automatiser l'Extraction

> **Compétence**: Automatiser l'extraction de données depuis un service web, une page web (scraping), un fichier de données, une base de données et un système big data en programmant le script adapté afin de pérenniser la collecte des données nécessaires au projet.

### 1.1 Extraction CSV

**Fichiers sources**:
- [data/csv/liste_pokemon.csv](data/csv/liste_pokemon.csv): 188 Pokémon
- [data/csv/liste_capacite_lets_go.csv](data/csv/liste_capacite_lets_go.csv): 226 capacités
- [data/csv/table_type.csv](data/csv/table_type.csv): 18 types + efficacités

**Script d'extraction**: [etl_pokemon/scripts/etl_load_csv.py](etl_pokemon/scripts/etl_load_csv.py)

**Exemple de code**:
```python
def load_pokemon_csv(db: Session):
    """Load Pokemon species from CSV."""
    csv_path = BASE_DIR / "data" / "csv" / "liste_pokemon.csv"
    df = pd.read_csv(csv_path, encoding="utf-8")

    for _, row in df.iterrows():
        species = get_or_create_pokemon_species(
            db,
            name_fr=row["nom_fr"],
            name_en=row["nom_en"],
            pokedex_id=int(row["numero"])
        )
```

**Pérennisation**:
- Encodage UTF-8 spécifié
- Gestion des valeurs manquantes (`pd.notna()`)
- Scripts idempotents (réexécutables sans duplication)

### 1.2 Enrichissement PokéAPI

**Service web**: [https://pokeapi.co/api/v2/](https://pokeapi.co/api/v2/)

**Script**: [etl_pokemon/scripts/etl_enrich_pokeapi.py](etl_pokemon/scripts/etl_enrich_pokeapi.py)

**Exemple de code**:
```python
def enrich_pokemon_from_pokeapi(db: Session, pokemon: Pokemon):
    """Enrich Pokemon data from PokeAPI."""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon.species.pokedex_id}"
    response = requests.get(url, timeout=10)
    data = response.json()

    # Stats
    upsert_pokemon_stats(
        db,
        pokemon_id=pokemon.id,
        hp=data["stats"][0]["base_stat"],
        attack=data["stats"][1]["base_stat"],
        # ...
    )
```

**Pérennisation**:
- Rate limiting (1 req/s)
- Gestion des erreurs HTTP (retry)
- Cache local (évite requêtes répétées)

### 1.3 Scraping Poképédia

**Page web**: [https://www.pokepedia.fr/Liste_des_capacités_de_Pokémon_Let%27s_Go_Pikachu_et_Let%27s_Go_Évoli](https://www.pokepedia.fr/)

**Framework**: Scrapy

**Spider**: [etl_pokemon/pokepedia_scraper/pokepedia_scraper/spiders/lgpe_moves_sql_spider.py](etl_pokemon/pokepedia_scraper/pokepedia_scraper/spiders/lgpe_moves_sql_spider.py)

**Exemple de code**:
```python
class LGPEMovesSQLSpider(scrapy.Spider):
    name = "letsgo_moves_sql"
    start_urls = ["https://www.pokepedia.fr/..."]

    def parse(self, response):
        for table in response.css("table.tableaustandard"):
            # Parse move data
            yield {
                "move_name": move_name,
                "pokemon_name": pokemon_name,
                "learn_method": method,
                "learn_level": level
            }
```

**Pérennisation**:
- Sélecteurs CSS robustes
- Gestion des timeouts
- Logs structurés (niveau INFO/WARNING)
- Pipeline de nettoyage des données

---

## C2 - Développer des Requêtes SQL

> **Compétence**: Développer des requêtes de type SQL d'extraction des données depuis un système de gestion de base de données et un système big data en appliquant le langage de requête propre au système afin de préparer la collecte des données nécessaires au projet.

### 2.1 Requêtes ORM SQLAlchemy

**Exemple 1**: Liste des Pokémon avec types ([api_pokemon/services/pokemon_service.py:32-51](api_pokemon/services/pokemon_service.py#L32-L51))

```python
def list_pokemon(db: Session) -> List[Pokemon]:
    """Retrieve all Pokemon for list views."""
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.form),
            joinedload(Pokemon.types)
                .joinedload(PokemonType.type),
        )
        .order_by(Pokemon.id)
        .all()
    )
```

**Exemple 2**: Calcul des faiblesses d'un Pokémon ([api_pokemon/services/pokemon_service.py:128-169](api_pokemon/services/pokemon_service.py#L128-L169))

```python
def compute_pokemon_weaknesses(db: Session, pokemon_id: int):
    """Compute Pokemon weaknesses based on type effectiveness."""
    defending_type_ids = [pt.type_id for pt in pokemon.types]

    # Base multiplier = 1
    multipliers = defaultdict(lambda: Decimal("1.0"))

    # Query type effectiveness
    affinities = (
        db.query(TypeEffectiveness)
        .filter(TypeEffectiveness.defending_type_id.in_(defending_type_ids))
        .all()
    )

    # Multiply affinities for dual-type Pokemon
    for eff in affinities:
        multipliers[eff.attacking_type_id] *= eff.multiplier
```

### 2.2 Requêtes SQL Brutes pour ML

**Exemple**: Extraction dataset ML ([machine_learning/build_classification_dataset.py:71-102](machine_learning/build_classification_dataset.py#L71-L102))

```python
query = """
    SELECT
        p.id as pokemon_id,
        ps.name_en as pokemon_name,
        pstat.attack as attack,
        pstat.sp_attack as sp_attack,
        pstat.defense as defense,
        pstat.sp_defense as sp_defense,
        pt1.type_id as type_1_id,
        t1.name as type_1_name,
        pt2.type_id as type_2_id,
        t2.name as type_2_name
    FROM pokemon p
    JOIN pokemon_species ps ON p.species_id = ps.id
    JOIN pokemon_stat pstat ON p.id = pstat.pokemon_id
    LEFT JOIN LATERAL (
        SELECT type_id
        FROM pokemon_type
        WHERE pokemon_id = p.id
        ORDER BY slot
        LIMIT 1
    ) pt1 ON true
    LEFT JOIN LATERAL (
        SELECT type_id
        FROM pokemon_type
        WHERE pokemon_id = p.id
        ORDER BY slot
        LIMIT 1 OFFSET 1
    ) pt2 ON true
    JOIN type t1 ON pt1.type_id = t1.id
    LEFT JOIN type t2 ON pt2.type_id = t2.id
    ORDER BY p.id;
"""
```

**Optimisations**:
- `LATERAL JOIN` pour récupérer type_1 et type_2 séparément
- `LEFT JOIN` pour Pokémon mono-type
- Eager loading via `joinedload()` (N+1 queries évitées)

---

## C3 - Agrégation des Données

> **Compétence**: Développer des règles d'agrégation de données issues de différentes sources en programmant, sous forme de script, la suppression des entrées corrompues et en programmant l'homogénéisation des formats des données afin de préparer le stockage du jeu de données final.

### 3.1 Pipeline ETL Global

**Orchestrateur**: [etl_pokemon/pipeline.py](etl_pokemon/pipeline.py)

```python
def main(force: bool = False):
    """Run complete ETL pipeline."""

    # Check if already done (via DB, not file)
    if check_etl_already_done() and not force:
        print("ℹ️  ETL already done. Skipping.")
        return

    # 1. Load CSV
    run_etl_csv()

    # 2. Enrich from PokeAPI
    run_etl_pokeapi()

    # 3. Scrape Pokepedia
    run_scrapy()

    # 4. Post-processing
    run_post_process()
```

### 3.2 Nettoyage des Données

**Exemple 1**: Normalisation des noms ([etl_pokemon/db/guards/pokemon.py:15-24](etl_pokemon/db/guards/pokemon.py))

```python
def normalize_pokemon_name(name: str) -> str:
    """Normalize Pokemon name for matching."""
    return (
        name.lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("-", " ")
        .strip()
    )
```

**Exemple 2**: Suppression des entrées corrompues

```python
# Skip moves without power (non-damaging)
if move.power is None:
    continue

# Skip invalid accuracy values
if move.accuracy is not None and not (0 <= move.accuracy <= 100):
    logger.warning(f"Invalid accuracy for move {move.name}: {move.accuracy}")
    continue
```

### 3.3 Homogénéisation des Formats

**Transformation des types**:
- CSV: `"Plante"` → DB: `"plante"` (lowercase)
- PokéAPI: `"grass"` → DB: `"plante"` (traduction)
- Poképédia: `"Plante"` → DB: `"plante"` (normalisation)

**Script**: [etl_pokemon/scripts/etl_post_process.py:35-58](etl_pokemon/scripts/etl_post_process.py)

```python
def standardize_move_names(db: Session):
    """Standardize move names across sources."""
    moves = db.query(Move).all()

    for move in moves:
        # Remove extra spaces
        move.name = " ".join(move.name.split())

        # Capitalize first letter
        move.name = move.name.capitalize()

    db.commit()
```

### 3.4 Gestion des Doublons

```python
def get_or_create_pokemon_species(db: Session, **kwargs):
    """Get or create Pokemon species (idempotent)."""
    species = db.query(PokemonSpecies).filter_by(
        pokedex_id=kwargs["pokedex_id"]
    ).first()

    if species:
        # Update if exists
        for key, value in kwargs.items():
            setattr(species, key, value)
    else:
        # Create if not exists
        species = PokemonSpecies(**kwargs)
        db.add(species)

    db.commit()
    return species
```

---

## C4 - Créer une Base de Données

> **Compétence**: Créer une base de données dans le respect du RGPD en élaborant les modèles conceptuels et physiques des données à partir des données préparées et en programmant leur import afin de stocker le jeu de données du projet.

### 4.1 Modèle Conceptuel (MCD)

**Entités principales**:
- `PokemonSpecies`: Espèce (Pikachu, Dracaufeu)
- `Pokemon`: Forme concrète (Pikachu Base, Dracaufeu Méga X)
- `Move`: Capacité (Charge, Tonnerre)
- `Type`: Type élémentaire (Feu, Eau, Plante)

**Relations**:
- Un Pokémon **possède** 1 à 2 Types (1:N)
- Un Pokémon **apprend** plusieurs Capacités (N:M)
- Une Capacité **a** 1 Type (N:1)
- Un Type **est efficace contre** un autre Type (N:M)

### 4.2 Modèle Physique (SQLAlchemy)

**Exemple**: Table `pokemon` ([core/models/pokemon.py:35-68](core/models/pokemon.py))

```python
class Pokemon(Base):
    """Pokemon form (base, mega, alola, starter)."""

    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True)
    species_id = Column(Integer, ForeignKey("pokemon_species.id"), nullable=False)
    form_id = Column(Integer, ForeignKey("form.id"), nullable=False)
    sprite_url = Column(String(255))
    height_m = Column(Numeric(4, 2))
    weight_kg = Column(Numeric(5, 2))

    # Relationships
    species = relationship("PokemonSpecies", back_populates="pokemons")
    form = relationship("Form", back_populates="pokemons")
    stats = relationship("PokemonStat", back_populates="pokemon", uselist=False)
    types = relationship("PokemonType", back_populates="pokemon")
    moves = relationship("PokemonMove", back_populates="pokemon")
```

**Contraintes d'intégrité**:
- Primary Keys: `id` (auto-incrémenté)
- Foreign Keys: Cascade DELETE (ex: suppression Pokémon → suppression stats)
- Unique constraints: `(pokemon_id, type_id, slot)` pour `pokemon_type`

### 4.3 Conformité RGPD

**Analyse des données personnelles**:
- ❌ Aucune donnée utilisateur collectée
- ❌ Aucune donnée sensible (santé, origine, religion, etc.)
- ✅ Données publiques uniquement (Pokémon, capacités)
- ✅ Sources légitimes (PokéAPI, Poképédia sous Creative Commons)

**Mesures de sécurité**:
- Connexion PostgreSQL sécurisée (credentials via `.env`)
- Isolation Docker (réseau interne)
- Aucune exposition de données personnelles via API

### 4.4 Initialisation de la Base

**Script**: [core/db/session.py:21-44](core/db/session.py)

```python
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

    # Initialize controlled vocabularies
    db = SessionLocal()
    try:
        init_move_categories(db)
        init_learn_methods(db)
        init_forms(db)
    finally:
        db.close()
```

**Migration Alembic** (non utilisé volontairement):
- Projet éducatif avec schéma stable
- `create_all()` suffisant pour reproductibilité
- Possibilité d'intégrer Alembic en production future

---

## C5 - Partager le Jeu de Données

> **Compétence**: Partager le jeu de données en configurant des interfaces logicielles et en créant des interfaces programmables afin de mettre à disposition le jeu de données pour le développement du projet.

### 5.1 API REST FastAPI

**Framework**: FastAPI
**Documentation**: Swagger UI auto-générée (`/docs`)
**Format**: JSON
**Fichier**: [api_pokemon/main.py](api_pokemon/main.py)

```python
app = FastAPI(
    title="Pokémon Let's Go API",
    description="REST API for Pokémon Let's Go Pikachu / Eevee",
    version="1.0.0",
)

app.include_router(pokemon_route.router)
app.include_router(moves_route.router)
app.include_router(type_route.router)
```

### 5.2 Endpoints Exposés

#### 5.2.1 Endpoint `/pokemon`

**GET** `/pokemon/` - Liste tous les Pokémon
**Réponse**: `List[PokemonListItem]`

```json
[
  {
    "id": 1,
    "form": {"id": 1, "name": "base"},
    "species": {
      "pokedex_id": 1,
      "name_fr": "Bulbizarre",
      "name_en": "Bulbasaur"
    },
    "sprite_url": "https://raw.githubusercontent.com/.../1.png",
    "types": [
      {"slot": 1, "name": "plante"},
      {"slot": 2, "name": "poison"}
    ]
  }
]
```

**GET** `/pokemon/search?name=pika&lang=fr` - Recherche par nom
**Réponse**: `List[PokemonListItem]`

**GET** `/pokemon/{pokemon_id}` - Détail d'un Pokémon
**Réponse**: `PokemonDetail`

```json
{
  "id": 25,
  "species": {
    "pokedex_id": 25,
    "name_fr": "Pikachu"
  },
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "sp_attack": 50,
    "sp_defense": 50,
    "speed": 90
  },
  "types": [
    {"slot": 1, "name": "électrik"}
  ],
  "moves": [
    {
      "name": "Tonnerre",
      "type": "électrik",
      "category": "spécial",
      "power": 90,
      "accuracy": 100,
      "learn_method": "CT",
      "learn_level": null
    }
  ]
}
```

**GET** `/pokemon/{pokemon_id}/weaknesses` - Faiblesses d'un Pokémon
**Réponse**: `List[PokemonWeaknessOut]`

```json
[
  {"attacking_type": "sol", "multiplier": 2.0},
  {"attacking_type": "psy", "multiplier": 1.0},
  {"attacking_type": "feu", "multiplier": 0.5}
]
```

#### 5.2.2 Endpoint `/moves`

**GET** `/moves/` - Liste toutes les capacités
**GET** `/moves/{move_id}` - Détail d'une capacité
**GET** `/moves/search?name=charge` - Recherche par nom

#### 5.2.3 Endpoint `/types`

**GET** `/types/` - Liste tous les types
**GET** `/types/{type_id}/effectiveness` - Tableau d'efficacité

### 5.3 Schémas Pydantic (Validation)

**Exemple**: [core/schemas/pokemon.py:66-76](core/schemas/pokemon.py)

```python
class PokemonListItem(BaseModel):
    """Pokemon schema for list views."""
    id: int
    form: FormOut
    species: PokemonSpeciesOut
    sprite_url: Optional[str]
    types: List[PokemonTypeOut]

    model_config = ConfigDict(from_attributes=True)
```

### 5.4 Accès pour l'Interface Streamlit

**Client HTTP**: [interface/services/api_client.py](interface/services/api_client.py)

```python
class APIClient:
    def __init__(self, base_url: str = "http://api:8000"):
        self.base_url = base_url

    def get_pokemon_list(self) -> List[dict]:
        response = requests.get(f"{self.base_url}/pokemon/")
        return response.json()
```

### 5.5 Accès pour le Machine Learning

**Export Parquet**: [data/ml/processed/train.parquet](data/ml/processed/train.parquet)
**Format**: Columnar, compressé, types préservés
**Accès Python**:

```python
import pandas as pd
df = pd.read_parquet("data/ml/processed/train.parquet")
```

---

## Limites et Améliorations

### Limites Connues

#### 1. Capacités Niveau "Départ"

**Problème**: Certaines capacités de niveau 1 sont regroupées dans une cellule source sur Poképédia.

**Exemple**: Dracolosse apprend "Charge + Cage-Éclair + Dracochoc" au niveau départ.

**Impact**: Perte potentielle d'information sur les capacités exactes.

**Statut**: Limite identifiée, non bloquante pour le MVP.

**Piste d'amélioration**: Parser plus finement les cellules multi-valeurs ou utiliser une source alternative.

#### 2. Méga-Évolutions Partielles

**Problème**: Seules les méga-évolutions présentes dans Let's Go sont incluses (Dracaufeu X/Y, Mewtwo X/Y).

**Impact**: Dataset incomplet pour générations ultérieures.

**Statut**: Conforme au périmètre Let's Go Pikachu/Eevee.

#### 3. Dépendance Réseau pour PokéAPI

**Problème**: L'enrichissement nécessite une connexion internet active.

**Mitigation**: Cache local + fallback sur données CSV si API indisponible.

**Statut**: Acceptable pour environnement de développement Docker.

### Améliorations Futures

1. **Migration Alembic**: Pour gestion versionnée du schéma en production
2. **Cache Redis**: Pour réduire latence API et charge DB
3. **GraphQL**: Alternative à REST pour requêtes complexes
4. **Webhooks**: Notification automatique lors d'ajout de nouveaux Pokémon
5. **Internationalisation**: Support multilingue complet (actuellement FR/EN/JP)

---

## Conclusion E1

### Compétences Validées

| Code | Compétence | Statut | Preuves |
|------|-----------|--------|---------|
| **C1** | Automatiser extraction | ✅ | CSV, PokéAPI, Scrapy |
| **C2** | Requêtes SQL | ✅ | SQLAlchemy ORM, SQL brut |
| **C3** | Agrégation données | ✅ | Pipeline ETL, nettoyage |
| **C4** | Créer BDD RGPD | ✅ | PostgreSQL, modèles SQLAlchemy |
| **C5** | Partager dataset | ✅ | API FastAPI, Parquet |

### Métriques Finales

- **188 Pokémon** stockés
- **226 capacités** enrichies
- **324 règles d'efficacité** calculées
- **3 endpoints API** exposés
- **100% reproductible** (Docker + scripts)
- **0 donnée personnelle** (RGPD OK)

### Livrables E1

1. ✅ Base de données PostgreSQL normalisée
2. ✅ Scripts ETL automatisés et idempotents
3. ✅ API REST FastAPI documentée (Swagger)
4. ✅ Dataset ML au format Parquet (1.35M lignes)
5. ✅ Interface Streamlit fonctionnelle (3 pages)
6. ✅ Containerisation Docker complète

---

**Date de validation**: 2026-01-20
**Prêt pour E3**: ✅ Oui
