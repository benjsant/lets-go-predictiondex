# interface/pages/2_Compare.py
import streamlit as st
from interface.utils.ui_helpers import (
    get_pokemon_options,
    get_moves_for_pokemon,
    get_pokemon_weaknesses,
)
from interface.services.api_client import predict_best_move
from utils.pokemon_theme import (
    load_custom_css,
    page_header,
    type_badge,
    POKEMON_COLORS
)

# ======================================================
# Page config
# ======================================================
st.set_page_config(
    page_title="Pokémon – Comparaison",
    page_icon="⚔️",
    layout="wide",
)

# Load theme
load_custom_css()

page_header("Comparaison de Pokémon", "Compare deux Pokémon et découvre quelle capacité utiliser !", "⚔️")

# ======================================================
# Chargement Pokémon
# ======================================================
pokemon_options = get_pokemon_options()
if not pokemon_options:
    st.error("Impossible de charger les Pokémon.")
    st.stop()

pokemon_lookup = {p.id: p for p in pokemon_options}

# ======================================================
# Sélection Pokémon
# ======================================================
col_left, col_right = st.columns(2)

with col_left:
    p1_id = st.selectbox(
        "🥊 Ton Pokémon (Attaquant)",
        options=list(pokemon_lookup.keys()),
        format_func=lambda pid: pokemon_lookup[pid].name,
        key="p1",
    )

with col_right:
    p2_id = st.selectbox(
        "🛡️ Pokémon Adverse (Défenseur)",
        options=list(pokemon_lookup.keys()),
        format_func=lambda pid: pokemon_lookup[pid].name,
        key="p2",
    )

p1 = pokemon_lookup[p1_id]
p2 = pokemon_lookup[p2_id]

# ======================================================
# Couleurs types
# ======================================================
TYPE_COLORS = {
    "plante": "#78C850",
    "poison": "#A040A0",
    "feu": "#F08030",
    "vol": "#A890F0",
    "eau": "#6890F0",
    "insecte": "#A8B820",
    "combat": "#C03028",
    "normal": "#A8A878",
    "sol": "#E0C068",
    "spectre": "#705898",
    "psy": "#F85888",
    "acier": "#B8B8D0",
    "ténèbres": "#705848",
    "glace": "#98D8D8",
    "fée": "#EE99AC",
    "électrik": "#F8D030",
    "dragon": "#7038F8",
    "roche": "#B8A038",
}

# ======================================================
# Carte Pokémon
# ======================================================
def display_pokemon_card(pokemon):
    st.markdown(f"### {pokemon.name}")

    if pokemon.sprite_url:
        st.image(pokemon.sprite_url, width=120)

    # Types
    if pokemon.types:
        types_html = " ".join([type_badge(t, "small") for t in pokemon.types])
        st.markdown(f"<div style='margin:10px 0;'>{types_html}</div>", unsafe_allow_html=True)

    # Stats
    if pokemon.stats:
        cols = st.columns(3)
        stats_keys = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
        for i, key in enumerate(stats_keys):
            cols[i % 3].metric(key.upper(), int(pokemon.stats.get(key, 0)))

# ======================================================
# Affichage Pokémon côte à côte
# ======================================================
col1, col2 = st.columns(2)
with col1:
    display_pokemon_card(p1)
with col2:
    display_pokemon_card(p2)

# ======================================================
# Heatmap comparatif faiblesses / affinités
# ======================================================
st.subheader("⚠️ Comparaison des affinités de types")

weak_p1 = {w["attacking_type"].capitalize(): float(w["multiplier"])
           for w in get_pokemon_weaknesses(p1.id)}
weak_p2 = {w["attacking_type"].capitalize(): float(w["multiplier"])
           for w in get_pokemon_weaknesses(p2.id)}

all_types = sorted(set(weak_p1.keys()) | set(weak_p2.keys()))

def format_mult(m):
    return {0.0: "0", 0.25: "¼", 0.5: "½", 1.0: "1", 2.0: "2", 4.0: "4"}.get(m, str(m))

def color_mult(m):
    if m == 0:
        return "#1f77b4"   # immunité
    if m < 1:
        return "#2ca02c"   # résistance
    if m == 1:
        return "#888888"   # neutre
    if m <= 2:
        return "#ff7f0e"   # faible
    return "#d62728"       # très faible

# Build header row
header_cells = [f"<div style='width:55px;text-align:center;font-weight:600;color:{POKEMON_COLORS['text_primary']};'>{t}</div>" for t in all_types]
header_row = f"<div style='display:flex;gap:4px;margin-bottom:6px;'><div style='width:110px;'></div>{''.join(header_cells)}</div>"

# Build data rows
data_rows = []
for name, data in [(p1.name, weak_p1), (p2.name, weak_p2)]:
    cells = []
    for t in all_types:
        m = data.get(t, 1.0)
        cell = f"<div style='width:55px;background:{color_mult(m)};color:white;text-align:center;border-radius:6px;padding:4px 0;font-size:0.85rem;'>{format_mult(m)}</div>"
        cells.append(cell)
    row = f"<div style='display:flex;gap:4px;margin-bottom:4px;'><div style='width:110px;font-weight:700;text-align:right;color:{POKEMON_COLORS['text_primary']};'>{name}</div>{''.join(cells)}</div>"
    data_rows.append(row)

# Complete HTML
heatmap_html = f"<div style='overflow-x:auto;background:{POKEMON_COLORS['bg_card']};padding:15px;border-radius:8px;'>{header_row}{''.join(data_rows)}</div>"
st.markdown(heatmap_html, unsafe_allow_html=True)

# ======================================================
# Sélection des Moves
# ======================================================
st.subheader(f"🎯 Choisis les capacités de {p1.name}")

st.info("""
💡 **Note :** Le modèle sélectionne automatiquement la **meilleure capacité** du Pokémon
adverse pour chaque scénario. C'est un "worst-case" : tu affrontes un adversaire qui joue
au mieux ! Tes vraies chances peuvent être meilleures si l'adversaire ne joue pas optimalement.

🚀 **Version 2 en développement :** Possibilité de choisir les capacités spécifiques de l'adversaire.
""")

moves = get_moves_for_pokemon(p1.id)
if not moves:
    st.warning("Aucune attaque disponible.")
    st.stop()

# Filtrer moves offensives uniquement
offensive_moves = [m for m in moves if m.power and m.power > 0]

if not offensive_moves:
    st.error("Aucune capacité offensive disponible pour ce Pokémon.")
    st.stop()

move_names = [m.name for m in offensive_moves]

# Multiselect avec suggestions
selected_move_names = st.multiselect(
    "🎯 Sélectionne jusqu'à 4 capacités offensives",
    options=move_names,
    default=move_names[:4] if len(move_names) >= 4 else move_names,
    max_selections=4,
    help="💡 Sélectionne les capacités que tu veux tester contre l'adversaire"
)

if len(selected_move_names) < 1:
    st.warning("⚠️ Sélectionne au moins 1 capacité pour continuer.")
    st.stop()

# ======================================================
# Prédiction ML
# ======================================================
st.divider()

if st.button("🔮 Prédire la Meilleure Capacité", type="primary", use_container_width=True):
    with st.spinner("🤖 Le modèle analyse le combat..."):
        try:
            result = predict_best_move(
                pokemon_a_id=p1.id,
                pokemon_b_id=p2.id,
                available_moves=selected_move_names
            )

            # Affichage du résultat principal
            st.success(f"🏆 **Capacité recommandée : {result['recommended_move']}**")

            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric(
                    "📊 Probabilité de victoire",
                    f"{result['win_probability']*100:.1f}%",
                    help="Probabilité que ton Pokémon gagne avec cette capacité"
                )
            with col_metric2:
                best_move_data = result['all_moves'][0]
                type_icon = {"feu": "🔥", "eau": "💧", "plante": "🌿", "électrik": "⚡", "glace": "🧊", "combat": "🥊"}.get(best_move_data['move_type'].lower(), "💫")
                st.metric(
                    "💥 Type de la capacité",
                    f"{type_icon} {best_move_data['move_type'].capitalize()}"
                )

            # Classement complet des capacités
            st.subheader("📊 Classement de tes capacités")

            for i, move_data in enumerate(result['all_moves'], 1):
                win_prob = move_data['win_probability'] * 100

                # Icône selon probabilité
                if win_prob >= 80:
                    icon = "🥇"
                    color = "success"
                elif win_prob >= 60:
                    icon = "🥈"
                    color = "info"
                elif win_prob >= 40:
                    icon = "🥉"
                    color = "warning"
                else:
                    icon = "❌"
                    color = "error"

                with st.expander(f"{icon} **#{i} - {move_data['move_name']}** — {win_prob:.1f}%", expanded=(i==1)):
                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("Type", move_data['move_type'].capitalize())
                    col2.metric("Puissance", move_data['move_power'])
                    col3.metric("STAB", f"{move_data['stab']}x")
                    col4.metric("Type Mult", f"{move_data['type_multiplier']}x")

                    if move_data.get('priority', 0) != 0:
                        st.caption(f"⚡ Priorité: {move_data['priority']} (attaque {'en premier' if move_data['priority'] > 0 else 'en dernier'})")

                    # Verdict
                    if move_data['predicted_winner'] == 'A':
                        st.success(f"✅ Tu devrais gagner avec cette capacité ! ({win_prob:.1f}%)")
                    else:
                        st.error(f"⚠️ Attention, tu risques de perdre... ({100-win_prob:.1f}% pour l'adversaire)")

            # Disclaimer important
            st.info("""
            💡 **Précision du modèle : 94.24%** sur 34,040 combats analysés.

            ⚠️ **Scénario "worst-case" :** Le modèle suppose que {opponent} utilise **sa meilleure
            capacité possible** contre toi. Tes vraies chances peuvent être meilleures si ton
            adversaire ne choisit pas sa meilleure move ou n'y a pas accès !

            🚀 **Version 2 à venir :** Possibilité de spécifier les capacités exactes de l'adversaire
            pour des simulations encore plus précises.
            """.format(opponent=p2.name))

            # Fun fact
            with st.expander("🤓 Comment ça marche ?"):
                st.markdown("""
                Le modèle ML (XGBoost) prend en compte :

                **Pour ton Pokémon attaquant :**
                - 📊 Statistiques de base (HP, Attaque, Défense, Att. Spé, Déf. Spé, Vitesse)
                - 💥 Puissance et type de chaque capacité testée
                - ⚡ STAB (bonus ×1.5 si le type de la capacité = type du Pokémon)
                - 🎯 Multiplicateur de type contre l'adversaire
                - ⚠️ Priorité de la capacité (attaque en premier)

                **Pour le Pokémon adverse :**
                - 📊 Statistiques de base (HP, Attaque, Défense, Att. Spé, Déf. Spé, Vitesse)
                - 🛡️ Types (pour calculer les faiblesses)
                - 💥 **Meilleure capacité offensive** sélectionnée automatiquement parmi toutes ses moves
                - ⚡ STAB et multiplicateur de type de cette capacité
                - ⚠️ Priorité de la capacité

                **Processus de prédiction :**
                1. Pour chaque capacité de ton Pokémon
                2. Le modèle sélectionne la meilleure réponse de l'adversaire
                3. Il simule le combat avec ces deux capacités
                4. Il prédit le vainqueur et la probabilité de victoire

                **Ce que le modèle ne prend PAS en compte :**
                - ❌ EV/IV (n'existent pas dans Let's Go)
                - ❌ Niveau (tous à niveau 50)
                - ❌ Objets tenus, capacités passives, météo, statuts

                **🚀 Version 2 (en développement) :**
                - Possibilité de spécifier les 4 capacités exactes de l'adversaire
                - Simulation de combat plus réaliste avec movesets fixes

                Le modèle a été entraîné sur **34,040 combats simulés** entre tous
                les Pokémon de Let's Go avec différentes configurations de capacités !
                """)

        except Exception as e:
            st.error(f"❌ Erreur lors de la prédiction : {str(e)}")
            with st.expander("🔍 Détails de l'erreur"):
                st.exception(e)
