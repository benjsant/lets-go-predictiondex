# interface/pages/7_Pokemon_Detail.py
import streamlit as st
import pandas as pd
from typing import List, Optional

from interface.utils.ui_helpers import (
    get_pokemon_by_id,
    get_pokemon_options,
    get_pokemon_weaknesses_ui,
)
from interface.formatters.ui.pokemon_ui import PokemonSelectItem
from utils.pokemon_theme import (
    load_custom_css,
    page_header,
    type_badge,
    TYPE_COLORS
)

# ======================================================
# Page Config
# ======================================================
st.set_page_config(
    page_title="Détails Pokémon",
    page_icon="📋",
    layout="wide",
)

# Load theme
load_custom_css()

# ======================================================
# Helper Functions
# ======================================================
def clean_text(t: Optional[str]) -> str:
    if not t:
        return ""
    return t.replace("\n", "").replace("\r", "").strip()

def normalize_type(t: str) -> str:
    """Normalize type name for consistent matching."""
    return clean_text(t).lower().replace("é", "e").replace("è", "e")

def format_type_badge(type_name: str) -> str:
    """Format a type as a colored badge."""
    color = TYPE_COLORS.get(normalize_type(type_name), "#999")
    return f"""
    <span style='
        background:{color};
        color:white;
        padding:4px 10px;
        border-radius:8px;
        font-size:0.8rem;
        font-weight:600;
        margin:2px;
        display:inline-block;
    '>
        {type_name.capitalize()}
    </span>
    """

def format_multiplier(m: float) -> str:
    """Format multiplier with special symbols."""
    mapping = {0.0: "0", 0.25: "¼", 0.5: "½", 1.0: "1", 2.0: "2", 4.0: "4"}
    return mapping.get(m, str(m))

def affinity_color(m: float) -> str:
    """Get color based on affinity multiplier."""
    if m == 0:
        return "#1f77b4"   # immunité
    if m < 1:
        return "#2ca02c"   # résistance
    if m == 1:
        return "#888888"   # neutralité
    if m <= 2:
        return "#ff7f0e"   # faible
    return "#d62728"       # très faible

# ======================================================
# Load Pokemon Options
# ======================================================
pokemon_options = get_pokemon_options()
if not pokemon_options:
    st.error("Aucun Pokémon disponible.")
    st.stop()

pokemon_lookup = {p.id: p for p in pokemon_options}

# ======================================================
# Pokemon Selector
# ======================================================
page_header("Fiche Pokémon Détaillée", "Découvre tous les détails de tes Pokémon favoris !", "📋")

# Check if coming from another page with pokemon_id in query params
query_params = st.query_params
pokemon_id_from_query = query_params.get('id', None)

# Default selection - use query param if available
if pokemon_id_from_query:
    try:
        default_id = int(pokemon_id_from_query)
        if default_id not in pokemon_lookup:
            default_id = list(pokemon_lookup.keys())[0]
    except:
        default_id = list(pokemon_lookup.keys())[0]
else:
    default_id = list(pokemon_lookup.keys())[0]

# Use session state to track selection changes
if 'last_selected_pokemon_id' not in st.session_state:
    st.session_state.last_selected_pokemon_id = default_id

selected_pokemon_id = st.selectbox(
    "🔍 Sélectionne un Pokémon",
    options=list(pokemon_lookup.keys()),
    format_func=lambda pid: f"#{pokemon_lookup[pid].pokedex_number:03d} - {pokemon_lookup[pid].name}",
    index=list(pokemon_lookup.keys()).index(default_id),
    key="pokemon_selector"
)

# Update query params when selection changes
if selected_pokemon_id != st.session_state.last_selected_pokemon_id:
    st.query_params.update({"id": selected_pokemon_id})
    st.session_state.last_selected_pokemon_id = selected_pokemon_id

st.divider()

# ======================================================
# Load Pokemon Details
# ======================================================
selected: PokemonSelectItem = get_pokemon_by_id(selected_pokemon_id)
if not selected:
    st.error("Impossible de récupérer ce Pokémon.")
    st.stop()

# ======================================================
# Display Pokemon Header
# ======================================================
st.header(f"{selected.name} (N° {selected.pokedex_number or '?'})")

col_img, col_info = st.columns([1, 4])

with col_img:
    if selected.sprite_url:
        st.image(selected.sprite_url, width=140)

with col_info:
    # Types - Using badges like in Moves.py
    if selected.types:
        types_badges = " ".join([
            f'<span style="background:{TYPE_COLORS.get(normalize_type(t), "#999")};'
            f'color:white;padding:4px 12px;border-radius:8px;font-size:0.9rem;'
            f'font-weight:600;margin:2px 4px;display:inline-block;">{t.capitalize()}</span>'
            for t in selected.types
        ])
        st.markdown(f"🧬 **Types :** {types_badges}", unsafe_allow_html=True)

    # Physical characteristics
    col_a, col_b = st.columns(2)
    with col_a:
        if selected.height_m:
            st.write(f"📏 **Taille :** {selected.height_m} m")
    with col_b:
        if selected.weight_kg:
            st.write(f"⚖️ **Poids :** {selected.weight_kg} kg")

st.divider()

# ======================================================
# Stats with Progress Bars
# ======================================================
if selected.stats:
    st.subheader("📊 Statistiques")

    stats_order = [
        ("hp", "PV", "#FF5959"),
        ("attack", "Attaque", "#F08030"),
        ("defense", "Défense", "#FAE078"),
        ("sp_attack", "Attaque Spéciale", "#6890F0"),
        ("sp_defense", "Défense Spéciale", "#78C850"),
        ("speed", "Vitesse", "#F85888"),
    ]

    max_stat = 255

    for key, label, color in stats_order:
        stat_value = int(selected.stats.get(key, 0))

        col_stat, col_bar = st.columns([1, 3])
        with col_stat:
            st.metric(label, stat_value)
        with col_bar:
            st.markdown(f"""
                <div style='background:#e0e0e0;border-radius:8px;overflow:hidden;height:40px;margin-top:10px;'>
                    <div style='background:{color};height:100%;width:{(stat_value/max_stat)*100}%;
                                display:flex;align-items:center;justify-content:center;
                                color:white;font-weight:600;'>
                        {stat_value}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if selected.total_stats:
        st.caption(f"🔢 Total des stats : **{int(selected.total_stats)}**")

        # Ranking
        all_totals = [p.total_stats for p in pokemon_options if p.total_stats]
        all_totals_sorted = sorted(all_totals, reverse=True)
        rank = all_totals_sorted.index(selected.total_stats) + 1 if selected.total_stats in all_totals_sorted else len(pokemon_options)
        st.caption(f"🏆 Classement: #{rank}/{len(pokemon_options)}")

st.divider()

# ======================================================
# Weaknesses / Affinités – Responsive Badges
# ======================================================
st.subheader("⚠️ Faiblesses / Multiplicateurs")
weaknesses = get_pokemon_weaknesses_ui(selected.id)

if weaknesses:
    # Start parent flex wrap div
    badges_html = "<div style='display:flex;flex-wrap:wrap;justify-content:center;gap:6px;'>"

    for w in weaknesses:
        multiplier = float(w["multiplier"])
        type_name = w["attacking_type"].capitalize()
        color = affinity_color(multiplier)

        # Badge inline-flex
        badges_html += (
            f"<div style='display:inline-flex;align-items:center;justify-content:space-between;"
            f"padding:6px 12px;border-radius:14px;background-color:{color};color:white;"
            f"font-size:0.85rem;font-weight:600;white-space:nowrap;min-width:90px;max-width:140px;'>"
            f"<span>{type_name}</span><span>×{format_multiplier(multiplier)}</span>"
            f"</div>"
        )

    badges_html += "</div>"
    st.markdown(badges_html, unsafe_allow_html=True)
else:
    st.info("Aucune faiblesse trouvée.")

st.divider()

# ======================================================
# Moves Section
# ======================================================
st.subheader("📋 Capacités")

# Get full pokemon detail from API to access moves
from interface.services.pokemon_service import get_pokemon_detail
pokemon_detail = get_pokemon_detail(selected.id)

if pokemon_detail and pokemon_detail.get('moves'):
    moves_json = pokemon_detail['moves']

    # Filters
    type_options = ["Toutes"] + sorted({clean_text(m.get('type', '')) for m in moves_json if m.get('type')})
    category_options = ["Toutes", "physique", "spécial", "autre"]

    learn_method_map = {
        "Level-up": "level_up",
        "Hérité": "before_evolution",
        "CT": "ct",
        "Move Tutor": "move_tutor"
    }

    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        type_filter = st.selectbox("Type", type_options, key="detail_type_filter")
    with c2:
        category_filter = st.selectbox("Catégorie", category_options, key="detail_category_filter")
    with c3:
        selected_methods = st.multiselect(
            "Méthodes d'apprentissage",
            list(learn_method_map.keys()),
            default=list(learn_method_map.keys()),
            key="detail_learn_methods"
        )

    learn_methods_filter = [learn_method_map[m] for m in selected_methods]

    type_filter_normalized = None if type_filter == "Toutes" else normalize_type(type_filter)
    category_filter_normalized = None if category_filter == "Toutes" else category_filter.lower()

    # Filter moves
    filtered_moves = moves_json

    if type_filter_normalized:
        filtered_moves = [m for m in filtered_moves if normalize_type(m.get('type', '')) == type_filter_normalized]

    if category_filter_normalized:
        filtered_moves = [m for m in filtered_moves if m.get('category', '').lower() == category_filter_normalized]

    if learn_methods_filter:
        filtered_moves = [m for m in filtered_moves if m.get('learn_method') in learn_methods_filter]

    # Build table
    rows = []
    pokemon_types_normalized = [normalize_type(t) for t in selected.types]

    learn_method_labels = {"level_up": "Level-up", "before_evolution": "Hérité", "ct": "CT", "move_tutor": "Move Tutor"}

    for m in filtered_moves:
        learn_method = m.get('learn_method', '')

        if learn_method == "level_up":
            learn_level = m.get('learn_level')
            if learn_level == 0:
                learn_label = "Départ"
            elif learn_level == -1:
                learn_label = "Évolution"
            elif learn_level == -2:
                learn_label = "Hérité 🧬"
            elif learn_level is not None:
                learn_label = f"Niv. {int(learn_level)}"
            else:
                learn_label = None
        elif learn_method == "before_evolution":
            learn_label = "Hérité 🧬"
        else:
            learn_label = learn_method_labels.get(learn_method)

        rows.append({
            "Capacité": m.get('name', ''),
            "Type": clean_text(m.get('type', '')).capitalize(),
            "Catégorie": m.get('category', '').capitalize(),
            "Puissance": int(m['power']) if m.get('power') else None,
            "Précision": int(m['accuracy']) if m.get('accuracy') else None,
            "Méthode": learn_label,
            "STAB": "⭐" if normalize_type(m.get('type', '')) in pokemon_types_normalized else "",
        })

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
            column_config={
                "Puissance": st.column_config.NumberColumn(format="%d"),
                "Précision": st.column_config.NumberColumn(format="%d"),
            },
        )
    else:
        st.info("Aucune capacité correspondant aux filtres.")
else:
    st.info("Aucune capacité trouvée.")

st.divider()

# ======================================================
# Navigation Actions
# ======================================================
st.markdown("### Actions Rapides")

col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("⚔️ Comparer", use_container_width=True, key="btn_compare"):
        st.switch_page("pages/2_Compare.py")

with col_b:
    if st.button("💥 Capacités", use_container_width=True, key="btn_moves"):
        st.switch_page("pages/9_Moves_List.py")

with col_c:
    if st.button("🌈 Types", use_container_width=True, key="btn_types"):
        st.switch_page("pages/8_Types.py")
