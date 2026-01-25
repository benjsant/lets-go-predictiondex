#!/usr/bin/env python3
"""
Script de test pour vérifier l'héritage des capacités before_evolution
pour les formes Alola.

Vérifie:
1. Nombre de Pokémon traités (Base + Alola + Starter)
2. Exemple concret: Rattatac Alola doit hériter de Rattata
"""

import sys
sys.path.insert(0, '/app')

from sqlalchemy import select, func
from core.db.session import SessionLocal
from core.models import Pokemon, PokemonMove, LearnMethod, Form

def test_before_evolution_inheritance():
    """Test l'héritage des capacités before_evolution."""
    session = SessionLocal()
    
    print("="*70)
    print("TEST - Héritage Capacités before_evolution")
    print("="*70)
    
    # 1. Nombre de Pokémon par forme
    print("\n📊 RÉPARTITION PAR FORME:")
    forms_count = (
        session.query(Form.name, func.count(Pokemon.id))
        .join(Pokemon, Pokemon.form_id == Form.id)
        .group_by(Form.name)
        .all()
    )
    for form_name, count in forms_count:
        print(f"   {form_name:10s}: {count:3d} Pokémon")
    
    # 2. Méthode d'apprentissage before_evolution
    before_evo = session.query(LearnMethod).filter_by(name="before_evolution").first()
    if not before_evo:
        print("\n❌ ERREUR: LearnMethod 'before_evolution' introuvable")
        return
    
    print(f"\n✅ LearnMethod 'before_evolution' ID: {before_evo.id}")
    
    # 3. Capacités héritées par forme
    print("\n📋 CAPACITÉS HÉRITÉES (learn_method = before_evolution):")
    inherited_by_form = (
        session.query(
            Form.name,
            func.count(PokemonMove.id).label('moves_count')
        )
        .join(Pokemon, PokemonMove.pokemon_id == Pokemon.id)
        .join(Form, Pokemon.form_id == Form.id)
        .filter(PokemonMove.learn_method_id == before_evo.id)
        .filter(PokemonMove.learn_level == -2)
        .group_by(Form.name)
        .all()
    )
    
    total_inherited = 0
    for form_name, moves_count in inherited_by_form:
        print(f"   {form_name:10s}: {moves_count:4d} capacités héritées")
        total_inherited += moves_count
    
    print(f"\n   {'TOTAL':10s}: {total_inherited:4d} capacités héritées")
    
    # 4. Exemple concret: Formes Alola
    print("\n🧪 TEST CAS CONCRET - Formes Alola:")
    
    alola_examples = [
        ("rattata-alola", "Rattata Alola"),
        ("raticate-alola", "Rattatac Alola"),
        ("raichu-alola", "Raichu Alola"),
        ("sandshrew-alola", "Sabelette Alola"),
        ("sandslash-alola", "Sablaireau Alola"),
    ]
    
    for name_pokeapi, name_fr in alola_examples:
        pokemon = session.query(Pokemon).filter_by(name_pokeapi=name_pokeapi).first()
        if not pokemon:
            print(f"   ⚠️  {name_fr:20s}: NON TROUVÉ en DB")
            continue
        
        inherited_moves = (
            session.query(PokemonMove)
            .filter_by(
                pokemon_id=pokemon.id,
                learn_method_id=before_evo.id,
                learn_level=-2
            )
            .count()
        )
        
        if inherited_moves > 0:
            print(f"   ✅ {name_fr:20s}: {inherited_moves:2d} capacités héritées")
        else:
            print(f"   ❌ {name_fr:20s}: 0 capacité héritée (PROBLÈME)")
    
    # 5. Comparaison Base vs Alola (Rattata)
    print("\n🔍 COMPARAISON DÉTAILLÉE - Rattata Base vs Alola:")
    
    rattata_base = session.query(Pokemon).filter_by(name_pokeapi="rattata").first()
    rattata_alola = session.query(Pokemon).filter_by(name_pokeapi="rattata-alola").first()
    
    if rattata_base and rattata_alola:
        # Moves totales
        base_total = len(rattata_base.moves)
        alola_total = len(rattata_alola.moves)
        
        # Moves héritées
        base_inherited = sum(
            1 for pm in rattata_base.moves 
            if pm.learn_method_id == before_evo.id and pm.learn_level == -2
        )
        alola_inherited = sum(
            1 for pm in rattata_alola.moves 
            if pm.learn_method_id == before_evo.id and pm.learn_level == -2
        )
        
        print(f"   Rattata Base:   {base_total:2d} moves totales, {base_inherited:2d} héritées")
        print(f"   Rattata Alola:  {alola_total:2d} moves totales, {alola_inherited:2d} héritées")
        
        if base_inherited == 0 and alola_inherited == 0:
            print("   ℹ️  Normal: Rattata est un starter, pas d'évolution précédente")
        elif alola_inherited == 0 and base_inherited > 0:
            print("   ❌ PROBLÈME: Alola devrait aussi avoir des moves héritées")
    
    print("\n" + "="*70)
    print("FIN DU TEST")
    print("="*70)
    
    session.close()

if __name__ == "__main__":
    test_before_evolution_inheritance()
