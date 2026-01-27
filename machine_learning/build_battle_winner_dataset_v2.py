#!/usr/bin/env python3
"""
Generate ML Dataset v2 for Pokemon Battle Winner Prediction - Multi-Scenarios
=============================================================================

This script extends v1 to support multiple battle scenarios:
1. best_move: B uses its best offensive move (original behavior)
2. random_move: B uses a random offensive move (N samples per matchup)
3. all_combinations: Generate all possible moveA × moveB combinations

Key Changes from v1:
- Added --scenario-type argument to select generation mode
- Added --num-random-samples for random_move scenario
- Added 'scenario_type' column to output dataset
- Support for filtering and combining scenarios

This enables training ML models that generalize better across different
opponent behavior patterns, improving prediction accuracy when opponent
moves are partially or fully known.

Output:
- data/ml/battle_winner_v2/raw/matchups_{scenario}.parquet
- data/ml/battle_winner_v2/processed/train.parquet (with scenario_type column)
- data/ml/battle_winner_v2/processed/test.parquet (with scenario_type column)

Usage:
    # Generate only best_move scenario (similar to v1)
    python machine_learning/build_battle_winner_dataset_v2.py --scenario-type best_move

    # Generate random_move scenario with 5 random samples per matchup
    python machine_learning/build_battle_winner_dataset_v2.py --scenario-type random_move --num-random-samples 5

    # Generate all moveA × moveB combinations (large dataset)
    python machine_learning/build_battle_winner_dataset_v2.py --scenario-type all_combinations

    # Generate all scenarios and combine them
    python machine_learning/build_battle_winner_dataset_v2.py --scenario-type all

Validation:
    - Compétence C12: Dataset quality checks per scenario
    - Compétence C13: Versioned dataset generation for ML pipeline
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load environment
load_dotenv()

# Database connection
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")

# Output paths (v2 specific directories)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "ml" / "battle_winner_v2"
RAW_DIR = OUTPUT_DIR / "raw"
PROCESSED_DIR = OUTPUT_DIR / "processed"

# Battle parameters
BATTLE_LEVEL = 50  # Fixed level for all Pokemon
RANDOM_SEED = 42

# Scenario types
SCENARIO_TYPES = {
    "best_move": "B uses its best offensive move (original v1 behavior)",
    "random_move": "B uses a random offensive move (N samples per matchup)",
    "all_combinations": "Generate all possible moveA × moveB combinations",
    "all": "Generate all scenarios and combine them"
}

# Damage types to include (offensive calculable moves only)
ALLOWED_DAMAGE_TYPES = {
    "offensif",
    "multi_coups",           # Average x3 hits
    "double_degats",         # x2 power
    "deux_tours",            # /2 power (charge turn)
    "prioritaire",           # +1 priority (but exclude Bluff)
    "prioritaire_conditionnel",  # Coup Bas
    "prioritaire_critique",      # Pika-Sprint
    "prioritaire_deux",          # Ruse (+2 priority)
    "fixe_niveau",           # Damage = level
    "fixe_degat_20",         # Sonicboom = 20
    "fixe_degat_40",         # Draco-Rage = 40
    "attk_adversaire",       # Tricherie (uses opponent's ATK)
}

# Moves to explicitly exclude
EXCLUDED_MOVES = {"Bluff"}  # Only works on first turn


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )


def fetch_pokemon_data():
    """Fetch all Pokemon with their stats and types."""
    print("Fetching Pokemon data...")

    conn = get_db_connection()

    query = """
        SELECT
            p.id as pokemon_id,
            COALESCE(ps.name_en, ps.name_fr) as pokemon_name,
            pstat.hp,
            pstat.attack,
            pstat.defense,
            pstat.sp_attack,
            pstat.sp_defense,
            pstat.speed,
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

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"  Loaded {len(df)} Pokemon")
    return df


def fetch_pokemon_moves():
    """Fetch Pokemon -> Move associations with move details."""
    print("Fetching Pokemon moves...")

    conn = get_db_connection()

    query = """
        SELECT
            pm.pokemon_id,
            m.id as move_id,
            m.name as move_name,
            m.type_id as move_type_id,
            t.name as move_type_name,
            mc.name as move_category,
            m.power as move_power,
            m.accuracy as move_accuracy,
            m.damage_type,
            m.priority
        FROM pokemon_move pm
        JOIN move m ON pm.move_id = m.id
        JOIN type t ON m.type_id = t.id
        JOIN move_category mc ON m.category_id = mc.id
        WHERE m.power IS NOT NULL
        AND mc.name IN ('physique', 'spécial')
        ORDER BY pm.pokemon_id, m.id;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"  Loaded {len(df)} Pokemon-Move associations")
    return df


def fetch_type_effectiveness():
    """Fetch type effectiveness multipliers as a lookup dict."""
    print("Fetching Type Effectiveness...")

    conn = get_db_connection()

    query = """
        SELECT attacking_type_id, defending_type_id, multiplier
        FROM type_effectiveness;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Build lookup dict
    type_eff = defaultdict(lambda: 1.0)
    for _, row in df.iterrows():
        type_eff[(row['attacking_type_id'], row['defending_type_id'])] = float(row['multiplier'])

    print(f"  Loaded {len(df)} type effectiveness rules")
    return type_eff


def get_type_multiplier(move_type_id, defender_type_1_id, defender_type_2_id, type_eff):
    """Calculate total type effectiveness multiplier."""
    mult = type_eff[(move_type_id, defender_type_1_id)]
    if pd.notna(defender_type_2_id):
        mult *= type_eff[(move_type_id, int(defender_type_2_id))]
    return mult


def calculate_effective_power(move, damage_type):
    """Calculate effective power based on damage_type."""
    power = move['move_power']

    if damage_type == "multi_coups":
        return power * 3
    elif damage_type == "double_degats":
        return power * 2
    elif damage_type == "deux_tours":
        return power / 2
    else:
        return power


def calculate_damage(level, power, atk_stat, def_stat, stab, type_mult):
    """Pokemon damage formula (simplified, deterministic)."""
    if power == 0 or def_stat == 0:
        return 0
    base = ((2 * level / 5 + 2) * power * (atk_stat / def_stat)) / 50 + 2
    return base * stab * type_mult


def get_all_valid_moves(pokemon_id, pokemon_moves_df, attacker):
    """
    Get all valid offensive moves for a Pokemon.

    Returns list of move dicts with basic info.
    """
    moves = pokemon_moves_df[pokemon_moves_df['pokemon_id'] == pokemon_id].copy()

    if len(moves) == 0:
        return []

    # Filter by allowed damage types
    moves = moves[
        (moves['damage_type'].isin(ALLOWED_DAMAGE_TYPES)) &
        (~moves['move_name'].isin(EXCLUDED_MOVES))
    ]

    return moves.to_dict('records')


def get_move_score_and_info(move, attacker, defender, type_eff):
    """
    Calculate move score and return move info dict.

    Args:
        move: Move dict from pokemon_moves_df
        attacker: Attacker Pokemon dict
        defender: Defender Pokemon dict
        type_eff: Type effectiveness lookup

    Returns:
        Dict with move info including score
    """
    damage_type = move['damage_type'] or "offensif"

    # Calculate effective power
    eff_power = calculate_effective_power(move, damage_type)

    # Get attacker types for STAB calculation
    attacker_types = [attacker['type_1_id']]
    if pd.notna(attacker['type_2_id']):
        attacker_types.append(int(attacker['type_2_id']))

    # STAB bonus
    stab = 1.5 if move['move_type_id'] in attacker_types else 1.0

    # Type effectiveness
    type_mult = get_type_multiplier(
        move['move_type_id'],
        defender['type_1_id'],
        defender['type_2_id'],
        type_eff
    )

    # Accuracy factor
    accuracy = move['move_accuracy'] if pd.notna(move['move_accuracy']) else 100

    # Score = expected damage (power * stab * type_eff * accuracy)
    score = eff_power * stab * type_mult * (accuracy / 100)

    # Add priority bonus (moves first = advantage)
    priority = move['priority'] if pd.notna(move['priority']) else 0
    score += priority * 50  # Priority bonus

    return {
        'move_id': move['move_id'],
        'move_name': move['move_name'],
        'move_type_id': move['move_type_id'],
        'move_type_name': move['move_type_name'],
        'move_category': move['move_category'],
        'move_power': move['move_power'],
        'effective_power': eff_power,
        'move_accuracy': accuracy,
        'damage_type': damage_type,
        'priority': priority,
        'stab': stab,
        'type_multiplier': type_mult,
        'score': score,
    }


def get_best_move(pokemon_id, pokemon_moves_df, attacker, defender, type_eff):
    """
    Select the best move for a Pokemon against a specific defender.

    Returns dict with move info or None if no valid moves.
    """
    valid_moves = get_all_valid_moves(pokemon_id, pokemon_moves_df, attacker)

    if not valid_moves:
        return None

    best_move = None
    best_score = -1

    for move in valid_moves:
        move_info = get_move_score_and_info(move, attacker, defender, type_eff)

        if move_info['score'] > best_score:
            best_score = move_info['score']
            best_move = move_info

    return best_move


def determine_who_moves_first(a_priority, a_speed, b_priority, b_speed):
    """
    Determine which Pokemon moves first.

    Returns: 1 if A moves first, 0 if B moves first
    """
    if a_priority > b_priority:
        return 1
    if b_priority > a_priority:
        return 0
    if a_speed > b_speed:
        return 1
    if b_speed > a_speed:
        return 0
    return 1  # Speed tie = A wins for determinism


def simulate_battle(attacker_a, attacker_b, move_a, move_b, type_eff):
    """
    Simulate a battle and determine the winner.

    Returns: 1 if A wins, 0 if B wins
    """
    # Calculate damage for each side
    # A attacking B
    if move_a['move_category'] == 'physique':
        atk_stat_a = attacker_a['attack']
        def_stat_b = attacker_b['defense']
    else:
        atk_stat_a = attacker_a['sp_attack']
        def_stat_b = attacker_b['sp_defense']

    damage_a = calculate_damage(
        BATTLE_LEVEL,
        move_a['effective_power'],
        atk_stat_a,
        def_stat_b,
        move_a['stab'],
        move_a['type_multiplier']
    )

    # B attacking A
    if move_b['move_category'] == 'physique':
        atk_stat_b = attacker_b['attack']
        def_stat_a = attacker_a['defense']
    else:
        atk_stat_b = attacker_b['sp_attack']
        def_stat_a = attacker_a['sp_defense']

    damage_b = calculate_damage(
        BATTLE_LEVEL,
        move_b['effective_power'],
        atk_stat_b,
        def_stat_a,
        move_b['stab'],
        move_b['type_multiplier']
    )

    # Calculate turns to KO
    hp_a = attacker_a['hp']
    hp_b = attacker_b['hp']

    turns_to_ko_b = hp_b / max(damage_a, 0.1)
    turns_to_ko_a = hp_a / max(damage_b, 0.1)

    # Who moves first?
    a_moves_first = determine_who_moves_first(
        move_a['priority'], attacker_a['speed'],
        move_b['priority'], attacker_b['speed']
    )

    # Determine winner
    if a_moves_first:
        if turns_to_ko_b <= turns_to_ko_a:
            return 1  # A wins
        else:
            return 0  # B wins
    else:
        if turns_to_ko_a <= turns_to_ko_b:
            return 0  # B wins
        else:
            return 1  # A wins


def build_sample_dict(pokemon_a, pokemon_b, move_a, move_b, winner, scenario_type):
    """Build a sample dictionary for the dataset."""
    a_moves_first = determine_who_moves_first(
        move_a['priority'], pokemon_a['speed'],
        move_b['priority'], pokemon_b['speed']
    )

    return {
        # Metadata
        'scenario_type': scenario_type,

        # IDs (for reference, not features)
        'pokemon_a_id': pokemon_a['pokemon_id'],
        'pokemon_b_id': pokemon_b['pokemon_id'],
        'pokemon_a_name': pokemon_a['pokemon_name'],
        'pokemon_b_name': pokemon_b['pokemon_name'],

        # Pokemon A stats
        'a_hp': pokemon_a['hp'],
        'a_attack': pokemon_a['attack'],
        'a_defense': pokemon_a['defense'],
        'a_sp_attack': pokemon_a['sp_attack'],
        'a_sp_defense': pokemon_a['sp_defense'],
        'a_speed': pokemon_a['speed'],
        'a_type_1': pokemon_a['type_1_name'],
        'a_type_2': pokemon_a['type_2_name'] if pd.notna(pokemon_a['type_2_name']) else 'none',

        # Pokemon B stats
        'b_hp': pokemon_b['hp'],
        'b_attack': pokemon_b['attack'],
        'b_defense': pokemon_b['defense'],
        'b_sp_attack': pokemon_b['sp_attack'],
        'b_sp_defense': pokemon_b['sp_defense'],
        'b_speed': pokemon_b['speed'],
        'b_type_1': pokemon_b['type_1_name'],
        'b_type_2': pokemon_b['type_2_name'] if pd.notna(pokemon_b['type_2_name']) else 'none',

        # Best move A info
        'a_move_name': move_a['move_name'],
        'a_move_power': move_a['effective_power'],
        'a_move_type': move_a['move_type_name'],
        'a_move_priority': move_a['priority'],
        'a_move_stab': move_a['stab'],
        'a_move_type_mult': move_a['type_multiplier'],

        # Best move B info
        'b_move_name': move_b['move_name'],
        'b_move_power': move_b['effective_power'],
        'b_move_type': move_b['move_type_name'],
        'b_move_priority': move_b['priority'],
        'b_move_stab': move_b['stab'],
        'b_move_type_mult': move_b['type_multiplier'],

        # Computed features
        'speed_diff': pokemon_a['speed'] - pokemon_b['speed'],
        'hp_diff': pokemon_a['hp'] - pokemon_b['hp'],
        'a_total_stats': (pokemon_a['hp'] + pokemon_a['attack'] + pokemon_a['defense'] +
                          pokemon_a['sp_attack'] + pokemon_a['sp_defense'] + pokemon_a['speed']),
        'b_total_stats': (pokemon_b['hp'] + pokemon_b['attack'] + pokemon_b['defense'] +
                          pokemon_b['sp_attack'] + pokemon_b['sp_defense'] + pokemon_b['speed']),
        'a_moves_first': a_moves_first,

        # Target
        'winner': winner,
    }


def generate_best_move_scenario(pokemon_df, pokemon_moves_df, type_eff):
    """
    Generate dataset with best_move scenario (original v1 behavior).

    For each matchup, both A and B use their best offensive move.
    """
    print("\n🎯 Generating BEST_MOVE scenario...")
    samples = []
    skipped = 0

    for idx_a, pokemon_a in pokemon_df.iterrows():
        for idx_b, pokemon_b in pokemon_df.iterrows():
            if pokemon_a['pokemon_id'] == pokemon_b['pokemon_id']:
                skipped += 1
                continue

            # Get best moves
            move_a = get_best_move(
                pokemon_a['pokemon_id'], pokemon_moves_df,
                pokemon_a, pokemon_b, type_eff
            )
            move_b = get_best_move(
                pokemon_b['pokemon_id'], pokemon_moves_df,
                pokemon_b, pokemon_a, type_eff
            )

            if move_a is None or move_b is None:
                skipped += 1
                continue

            # Simulate battle
            winner = simulate_battle(pokemon_a, pokemon_b, move_a, move_b, type_eff)

            # Build sample
            sample = build_sample_dict(pokemon_a, pokemon_b, move_a, move_b, winner, "best_move")
            samples.append(sample)

        if (idx_a + 1) % 20 == 0:
            print(f"  Progress: {idx_a + 1}/{len(pokemon_df)} Pokemon processed")

    df = pd.DataFrame(samples)
    print(f"\n  Generated {len(df):,} samples (skipped {skipped:,})")
    return df


def generate_random_move_scenario(pokemon_df, pokemon_moves_df, type_eff, num_samples=5):
    """
    Generate dataset with random_move scenario.

    For each matchup:
    - A uses its best move
    - B uses a random offensive move (repeated num_samples times)
    """
    print(f"\n🎲 Generating RANDOM_MOVE scenario ({num_samples} samples per matchup)...")
    samples = []
    skipped = 0
    np.random.seed(RANDOM_SEED)

    for idx_a, pokemon_a in pokemon_df.iterrows():
        for idx_b, pokemon_b in pokemon_df.iterrows():
            if pokemon_a['pokemon_id'] == pokemon_b['pokemon_id']:
                skipped += num_samples
                continue

            # Get best move for A
            move_a = get_best_move(
                pokemon_a['pokemon_id'], pokemon_moves_df,
                pokemon_a, pokemon_b, type_eff
            )

            if move_a is None:
                skipped += num_samples
                continue

            # Get all valid moves for B
            valid_moves_b = get_all_valid_moves(
                pokemon_b['pokemon_id'], pokemon_moves_df, pokemon_b
            )

            if not valid_moves_b:
                skipped += num_samples
                continue

            # Generate N random samples
            for _ in range(num_samples):
                # Pick random move for B
                random_move = np.random.choice(valid_moves_b)
                move_b = get_move_score_and_info(random_move, pokemon_b, pokemon_a, type_eff)

                # Simulate battle
                winner = simulate_battle(pokemon_a, pokemon_b, move_a, move_b, type_eff)

                # Build sample
                sample = build_sample_dict(pokemon_a, pokemon_b, move_a, move_b, winner, "random_move")
                samples.append(sample)

        if (idx_a + 1) % 20 == 0:
            print(f"  Progress: {idx_a + 1}/{len(pokemon_df)} Pokemon processed")

    df = pd.DataFrame(samples)
    print(f"\n  Generated {len(df):,} samples (skipped {skipped:,})")
    return df


def generate_all_combinations_scenario(pokemon_df, pokemon_moves_df, type_eff, max_combinations_per_matchup=20):
    """
    Generate dataset with all_combinations scenario.

    For each matchup, generate all possible moveA × moveB combinations.
    Limited to max_combinations_per_matchup to prevent explosion.
    """
    print(f"\n🔄 Generating ALL_COMBINATIONS scenario (max {max_combinations_per_matchup} per matchup)...")
    samples = []
    skipped = 0

    for idx_a, pokemon_a in pokemon_df.iterrows():
        for idx_b, pokemon_b in pokemon_df.iterrows():
            if pokemon_a['pokemon_id'] == pokemon_b['pokemon_id']:
                skipped += 1
                continue

            # Get all valid moves for both
            valid_moves_a = get_all_valid_moves(
                pokemon_a['pokemon_id'], pokemon_moves_df, pokemon_a
            )
            valid_moves_b = get_all_valid_moves(
                pokemon_b['pokemon_id'], pokemon_moves_df, pokemon_b
            )

            if not valid_moves_a or not valid_moves_b:
                skipped += 1
                continue

            # Generate all combinations (with limit)
            combinations = []
            for move_a_raw in valid_moves_a:
                for move_b_raw in valid_moves_b:
                    combinations.append((move_a_raw, move_b_raw))

            # Limit combinations if too many
            if len(combinations) > max_combinations_per_matchup:
                combinations = np.random.choice(
                    len(combinations),
                    size=max_combinations_per_matchup,
                    replace=False
                )
                combinations = [
                    (valid_moves_a[i // len(valid_moves_b)], valid_moves_b[i % len(valid_moves_b)])
                    for i in combinations
                ]

            # Generate samples for each combination
            for move_a_raw, move_b_raw in combinations:
                move_a = get_move_score_and_info(move_a_raw, pokemon_a, pokemon_b, type_eff)
                move_b = get_move_score_and_info(move_b_raw, pokemon_b, pokemon_a, type_eff)

                # Simulate battle
                winner = simulate_battle(pokemon_a, pokemon_b, move_a, move_b, type_eff)

                # Build sample
                sample = build_sample_dict(pokemon_a, pokemon_b, move_a, move_b, winner, "all_combinations")
                samples.append(sample)

        if (idx_a + 1) % 20 == 0:
            print(f"  Progress: {idx_a + 1}/{len(pokemon_df)} Pokemon processed")

    df = pd.DataFrame(samples)
    print(f"\n  Generated {len(df):,} samples (skipped {skipped:,})")
    return df


def split_and_save(df, scenario_type, test_size=0.2):
    """Split into train/test and save to Parquet."""
    print(f"\n💾 Saving datasets for scenario: {scenario_type}...")

    # Create directories
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save raw
    raw_path = RAW_DIR / f"matchups_{scenario_type}.parquet"
    df.to_parquet(raw_path, index=False, engine='pyarrow')
    print(f"  Raw dataset: {raw_path}")
    print(f"  Size: {raw_path.stat().st_size / (1024*1024):.2f} MB")

    # Split train/test (stratified on winner)
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=RANDOM_SEED,
        stratify=df['winner']
    )

    return train_df, test_df


def combine_and_save_all_scenarios(train_dfs, test_dfs):
    """Combine all scenarios into single train/test files."""
    print("\n📦 Combining all scenarios into single train/test files...")

    # Combine
    train_combined = pd.concat(train_dfs, ignore_index=True)
    test_combined = pd.concat(test_dfs, ignore_index=True)

    # Shuffle
    train_combined = train_combined.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    test_combined = test_combined.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # Save
    train_path = PROCESSED_DIR / "train.parquet"
    test_path = PROCESSED_DIR / "test.parquet"

    train_combined.to_parquet(train_path, index=False, engine='pyarrow')
    test_combined.to_parquet(test_path, index=False, engine='pyarrow')

    print(f"  Train: {len(train_combined):,} samples ({train_path})")
    print(f"  Test: {len(test_combined):,} samples ({test_path})")

    return train_combined, test_combined


def print_summary(train_df, test_df, scenario_type):
    """Print dataset summary."""
    print("\n" + "=" * 70)
    print(f"DATASET SUMMARY - {scenario_type.upper()}")
    print("=" * 70)

    if 'scenario_type' in train_df.columns:
        print("\n📊 Samples by Scenario:")
        for scenario in train_df['scenario_type'].unique():
            train_count = (train_df['scenario_type'] == scenario).sum()
            test_count = (test_df['scenario_type'] == scenario).sum()
            print(f"  {scenario:20s}: Train {train_count:,} | Test {test_count:,}")

    print(f"\n📈 Total Samples:")
    print(f"  Train: {len(train_df):,}")
    print(f"  Test:  {len(test_df):,}")

    print(f"\n⚖️  Class Balance (Train):")
    print(f"  A wins: {train_df['winner'].sum():,} ({train_df['winner'].mean()*100:.1f}%)")
    print(f"  B wins: {(train_df['winner'] == 0).sum():,} ({(1-train_df['winner'].mean())*100:.1f}%)")

    print(f"\n⚖️  Class Balance (Test):")
    print(f"  A wins: {test_df['winner'].sum():,} ({test_df['winner'].mean()*100:.1f}%)")
    print(f"  B wins: {(test_df['winner'] == 0).sum():,} ({(1-test_df['winner'].mean())*100:.1f}%)")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Generate Pokemon Battle Winner Dataset v2 with Multi-Scenarios"
    )
    parser.add_argument(
        "--scenario-type",
        choices=list(SCENARIO_TYPES.keys()),
        default="best_move",
        help="Type of scenario to generate"
    )
    parser.add_argument(
        "--num-random-samples",
        type=int,
        default=5,
        help="Number of random samples per matchup for random_move scenario"
    )
    parser.add_argument(
        "--max-combinations",
        type=int,
        default=20,
        help="Max combinations per matchup for all_combinations scenario"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("BATTLE WINNER PREDICTION DATASET GENERATION v2")
    print("=" * 70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Battle Level: {BATTLE_LEVEL}")
    print(f"Scenario Type: {args.scenario_type}")
    print(f"Description: {SCENARIO_TYPES[args.scenario_type]}")

    try:
        # Fetch data
        pokemon_df = fetch_pokemon_data()
        pokemon_moves_df = fetch_pokemon_moves()
        type_eff = fetch_type_effectiveness()

        train_dfs = []
        test_dfs = []

        # Generate based on scenario type
        if args.scenario_type == "best_move":
            df = generate_best_move_scenario(pokemon_df, pokemon_moves_df, type_eff)
            train_df, test_df = split_and_save(df, "best_move")
            train_dfs.append(train_df)
            test_dfs.append(test_df)

        elif args.scenario_type == "random_move":
            df = generate_random_move_scenario(
                pokemon_df, pokemon_moves_df, type_eff,
                num_samples=args.num_random_samples
            )
            train_df, test_df = split_and_save(df, "random_move")
            train_dfs.append(train_df)
            test_dfs.append(test_df)

        elif args.scenario_type == "all_combinations":
            df = generate_all_combinations_scenario(
                pokemon_df, pokemon_moves_df, type_eff,
                max_combinations_per_matchup=args.max_combinations
            )
            train_df, test_df = split_and_save(df, "all_combinations")
            train_dfs.append(train_df)
            test_dfs.append(test_df)

        elif args.scenario_type == "all":
            # Generate all scenarios
            df_best = generate_best_move_scenario(pokemon_df, pokemon_moves_df, type_eff)
            train_best, test_best = split_and_save(df_best, "best_move")
            train_dfs.append(train_best)
            test_dfs.append(test_best)

            df_random = generate_random_move_scenario(
                pokemon_df, pokemon_moves_df, type_eff,
                num_samples=args.num_random_samples
            )
            train_random, test_random = split_and_save(df_random, "random_move")
            train_dfs.append(train_random)
            test_dfs.append(test_random)

            df_all_comb = generate_all_combinations_scenario(
                pokemon_df, pokemon_moves_df, type_eff,
                max_combinations_per_matchup=args.max_combinations
            )
            train_all_comb, test_all_comb = split_and_save(df_all_comb, "all_combinations")
            train_dfs.append(train_all_comb)
            test_dfs.append(test_all_comb)

        # Combine if multiple scenarios
        if len(train_dfs) > 1:
            train_combined, test_combined = combine_and_save_all_scenarios(train_dfs, test_dfs)
            print_summary(train_combined, test_combined, args.scenario_type)
        else:
            print_summary(train_dfs[0], test_dfs[0], args.scenario_type)

        print("\n" + "=" * 70)
        print("✅ DATASET GENERATION COMPLETE")
        print("=" * 70)

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
