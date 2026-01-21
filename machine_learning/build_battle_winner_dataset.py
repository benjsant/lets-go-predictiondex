#!/usr/bin/env python3
"""
Generate ML Dataset for Pokemon Battle Winner Prediction.

This script:
1. Queries PostgreSQL for Pokemon, Moves, Stats, and Type Effectiveness data
2. Generates all matchups (Pokemon A vs Pokemon B)
3. For each matchup, selects the "best move" for each Pokemon
4. Simulates battle outcome based on damage potential
5. Exports dataset for ML training

Target: winner = 1 if Pokemon A wins, 0 if Pokemon B wins

Output:
- data/ml/battle_winner/raw/matchups.parquet
- data/ml/battle_winner/processed/train.parquet
- data/ml/battle_winner/processed/test.parquet
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import psycopg2
import pandas as pd
import numpy as np
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

# Output paths
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "ml" / "battle_winner"
RAW_DIR = OUTPUT_DIR / "raw"
PROCESSED_DIR = OUTPUT_DIR / "processed"

# Battle parameters
BATTLE_LEVEL = 50  # Fixed level for all Pokemon
RANDOM_SEED = 42

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
        # Average 3.17 hits, round to 3
        return power * 3
    elif damage_type == "double_degats":
        return power * 2
    elif damage_type == "deux_tours":
        # Charge turn = half damage per turn
        return power / 2
    else:
        return power


def calculate_damage(level, power, atk_stat, def_stat, stab, type_mult):
    """Pokemon damage formula (simplified, deterministic)."""
    if power == 0 or def_stat == 0:
        return 0
    base = ((2 * level / 5 + 2) * power * (atk_stat / def_stat)) / 50 + 2
    return base * stab * type_mult


def get_best_move(pokemon_id, pokemon_moves_df, attacker, defender, type_eff):
    """
    Select the best move for a Pokemon against a specific defender.

    Returns dict with move info or None if no valid moves.
    """
    # Get moves for this Pokemon
    moves = pokemon_moves_df[pokemon_moves_df['pokemon_id'] == pokemon_id].copy()

    if len(moves) == 0:
        return None

    # Filter by allowed damage types
    moves = moves[
        (moves['damage_type'].isin(ALLOWED_DAMAGE_TYPES)) &
        (~moves['move_name'].isin(EXCLUDED_MOVES))
    ]

    if len(moves) == 0:
        return None

    # Get attacker types for STAB calculation
    attacker_types = [attacker['type_1_id']]
    if pd.notna(attacker['type_2_id']):
        attacker_types.append(int(attacker['type_2_id']))

    best_move = None
    best_score = -1

    for _, move in moves.iterrows():
        damage_type = move['damage_type'] or "offensif"

        # Calculate effective power
        eff_power = calculate_effective_power(move, damage_type)

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

        if score > best_score:
            best_score = score
            best_move = {
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

    return best_move


def determine_who_moves_first(a_priority, a_speed, b_priority, b_speed):
    """
    Determine which Pokemon moves first.

    Returns: 1 if A moves first, 0 if B moves first
    """
    # Higher priority always goes first
    if a_priority > b_priority:
        return 1
    if b_priority > a_priority:
        return 0
    # Same priority = faster Pokemon goes first
    if a_speed > b_speed:
        return 1
    if b_speed > a_speed:
        return 0
    # Speed tie = random (we'll say A wins ties for determinism)
    return 1


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

    turns_to_ko_b = hp_b / max(damage_a, 0.1)  # A needs this many turns to KO B
    turns_to_ko_a = hp_a / max(damage_b, 0.1)  # B needs this many turns to KO A

    # Who moves first?
    a_moves_first = determine_who_moves_first(
        move_a['priority'], attacker_a['speed'],
        move_b['priority'], attacker_b['speed']
    )

    # If A moves first and can KO B before B KOs A, A wins
    # If B moves first and can KO A before A KOs B, B wins
    if a_moves_first:
        # A gets the first hit advantage
        if turns_to_ko_b <= turns_to_ko_a:
            return 1  # A wins
        else:
            return 0  # B wins
    else:
        # B gets the first hit advantage
        if turns_to_ko_a <= turns_to_ko_b:
            return 0  # B wins
        else:
            return 1  # A wins


def generate_dataset(pokemon_df, pokemon_moves_df, type_eff):
    """Generate the battle winner dataset."""
    print("\nGenerating battle matchups...")

    samples = []
    skipped = 0
    total = len(pokemon_df) * len(pokemon_df)

    for idx_a, pokemon_a in pokemon_df.iterrows():
        for idx_b, pokemon_b in pokemon_df.iterrows():
            # Skip same Pokemon matchups
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

            # Skip if either Pokemon has no valid moves
            if move_a is None or move_b is None:
                skipped += 1
                continue

            # Determine who moves first
            a_moves_first = determine_who_moves_first(
                move_a['priority'], pokemon_a['speed'],
                move_b['priority'], pokemon_b['speed']
            )

            # Simulate battle
            winner = simulate_battle(pokemon_a, pokemon_b, move_a, move_b, type_eff)

            # Build sample
            sample = {
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

            samples.append(sample)

        # Progress
        if (idx_a + 1) % 20 == 0:
            print(f"  Progress: {idx_a + 1}/{len(pokemon_df)} Pokemon processed")

    df = pd.DataFrame(samples)

    print(f"\nDataset generated:")
    print(f"  Total matchups: {len(df):,}")
    print(f"  Skipped: {skipped:,}")
    print(f"  A wins: {df['winner'].sum():,} ({df['winner'].mean()*100:.1f}%)")
    print(f"  B wins: {(df['winner'] == 0).sum():,} ({(1-df['winner'].mean())*100:.1f}%)")

    return df


def split_and_save(df, test_size=0.2):
    """Split into train/test and save to Parquet."""
    print("\nSaving datasets...")

    # Create directories
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save raw
    raw_path = RAW_DIR / "matchups.parquet"
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

    # Save train
    train_path = PROCESSED_DIR / "train.parquet"
    train_df.to_parquet(train_path, index=False, engine='pyarrow')
    print(f"  Train: {len(train_df):,} samples ({train_path})")

    # Save test
    test_path = PROCESSED_DIR / "test.parquet"
    test_df.to_parquet(test_path, index=False, engine='pyarrow')
    print(f"  Test: {len(test_df):,} samples ({test_path})")

    return train_df, test_df


def print_summary(train_df, test_df):
    """Print dataset summary."""
    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    print(f"\nTrain Set: {len(train_df):,} samples")
    print(f"  A wins: {train_df['winner'].sum():,} ({train_df['winner'].mean()*100:.1f}%)")
    print(f"  B wins: {(train_df['winner'] == 0).sum():,}")

    print(f"\nTest Set: {len(test_df):,} samples")
    print(f"  A wins: {test_df['winner'].sum():,} ({test_df['winner'].mean()*100:.1f}%)")
    print(f"  B wins: {(test_df['winner'] == 0).sum():,}")

    print("\nFeature columns:")
    feature_cols = [c for c in train_df.columns if c not in ['pokemon_a_id', 'pokemon_b_id',
                                                              'pokemon_a_name', 'pokemon_b_name',
                                                              'a_move_name', 'b_move_name', 'winner']]
    print(f"  Total: {len(feature_cols)}")
    for col in feature_cols[:10]:
        print(f"    - {col}")
    if len(feature_cols) > 10:
        print(f"    ... and {len(feature_cols) - 10} more")


def main():
    """Main execution."""
    print("=" * 60)
    print("BATTLE WINNER PREDICTION DATASET GENERATION")
    print("=" * 60)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Battle Level: {BATTLE_LEVEL}")

    try:
        # Fetch data
        pokemon_df = fetch_pokemon_data()
        pokemon_moves_df = fetch_pokemon_moves()
        type_eff = fetch_type_effectiveness()

        # Generate dataset
        dataset_df = generate_dataset(pokemon_df, pokemon_moves_df, type_eff)

        # Split and save
        train_df, test_df = split_and_save(dataset_df)

        # Summary
        print_summary(train_df, test_df)

        print("\n" + "=" * 60)
        print("DATASET GENERATION COMPLETE")
        print("=" * 60)

    except psycopg2.Error as e:
        print(f"\nDatabase error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
