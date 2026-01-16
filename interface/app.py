import streamlit as st

from ui_helpers import get_pokemon_options, get_moves_for_pokemon
from api_client import get_types

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Pokémon Moves",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/github-%23121011.svg?"
        "style=for-the-badge&logo=github&logoColor=white)]"
        "(https://github.com/ton-projet)"
    )

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
# Move filters
# -----------------------------
types_api = get_types()
types = ["Toutes"] + [t.get("name", "") for t in types_api]

type_filter = st.selectbox("Filtrer par type", types)
category_filter = st.selectbox(
    "Filtrer par catégorie", ["Toutes", "Physique", "Spécial", "Statut"]
)
level_only = st.checkbox("Level-up only")

# -----------------------------
# Fetch moves
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
st.header("Pokémon sélectionné")
selected_pokemon = next(p for p in pokemon_options if p.id == pokemon_id)

col1, col2 = st.columns([0.3, 0.7])
with col1:
    if selected_pokemon.sprite_url:
        st.image(selected_pokemon.sprite_url, width=120)
    else:
        st.write("Pas d'image disponible")

with col2:
    st.write(f"**Nom :** {selected_pokemon.name}")
    types_list = getattr(selected_pokemon, "types", [])
    st.write(f"**Types :** {', '.join(types_list) if types_list else 'Non renseigné'}")

# -----------------------------
# Display moves
# -----------------------------
st.header("Moves")
if moves:
    st.write(f"{len(moves)} moves trouvées")
    for m in moves:
        st.write(f"• {m.label}")
else:
    st.write("Aucun move trouvé pour ce Pokémon")
