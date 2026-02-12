# interface/pages/4_Types_et_Affinités_Fusion.py
from typing import Optional
import pandas as pd
import streamlit as st
from interface.utils.pokemon_theme import load_custom_css, page_header, type_badge
from interface.services.api_client import get_all_types, get_type_affinities

# Page config
st.set_page_config(page_title="Types Pokémon", layout="wide")
load_custom_css()


# Helper functions
def clean_text(t: Optional[str]) -> str:
    return t.replace("\n", "").replace("\r", "").strip() if t else ""


def normalize_type(t: str) -> str:
    return clean_text(t).lower().replace("é", "e").replace("è", "e")


def format_multiplier(m: float) -> str:
    return {0.0: "0", 0.25: "¼", 0.5: "½", 1.0: "1", 2.0: "2", 4.0: "4"}.get(m, str(m))


def multiplier_color(m: float) -> str:
    if m == 0:
        return "#1f77b4"
    if m < 1:
        return "#2ca02c"
    if m == 1:
        return "#888888"
    if m <= 2:
        return "#ff7f0e"
    return "#d62728"


def display_affinities_grouped(title: str, affinities: list, type_key: str):
    """Display affinities grouped by effectiveness level."""
    if not affinities:
        st.info(f"Aucune donnée pour {title}")
        return

    super_eff = [a for a in affinities if a['multiplier'] > 1]
    weak = [a for a in affinities if 0 < a['multiplier'] < 1]
    immune = [a for a in affinities if a['multiplier'] == 0]

    st.markdown(f"### {title}")

    if super_eff:
        st.markdown("**Super Efficace (x2 ou x4)**")
        for a in sorted(super_eff, key=lambda x: x['multiplier'], reverse=True):
            st.markdown(
                f"{type_badge(a[type_key])} "
                f"<span style='color:{multiplier_color(a['multiplier'])}; font-weight:700;'>×{format_multiplier(a['multiplier'])}</span>",
                unsafe_allow_html=True)
    if weak:
        st.markdown("**Peu Efficace (x1/2 ou x1/4)**")
        for a in sorted(weak, key=lambda x: x['multiplier']):
            st.markdown(
                f"{type_badge(a[type_key])} "
                f"<span style='color:{multiplier_color(a['multiplier'])}; font-weight:700;'>×{format_multiplier(a['multiplier'])}</span>",
                unsafe_allow_html=True)
    if immune:
        st.markdown("**Sans Effet (x0)**")
        for a in immune:
            st.markdown(
                f"{type_badge(a[type_key])} "
                f"<span style='color:{multiplier_color(a['multiplier'])}; font-weight:700;'>×0</span>",
                unsafe_allow_html=True
            )


@st.cache_data(ttl=3600)
def load_types_data():
    types_list = get_all_types()
    affinities_raw = get_type_affinities()
    type_map = {t['id']: t['name'] for t in types_list}
    affinities = [
        {'attacking_type': type_map.get(a['attacking_type_id'], 'Unknown'),
         'defending_type': type_map.get(a['defending_type_id'], 'Unknown'),
         'multiplier': float(a['multiplier'])}
        for a in affinities_raw
    ]
    return types_list, affinities


types_list, affinities = load_types_data()

# Page header
page_header("Types Pokémon", "Matrice complète des 18 types avec toutes les affinités")
st.markdown(f"**Explore les {len(types_list)} types et leurs {len(affinities)} interactions !**")
st.divider()

# Type dropdown and details
st.subheader("Analyse d'un Type Spécifique")
col1, col2 = st.columns(2)
with col1:
    type_names = sorted([t['name'] for t in types_list])
    selected_type = st.selectbox("Sélectionne un type", options=type_names)
with col2:
    st.markdown(f"<div style='margin-top:28px'>{type_badge(selected_type, size='large')}</div>", unsafe_allow_html=True)

attacking = [a for a in affinities if a['attacking_type'] == selected_type]
defending = [a for a in affinities if a['defending_type'] == selected_type]

col_attack, col_defend = st.columns(2)
with col_attack:
    display_affinities_grouped(f"{selected_type} Attaque", attacking, "defending_type")
with col_defend:
    display_affinities_grouped(f"{selected_type} Défend", defending, "attacking_type")

st.divider()

# Full type matrix
st.subheader("Matrice Complète des Affinités")
st.caption("Lignes = type attaquant | Colonnes = type défenseur | Couleurs = efficacité")

type_names_sorted = sorted([t['name'] for t in types_list])
matrix = pd.DataFrame(
    {att: {def_: format_multiplier(
        next((x['multiplier'] for x in affinities
              if x['attacking_type'] == att and x['defending_type'] == def_), 1))
     for def_ in type_names_sorted} for att in type_names_sorted}
).T


def style_matrix(val):
    val_clean = val.replace("¼", "0.25").replace("½", "0.5")
    try:
        m = float(val_clean)
    except BaseException:
        m = 1.0
    return f'background-color:{multiplier_color(m)}; color:white; font-weight:600; text-align:center;'


# Render styled matrix as HTML
styled_html = matrix.style.map(style_matrix).to_html()
st.markdown(styled_html, unsafe_allow_html=True)

# Legend
st.markdown("### Légende")
for mult, desc, color in [(0, "Sans Effet", "#1f77b4"), (0.5, "Peu efficace", "#2ca02c"),
                          (1, "Neutre", "#888888"), (2, "Efficace", "#ff7f0e")]:
    st.markdown(
        f"<div style='background:{color}; color:white; padding:6px; border-radius:8px; text-align:center;'>"
        f"×{mult} - {desc}</div>", unsafe_allow_html=True
    )

# Tips section
with st.expander("Astuces - Comment utiliser cette page"):
    st.markdown("""
    ### Utilisation
    1. Sélectionne un type pour voir ses forces (Attaque) et faiblesses (Défend)
    2. Matrice complète: Lignes = Type attaquant, Colonnes = Type défenseur, Couleurs = efficacité
    3. Exemples:
       - Feu attaque Plante : x2 (super efficace)
       - Eau attaque Feu : x2 (super efficace)
       - Électrik attaque Sol : x0 (sans effet)
       - Spectre attaque Normal : x0 (sans effet)
    4. Double types: Les multiplicateurs se multiplient
       - Bulbizarre (Plante/Poison) contre Feu = x2 * x1 = x2
       - Insécateur (Insecte/Vol) contre Roche = x2 * x2 = x4
    """)
