# api_pokemon/routes/moves_route.py
"""
API routes – Pokémon moves
==========================

FastAPI endpoints for Pokémon moves.
Designed to be Streamlit-friendly and unambiguous.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_pokemon.services.move_service import (
    get_move_by_id,
    list_moves,
    list_moves_by_type,
    search_moves_by_name,
)
from core.db.session import get_db
from core.schemas.move import (
    MoveDetail,
    MoveListItem,
    MoveSelectableOut,
)
from core.schemas.type import TypeOut

router = APIRouter(prefix="/moves", tags=["Moves"])


# ============================================================
# 🔹 LIST ALL MOVES
# ============================================================
@router.get("/", response_model=List[MoveListItem])
def get_moves(db: Session = Depends(get_db)):
    """
    List all Pokémon moves from the database.

    Returns a complete list of all 226 moves available in Pokémon Let's Go
    with basic information (lightweight for performance).

    **Returns:**
    List of moves with:
    - id: Move unique identifier
    - name: Move name (French)
    - category: Physical/Special/Status
    - power: Base power (null for status moves)
    - accuracy: Accuracy percentage (null for moves that never miss)
    - description: Move description
    - type: Move type (Fire, Water, Electric, etc.)

    **Example Response:**
    ```json
    [
      {
        "id": 1,
        "name": "Charge",
        "category": "Physical",
        "power": 50,
        "accuracy": 100,
        "description": "A physical attack...",
        "type": {"id": 1, "name": "Normal"}
      }
    ]
    ```

    **Use Case:**
    Populate move selection lists in Streamlit interface.
    """
    moves = list_moves(db)

    return [
        MoveListItem(
            id=move.id,
            name=move.name,
            category=move.category.name,
            power=move.power,
            accuracy=move.accuracy,
            description=move.description,
            type=TypeOut(
                id=move.type.id,
                name=move.type.name,
            ),
        )
        for move in moves
    ]


# ============================================================
# 🔹 SEARCH MOVES BY NAME (FR)
# ============================================================
@router.get("/search", response_model=List[MoveListItem])
def search_moves(
    name: str = Query(
        ...,
        min_length=1,
        description="Partial or full move name (French, accent-insensitive)",
    ),
    db: Session = Depends(get_db),
):
    """
    Search for moves by French name (partial or full match).

    Performs case-insensitive and accent-insensitive partial match on move names.
    Designed to be Streamlit-friendly by returning empty list instead of 404.

    **Query Parameters:**
    - name: Move name to search (minimum 1 character)
      - Partial match supported (e.g., "foud" matches "Fatal-Foudre")
      - Accent-insensitive (e.g., "eclair" matches "Éclair")
      - Case-insensitive

    **Returns:**
    List of matching moves (empty list if no matches)

    **Example Request:**
    ```
    GET /moves/search?name=foud
    ```

    **Example Response:**
    ```json
    [
      {
        "id": 87,
        "name": "Fatal-Foudre",
        "category": "Special",
        "power": 110,
        "accuracy": 70,
        "description": "Une puissante décharge électrique...",
        "type": {"id": 4, "name": "Electric"}
      }
    ]
    ```

    **Note:**
    - No 404 error if no match (returns empty list)
    - Optimized for autocomplete and search-as-you-type interfaces

    **Use Case:**
    Move search in Streamlit interface (autocomplete).
    """
    moves = search_moves_by_name(db, name)

    return [
        MoveListItem(
            id=move.id,
            name=move.name,
            category=move.category.name,
            power=move.power,
            accuracy=move.accuracy,
            description=move.description,
            type=TypeOut(
                id=move.type.id,
                name=move.type.name,
            ),
        )
        for move in moves
    ]


# ============================================================
# 🔹 LIST MOVES BY TYPE (+ optional Pokémon filter)
# ============================================================
@router.get(
    "/by-type/{type_name}",
    response_model=List[MoveSelectableOut],
)
def get_moves_by_type(
    type_name: str,
    pokemon_id: Optional[int] = Query(
        None,
        description="Optional Pokémon ID to restrict to learnable moves",
    ),
    db: Session = Depends(get_db),
):
    """
    List all moves of a specific type.

    Returns all moves of the specified type. If a Pokémon ID is provided,
    includes learning information (method and level) for that specific Pokémon.

    **Path Parameters:**
    - type_name: Type name (e.g., "Fire", "Water", "Electric")

    **Query Parameters:**
    - pokemon_id (optional): Filter to show only moves learnable by this Pokémon
      - If provided: Includes learn_method and learn_level
      - If omitted: Returns all moves of the type

    **Returns:**
    List of moves with:
    - id: Move unique identifier
    - name: Move name
    - category: Physical/Special/Status
    - power: Base power
    - accuracy: Accuracy percentage
    - description: Move description
    - type: Move type
    - learn_method (if pokemon_id provided): Level-up/TM/Egg/Tutor
    - learn_level (if pokemon_id provided): Level learned (null for TM/Egg/Tutor)

    **Example Request:**
    ```
    GET /moves/by-type/Fire?pokemon_id=6
    ```

    **Example Response:**
    ```json
    [
      {
        "id": 52,
        "name": "Lance-Flammes",
        "category": "Special",
        "power": 90,
        "accuracy": 100,
        "description": "Une puissante attaque de feu...",
        "type": {"id": 2, "name": "Fire"},
        "learn_method": "Level-up",
        "learn_level": 34
      }
    ]
    ```

    **Use Case:**
    - Move selection filtered by type
    - STAB move recommendations (Same Type Attack Bonus)
    - Team building with type coverage
    """
    items = list_moves_by_type(
        db=db,
        type_name=type_name,
        pokemon_id=pokemon_id,
    )

    return [
        MoveSelectableOut(
            id=item["move"].id,
            name=item["move"].name,
            category=item["move"].category.name,
            power=item["move"].power,
            accuracy=item["move"].accuracy,
            description=item["move"].description,
            type=TypeOut(
                id=item["move"].type.id,
                name=item["move"].type.name,
            ),
            learn_method=item.get("learn_method"),
            learn_level=item.get("learn_level"),
        )
        for item in items
    ]


# ============================================================
# 🔹 MOVE DETAIL (ID – NON AMBIGUOUS)
# ============================================================
@router.get("/id/{move_id}", response_model=MoveDetail)
def get_move(
    move_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information for a specific move by ID.

    Returns comprehensive data about a move including all attributes
    needed for battle calculations and UI display.

    **Path Parameters:**
    - move_id: Move unique identifier (1-226)

    **Returns:**
    - id: Move unique identifier
    - name: Move name (French)
    - category: Physical/Special/Status
    - power: Base power (null for status moves)
    - accuracy: Accuracy percentage (null for never-miss moves)
    - description: Detailed move description
    - damage_type: Special damage mechanics (e.g., "multi_coups", "deux_tours")
    - type: Move type

    **Example Response:**
    ```json
    {
      "id": 87,
      "name": "Fatal-Foudre",
      "category": "Special",
      "power": 110,
      "accuracy": 70,
      "description": "Une puissante décharge électrique qui peut aussi paralyser l'ennemi.",
      "damage_type": null,
      "type": {"id": 4, "name": "Electric"}
    }
    ```

    **Errors:**
    - 404: Move not found (invalid ID)

    **Use Case:**
    Display move details in Streamlit interface (move info cards, battle simulator).
    """
    move = get_move_by_id(db, move_id)

    if not move:
        raise HTTPException(status_code=404, detail="Move not found")

    return MoveDetail(
        id=move.id,
        name=move.name,
        category=move.category.name,
        power=move.power,
        accuracy=move.accuracy,
        description=move.description,
        damage_type=move.damage_type,
        type=TypeOut(
            id=move.type.id,
            name=move.type.name,
        ),
    )
