# interface/pages/1_Moves.py
import streamlit as st
import pandas as pd
from typing import List, Optional

from interface.utils.ui_helpers import (
    get_pokemon_by_id,
    get_pokemon_options,
    get_moves_for_pokemon,
    get_pokemon_weaknesses,
)
from interface.formatters.ui.move_ui import MoveSelectItem
from interface.formatters.ui.pokemon_ui import PokemonSelectItem

# ======================================================
# Config
# ======================================================
st.set_page_config(
    page_title="Pokémon – Capacités",
    page_icon="⚡",
    layout="wide",
)
st.title("⚡ Capacités Pokémon")

# ======================================================
# Utils
# ======================================================
def clean_text(t: Optional[str]) -> str:
    if not t:
        return ""
    return t.replace("\n", "").replace("\r", "").strip()

def normalize_type(t: str) -> str:
    return clean_text(t).lower().replace("é", "e").replace("è", "e")

# ======================================================
# Badges affinités – Responsive
# ======================================================
def format_multiplier(m: float) -> str:
    mapping = {0.0: "0", 0.25: "¼", 0.5: "½", 1.0: "1", 2.0: "2", 4.0: "4"}
    return mapping.get(m, str(m))

def affinity_color(m: float) -> str:
    if m == 0:
        return "#1f77b4"   # immunité
    if m < 1:
        return "#2ca02c"   # résistance
    if m == 1:
        return "#888888"   # neutralité
    if m <= 2:
        return "#ff7f0e"   # faible
    return "#d62728"       # très faible

def weakness_badge(type_name: str, multiplier: float) -> str:
    """Retourne un badge HTML pour un type / multiplicateur"""
    return f"""
    <div style="
        display:inline-flex;
        align-items:center;
        justify-content:space-between;
        gap:8px;
        padding:6px 12px;
        margin:6px;
        min-width:90px;
        max-width:140px;
        border-radius:14px;
        background-color:{affinity_color(multiplier)};
        color:white;
        font-size:0.85rem;
        font-weight:600;
        white-space:nowrap;
        box-sizing:border-box;
    ">
        <span>{type_name.capitalize()}</span>
        <span>×{format_multiplier(multiplier)}</span>
    </div>
    """

# ======================================================
# Sélection Pokémon
# ======================================================
pokemon_options = get_pokemon_options()
if not pokemon_options:
    st.error("Aucun Pokémon disponible.")
    st.stop()

pokemon_lookup = {p.id: p for p in pokemon_options}
pokemon_id = st.selectbox(
    "Choisir un Pokémon",
    options=list(pokemon_lookup.keys()),
    format_func=lambda pid: pokemon_lookup[pid].name,
)
selected: PokemonSelectItem = get_pokemon_by_id(pokemon_id)
if not selected:
    st.error("Impossible de récupérer ce Pokémon.")
    st.stop()

# ======================================================
# Infos Pokémon
# ======================================================
st.header(f"{selected.name} (N° {selected.pokedex_number or '?'})")
col_img, col_info = st.columns([1, 4])

with col_img:
    if selected.sprite_url:
        st.image(selected.sprite_url, width=140)

with col_info:
    if selected.types:
        st.write("🧬 **Types :** " + ", ".join(t.capitalize() for t in selected.types))
    if selected.height_m:
        st.write(f"📏 **Taille :** {selected.height_m} m")
    if selected.weight_kg:
        st.write(f"⚖️ **Poids :** {selected.weight_kg} kg")

# ======================================================
# Stats Pokémon
# ======================================================
if selected.stats:
    st.subheader("📊 Statistiques")
    stats_order = [
        ("hp", "PV"), ("attack", "Attaque"), ("defense", "Défense"),
        ("sp_attack", "Attaque Spéciale"), ("sp_defense", "Défense Spéciale"), ("speed", "Vitesse")
    ]
    stats_rows = [{"Stat": label, "Valeur": int(selected.stats.get(key, 0))} for key, label in stats_order]
    st.table(pd.DataFrame(stats_rows))
    if selected.total_stats:
        st.caption(f"🔢 Total des stats : **{int(selected.total_stats)}**")

# ======================================================
# Weaknesses / Affinités – Badges responsive
# ======================================================
st.subheader("⚠️ Faiblesses / Multiplicateurs")
weaknesses = get_pokemon_weaknesses(selected.id)

if weaknesses:
    # On commence le div parent flex wrap
    badges_html = "<div style='display:flex;flex-wrap:wrap;justify-content:center;gap:6px;'>"

    for w in weaknesses:
        multiplier = float(w["multiplier"])
        type_name = w["attacking_type"].capitalize()

        # Couleur selon multiplicateur
        if multiplier == 0:
            color = "#1f77b4"
        elif multiplier < 1:
            color = "#2ca02c"
        elif multiplier == 1:
            color = "#888888"
        elif multiplier <= 2:
            color = "#ff7f0e"
        else:
            color = "#d62728"

        # Badge inline-flex, mais tout dans la même chaîne
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


# ======================================================
# Capacités
# ======================================================
st.subheader("📋 Capacités")
all_moves: List[MoveSelectItem] = get_moves_for_pokemon(selected.id)
if not all_moves:
    st.info("Aucune capacité trouvée.")
    st.stop()

# -----------------------------
# Filtres
# -----------------------------
type_options = ["Toutes"] + sorted({clean_text(m.type) for m in all_moves if m.type})
category_options = ["Toutes", "physique", "spécial", "autre"]
learn_method_map = {"Level-up": "level_up", "CT": "ct", "Move Tutor": "move_tutor"}

c1, c2, c3 = st.columns([2, 2, 3])
with c1:
    type_filter = st.selectbox("Type", type_options)
with c2:
    category_filter = st.selectbox("Catégorie", category_options)
with c3:
    selected_methods = st.multiselect(
        "Méthodes d'apprentissage",
        list(learn_method_map.keys()),
        default=list(learn_method_map.keys())
    )
learn_methods_filter = [learn_method_map[m] for m in selected_methods]

type_filter = None if type_filter == "Toutes" else type_filter.lower()
category_filter = None if category_filter == "Toutes" else category_filter.lower()

def filter_moves(moves: List[MoveSelectItem]) -> List[MoveSelectItem]:
    res = moves
    if type_filter:
        res = [m for m in res if normalize_type(m.type) == type_filter]
    if category_filter:
        res = [m for m in res if m.category.lower() == category_filter]
    if learn_methods_filter:
        res = [m for m in res if m.learn_method in learn_methods_filter]
    return res

moves = filter_moves(all_moves)

# -----------------------------
# Tableau des capacités (ZÉRO FLOAT)
# -----------------------------
rows = []
pokemon_types = [normalize_type(t) for t in selected.types]

learn_method_labels = {"level_up": "Level-up", "ct": "CT", "move_tutor": "Move Tutor"}

for m in moves:
    if m.learn_method == "level_up":
        if m.learn_level == 0:
            learn_label = "Départ"
        elif m.learn_level == -1:
            learn_label = "Évolution"
        elif m.learn_level is not None:
            learn_label = f"Niv. {int(m.learn_level)}"
        else:
            learn_label = None
    else:
        learn_label = learn_method_labels.get(m.learn_method)

    rows.append({
        "Capacité": m.name,
        "Type": clean_text(m.type).capitalize(),
        "Catégorie": m.category.capitalize(),
        "Puissance": int(m.power) if isinstance(m.power, (int, float)) else None,
        "Précision": int(m.accuracy) if isinstance(m.accuracy, (int, float)) else None,
        "Méthode": learn_label,
        "STAB": "⭐" if normalize_type(m.type) in pokemon_types else "",
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
