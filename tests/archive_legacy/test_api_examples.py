#!/usr/bin/env python3
"""
Generate API Examples for Documentation
========================================

Creates markdown examples of API responses by directly calling services.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from core.db.session import SessionLocal
from api_pokemon.services import prediction_service, pokemon_service, move_service

def example_1_squirtle_vs_charmander():
    """Example: Squirtle vs Charmander - Super effective water moves."""
    print("=" * 80)
    print("EXAMPLE 1: Squirtle vs Charmander (Water super effective against Fire)")
    print("=" * 80)

    db = SessionLocal()
    try:
        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=7,  # Squirtle
            pokemon_b_id=4,  # Charmander
            available_moves_a=["Charge", "Pistolet à O", "Hydrocanon", "Surf"]
        )

        print(f"\n🔵 {result['pokemon_a_name']} (ID: {result['pokemon_a_id']})")
        print(f"   Types: Eau")
        print(f"\n🔴 {result['pokemon_b_name']} (ID: {result['pokemon_b_id']})")
        print(f"   Types: Feu")

        print(f"\n⭐ RECOMMENDED MOVE: {result['recommended_move']}")
        print(f"   Win Probability: {result['win_probability']*100:.1f}%")

        print(f"\n📊 All Moves Ranked:\n")
        for i, move in enumerate(result['all_moves'], 1):
            winner_badge = "✅ WIN " if move['predicted_winner'] == 'A' else "❌ LOSE"
            print(f"   {i}. {winner_badge} | {move['move_name']:<20} "
                  f"| Win: {move['win_probability']*100:>5.1f}% "
                  f"| Power: {move['move_power']:>3} "
                  f"| Type Mult: {move['type_multiplier']:.1f}x "
                  f"| STAB: {move['stab']:.1f}x")

        print("\n" + "-" * 80)
        print("ANALYSIS:")
        print(f"• Hydrocanon has the highest win probability ({result['all_moves'][0]['win_probability']*100:.1f}%)")
        print(f"• Water type is SUPER EFFECTIVE against Fire (2x multiplier)")
        print(f"• STAB bonus applies (1.5x) because Squirtle is Water type")
        print(f"• Effective power: {result['all_moves'][0]['effective_power']}")
        print("-" * 80)

        return result

    finally:
        db.close()


def example_2_bulbasaur_vs_charmander():
    """Example: Bulbasaur vs Charmander - Type disadvantage (Grass weak to Fire)."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Bulbasaur vs Charmander (Grass WEAK against Fire)")
    print("=" * 80)

    db = SessionLocal()
    try:
        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=1,  # Bulbasaur
            pokemon_b_id=4,  # Charmander
            available_moves_a=["Charge", "Fouet Lianes", "Tranch'Herbe", "Lance-Soleil"]
        )

        print(f"\n🟢 {result['pokemon_a_name']} (ID: {result['pokemon_a_id']})")
        print(f"   Types: Plante/Poison")
        print(f"\n🔴 {result['pokemon_b_name']} (ID: {result['pokemon_b_id']})")
        print(f"   Types: Feu")

        print(f"\n⚠️  BEST AVAILABLE MOVE: {result['recommended_move']}")
        print(f"   Win Probability: {result['win_probability']*100:.1f}% (LOW - type disadvantage)")

        print(f"\n📊 All Moves Ranked:\n")
        for i, move in enumerate(result['all_moves'], 1):
            winner_badge = "✅ WIN " if move['predicted_winner'] == 'A' else "❌ LOSE"
            print(f"   {i}. {winner_badge} | {move['move_name']:<20} "
                  f"| Win: {move['win_probability']*100:>5.1f}% "
                  f"| Power: {move['move_power']:>3} "
                  f"| Type Mult: {move['type_multiplier']:.1f}x")

        print("\n" + "-" * 80)
        print("ANALYSIS:")
        print(f"• All moves have LOW win probability (all < 50%)")
        print(f"• Grass moves have 0.5x effectiveness against Fire (resisted)")
        print(f"• Even with STAB bonus, Grass moves are not effective")
        print(f"• Charge (Normal type) has 1.0x effectiveness but low power")
        print("-" * 80)

        return result

    finally:
        db.close()


def example_3_pikachu_vs_gyarados():
    """Example: Pikachu vs Gyarados - Electric super effective against Water/Flying."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Pikachu vs Gyarados (Electric super effective)")
    print("=" * 80)

    db = SessionLocal()
    try:
        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=25,  # Pikachu
            pokemon_b_id=130,  # Gyarados
            available_moves_a=["Charge", "Éclair", "Tonnerre", "Fatal-Foudre"]
        )

        print(f"\n⚡ {result['pokemon_a_name']} (ID: {result['pokemon_a_id']})")
        print(f"   Types: Électrik")
        print(f"\n🐉 {result['pokemon_b_name']} (ID: {result['pokemon_b_id']})")
        print(f"   Types: Eau/Vol")

        print(f"\n⭐ RECOMMENDED MOVE: {result['recommended_move']}")
        print(f"   Win Probability: {result['win_probability']*100:.1f}%")

        print(f"\n📊 All Moves Ranked:\n")
        for i, move in enumerate(result['all_moves'], 1):
            winner_badge = "✅ WIN " if move['predicted_winner'] == 'A' else "❌ LOSE"
            print(f"   {i}. {winner_badge} | {move['move_name']:<20} "
                  f"| Win: {move['win_probability']*100:>5.1f}% "
                  f"| Power: {move['move_power']:>3} "
                  f"| Type Mult: {move['type_multiplier']:.1f}x "
                  f"| STAB: {move['stab']:.1f}x")

        print("\n" + "-" * 80)
        print("ANALYSIS:")
        print(f"• Electric is SUPER EFFECTIVE against Water (2x)")
        print(f"• STAB bonus applies (1.5x) because Pikachu is Electric type")
        print(f"• High-power moves like Tonnerre strongly recommended")
        print(f"• Note: Gyarados' Flying type doesn't reduce Electric effectiveness")
        print("-" * 80)

        return result

    finally:
        db.close()


def example_4_pokemon_details():
    """Example: Get Pokémon details with relationships."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 4: Pokémon Details API (with stats, types, and moves)")
    print("=" * 80)

    db = SessionLocal()
    try:
        # Get Charizard details
        pokemon = pokemon_service.get_pokemon_with_details(db, pokemon_id=6)

        print(f"\n🔥 {pokemon.species.name_fr} (#{pokemon.species.pokedex_number:03d})")
        print(f"   Form: {pokemon.form.name}")
        print(f"   Height: {pokemon.height_m}m | Weight: {pokemon.weight_kg}kg")

        print(f"\n   Types:")
        for pt in pokemon.pokemon_types:
            print(f"      • {pt.type.name.upper()} (slot {pt.slot})")

        print(f"\n   Base Stats:")
        print(f"      HP:         {pokemon.stats.hp}")
        print(f"      Attack:     {pokemon.stats.attack}")
        print(f"      Defense:    {pokemon.stats.defense}")
        print(f"      Sp. Attack: {pokemon.stats.sp_attack}")
        print(f"      Sp. Defense:{pokemon.stats.sp_defense}")
        print(f"      Speed:      {pokemon.stats.speed}")
        total = (pokemon.stats.hp + pokemon.stats.attack + pokemon.stats.defense +
                pokemon.stats.sp_attack + pokemon.stats.sp_defense + pokemon.stats.speed)
        print(f"      TOTAL:      {total}")

        print(f"\n   Learned Moves (showing first 10):")
        moves_sorted = sorted(pokemon.pokemon_moves, key=lambda pm: (pm.learn_level or 0))
        for pm in moves_sorted[:10]:
            level = f"Lvl {pm.learn_level:>2}" if pm.learn_level else "     "
            method = pm.learn_method.name.upper()
            print(f"      {level} | {method:<10} | {pm.move.name:<25} "
                  f"| {pm.move.type.name:<10} | Power: {pm.move.power or 0:>3}")

        print(f"\n   Total Moves Learnable: {len(pokemon.pokemon_moves)}")

        return pokemon

    finally:
        db.close()


def example_5_model_info():
    """Example: Get ML model information."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 5: ML Model Information")
    print("=" * 80)

    model = prediction_service.prediction_model
    model.load()

    metadata = model.metadata

    print(f"\n🤖 Model Type: {metadata['model_type']}")
    print(f"   Version: {metadata['version']}")
    print(f"   Number of Features: {metadata['n_features']}")
    print(f"   Trained: {metadata['trained_at']}")

    print(f"\n📊 Performance Metrics (Test Set):")
    metrics = metadata['metrics']
    print(f"   Accuracy:  {metrics['test_accuracy']:.4f} ({metrics['test_accuracy']*100:.2f}%)")
    print(f"   Precision: {metrics['test_precision']:.4f}")
    print(f"   Recall:    {metrics['test_recall']:.4f}")
    print(f"   F1-Score:  {metrics['test_f1']:.4f}")
    print(f"   ROC-AUC:   {metrics['test_roc_auc']:.4f}")

    print(f"\n⚙️  Hyperparameters:")
    for key, value in metadata['hyperparameters'].items():
        print(f"   {key:<20}: {value}")

    print(f"\n📁 Model Files:")
    print(f"   Model:    models/battle_winner_model_v1.pkl (983 KB)")
    print(f"   Scalers:  models/battle_winner_scalers_v1.pkl (1.7 KB)")
    print(f"   Metadata: models/battle_winner_metadata.pkl (2.8 KB)")

    return metadata


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LET'S GO PREDICTIONDEX API EXAMPLES" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Run examples
        example_1_squirtle_vs_charmander()
        example_2_bulbasaur_vs_charmander()
        example_3_pikachu_vs_gyarados()
        example_4_pokemon_details()
        example_5_model_info()

        print("\n\n" + "=" * 80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\n💡 Use these examples in your API documentation!")
        print("   Each example shows realistic usage scenarios for:")
        print("   • Battle predictions with type advantages/disadvantages")
        print("   • Pokémon data retrieval with relationships")
        print("   • Model information and metrics")

    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
