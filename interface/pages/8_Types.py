# interface/pages/8_Types.py
import streamlit as st
import pandas as pd
from typing import Optional

from interface.services.api_client import get_all_types, get_type_affinities
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
    page_title="Types Pokémon",
    page_icon="🌈",
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

def format_multiplier(m: float) -> str:
    """Format multiplier with special symbols."""
    mapping = {0.0: "0", 0.25: "¼", 0.5: "½", 1.0: "1", 2.0: "2", 4.0: "4"}
    return mapping.get(m, str(m))

def get_multiplier_color(m: float) -> str:
    """Get background color based on multiplier."""
    if m == 0:
        return "#1f77b4"   # immunité - bleu
    if m < 1:
        return "#2ca02c"   # résistance - vert
    if m == 1:
        return "#888888"   # neutralité - gris
    if m <= 2:
        return "#ff7f0e"   # faible - orange
    return "#d62728"       # très faible - rouge

# ======================================================
# Load Data
# ======================================================
@st.cache_data(ttl=3600)
def load_types_data():
    """Load and cache types and affinities."""
    types_list = get_all_types()
    affinities_raw = get_type_affinities()

    # Create type ID to name mapping
    type_map = {t['id']: t['name'] for t in types_list}

    # Enrich affinities with type names
    affinities = []
    for aff in affinities_raw:
        affinities.append({
            'attacking_type': type_map.get(aff['attacking_type_id'], 'Unknown'),
            'defending_type': type_map.get(aff['defending_type_id'], 'Unknown'),
            'multiplier': float(aff['multiplier'])
        })

    return types_list, affinities

types_list, affinities = load_types_data()

# ======================================================
# Page Header
# ======================================================
page_header("Types Pokémon", "Matrice complète des 18 types avec toutes les affinités", "🌈")
st.markdown(f"**Explore les {len(types_list)} types et leurs {len(affinities)} interactions !**")

st.divider()

# ======================================================
# Type Selection
# ======================================================
st.subheader("🔍 Analyse d'un Type Spécifique")

col1, col2 = st.columns(2)

with col1:
    type_names = sorted([t['name'] for t in types_list])
    selected_type = st.selectbox(
        "Sélectionne un type pour voir ses affinités détaillées",
        options=type_names,
        key="selected_type"
    )

with col2:
    # Type badge
    type_color = TYPE_COLORS.get(normalize_type(selected_type), "#999")
    st.markdown(
        f'<div style="margin-top:28px;">'
        f'<span style="background:{type_color};color:white;padding:8px 24px;'
        f'border-radius:12px;font-size:1.2rem;font-weight:700;">{selected_type.capitalize()}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

st.divider()

# ======================================================
# Type Details - Attacking & Defending
# ======================================================

# Filter affinities for selected type
attacking_affinities = [a for a in affinities if a['attacking_type'] == selected_type]
defending_affinities = [a for a in affinities if a['defending_type'] == selected_type]

col_attack, col_defend = st.columns(2)

# ======================================================
# Attacking
# ======================================================
with col_attack:
    st.markdown(f"### ⚔️ {selected_type.capitalize()} Attaque")
    st.caption("Efficacité de ce type contre les autres types")

    # Group by effectiveness
    super_effective = [a for a in attacking_affinities if a['multiplier'] > 1]
    not_very_effective = [a for a in attacking_affinities if 0 < a['multiplier'] < 1]
    no_effect = [a for a in attacking_affinities if a['multiplier'] == 0]
    neutral = [a for a in attacking_affinities if a['multiplier'] == 1]

    if super_effective:
        st.markdown("**🔥 Super Efficace (×2 ou ×4)**")
        for aff in sorted(super_effective, key=lambda x: x['multiplier'], reverse=True):
            mult = aff['multiplier']
            defending = aff['defending_type']
            color = TYPE_COLORS.get(normalize_type(defending), "#999")
            st.markdown(
                f'<span style="background:{color};color:white;padding:4px 12px;'
                f'border-radius:8px;font-size:0.85rem;font-weight:600;margin:2px;display:inline-block;">'
                f'{defending.capitalize()}</span> '
                f'<span style="color:#d62728;font-weight:700;">×{format_multiplier(mult)}</span>',
                unsafe_allow_html=True
            )

    if not_very_effective:
        st.markdown("**💚 Peu Efficace (×½ ou ×¼)**")
        for aff in sorted(not_very_effective, key=lambda x: x['multiplier']):
            mult = aff['multiplier']
            defending = aff['defending_type']
            color = TYPE_COLORS.get(normalize_type(defending), "#999")
            st.markdown(
                f'<span style="background:{color};color:white;padding:4px 12px;'
                f'border-radius:8px;font-size:0.85rem;font-weight:600;margin:2px;display:inline-block;">'
                f'{defending.capitalize()}</span> '
                f'<span style="color:#2ca02c;font-weight:700;">×{format_multiplier(mult)}</span>',
                unsafe_allow_html=True
            )

    if no_effect:
        st.markdown("**🛡️ Sans Effet (×0)**")
        for aff in no_effect:
            defending = aff['defending_type']
            color = TYPE_COLORS.get(normalize_type(defending), "#999")
            st.markdown(
                f'<span style="background:{color};color:white;padding:4px 12px;'
                f'border-radius:8px;font-size:0.85rem;font-weight:600;margin:2px;display:inline-block;">'
                f'{defending.capitalize()}</span> '
                f'<span style="color:#1f77b4;font-weight:700;">×0</span>',
                unsafe_allow_html=True
            )

# ======================================================
# Defending
# ======================================================
with col_defend:
    st.markdown(f"### 🛡️ {selected_type.capitalize()} Défend")
    st.caption("Résistance de ce type aux autres types")

    # Group by effectiveness
    weak_to = [a for a in defending_affinities if a['multiplier'] > 1]
    resistant_to = [a for a in defending_affinities if 0 < a['multiplier'] < 1]
    immune_to = [a for a in defending_affinities if a['multiplier'] == 0]
    neutral_to = [a for a in defending_affinities if a['multiplier'] == 1]

    if weak_to:
        st.markdown("**❤️ Faible Contre (×2 ou ×4)**")
        for aff in sorted(weak_to, key=lambda x: x['multiplier'], reverse=True):
            mult = aff['multiplier']
            attacking = aff['attacking_type']
            color = TYPE_COLORS.get(normalize_type(attacking), "#999")
            st.markdown(
                f'<span style="background:{color};color:white;padding:4px 12px;'
                f'border-radius:8px;font-size:0.85rem;font-weight:600;margin:2px;display:inline-block;">'
                f'{attacking.capitalize()}</span> '
                f'<span style="color:#d62728;font-weight:700;">×{format_multiplier(mult)}</span>',
                unsafe_allow_html=True
            )

    if resistant_to:
        st.markdown("**💚 Résiste à (×½ ou ×¼)**")
        for aff in sorted(resistant_to, key=lambda x: x['multiplier']):
            mult = aff['multiplier']
            attacking = aff['attacking_type']
            color = TYPE_COLORS.get(normalize_type(attacking), "#999")
            st.markdown(
                f'<span style="background:{color};color:white;padding:4px 12px;'
                f'border-radius:8px;font-size:0.85rem;font-weight:600;margin:2px;display:inline-block;">'
                f'{attacking.capitalize()}</span> '
                f'<span style="color:#2ca02c;font-weight:700;">×{format_multiplier(mult)}</span>',
                unsafe_allow_html=True
            )

    if immune_to:
        st.markdown("**🛡️ Immunisé à (×0)**")
        for aff in immune_to:
            attacking = aff['attacking_type']
            color = TYPE_COLORS.get(normalize_type(attacking), "#999")
            st.markdown(
                f'<span style="background:{color};color:white;padding:4px 12px;'
                f'border-radius:8px;font-size:0.85rem;font-weight:600;margin:2px;display:inline-block;">'
                f'{attacking.capitalize()}</span> '
                f'<span style="color:#1f77b4;font-weight:700;">×0</span>',
                unsafe_allow_html=True
            )

st.divider()

# ======================================================
# Full Type Chart - Matrix View
# ======================================================
st.subheader("📊 Matrice Complète des Affinités")
st.caption("Ligne = Type Attaquant | Colonne = Type Défenseur")

# Build matrix
type_names_sorted = sorted([t['name'] for t in types_list])
matrix_data = {}

for attacking_type in type_names_sorted:
    row = {}
    for defending_type in type_names_sorted:
        # Find affinity
        aff = next(
            (a for a in affinities
             if a['attacking_type'] == attacking_type and a['defending_type'] == defending_type),
            None
        )
        if aff:
            row[defending_type.capitalize()] = format_multiplier(aff['multiplier'])
        else:
            row[defending_type.capitalize()] = "1"
    matrix_data[attacking_type.capitalize()] = row

# Create DataFrame
df = pd.DataFrame(matrix_data).T

# Custom styling function
def color_multiplier(val):
    """Color cells based on multiplier value."""
    val_clean = val.replace("¼", "0.25").replace("½", "0.5")
    try:
        m = float(val_clean)
    except:
        m = 1.0

    color = get_multiplier_color(m)
    return f'background-color: {color}; color: white; font-weight: 600; text-align: center;'

# Display styled dataframe
st.dataframe(
    df.style.applymap(color_multiplier),
    use_container_width=True,
    height=600
)

# Legend
st.markdown("### 📖 Légende")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        '<div style="background:#1f77b4;color:white;padding:8px;border-radius:8px;text-align:center;">'
        '×0 - Sans Effet</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '<div style="background:#2ca02c;color:white;padding:8px;border-radius:8px;text-align:center;">'
        '×¼ / ×½ - Peu Efficace</div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        '<div style="background:#888888;color:white;padding:8px;border-radius:8px;text-align:center;">'
        '×1 - Neutre</div>',
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        '<div style="background:#ff7f0e;color:white;padding:8px;border-radius:8px;text-align:center;">'
        '×2 - Efficace</div>',
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        '<div style="background:#d62728;color:white;padding:8px;border-radius:8px;text-align:center;">'
        '×4 - Très Efficace</div>',
        unsafe_allow_html=True
    )

st.divider()

# ======================================================
# Tips Section
# ======================================================
with st.expander("💡 Astuces - Comment utiliser cette page"):
    st.markdown("""
    ### 🎯 Utilisation

    **1. Analyse d'un type spécifique:**
    - Sélectionne un type dans le dropdown
    - Voir ses forces (⚔️ Attaque) et faiblesses (🛡️ Défend)

    **2. Matrice complète:**
    - Lignes = Type attaquant
    - Colonnes = Type défenseur
    - Couleurs = Efficacité

    **3. Exemples:**
    - Feu attaque Plante : ×2 (super efficace) 🔥
    - Eau attaque Feu : ×2 (super efficace) 💧
    - Électrik attaque Sol : ×0 (sans effet) ⚡
    - Spectre attaque Normal : ×0 (sans effet) 👻

    **4. Double types:**
    - Les multiplicateurs se multiplient !
    - Ex: Bulbizarre (Plante/Poison) contre Feu = ×2 (Plante) × ×1 (Poison) = **×2**
    - Ex: Insécateur (Insecte/Vol) contre Roche = ×2 (Vol) × ×2 (Insecte) = **×4** !
    """)
