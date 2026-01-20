# machine_learning/build_dataset_ml_v2.py

from pathlib import Path
from collections import defaultdict
import pandas as pd
from sqlalchemy.orm import Session, joinedload

from core.db.session import SessionLocal
from core.models import (
    Pokemon,
    PokemonType,
    TypeEffectiveness,
    Type,
    PokemonMove,
    Move,
)

# ----------------------------------
# Config
# ----------------------------------
OUTPUT_PATH = Path("data/datasets")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_PATH / "pokemon_damage_ml.parquet"

# Using only level 50 to reduce dataset size (was [50, 60, 70, 75] = 9M rows)
ATTACKER_LEVELS = [50]
DEFENDER_LEVELS = [50]

# ----------------------------------
# Damage computation
# ----------------------------------
def compute_damage(level, power, atk, defense, stab, type_mult):
    """Formule Pokémon simplifiée et déterministe"""
    base = ((2 * level / 5 + 2) * power * (atk / defense)) / 50 + 2
    return base * stab * type_mult


# ----------------------------------
# Dataset builder
# ----------------------------------
def build_dataset(
    offensive_only: bool = True,
    allowed_damage_types: list[str] | None = None,
):
    """
    Generate ML dataset for Pokémon move effectiveness.

    Parameters
    ----------
    offensive_only : bool
        If True, only damage_type == 'offensif' is kept.
    allowed_damage_types : list[str] | None
        Explicit list of damage_type values to include.
        Overrides offensive_only if provided.
    """
    session: Session = SessionLocal()

    try:
        print("🔹 Chargement Pokémon, stats, types et moves")

        pokemons = (
            session.query(Pokemon)
            .options(
                joinedload(Pokemon.stats),
                joinedload(Pokemon.types).joinedload(PokemonType.type),
                joinedload(Pokemon.moves)
                    .joinedload(PokemonMove.move)
                    .joinedload(Move.type),
            )
            .all()
        )

        # Type effectiveness map
        type_effectiveness = defaultdict(lambda: 1.0)
        for te in session.query(TypeEffectiveness).all():
            type_effectiveness[(te.attacking_type_id, te.defending_type_id)] = float(
                te.multiplier
            )

        rows = []
        print("🔹 Génération des combinaisons attaquant / défenseur / capacité")

        for atk_lvl in ATTACKER_LEVELS:
            for def_lvl in DEFENDER_LEVELS:
                for attacker in pokemons:

                    attacker_types = [pt.type.name for pt in attacker.types]
                    if len(attacker_types) == 1:
                        attacker_types.append("none")

                    # -------------------------
                    # Filtrage des capacités
                    # -------------------------
                    moves = []
                    for pm in attacker.moves:
                        move = pm.move

                        # Exclure capacités non offensives ou incomplètes
                        if move.power is None:
                            continue

                        damage_type = move.damage_type or "offensif"

                        if allowed_damage_types:
                            if damage_type not in allowed_damage_types:
                                continue
                        elif offensive_only and damage_type != "offensif":
                            continue

                        moves.append(move)

                    for move in moves:
                        move_type = move.type.name
                        category = move.category.name  # Extract name instead of object
                        accuracy = move.accuracy or 100
                        damage_type = move.damage_type or "offensif"

                        for defender in pokemons:
                            defender_types = [pt.type.name for pt in defender.types]
                            if len(defender_types) == 1:
                                defender_types.append("none")

                            # STAB
                            stab = 1.5 if move_type in attacker_types else 1.0

                            # Type multiplier
                            type_mult = 1.0
                            for def_type in defender_types:
                                if def_type != "none":
                                    type_mult *= type_effectiveness[
                                        (move.type.id, defender.types[0].type.id)
                                    ]

                            # -------------------------
                            # Choix de la stat d'attaque
                            # -------------------------
                            if damage_type == "attk_adversaire":
                                atk_stat = defender.stats.attack
                            elif category.lower() == "physique":
                                atk_stat = attacker.stats.attack
                            else:
                                atk_stat = attacker.stats.sp_attack

                            def_stat = (
                                defender.stats.defense
                                if category.lower() == "physique"
                                else defender.stats.sp_defense
                            )

                            # -------------------------
                            # Effective power
                            # -------------------------
                            effective_power = move.power

                            if damage_type == "double_degats":
                                effective_power *= 2

                            elif damage_type == "deux_tours":
                                effective_power /= 2

                            elif damage_type == "fixe_niveau":
                                damage = atk_lvl
                                expected_damage = damage * (accuracy / 100)
                                rows.append({
                                    "attacker_id": attacker.id,
                                    "defender_id": defender.id,
                                    "attacker_level": atk_lvl,
                                    "defender_level": def_lvl,
                                    "move_name": move.name,
                                    "move_type": move_type,
                                    "move_category": category,
                                    "move_power": move.power,
                                    "move_accuracy": accuracy,
                                    "damage_type": damage_type,
                                    "stab": stab,
                                    "type_multiplier": type_mult,
                                    "expected_damage": expected_damage,
                                })
                                continue

                            # -------------------------
                            # Damage computation
                            # -------------------------
                            damage = compute_damage(
                                atk_lvl,
                                effective_power,
                                atk_stat,
                                def_stat,
                                stab,
                                type_mult,
                            )

                            if damage_type == "tque_100":
                                damage *= 1.5

                            expected_damage = damage * (accuracy / 100)

                            rows.append({
                                "attacker_id": attacker.id,
                                "defender_id": defender.id,
                                "attacker_level": atk_lvl,
                                "defender_level": def_lvl,
                                "move_name": move.name,
                                "move_type": move_type,
                                "move_category": category,
                                "move_power": move.power,
                                "move_accuracy": accuracy,
                                "damage_type": damage_type,
                                "stab": stab,
                                "type_multiplier": type_mult,
                                "expected_damage": expected_damage,
                            })

        df = pd.DataFrame(rows)
        df.to_parquet(OUTPUT_FILE, index=False)

        print(f"✅ Dataset ML généré : {OUTPUT_FILE}")
        print(f"➡ Lignes : {len(df)}")

    finally:
        session.close()


if __name__ == "__main__":
    build_dataset(offensive_only=True)
