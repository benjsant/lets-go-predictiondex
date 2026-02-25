# Core - Base de données

Couche d'accès aux données : modèles SQLAlchemy ORM, connexion PostgreSQL et schémas Pydantic.

## Structure

```
core/
├── db/
│   ├── base.py       # DeclarativeBase SQLAlchemy
│   ├── session.py    # SessionLocal, get_db()
│   └── guards/       # Validators
├── models/           # 11 modèles ORM
│   ├── pokemon.py, pokemon_type.py, pokemon_stat.py, pokemon_move.py
│   ├── pokemon_species.py
│   ├── type.py, type_effectiveness.py
│   ├── move.py, move_category.py, learn_method.py
│   └── form.py       # Alola, Mega
└── schemas/          # Schémas Pydantic (pokemon, move, type)
```

## Modèles

Entités principales : `Pokemon` (188), `Type` (18), `Move` (226), `MoveCategory` (3).

Tables d'association : `PokemonType` (dual types), `PokemonMove`, `PokemonStat` (HP/Atk/Def/SpA/SpD/Spe), `TypeEffectiveness` (matrice 18x18).

Tables de référence : `Form` (normal, alola, mega_x, mega_y), `LearnMethod` (level-up, ct, move-tutor, before-evolution), `PokemonSpecies` (lien espèce → formes).

## Relations clés

- Un `Pokemon` appartient à une `PokemonSpecies` et a une `Form`
- Un `Pokemon` a 1-2 `PokemonType` (via table d'association, `slot` 1 ou 2)
- Un `Pokemon` a 6 `PokemonStat` (HP, Atk, Def, SpA, SpD, Spe)
- Un `Pokemon` apprend des `Move` via `PokemonMove` (avec `LearnMethod` et niveau)
- Un `Move` a un `Type` et une `MoveCategory` (physique, spécial, statut)
- `TypeEffectiveness` stocke les 324 multiplicateurs (18x18), valeurs : 0, 0.5, 1, 2

## Utilisation

```python
from core.db.session import get_db, SessionLocal
from core.models import Pokemon, Type, Move

# Via FastAPI dependency injection
def get_pokemon(db: Session = Depends(get_db)):
    return db.query(Pokemon).all()

# Directement
with SessionLocal() as db:
    pokemon = db.query(Pokemon).filter_by(name="Pikachu").first()
    types = [pt.type.name for pt in pokemon.pokemon_types]
```

## Configuration

Variables d'environnement pour la connexion :

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password
```

## Schéma relationnel

```
pokemon ─┬─ pokemon_type ─── type
         ├─ pokemon_stat
         ├─ pokemon_move ── move ── move_category
         └─ pokemon_species      learn_method
              │
              form

type ── type_effectiveness ── type
```
