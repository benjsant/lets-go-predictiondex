import streamlit as st

from app.streamlit.ui_helpers import (
    get_pokemon_options,
    get_moves_for_pokemon,
)
from app.streamlit.api_client import get_types

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Pokémon Moves",
    page_icon="⚡",
    layout="wide",
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/github-%23121011.svg?"
        "style=for-the-badge&logo=github&logoColor=white)]"
        "(https://github.com/ton-projet)"
    )

# --------------------------------------------------
# Banner
# --------------------------------------------------
st.image("img/banner_bot.png", use_column_width=True)

# --------------------------------------------------
# Pokémon selector
# --------------------------------------------------
pokemon_options = get_pokemon_options()

pokemon_id = st.selectbox(
    "Choisir un Pokémon",
    options=[p["id"] for p in pokemon_options],
    format_func=lambda x: next(
        p["label"] for p in pokemon_options if p["id"] == x
    ),
)

# --------------------------------------------------
# Move filters
# --------------------------------------------------
types_api = get_types()
types = ["Toutes"] + [t["name"] for t in types_api]

type_filter = st.selectbox("Filtrer par type", types)
category_filter = st.selectbox(
    "Filtrer par catégorie",
    ["Toutes", "Physique", "Spécial", "Statut"],
)
level_only = st.checkbox("Level-up only")

# --------------------------------------------------
# Fetch moves
# --------------------------------------------------
moves = get_moves_for_pokemon(
    pokemon_id,
    type_filter=None if type_filter == "Toutes" else type_filter,
    category_filter=None if category_filter == "Toutes" else category_filter,
    level_only=level_only,
)

# --------------------------------------------------
# Display Pokémon
# --------------------------------------------------
st.header("Pokémon sélectionné")

selected_pokemon = next(
    p for p in pokemon_options if p["id"] == pokemon_id
)

col1, col2 = st.columns([0.3, 0.7])

with col1:
    if selected_pokemon.get("sprite_url"):
        st.image(selected_pokemon["sprite_url"], width=120)

with col2:
    st.write(f"**Nom:** {selected_pokemon['label']}")
    st.write(f"**Types:** {', '.join(selected_pokemon['types'])}")

# --------------------------------------------------
# Display moves
# --------------------------------------------------
st.header("Moves")
st.write(f"{len(moves)} moves trouvées")

for m in moves:
    st.write(f"• {m['label']}")
