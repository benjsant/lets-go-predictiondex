# 🗄️ Core - Modèles et Base de Données

> Couche d'abstraction pour la base de données PostgreSQL

## 📋 Vue d'ensemble

Ce module contient :
- Les modèles SQLAlchemy ORM (11 tables)
- La configuration de connexion à la BDD
- Les schémas Pydantic de validation
- Les guards et utilitaires

## 📁 Structure

```
core/
├── __init__.py
├── db/                       # Configuration base de données
│   ├── __init__.py
│   ├── base.py               # DeclarativeBase SQLAlchemy
│   ├── session.py            # SessionLocal, get_db()
│   └── guards/               # Validators et guards
├── models/                   # Modèles ORM SQLAlchemy
│   ├── __init__.py
│   ├── pokemon.py            # Pokemon
│   ├── pokemon_type.py       # PokemonType (association)
│   ├── pokemon_stat.py       # PokemonStat
│   ├── pokemon_move.py       # PokemonMove (association)
│   ├── pokemon_species.py    # PokemonSpecies
│   ├── type.py               # Type
│   ├── type_effectiveness.py # TypeEffectiveness
│   ├── move.py               # Move
│   ├── move_category.py      # MoveCategory
│   ├── learn_method.py       # LearnMethod
│   └── form.py               # Form (Alola, Mega)
└── schemas/                  # Schémas Pydantic
    ├── __init__.py
    ├── pokemon.py
    ├── move.py
    └── type.py
```

## 🗄️ Modèles ORM

### Entités principales

| Modèle | Table | Description | Colonnes clés |
|--------|-------|-------------|---------------|
| `Pokemon` | pokemon | Pokémon (188) | id, name, pokedex_number |
| `Type` | type | Types (18) | id, name, color |
| `Move` | move | Capacités (226) | id, name, power, accuracy |
| `MoveCategory` | move_category | Catégories (3) | physical, special, status |

### Tables d'association

| Modèle | Table | Description |
|--------|-------|-------------|
| `PokemonType` | pokemon_type | Pokémon ↔ Types (dual types) |
| `PokemonMove` | pokemon_move | Pokémon ↔ Moves |
| `PokemonStat` | pokemon_stat | Stats (HP, Atk, Def, SpA, SpD, Spe) |
| `TypeEffectiveness` | type_effectiveness | Matrice 18×18 affinités |

## 💻 Utilisation

### Connexion à la base

```python
from core.db.session import get_db, SessionLocal

# Via dependency injection (FastAPI)
def get_pokemon(db: Session = Depends(get_db)):
    return db.query(Pokemon).all()

# Via context manager
with SessionLocal() as db:
    pokemon = db.query(Pokemon).filter_by(name="Pikachu").first()
```

### Requêtes ORM

```python
from core.models import Pokemon, Type, Move, PokemonType

# Récupérer un Pokémon avec ses types
pokemon = db.query(Pokemon).filter_by(id=25).first()
types = [pt.type.name for pt in pokemon.pokemon_types]

# Jointure complexe
query = (
    db.query(Pokemon, Move)
    .join(PokemonMove)
    .join(Move)
    .filter(Pokemon.id == 25)
)
```

### Schémas Pydantic

```python
from core.schemas import PokemonResponse, MoveResponse

# Validation automatique
pokemon_data = PokemonResponse.model_validate(pokemon)
```

## ⚙️ Configuration

Variables d'environnement pour la connexion :

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password
```

Construction de l'URL dans `session.py` :

```python
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
```

## 🧪 Tests

```bash
pytest tests/core/ -v
```

## 📊 Schéma Relationnel

```
pokemon ─────┬───── pokemon_type ───── type
             │                           │
             ├───── pokemon_stat         │
             │                           │
             ├───── pokemon_move ── move ┴── move_category
             │             │
             └── pokemon_species    learn_method
                    │
                   form

type ───── type_effectiveness ───── type
(attacking_type)              (defending_type)
```
