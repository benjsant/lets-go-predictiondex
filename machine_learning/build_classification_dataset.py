#!/usr/bin/env python3
"""
Generate ML Classification Dataset for Pokemon Move Effectiveness Prediction.

This script:
1. Queries PostgreSQL for Pokemon, Moves, and Type Effectiveness data
2. Generates combinations of (attacker, defender, move)
3. Computes features and target label
4. Applies intelligent sampling to reduce dataset size
5. Splits into train/test sets
6. Exports to Parquet format

Target: is_effective = 1 if type_multiplier >= 2 else 0

Output:
- data/ml/raw/battle_samples.parquet
- data/ml/processed/train.parquet
- data/ml/processed/test.parquet
"""

import os
import sys
from pathlib import Path
from datetime import datetime
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
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "ml"
RAW_DIR = OUTPUT_DIR / "raw"
PROCESSED_DIR = OUTPUT_DIR / "processed"

# Sampling parameters
SAMPLE_RATIO_NOT_EFFECTIVE = 0.15  # Keep 15% of not-effective combinations
RANDOM_SEED = 42


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
    print("📥 Fetching Pokemon data...")

    conn = get_db_connection()

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

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"✓ Loaded {len(df)} Pokemon")
    return df


def fetch_moves_data():
    """Fetch all damaging moves with their properties."""
    print("📥 Fetching Moves data...")

    conn = get_db_connection()

    # Based on build_dataset_ml_v1.py filtering logic:
    # - Only moves with power defined (damaging moves)
    # - Only physique/spécial categories (no status moves)
    # - No damage_type filtering here (build_dataset_ml_v1.py uses offensive_only=True)
    query = """
        SELECT
            m.id as move_id,
            m.name as move_name,
            m.type_id as move_type_id,
            t.name as move_type_name,
            mc.name as move_category,
            m.power as move_power,
            m.accuracy as move_accuracy,
            m.damage_type as damage_type
        FROM move m
        JOIN type t ON m.type_id = t.id
        JOIN move_category mc ON m.category_id = mc.id
        WHERE m.power IS NOT NULL  -- Only damaging moves
        AND mc.name IN ('physique', 'spécial')  -- Exclude status moves
        ORDER BY m.id;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"✓ Loaded {len(df)} damaging moves")
    return df


def fetch_type_effectiveness():
    """Fetch type effectiveness multipliers."""
    print("📥 Fetching Type Effectiveness data...")

    conn = get_db_connection()

    query = """
        SELECT
            attacking_type_id,
            defending_type_id,
            multiplier
        FROM type_effectiveness
        ORDER BY attacking_type_id, defending_type_id;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"✓ Loaded {len(df)} type effectiveness rules")
    return df


def calculate_type_multiplier(attacker_types, defender_types, move_type_id, type_eff_df):
    """
    Calculate the total type effectiveness multiplier.

    Args:
        attacker_types: tuple (type1_id, type2_id or None)
        defender_types: tuple (type1_id, type2_id or None)
        move_type_id: int
        type_eff_df: DataFrame with type effectiveness

    Returns:
        float: Total multiplier
    """
    defender_type_1, defender_type_2 = defender_types

    # Get multiplier vs defender type 1
    mult_1 = type_eff_df[
        (type_eff_df['attacking_type_id'] == move_type_id) &
        (type_eff_df['defending_type_id'] == defender_type_1)
    ]['multiplier'].values[0]

    # If defender has a second type, multiply
    if pd.notna(defender_type_2):
        mult_2 = type_eff_df[
            (type_eff_df['attacking_type_id'] == move_type_id) &
            (type_eff_df['defending_type_id'] == defender_type_2)
        ]['multiplier'].values[0]
        return mult_1 * mult_2

    return mult_1


def calculate_stab(attacker_types, move_type_id):
    """
    Check if move benefits from STAB (Same Type Attack Bonus).

    Returns:
        int: 1 if STAB, 0 otherwise
    """
    type_1, type_2 = attacker_types
    if move_type_id == type_1:
        return 1
    if pd.notna(type_2) and move_type_id == type_2:
        return 1
    return 0


def generate_dataset(pokemon_df, moves_df, type_eff_df, sample_ratio=SAMPLE_RATIO_NOT_EFFECTIVE):
    """
    Generate the ML dataset with intelligent sampling.

    Strategy:
    - Keep ALL effective combinations (type_multiplier >= 2)
    - Sample a subset of not-effective combinations
    - Balance classes
    """
    print("\n🔄 Generating dataset...")
    print(f"   Sampling ratio for not-effective: {sample_ratio * 100}%")

    np.random.seed(RANDOM_SEED)

    samples = []

    total_combinations = len(pokemon_df) * len(pokemon_df) * len(moves_df)
    print(f"   Theoretical combinations: {total_combinations:,}")

    processed = 0
    kept_effective = 0
    kept_not_effective = 0

    # Iterate over all combinations
    for _, attacker in pokemon_df.iterrows():
        for _, defender in pokemon_df.iterrows():
            for _, move in moves_df.iterrows():
                processed += 1

                if processed % 100000 == 0:
                    print(f"   Processed: {processed:,}/{total_combinations:,} ({processed/total_combinations*100:.1f}%)")

                # Calculate type multiplier
                attacker_types = (attacker['type_1_id'], attacker['type_2_id'])
                defender_types = (defender['type_1_id'], defender['type_2_id'])

                type_multiplier = calculate_type_multiplier(
                    attacker_types,
                    defender_types,
                    move['move_type_id'],
                    type_eff_df
                )

                # Calculate target
                is_effective = 1 if type_multiplier >= 2 else 0

                # Sampling strategy
                if is_effective == 1:
                    # Keep ALL effective combinations
                    keep = True
                    kept_effective += 1
                else:
                    # Sample not-effective combinations
                    keep = np.random.rand() < sample_ratio
                    if keep:
                        kept_not_effective += 1

                if not keep:
                    continue

                # Calculate STAB
                is_stab = calculate_stab(attacker_types, move['move_type_id'])

                # Calculate stat ratios (useful features)
                if move['move_category'] == 'physique':
                    stat_ratio = attacker['attack'] / max(defender['defense'], 1)
                else:  # spécial
                    stat_ratio = attacker['sp_attack'] / max(defender['sp_defense'], 1)

                # Build sample
                sample = {
                    # IDs (for reference)
                    'attacker_id': attacker['pokemon_id'],
                    'defender_id': defender['pokemon_id'],
                    'move_id': move['move_id'],

                    # Attacker features
                    'attacker_type_1': attacker['type_1_name'],
                    'attacker_type_2': attacker['type_2_name'] if pd.notna(attacker['type_2_name']) else 'none',
                    'attacker_attack': attacker['attack'],
                    'attacker_sp_attack': attacker['sp_attack'],

                    # Defender features
                    'defender_type_1': defender['type_1_name'],
                    'defender_type_2': defender['type_2_name'] if pd.notna(defender['type_2_name']) else 'none',
                    'defender_defense': defender['defense'],
                    'defender_sp_defense': defender['sp_defense'],

                    # Move features
                    'move_type': move['move_type_name'],
                    'move_category': move['move_category'],
                    'move_power': move['move_power'],
                    'move_accuracy': move['move_accuracy'] if pd.notna(move['move_accuracy']) else 100,

                    # Computed features
                    'type_multiplier': type_multiplier,
                    'is_stab': is_stab,
                    'stat_ratio': stat_ratio,
                    'has_dual_type_attacker': 1 if pd.notna(attacker['type_2_id']) else 0,
                    'has_dual_type_defender': 1 if pd.notna(defender['type_2_id']) else 0,

                    # Target
                    'is_effective': is_effective
                }

                samples.append(sample)

    df = pd.DataFrame(samples)

    print(f"\n✓ Dataset generated:")
    print(f"   - Total samples: {len(df):,}")
    print(f"   - Effective (1): {kept_effective:,} ({kept_effective/len(df)*100:.1f}%)")
    print(f"   - Not Effective (0): {kept_not_effective:,} ({kept_not_effective/len(df)*100:.1f}%)")
    print(f"   - Compression ratio: {len(df)/total_combinations*100:.2f}%")

    return df


def split_and_save(df, test_size=0.2):
    """Split into train/test and save to Parquet."""
    print("\n💾 Saving datasets...")

    # Create directories
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save raw
    raw_path = RAW_DIR / "battle_samples.parquet"
    df.to_parquet(raw_path, index=False, engine='pyarrow')
    print(f"✓ Saved raw dataset: {raw_path}")
    print(f"   Size: {raw_path.stat().st_size / (1024*1024):.2f} MB")

    # Split train/test
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=RANDOM_SEED,
        stratify=df['is_effective']  # Stratified split
    )

    # Save train
    train_path = PROCESSED_DIR / "train.parquet"
    train_df.to_parquet(train_path, index=False, engine='pyarrow')
    print(f"✓ Saved train dataset: {train_path}")
    print(f"   Samples: {len(train_df):,}")
    print(f"   Size: {train_path.stat().st_size / (1024*1024):.2f} MB")

    # Save test
    test_path = PROCESSED_DIR / "test.parquet"
    test_df.to_parquet(test_path, index=False, engine='pyarrow')
    print(f"✓ Saved test dataset: {test_path}")
    print(f"   Samples: {len(test_df):,}")
    print(f"   Size: {test_path.stat().st_size / (1024*1024):.2f} MB")

    return train_df, test_df


def print_dataset_summary(train_df, test_df):
    """Print dataset summary statistics."""
    print("\n" + "=" * 80)
    print("📊 DATASET SUMMARY")
    print("=" * 80)

    print("\n✓ Train Set:")
    print(f"   - Samples: {len(train_df):,}")
    print(f"   - Effective: {train_df['is_effective'].sum():,} ({train_df['is_effective'].mean()*100:.1f}%)")
    print(f"   - Not Effective: {(train_df['is_effective'] == 0).sum():,} ({(1-train_df['is_effective'].mean())*100:.1f}%)")

    print("\n✓ Test Set:")
    print(f"   - Samples: {len(test_df):,}")
    print(f"   - Effective: {test_df['is_effective'].sum():,} ({test_df['is_effective'].mean()*100:.1f}%)")
    print(f"   - Not Effective: {(test_df['is_effective'] == 0).sum():,} ({(1-test_df['is_effective'].mean())*100:.1f}%)")

    print("\n✓ Features:")
    features = [col for col in train_df.columns if col not in ['attacker_id', 'defender_id', 'move_id', 'is_effective']]
    print(f"   - Total: {len(features)}")
    print(f"   - Categorical: {len([f for f in features if train_df[f].dtype == 'object'])}")
    print(f"   - Numerical: {len([f for f in features if train_df[f].dtype in ['int64', 'float64']])}")

    print("\n✓ Type Multiplier Distribution:")
    for mult in sorted(train_df['type_multiplier'].unique()):
        count = (train_df['type_multiplier'] == mult).sum()
        print(f"   - {mult}x: {count:,} ({count/len(train_df)*100:.1f}%)")


def main():
    """Main execution."""
    print("=" * 80)
    print("🤖 ML CLASSIFICATION DATASET GENERATION")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: {OUTPUT_DIR}")

    try:
        # Fetch data
        pokemon_df = fetch_pokemon_data()
        moves_df = fetch_moves_data()
        type_eff_df = fetch_type_effectiveness()

        # Generate dataset
        dataset_df = generate_dataset(pokemon_df, moves_df, type_eff_df)

        # Split and save
        train_df, test_df = split_and_save(dataset_df)

        # Summary
        print_dataset_summary(train_df, test_df)

        print("\n" + "=" * 80)
        print("✅ DATASET GENERATION COMPLETE")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Explore data with notebooks/01_exploration.ipynb")
        print("2. Feature engineering with notebooks/02_feature_engineering.ipynb")
        print("3. Train model with notebooks/03_training_evaluation.ipynb\n")

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
