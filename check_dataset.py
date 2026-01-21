#!/usr/bin/env python3
"""Quick script to check dataset structure."""

import pandas as pd
from pathlib import Path

# Load dataset
df = pd.read_parquet('data/ml/raw/battle_samples.parquet')

print("=" * 80)
print("COLONNES DU DATASET")
print("=" * 80)
for i, col in enumerate(df.columns, 1):
    dtype = str(df[col].dtype)
    null_count = df[col].isna().sum()
    unique = df[col].nunique()
    print(f"{i:2d}. {col:30s} | {dtype:15s} | Null: {null_count:6d} | Unique: {unique:6d}")

print(f"\n{'=' * 80}")
print(f"SHAPE: {df.shape}")
print(f"{'=' * 80}")

print("\nPREMIÈRES LIGNES:")
print(df.head(3).to_string())
