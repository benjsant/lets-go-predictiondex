#!/usr/bin/env python3
"""
Generate ML Dataset for Pokemon Battle Winner Prediction using SQLAlchemy ORM.

This script:
1. Queries the database using SQLAlchemy models for Pokemon, Moves, Stats, and Type Effectiveness
2. Generates all matchups (Pokemon A vs Pokemon B)
3. For each matchup, selects the "best move" for each Pokemon
4. Simulates battle outcome based on damage potential
5. Exports dataset for ML training

Target: winner = 1 if Pokemon A wins, 0 if Pokemon B wins
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine

# --- Import ORM models ---
from core.db.base import Base
from core.models.pokemon import Pokemon
from core.models.pokemon_stat import PokemonStat
from core.models.pokemon_type import PokemonType
from core.models.move import Move
from core.models.pokemon_move import PokemonMove
from core.models.type import Type
from core.models.type_effectiveness import TypeEffectiveness
from core.models.move_category import MoveCategory

# --- Load environment ---
load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "postgresql://letsgo_user:letsgo_password@localhost:5432/letsgo_db")

# --- Output directories ---
OUTPUT_DIR = Path("data/ml/battle_winner")
RAW_DIR = OUTPUT_DIR / "raw"
PROCESSED_DIR = OUTPUT_DIR / "processed"

# --- Battle parameters ---
BATTLE_LEVEL = 50
RANDOM_SEED = 42

# Allowed damage types
ALLOWED_DAMAGE_TYPES = {
    "offensif", "multi_coups", "double_degats", "deux_tours",
    "prioritaire", "prioritaire_conditionnel", "prioritaire_critique",
    "prioritaire_deux", "fixe_niveau", "fixe_degat_20", "fixe_degat_40",
    "attk_adversaire"
}

EXCLUDED_MOVES = {"Bluff"}  # Only works on first turn


# --- Setup SQLAlchemy session ---
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()


def fetch_pokemon_data():
    """Fetch all Pokemon with stats and types using ORM."""
    print("Fetching Pokemon data...")
    pokemons = (
        session.query(Pokemon)
        .options(
            joinedload(Pokemon.stats),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
            joinedload(Pokemon.species)
        )
        .all()
    )

    data = []
    for p in pokemons:
        t1 = p.types[0].type.name if len(p.types) >= 1 else None
        t2 = p.types[1].type.name if len(p.types) >= 2 else None

        data.append({
            "pokemon_id": p.id,
            "pokemon_name": p.species.name_en or p.species.name_fr,
            "hp": p.stats.hp,
            "attack": p.stats.attack,
            "defense": p.stats.defense,
            "sp_attack": p.stats.sp_attack,
            "sp_defense": p.stats.sp_defense,
            "speed": p.stats.speed,
            "type_1_name": t1,
            "type_2_name": t2
        })
    df = pd.DataFrame(data)
    print(f"  Loaded {len(df)} Pokemon")
    return df


def fetch_pokemon_moves():
    """Fetch Pokemon moves with move details using ORM."""
    print("Fetching Pokemon moves...")
    moves = (
        session.query(PokemonMove)
        .join(PokemonMove.move)
        .join(Move.type)
        .join(Move.category)
        .options(
            joinedload(PokemonMove.move).joinedload(Move.type),
            joinedload(PokemonMove.move).joinedload(Move.category)
        )
        .all()
    )

    data = []
    for pm in moves:
        m = pm.move
        if m.power is None or m.category.name.lower() not in ['physique', 'spécial']:
            continue
        if m.name in EXCLUDED_MOVES:
            continue

        data.append({
            "pokemon_id": pm.pokemon_id,
            "move_id": m.id,
            "move_name": m.name,
            "move_type_id": m.type.id,
            "move_type_name": m.type.name,
            "move_category": m.category.name.lower(),
            "move_power": m.power,
            "move_accuracy": m.accuracy,
            "damage_type": m.damage_type or "offensif",
            "priority": m.priority or 0
        })

    df = pd.DataFrame(data)
    print(f"  Loaded {len(df)} Pokemon-Move associations")
    return df


def fetch_type_effectiveness():
    """Fetch type effectiveness as dict using ORM."""
    print("Fetching type effectiveness...")
    multipliers = defaultdict(lambda: 1.0)
    te_list = session.query(TypeEffectiveness).all()
    for te in te_list:
        multipliers[(te.attacking_type_id, te.defending_type_id)] = float(te.multiplier)
    print(f"  Loaded {len(te_list)} type effectiveness rules")
    return multipliers


# --- Battle simulation functions ---
def get_type_multiplier(move_type_name, defender_type_1_name, defender_type_2_name, type_eff_dict, type_name_to_id):
    move_type_id = type_name_to_id[move_type_name]
    mult = type_eff_dict[(move_type_id, type_name_to_id.get(defender_type_1_name, move_type_id))]
    if defender_type_2_name and defender_type_2_name != 'none':
        mult *= type_eff_dict[(move_type_id, type_name_to_id.get(defender_type_2_name, move_type_id))]
    return mult


def calculate_damage(level, power, atk_stat, def_stat, stab, type_mult):
    if power == 0 or def_stat == 0:
        return 0
    base = ((2 * level / 5 + 2) * power * (atk_stat / def_stat)) / 50 + 2
    return base * stab * type_mult


def determine_who_moves_first(a_priority, a_speed, b_priority, b_speed):
    if a_priority > b_priority:
        return 1
    if b_priority > a_priority:
        return 0
    return 1 if a_speed >= b_speed else 0


def simulate_battle(attacker_a, attacker_b, move_a, move_b, type_eff_dict, type_name_to_id):
    # Calculate STAB
    attacker_types_a = [attacker_a['type_1_name'], attacker_a['type_2_name']]
    stab_a = 1.5 if move_a['move_type_name'] in attacker_types_a else 1.0
    attacker_types_b = [attacker_b['type_1_name'], attacker_b['type_2_name']]
    stab_b = 1.5 if move_b['move_type_name'] in attacker_types_b else 1.0

    # Type multiplier
    type_mult_a = get_type_multiplier(move_a['move_type_name'], attacker_b['type_1_name'], attacker_b['type_2_name'], type_eff_dict, type_name_to_id)
    type_mult_b = get_type_multiplier(move_b['move_type_name'], attacker_a['type_1_name'], attacker_a['type_2_name'], type_eff_dict, type_name_to_id)

    # Attack / Defense
    if move_a['move_category'] == 'physique':
        atk_stat_a, def_stat_b = attacker_a['attack'], attacker_b['defense']
    else:
        atk_stat_a, def_stat_b = attacker_a['sp_attack'], attacker_b['sp_defense']

    if move_b['move_category'] == 'physique':
        atk_stat_b, def_stat_a = attacker_b['attack'], attacker_a['defense']
    else:
        atk_stat_b, def_stat_a = attacker_b['sp_attack'], attacker_a['sp_defense']

    damage_a = calculate_damage(BATTLE_LEVEL, move_a['move_power'], atk_stat_a, def_stat_b, stab_a, type_mult_a)
    damage_b = calculate_damage(BATTLE_LEVEL, move_b['move_power'], atk_stat_b, def_stat_a, stab_b, type_mult_b)

    turns_to_ko_b = attacker_b['hp'] / max(damage_a, 0.1)
    turns_to_ko_a = attacker_a['hp'] / max(damage_b, 0.1)

    first = determine_who_moves_first(move_a['priority'], attacker_a['speed'], move_b['priority'], attacker_b['speed'])
    if first:
        return 1 if turns_to_ko_b <= turns_to_ko_a else 0
    else:
        return 0 if turns_to_ko_a <= turns_to_ko_b else 1


# --- Dataset generation ---
def generate_dataset(pokemon_df, pokemon_moves_df, type_eff_dict):
    print("\nGenerating battle matchups...")
    type_name_to_id = {t.name: t.id for t in session.query(Type).all()}

    samples = []
    total = len(pokemon_df)
    skipped = 0

    for idx_a, a in pokemon_df.iterrows():
        for idx_b, b in pokemon_df.iterrows():
            if a['pokemon_id'] == b['pokemon_id']:
                skipped += 1
                continue

            # Best moves
            moves_a = pokemon_moves_df[pokemon_moves_df['pokemon_id'] == a['pokemon_id']]
            moves_b = pokemon_moves_df[pokemon_moves_df['pokemon_id'] == b['pokemon_id']]
            if moves_a.empty or moves_b.empty:
                skipped += 1
                continue

            # Choose move with max (power * 1.0) as placeholder (can add STAB/type later)
            move_a = moves_a.iloc[0].to_dict()
            move_b = moves_b.iloc[0].to_dict()

            winner = simulate_battle(a, b, move_a, move_b, type_eff_dict, type_name_to_id)

            sample = {
                "pokemon_a_id": a['pokemon_id'], "pokemon_b_id": b['pokemon_id'],
                "a_hp": a['hp'], "a_attack": a['attack'], "a_defense": a['defense'],
                "a_sp_attack": a['sp_attack'], "a_sp_defense": a['sp_defense'], "a_speed": a['speed'],
                "a_type_1": a['type_1_name'], "a_type_2": a['type_2_name'] or "none",
                "b_hp": b['hp'], "b_attack": b['attack'], "b_defense": b['defense'],
                "b_sp_attack": b['sp_attack'], "b_sp_defense": b['sp_defense'], "b_speed": b['speed'],
                "b_type_1": b['type_1_name'], "b_type_2": b['type_2_name'] or "none",
                "winner": winner
            }
            samples.append(sample)
        if (idx_a+1) % 20 == 0:
            print(f"  Progress: {idx_a+1}/{total} Pokemon processed")

    df = pd.DataFrame(samples)
    print(f"Dataset generated: {len(df)} samples (skipped {skipped})")
    return df


def split_and_save(df, test_size=0.2):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw_path = RAW_DIR / "matchups.parquet"
    df.to_parquet(raw_path, index=False, engine='pyarrow')

    train_df, test_df = train_test_split(df, test_size=test_size, random_state=RANDOM_SEED, stratify=df['winner'])
    train_df.to_parquet(PROCESSED_DIR / "train.parquet", index=False, engine='pyarrow')
    test_df.to_parquet(PROCESSED_DIR / "test.parquet", index=False, engine='pyarrow')

    return train_df, test_df


def main():
    print("="*60)
    print("BATTLE WINNER PREDICTION DATASET GENERATION (ORM)")
    print("="*60)
    print(f"Timestamp: {datetime.now()}")

    pokemon_df = fetch_pokemon_data()
    pokemon_moves_df = fetch_pokemon_moves()
    type_eff_dict = fetch_type_effectiveness()

    dataset_df = generate_dataset(pokemon_df, pokemon_moves_df, type_eff_dict)
    train_df, test_df = split_and_save(dataset_df)

    print(f"Train samples: {len(train_df)}, Test samples: {len(test_df)}")


if __name__ == "__main__":
    main()
