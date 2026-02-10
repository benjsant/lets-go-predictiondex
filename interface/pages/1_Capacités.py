# interface/pages/9_Moves_List.py
from typing import Optional

import pandas as pd
import streamlit as st
from interface.utils.pokemon_theme import TYPE_COLORS, load_custom_css, page_header

from interface.services.api_client import get_all_moves

# ======================================================
# Page Config
# ======================================================
st.set_page_config(
    page_title="Liste des Capacités",
    page_icon="💥",
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

# ======================================================
# Load Data
# ======================================================


@st.cache_data(ttl=3600)
def load_all_moves():
    """Load and cache all moves."""
    return get_all_moves()


all_moves = load_all_moves()

# ======================================================
# Page Header
# ======================================================
page_header("Toutes les Capacités Pokémon", "Catalogue complet des 225 capacités avec filtres", "💥")
st.markdown(f"**Explore les {len(all_moves)} capacités disponibles dans Pokémon Let's Go !**")

st.divider()

# ======================================================
# Statistics Overview
# ======================================================
st.subheader("📊 Statistiques Globales")

col1, col2, col3, col4 = st.columns(4)

# Count by category
physical_count = len([m for m in all_moves if m.get('category', '').lower() == 'physique'])
special_count = len([m for m in all_moves if m.get('category', '').lower() == 'spécial'])
status_count = len([m for m in all_moves if m.get('category', '').lower() == 'autre'])

with col1:
    st.metric("Total Capacités", len(all_moves))

with col2:
    st.metric("💪 Physiques", physical_count)

with col3:
    st.metric("🌟 Spéciales", special_count)

with col4:
    st.metric("🛡️ Statut", status_count)

st.divider()

# ======================================================
# Filters
# ======================================================
st.subheader("🔍 Filtres")

col1, col2, col3, col4 = st.columns(4)

# Type filter
with col1:
    all_types = sorted(set(m['type']['name'] for m in all_moves if m.get('type')))
    selected_type = st.selectbox(
        "Type",
        options=["Tous"] + all_types,
        key="type_filter"
    )

# Category filter
with col2:
    category_options = ["Toutes", "Physique", "Spécial", "Statut"]
    category_map = {
        "Physique": "physique",
        "Spécial": "spécial",
        "Statut": "autre"
    }
    selected_category = st.selectbox(
        "Catégorie",
        options=category_options,
        key="category_filter"
    )

# Power filter
with col3:
    power_options = ["Toutes", "≥ 100", "80-99", "50-79", "< 50", "0 (Statut)"]
    selected_power = st.selectbox(
        "Puissance",
        options=power_options,
        key="power_filter"
    )

# Search
with col4:
    search_query = st.text_input(
        "🔍 Rechercher",
        placeholder="Ex: Fatal-Foudre, Surf...",
        key="search"
    )

# ======================================================
# Apply Filters
# ======================================================
filtered_moves = all_moves

# Filter by type
if selected_type != "Tous":
    filtered_moves = [
        m for m in filtered_moves
        if m.get('type', {}).get('name') == selected_type
    ]

# Filter by category
if selected_category != "Toutes":
    category_normalized = category_map[selected_category]
    filtered_moves = [
        m for m in filtered_moves
        if m.get('category', '').lower() == category_normalized
    ]

# Filter by power
if selected_power != "Toutes":
    if selected_power == "≥ 100":
        filtered_moves = [m for m in filtered_moves if m.get('power') and m['power'] >= 100]
    elif selected_power == "80-99":
        filtered_moves = [m for m in filtered_moves if m.get('power') and 80 <= m['power'] <= 99]
    elif selected_power == "50-79":
        filtered_moves = [m for m in filtered_moves if m.get('power') and 50 <= m['power'] <= 79]
    elif selected_power == "< 50":
        filtered_moves = [m for m in filtered_moves if m.get('power') and m['power'] < 50]
    elif selected_power == "0 (Statut)":
        filtered_moves = [m for m in filtered_moves if not m.get('power') or m['power'] == 0]

# Filter by search
if search_query:
    filtered_moves = [
        m for m in filtered_moves
        if search_query.lower() in m.get('name', '').lower()
    ]

st.caption(f"📊 {len(filtered_moves)} capacités affichées")

st.divider()

# ======================================================
# Display Options
# ======================================================
view_mode = st.radio(
    "Mode d'affichage",
    options=["Tableau", "Cartes"],
    horizontal=True,
    key="view_mode"
)

st.divider()

# ======================================================
# Display - Table View
# ======================================================
if view_mode == "Tableau":
    if filtered_moves:
        # Build table rows
        rows = []
        for m in filtered_moves:
            rows.append({
                "Nom": m.get('name', ''),
                "Type": clean_text(m.get('type', {}).get('name', '')).capitalize(),
                "Catégorie": m.get('category', '').capitalize(),
                "Puissance": int(m['power']) if m.get('power') else None,
                "Précision": int(m['accuracy']) if m.get('accuracy') else None,
            })

        # Display dataframe
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nom": st.column_config.TextColumn(width="medium"),
                "Type": st.column_config.TextColumn(width="small"),
                "Catégorie": st.column_config.TextColumn(width="small"),
                "Puissance": st.column_config.NumberColumn(format="%d", width="small"),
                "Précision": st.column_config.NumberColumn(format="%d", width="small"),
            },
        )
    else:
        st.info("Aucune capacité correspondant aux filtres.")

# ======================================================
# Display - Card View
# ======================================================
else:  # Cartes
    if filtered_moves:
        # Sort by power descending
        sorted_moves = sorted(
            filtered_moves,
            key=lambda x: (x.get('power') or 0),
            reverse=True
        )

        # Display in grid (3 per row)
        cols_per_row = 3
        for i in range(0, len(sorted_moves), cols_per_row):
            cols = st.columns(cols_per_row)

            for j, col in enumerate(cols):
                if i + j < len(sorted_moves):
                    move = sorted_moves[i + j]

                    with col:
                        # Card container
                        type_name = move.get('type', {}).get('name', '')
                        type_color = TYPE_COLORS.get(normalize_type(type_name), "#999")

                        # Card header
                        st.markdown(
                            f'<div style="background:{type_color};color:white;padding:12px;'
                            f'border-radius:8px 8px 0 0;font-weight:700;font-size:1rem;">'
                            f'{move.get("name", "")}</div>',
                            unsafe_allow_html=True
                        )

                        # Card body
                        with st.container():
                            st.markdown(f"**Type:** {type_name.capitalize()}")
                            st.markdown(f"**Catégorie:** {move.get('category', '').capitalize()}")

                            col_a, col_b = st.columns(2)
                            with col_a:
                                power = move.get('power')
                                if power:
                                    st.metric("💥 Puissance", int(power))
                                else:
                                    st.metric("💥 Puissance", "-")

                            with col_b:
                                accuracy = move.get('accuracy')
                                if accuracy:
                                    st.metric("🎯 Précision", int(accuracy))
                                else:
                                    st.metric("🎯 Précision", "-")

                        st.markdown("---")
    else:
        st.info("Aucune capacité correspondant aux filtres.")

st.divider()

# ======================================================
# Top Moves Section
# ======================================================
with st.expander("🏆 Top 10 Capacités par Puissance"):
    # Filter only offensive moves
    offensive_moves = [m for m in all_moves if m.get('power') and m['power'] > 0]

    # Sort by power
    top_moves = sorted(offensive_moves, key=lambda x: x['power'], reverse=True)[:10]

    if top_moves:
        top_rows = []
        for rank, m in enumerate(top_moves, start=1):
            top_rows.append({
                "Rang": rank,
                "Nom": m.get('name', ''),
                "Type": m.get('type', {}).get('name', '').capitalize(),
                "Puissance": int(m['power']),
                "Précision": int(m['accuracy']) if m.get('accuracy') else None,
            })

        st.dataframe(
            pd.DataFrame(top_rows),
            use_container_width=True,
            hide_index=True,
        )

# ======================================================
# Tips Section
# ======================================================
with st.expander("💡 Astuces - Comment utiliser cette page"):
    st.markdown("""
    ### 🎯 Utilisation

    **1. Filtres:**
    - **Type:** Filtre par type élémentaire (Feu, Eau, etc.)
    - **Catégorie:** Physique (💪), Spécial (🌟), ou Statut (🛡️)
    - **Puissance:** Filtre par tranche de puissance
    - **Recherche:** Trouve une capacité par son nom

    **2. Modes d'affichage:**
    - **Tableau:** Vue compacte avec toutes les infos
    - **Cartes:** Vue visuelle avec badges colorés par type

    **3. Exemples de recherches:**
    - Toutes les capacités Feu avec puissance ≥ 100
    - Capacités de statut (puissance = 0)
    - Capacités physiques de type Combat

    **4. Top 10:**
    - Voir les 10 capacités les plus puissantes du jeu
    - Classement par puissance brute (sans STAB ni multiplicateurs)

    **5. Légende Catégories:**
    - **Physique (💪):** Utilise l'Attaque du Pokémon
    - **Spécial (🌟):** Utilise l'Attaque Spéciale du Pokémon
    - **Statut (🛡️):** Ne fait pas de dégâts directs (buffs, debuffs, soins)
    """)
