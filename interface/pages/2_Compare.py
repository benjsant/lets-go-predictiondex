# interface/pages/2_Compare.py
import streamlit as st
from interface.utils.ui_helpers import (
    get_pokemon_options,
    get_moves_for_pokemon,
    get_pokemon_weaknesses,
)
from interface.services.prediction_service import predict_battle_stub

# ======================================================
# Page config
# ======================================================
st.set_page_config(
    page_title="Pokémon – Comparaison",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ Comparaison de Pokémon")

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
        "Pokémon Attaquant",
        options=list(pokemon_lookup.keys()),
        format_func=lambda pid: pokemon_lookup[pid].name,
        key="p1",
    )

with col_right:
    p2_id = st.selectbox(
        "Pokémon Défenseur",
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
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;'>"
        for t in pokemon.types:
            color = TYPE_COLORS.get(t.lower(), "#999")
            html += (
                f"<span style='background:{color};color:white;"
                f"padding:4px 10px;border-radius:8px;font-size:0.85rem;'>"
                f"{t}</span>"
            )
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

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

html = "<div style='overflow-x:auto;'>"

# Header
html += "<div style='display:flex;gap:4px;margin-bottom:6px;'>"
html += "<div style='width:110px;'></div>"
for t in all_types:
    html += f"<div style='width:55px;text-align:center;font-weight:600;'>{t}</div>"
html += "</div>"

# Rows
for name, data in [(p1.name, weak_p1), (p2.name, weak_p2)]:
    html += "<div style='display:flex;gap:4px;margin-bottom:4px;'>"
    html += f"<div style='width:110px;font-weight:700;text-align:right;'>{name}</div>"
    for t in all_types:
        m = data.get(t, 1.0)
        html += (
            f"<div style='width:55px;background:{color_mult(m)};"
            f"color:white;text-align:center;border-radius:6px;"
            f"padding:4px 0;font-size:0.85rem;'>"
            f"{format_mult(m)}</div>"
        )
    html += "</div>"

html += "</div>"
st.markdown(html, unsafe_allow_html=True)

# ======================================================
# Moves – ancien modèle (4 selects distincts)
# ======================================================
st.subheader(f"🎯 Attaques de {p1.name}")

moves = get_moves_for_pokemon(p1.id)
if not moves:
    st.warning("Aucune attaque disponible.")
    st.stop()

types = ["tous"] + sorted({m.type for m in moves})
cats = ["toutes", "physique", "spécial", "autre"]

t_filter = st.selectbox("Filtrer par type", types)
c_filter = st.selectbox("Filtrer par catégorie", cats)

def filter_moves(moves):
    out = moves
    if t_filter != "tous":
        out = [m for m in out if m.type.lower() == t_filter.lower()]
    if c_filter != "toutes":
        out = [m for m in out if m.category.lower() == c_filter.lower()]
    return out

moves_f = filter_moves(moves)

m1 = st.selectbox("Move 1", moves_f, format_func=lambda m: f"{m.name} ({m.type})")
m2 = st.selectbox("Move 2", moves_f, format_func=lambda m: f"{m.name} ({m.type})")
m3 = st.selectbox("Move 3", moves_f, format_func=lambda m: f"{m.name} ({m.type})")
m4 = st.selectbox("Move 4", moves_f, format_func=lambda m: f"{m.name} ({m.type})")

selected_moves = [m1, m2, m3, m4]

# ======================================================
# Prédiction
# ======================================================
st.divider()
if st.button("🔮 Prédire le combat"):
    result = predict_battle_stub(
        pokemon_1=p1,
        moves_1=selected_moves,
        pokemon_2=p2,
        moves_2=get_moves_for_pokemon(p2.id),
    )

    st.success(result["message"])
    st.json(result["probabilities"])
