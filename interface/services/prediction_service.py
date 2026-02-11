# interface/services/prediction_service.py
import random
from typing import List

from interface.formatters.ui.move_ui import MoveSelectItem
from interface.formatters.ui.pokemon_ui import PokemonSelectItem


def predict_battle_mock(
    pokemon_1: PokemonSelectItem,
    moves_1: List[MoveSelectItem],
    pokemon_2: PokemonSelectItem,
    moves_2: List[MoveSelectItem],
) -> dict:
    """Mock battle prediction based on stats and move power."""
    base_score_1 = pokemon_1.total_stats or 300
    base_score_2 = pokemon_2.total_stats or 300

    move_power_1 = sum(m.power or 0 for m in moves_1)
    move_power_2 = sum(m.power or 0 for m in moves_2)

    score_1 = base_score_1 + move_power_1 + random.randint(-20, 20)
    score_2 = base_score_2 + move_power_2 + random.randint(-20, 20)

    total = score_1 + score_2
    winner_name = pokemon_1.name if score_1 >= score_2 else pokemon_2.name

    return {
        "winner": winner_name,
        "message": f"Predicted winner: **{winner_name}**",
        "probabilities": {
            pokemon_1.name: round(score_1 / total, 2),
            pokemon_2.name: round(score_2 / total, 2),
        },
        "debug": {
            "pokemon_1_score": score_1,
            "pokemon_2_score": score_2,
        },
    }



predict_battle_stub = predict_battle_mock
