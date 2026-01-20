#!/usr/bin/env python3
"""
Analyze existing database to design intelligent sampling strategy for ML dataset.

This script analyzes:
- Distribution of Pokemon types
- Distribution of move types
- Type effectiveness multipliers
- Potential dataset size

Output: Statistics to guide dataset generation strategy.
"""

import os
import sys
from pathlib import Path
from collections import Counter
import psycopg2
from dotenv import load_dotenv

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


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )


def analyze_pokemon():
    """Analyze Pokemon distribution."""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("=" * 80)
    print("📊 POKEMON ANALYSIS")
    print("=" * 80)

    # Total count
    cursor.execute("SELECT COUNT(*) FROM pokemon;")
    total_pokemon = cursor.fetchone()[0]
    print(f"\n✓ Total Pokemon: {total_pokemon}")

    # Type distribution
    cursor.execute("""
        SELECT t.name, COUNT(*) as count
        FROM pokemon_type pt
        JOIN type t ON pt.type_id = t.id
        GROUP BY t.name
        ORDER BY count DESC;
    """)
    type_dist = cursor.fetchall()
    print(f"\n✓ Pokemon Type Distribution (top 10):")
    for i, (type_name, count) in enumerate(type_dist[:10], 1):
        print(f"   {i}. {type_name}: {count}")

    # Dual type Pokemon
    cursor.execute("""
        SELECT COUNT(DISTINCT pokemon_id)
        FROM pokemon_type
        GROUP BY pokemon_id
        HAVING COUNT(*) = 2;
    """)
    dual_type_count = len(cursor.fetchall())
    single_type_count = total_pokemon - dual_type_count
    print(f"\n✓ Type Configuration:")
    print(f"   - Single type: {single_type_count}")
    print(f"   - Dual type: {dual_type_count}")

    # Stats distribution
    cursor.execute("""
        SELECT
            AVG(ps.attack) as avg_attack,
            AVG(ps.special_attack) as avg_sp_attack,
            AVG(ps.defense) as avg_defense,
            AVG(ps.special_defense) as avg_sp_defense
        FROM pokemon_stat ps;
    """)
    avg_stats = cursor.fetchone()
    print(f"\n✓ Average Stats:")
    print(f"   - Attack: {avg_stats[0]:.1f}")
    print(f"   - Sp. Attack: {avg_stats[1]:.1f}")
    print(f"   - Defense: {avg_stats[2]:.1f}")
    print(f"   - Sp. Defense: {avg_stats[3]:.1f}")

    cursor.close()
    conn.close()


def analyze_moves():
    """Analyze move distribution."""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("⚔️  MOVE ANALYSIS")
    print("=" * 80)

    # Total count
    cursor.execute("SELECT COUNT(*) FROM move;")
    total_moves = cursor.fetchone()[0]
    print(f"\n✓ Total Moves: {total_moves}")

    # Category distribution
    cursor.execute("""
        SELECT mc.name, COUNT(*) as count
        FROM move m
        JOIN move_category mc ON m.category_id = mc.id
        GROUP BY mc.name
        ORDER BY count DESC;
    """)
    category_dist = cursor.fetchall()
    print(f"\n✓ Move Category Distribution:")
    for category, count in category_dist:
        print(f"   - {category.capitalize()}: {count}")

    # Type distribution
    cursor.execute("""
        SELECT t.name, COUNT(*) as count
        FROM move m
        JOIN type t ON m.type_id = t.id
        GROUP BY t.name
        ORDER BY count DESC;
    """)
    type_dist = cursor.fetchall()
    print(f"\n✓ Move Type Distribution (top 10):")
    for i, (type_name, count) in enumerate(type_dist[:10], 1):
        print(f"   {i}. {type_name}: {count}")

    # Power distribution (non-null only)
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(power) as with_power,
            AVG(power) as avg_power,
            MIN(power) as min_power,
            MAX(power) as max_power
        FROM move;
    """)
    power_stats = cursor.fetchone()
    print(f"\n✓ Move Power:")
    print(f"   - Total moves: {power_stats[0]}")
    print(f"   - With power: {power_stats[1]} ({power_stats[1]/power_stats[0]*100:.1f}%)")
    print(f"   - Average: {power_stats[2]:.1f}")
    print(f"   - Range: {power_stats[3]} - {power_stats[4]}")

    cursor.close()
    conn.close()


def analyze_type_effectiveness():
    """Analyze type effectiveness multipliers."""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("🎯 TYPE EFFECTIVENESS ANALYSIS")
    print("=" * 80)

    # Multiplier distribution
    cursor.execute("""
        SELECT multiplier, COUNT(*) as count
        FROM type_effectiveness
        GROUP BY multiplier
        ORDER BY multiplier;
    """)
    mult_dist = cursor.fetchall()
    print(f"\n✓ Multiplier Distribution:")
    total_combinations = sum(count for _, count in mult_dist)
    for multiplier, count in mult_dist:
        percentage = count / total_combinations * 100
        print(f"   - {multiplier}x: {count} ({percentage:.1f}%)")

    # Calculate is_effective distribution
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN multiplier >= 2 THEN 1 ELSE 0 END) as effective,
            SUM(CASE WHEN multiplier < 2 THEN 1 ELSE 0 END) as not_effective
        FROM type_effectiveness;
    """)
    effectiveness_dist = cursor.fetchone()
    total, effective, not_effective = effectiveness_dist
    print(f"\n✓ Binary Classification (is_effective = 1 if multiplier >= 2):")
    print(f"   - Effective (1): {effective} ({effective/total*100:.1f}%)")
    print(f"   - Not Effective (0): {not_effective} ({not_effective/total*100:.1f}%)")

    cursor.close()
    conn.close()


def estimate_dataset_size():
    """Estimate potential dataset size."""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("📏 DATASET SIZE ESTIMATION")
    print("=" * 80)

    # Get counts
    cursor.execute("SELECT COUNT(*) FROM pokemon;")
    n_pokemon = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM move WHERE power IS NOT NULL;")
    n_moves = cursor.fetchone()[0]

    # Full dataset size
    full_size = n_pokemon * n_pokemon * n_moves
    print(f"\n✓ Full Dataset (all combinations):")
    print(f"   - {n_pokemon} Pokemon × {n_pokemon} Pokemon × {n_moves} Moves")
    print(f"   - = {full_size:,} rows")
    print(f"   - ⚠️  TOO LARGE!")

    # Recommended sizes
    print(f"\n✓ Recommended Sampling Strategies:")

    strategies = [
        ("Conservative (10%)", 0.10),
        ("Moderate (20%)", 0.20),
        ("Aggressive (50%)", 0.50)
    ]

    for name, ratio in strategies:
        sampled_size = int(full_size * ratio)
        print(f"   - {name}: {sampled_size:,} rows (~{sampled_size // 1000}K)")

    # Intelligent sampling suggestion
    print(f"\n✓ Intelligent Sampling Recommendation:")
    print(f"   - Keep ALL type-effective combinations (multiplier >= 2)")
    print(f"   - Sample 20% of neutral/not-effective combinations")
    print(f"   - Balance classes to 50/50 effective/not-effective")
    print(f"   - Estimated size: 500K - 1M rows")

    cursor.close()
    conn.close()


def main():
    """Run all analyses."""
    print("\n" + "=" * 80)
    print("🔍 ML DATASET - DATA ANALYSIS")
    print("=" * 80)

    try:
        analyze_pokemon()
        analyze_moves()
        analyze_type_effectiveness()
        estimate_dataset_size()

        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print("\nNext step: Create build_classification_dataset.py with intelligent sampling\n")

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
