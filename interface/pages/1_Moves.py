import streamlit as st

from interface.utils.ui_helpers import (
    get_pokemon_options,
    get_moves_for_pokemon,
)
from interface.services.move_service import get_types


st.set_page_config(
    page_title="Pokémon Moves",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## Pokémon Let's Go – PredictionDex")

# -----------------------------
# Pokémon selector
# -----------------------------
pokemon_options = get_pokemon_options()

pokemon_id = st.selectbox(
    "Choisir un Pokémon",
    options=[p.id for p in pokemon_options],
    format_func=lambda x: next(p.name for p in pokemon_options if p.id == x),
)

# -----------------------------
# Filters
# -----------------------------
types_api = get_types()
types = ["Toutes"] + [t.get("name") for t in types_api]

type_filter = st.selectbox("Filtrer par type", types)
category_filter = st.selectbox(
    "Filtrer par catégorie", ["Toutes", "Physique", "Spécial", "Statut"]
)
level_only = st.checkbox("Level-up uniquement")

# -----------------------------
# Moves
# -----------------------------
moves = get_moves_for_pokemon(
    pokemon_id,
    type_filter=None if type_filter == "Toutes" else type_filter,
    category_filter=None if category_filter == "Toutes" else category_filter,
    level_only=level_only,
)

# -----------------------------
# Display Pokémon
# -----------------------------
selected = next(p for p in pokemon_options if p.id == pokemon_id)

st.header(selected.name)

cols = st.columns([1, 3])
with cols[0]:
    if selected.sprite_url:
        st.image(selected.sprite_url, width=120)

with cols[1]:
    st.write(f"**Types :** {', '.join(selected.types)}")

# -----------------------------
# Display moves
# -----------------------------
st.subheader("Moves disponibles")

if moves:
    for m in moves:
        st.write(f"• {m.label}")
else:
    st.info("Aucun move trouvé.")
