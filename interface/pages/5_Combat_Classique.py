# interface/pages/5_Combat_Classique.py
import streamlit as st
from interface.utils.ui_helpers import (
    get_pokemon_options,
    get_moves_for_pokemon,
)
from interface.services.api_client import predict_best_move
from utils.pokemon_theme import (
    load_custom_css,
    page_header,
    type_badge,
    pokeball_divider,
    TYPE_COLORS
)

# ======================================================
# Page Config
# ======================================================
st.set_page_config(
    page_title="Combat Classique",
    page_icon="⚔️",
    layout="wide",
)

# Load theme
load_custom_css()

# ======================================================
# Page Header
# ======================================================
page_header("Combat Classique", "Configure ton combat et découvre qui gagnera avec l'IA !", "⚔️")

# ======================================================
# Load Pokemon Options
# ======================================================
pokemon_options = get_pokemon_options()
if not pokemon_options:
    st.error("Impossible de charger les Pokémon.")
    st.stop()

pokemon_lookup = {p.id: p for p in pokemon_options}

# ======================================================
# Pokemon Selection
# ======================================================
col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown("### 🥊 Pokémon 1 (Ton équipe)")
    p1_id = st.selectbox(
        "Choisis ton Pokémon",
        options=list(pokemon_lookup.keys()),
        format_func=lambda pid: f"#{pokemon_lookup[pid].pokedex_number:03d} - {pokemon_lookup[pid].name}",
        key="p1_selector"
    )

    p1 = pokemon_lookup[p1_id]

    # Display sprite and types
    if p1.sprite_url:
        st.image(p1.sprite_url, width=150)

    if p1.types:
        types_html = " ".join([
            f'<span style="background:{TYPE_COLORS.get(t.lower(), "#999")};'
            f'color:white;padding:4px 12px;border-radius:8px;font-size:0.85rem;'
            f'font-weight:600;margin:2px;">{t.capitalize()}</span>'
            for t in p1.types
        ])
        st.markdown(types_html, unsafe_allow_html=True)

with col_p2:
    st.markdown("### 🛡️ Pokémon 2 (Équipe adverse)")
    p2_id = st.selectbox(
        "Choisis le Pokémon adverse",
        options=list(pokemon_lookup.keys()),
        format_func=lambda pid: f"#{pokemon_lookup[pid].pokedex_number:03d} - {pokemon_lookup[pid].name}",
        key="p2_selector"
    )

    p2 = pokemon_lookup[p2_id]

    # Display sprite and types
    if p2.sprite_url:
        st.image(p2.sprite_url, width=150)

    if p2.types:
        types_html = " ".join([
            f'<span style="background:{TYPE_COLORS.get(t.lower(), "#999")};'
            f'color:white;padding:4px 12px;border-radius:8px;font-size:0.85rem;'
            f'font-weight:600;margin:2px;">{t.capitalize()}</span>'
            for t in p2.types
        ])
        st.markdown(types_html, unsafe_allow_html=True)

st.divider()

# ======================================================
# Moves Selection - Interface Versus
# ======================================================
st.markdown(f"""
<div style='text-align:center;padding:20px;'>
    <h2 style='color:#F5B700;font-size:2.5rem;'>⚔️ COMBAT ⚔️</h2>
    <p style='font-size:1.2rem;'>Configure le moveset de chaque Pokémon</p>
</div>
""", unsafe_allow_html=True)

# Choix du mode de sélection
mode = st.radio(
    "🎮 Mode de simulation",
    options=["🤖 Auto (Adversaire optimal)", "🎯 Manuel (Tu choisis les deux movesets)"],
    help="Mode Auto: L'adversaire utilise toujours sa meilleure capacité\nMode Manuel: Tu choisis les 4 capacités de chaque Pokémon",
    key="battle_mode"
)

manual_mode = "Manuel" in mode

# Deux colonnes pour les movesets
col_moves_a, col_moves_b = st.columns(2)

# ======================================================
# Moves Pokémon 1 (Attaquant)
# ======================================================
with col_moves_a:
    st.markdown(f"### 🥊 Moveset de {p1.name}")
    
    moves_p1 = get_moves_for_pokemon(p1.id)
    
    # Filter offensive moves only
    offensive_p1 = [m for m in moves_p1 if m.power and m.power > 0]
    
    if not offensive_p1:
        st.error(f"{p1.name} n'a aucune capacité offensive !")
        st.stop()
    
    move_names_p1 = [m.name for m in offensive_p1]
    selected_moves_p1 = st.multiselect(
        "⚔️ Capacités disponibles",
        options=move_names_p1,
        default=move_names_p1[:4] if len(move_names_p1) >= 4 else move_names_p1,
        max_selections=4,
        key="moves_p1",
        help="💡 Sélectionne jusqu'à 4 capacités offensives"
    )
    
    if len(selected_moves_p1) < 1:
        st.warning("⚠️ Sélectionne au moins 1 capacité.")

# ======================================================
# Moves Pokémon 2 (Défenseur)
# ======================================================
with col_moves_b:
    st.markdown(f"### 🛡️ Moveset de {p2.name}")
    
    if manual_mode:
        moves_p2 = get_moves_for_pokemon(p2.id)
        
        # Filter offensive moves only
        offensive_p2 = [m for m in moves_p2 if m.power and m.power > 0]
        
        if not offensive_p2:
            st.error(f"{p2.name} n'a aucune capacité offensive !")
            st.stop()
        
        move_names_p2 = [m.name for m in offensive_p2]
        selected_moves_p2 = st.multiselect(
            "⚔️ Capacités disponibles",
            options=move_names_p2,
            default=move_names_p2[:4] if len(move_names_p2) >= 4 else move_names_p2,
            max_selections=4,
            key="moves_p2",
            help="💡 Sélectionne jusqu'à 4 capacités offensives"
        )
        
        if len(selected_moves_p2) < 1:
            st.warning("⚠️ Sélectionne au moins 1 capacité.")
    else:
        selected_moves_p2 = None
        st.info("""
        🤖 **Mode automatique**
        
        L'adversaire utilisera toujours sa **meilleure capacité possible** pour chaque scénario.
        
        C'est un "worst-case" : tu affrontes un adversaire qui joue au mieux !
        """)

# Validation
if len(selected_moves_p1) < 1:
    st.stop()

st.divider()

# ======================================================
# Battle Button
# ======================================================
# Affichage récapitulatif avant prédiction
st.markdown(f"""
<div style='background:#f0f0f0;padding:20px;border-radius:10px;margin:20px 0;'>
    <div style='display:flex;justify-content:space-around;align-items:center;'>
        <div style='text-align:center;'>
            <h3 style='color:#F5B700;'>🥊 {p1.name}</h3>
            <p style='font-size:1.1rem;'>{len(selected_moves_p1)} capacité(s)</p>
        </div>
        <div style='font-size:3rem;'>⚔️</div>
        <div style='text-align:center;'>
            <h3 style='color:#3CCCC4;'>🛡️ {p2.name}</h3>
            <p style='font-size:1.1rem;'>{len(selected_moves_p2) if selected_moves_p2 else "Auto"} capacité(s)</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if not selected_moves_p1:
    st.warning(f"⚠️ Sélectionne au moins une capacité pour {p1.name}")
else:
    if st.button("🎮 Lancer le Combat !", type="primary", use_container_width=True):
        with st.spinner("🔮 Calcul de la prédiction..."):
            try:
                # Call ML API
                result = predict_best_move(
                    pokemon_a_id=p1.id,
                    pokemon_b_id=p2.id,
                    available_moves=selected_moves_p1,
                    available_moves_b=selected_moves_p2  # None si mode auto
                )
                
                # Vérification que l'API a retourné un résultat
                if result is None:
                    st.error("❌ L'API n'a pas retourné de résultat. Vérifiez les logs de l'API pour plus de détails.")
                    st.stop()
                
                if not result.get('recommended_move'):
                    st.error("❌ Résultat invalide de l'API. Aucune capacité recommandée trouvée.")
                    st.stop()

                st.divider()

                # ======================================================
                # Display Results
                # ======================================================
                st.subheader("🏆 Résultat du Combat")

                # Winner announcement
                recommended_move = result.get('recommended_move', 'Inconnu')
                win_prob = result.get('win_probability', 0)

                col_result1, col_result2 = st.columns([2, 1])

                with col_result1:
                    st.markdown(f"### 🎯 Meilleure Capacité: **{recommended_move}**")
                    st.markdown(f"### 📊 Probabilité de Victoire: **{win_prob:.1%}**")

                with col_result2:
                    # Visual indicator
                    if win_prob >= 0.7:
                        st.success("✅ Victoire Probable !")
                    elif win_prob >= 0.5:
                        st.info("⚖️ Combat Équilibré")
                    else:
                        st.warning("⚠️ Défaite Probable")

                # Progress bar
                st.progress(win_prob)

                st.divider()

                # ======================================================
                # Detailed Results for All Moves
                # ======================================================
                st.subheader("📋 Détails de Toutes les Capacités")

                all_moves_results = result.get('all_moves', [])

                if all_moves_results:
                    # Sort by win probability descending
                    all_moves_results_sorted = sorted(
                        all_moves_results,
                        key=lambda x: x.get('win_probability', 0),
                        reverse=True
                    )

                    for move_result in all_moves_results_sorted:
                        move_name = move_result.get('move_name', 'Inconnu')
                        move_prob = move_result.get('win_probability', 0)
                        move_type = move_result.get('move_type', 'Normal')
                        stab = move_result.get('has_stab', False)
                        multiplier = move_result.get('type_multiplier', 1.0)

                        # Determine color based on probability
                        if move_prob >= 0.7:
                            prob_color = "#2ca02c"  # Green
                        elif move_prob >= 0.5:
                            prob_color = "#ff7f0e"  # Orange
                        else:
                            prob_color = "#d62728"  # Red

                        # Type badge
                        type_color = TYPE_COLORS.get(move_type.lower(), "#999")
                        type_badge = (
                            f'<span style="background:{type_color};color:white;'
                            f'padding:3px 8px;border-radius:6px;font-size:0.75rem;">'
                            f'{move_type.capitalize()}</span>'
                        )

                        # STAB indicator
                        stab_indicator = "⭐" if stab else ""

                        # Multiplier indicator
                        mult_text = f"×{multiplier:.2f}"
                        if multiplier > 1:
                            mult_color = "#2ca02c"  # Green (effective)
                        elif multiplier < 1:
                            mult_color = "#d62728"  # Red (not effective)
                        else:
                            mult_color = "#888"  # Gray (neutral)

                        # Display move card
                        st.markdown(
                            f"""
                            <div style='background:#f0f0f0;padding:12px;border-radius:8px;margin-bottom:8px;'>
                                <div style='display:flex;justify-content:space-between;align-items:center;'>
                                    <div>
                                        <strong style='font-size:1.1rem;'>{move_name}</strong> {stab_indicator}
                                        <br>
                                        {type_badge}
                                        <span style='color:{mult_color};font-weight:600;margin-left:8px;'>{mult_text}</span>
                                    </div>
                                    <div style='text-align:right;'>
                                        <div style='color:{prob_color};font-weight:700;font-size:1.3rem;'>
                                            {move_prob:.1%}
                                        </div>
                                        <div style='font-size:0.75rem;color:#666;'>
                                            Victoire
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.divider()

                # ======================================================
                # Explanation
                # ======================================================
                with st.expander("💡 Pourquoi ce Résultat ?"):
                    st.markdown(f"""
                    ### 🧠 Analyse du Combat

                    **Meilleure Capacité:** {recommended_move} ({win_prob:.1%} de victoire)

                    **Facteurs pris en compte par le modèle ML:**

                    1. **📊 Stats des Pokémon:**
                       - {p1.name}: HP {p1.stats.get('hp', '?')}, Attaque {p1.stats.get('attack', '?')}, Défense {p1.stats.get('defense', '?')}, Vitesse {p1.stats.get('speed', '?')}
                       - {p2.name}: HP {p2.stats.get('hp', '?')}, Attaque {p2.stats.get('attack', '?')}, Défense {p2.stats.get('defense', '?')}, Vitesse {p2.stats.get('speed', '?')}

                    2. **💥 Puissance des Capacités:**
                       - Les capacités sélectionnées et leurs dégâts potentiels

                    3. **⚡ STAB (Same Type Attack Bonus):**
                       - Bonus de ×1.5 si le type de la capacité correspond au type du Pokémon

                    4. **🎯 Affinités de Types:**
                       - Efficacité des attaques selon le tableau des types

                    5. **⚠️ Priorité:**
                       - Certaines capacités attaquent en premier

                    **Précision du modèle:** 94.46% (modèle v2 entraîné sur 898,472 combats)

                    {f"**Mode Manuel:** Le modèle a simulé tous les combats possibles avec les movesets que tu as choisis." if manual_mode else f"**Mode Auto (worst-case):** Le modèle suppose que {p2.name} utilise toujours sa meilleure capacité. En réalité, tes chances peuvent être meilleures !"}
                    """)

            except Exception as e:
                st.error(f"❌ Erreur lors de la prédiction: {str(e)}")

# ======================================================
# Tips Section
# ======================================================
st.divider()

with st.expander("💡 Astuces - Comment utiliser cette page"):
    st.markdown("""
    ### 🎯 Utilisation

    **1. Sélection des Pokémon:**
    - Choisis ton Pokémon (Pokémon 1)
    - Choisis le Pokémon adverse (Pokémon 2)

    **2. Sélection des Capacités:**
    - Sélectionne jusqu'à 4 capacités **offensives** pour ton Pokémon attaquant
    - Les capacités de statut (puissance = 0) sont automatiquement exclues
    - Par défaut, les 4 premières capacités sont pré-sélectionnées

    **3. Lancer le Combat:**
    - Clique sur "🎮 Lancer le Combat !"
    - L'IA calcule la meilleure capacité pour ton Pokémon
    - Affiche la probabilité de victoire pour chaque capacité

    **4. Interpréter les Résultats:**
    - **≥ 70%** : ✅ Victoire très probable
    - **50-70%** : ⚖️ Combat équilibré
    - **< 50%** : ⚠️ Défaite probable

    **5. Indicateurs:**
    - **⭐ STAB** : Bonus ×1.5 si type capacité = type Pokémon
    - **Multiplicateur** : Efficacité du type (×2 super, ×0.5 peu, ×0 sans effet)
    - **Couleur probabilité** : Vert (bon), Orange (moyen), Rouge (mauvais)

    **6. Différence avec Compare:**
    - **Combat Classique** : Choisir manuellement les 2 Pokémon qui s'affrontent
    - **Compare** : Même fonctionnalité mais avec interface différente (affichage des stats, faiblesses, etc.)

    **7. Stratégie:**
    - Privilégie les capacités avec STAB (⭐)
    - Cherche les super efficacités (×2 ou ×4)
    - Évite les types peu efficaces (×0.5 ou ×0.25)
    - Considère la vitesse : attaquer en premier peut faire la différence !
    """)
