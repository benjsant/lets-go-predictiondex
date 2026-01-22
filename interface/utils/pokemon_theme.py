# interface/utils/pokemon_theme.py
"""
Pokémon Theme Components
========================

Centralized styling and components for consistent Pokémon-themed UI.
"""

import streamlit as st

# ======================================================
# Color Palette
# ======================================================

POKEMON_COLORS = {
    # Primary colors - Mix Pikachu (jaune) + Évoli (brun)
    'primary': '#FFCC00',      # Jaune Pikachu
    'primary_alt': '#CD853F',  # Brun Évoli
    'secondary': '#3B4CCA',    # Bleu Pokéball
    'accent': '#FF0000',       # Rouge Pokéball

    # UI colors
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3',

    # Backgrounds - Teintes chaudes pour Pikachu/Évoli
    'bg_main': '#FFFAF0',      # Blanc cassé chaud (Floral White)
    'bg_card': '#FFFFFF',
    'bg_secondary': '#FFF8DC',  # Cornsilk - beige très clair
    'bg_hover': '#FFEFD5',     # Papaya Whip - pêche clair

    # Text
    'text_primary': '#2C3E50',
    'text_secondary': '#8B4513',  # Saddle Brown - brun pour rappeler Évoli
    'text_light': '#A0826D',      # Brun clair
}

# Type colors
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

TYPE_ICONS = {
    "feu": "🔥", "eau": "💧", "plante": "🌿", "électrik": "⚡", "glace": "🧊",
    "combat": "🥊", "poison": "☠️", "sol": "⛰️", "vol": "🦅", "psy": "🔮",
    "insecte": "🐛", "roche": "🪨", "spectre": "👻", "dragon": "🐲", "ténèbres": "🌑",
    "acier": "⚙️", "fée": "🧚", "normal": "⭐"
}

# ======================================================
# Custom CSS
# ======================================================

def load_custom_css():
    """Load custom CSS for Pokémon theme."""
    st.markdown(f"""
    <style>
    /* Global adjustments */
    .stApp {{
        background: linear-gradient(135deg, {POKEMON_COLORS['bg_main']} 0%, {POKEMON_COLORS['bg_secondary']} 100%);
        color: {POKEMON_COLORS['text_primary']};
    }}

    /* Header styling */
    h1 {{
        color: {POKEMON_COLORS['text_primary']};
        font-weight: 700;
        border-bottom: 3px solid {POKEMON_COLORS['primary']};
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}

    h2 {{
        color: {POKEMON_COLORS['secondary']};
        font-weight: 600;
        margin-top: 20px;
    }}

    h3 {{
        color: {POKEMON_COLORS['text_primary']};
        font-weight: 600;
    }}

    p {{
        color: {POKEMON_COLORS['text_primary']};
    }}

    /* Button styling */
    .stButton > button {{
        border-radius: 12px;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        background-color: {POKEMON_COLORS['bg_card']};
        color: {POKEMON_COLORS['text_primary']};
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background-color: {POKEMON_COLORS['bg_hover']};
    }}

    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {POKEMON_COLORS['primary']} 0%, {POKEMON_COLORS['primary_alt']} 100%);
        color: #2C3E50;
        border: 2px solid {POKEMON_COLORS['primary']};
    }}

    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {POKEMON_COLORS['primary_alt']} 0%, {POKEMON_COLORS['primary']} 100%);
    }}

    /* Metric styling */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
        color: {POKEMON_COLORS['secondary']};
    }}

    [data-testid="stMetricLabel"] {{
        color: {POKEMON_COLORS['text_secondary']};
    }}

    /* Info boxes */
    .stAlert {{
        border-radius: 12px;
        border-left: 4px solid;
        background-color: {POKEMON_COLORS['bg_card']};
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        border-radius: 8px;
        background-color: {POKEMON_COLORS['bg_secondary']};
        color: {POKEMON_COLORS['text_primary']};
        font-weight: 600;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {POKEMON_COLORS['bg_card']} 0%, {POKEMON_COLORS['bg_secondary']} 100%);
    }}

    [data-testid="stSidebar"] * {{
        color: {POKEMON_COLORS['text_primary']};
    }}

    /* Divider */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, {POKEMON_COLORS['primary']} 50%, transparent 100%);
        margin: 30px 0;
    }}

    /* Select boxes */
    .stSelectbox label, .stMultiSelect label {{
        color: {POKEMON_COLORS['text_primary']};
    }}

    .stSelectbox > div > div {{
        border-radius: 8px;
        background-color: {POKEMON_COLORS['bg_card']};
        color: {POKEMON_COLORS['text_primary']};
    }}

    /* Multiselect */
    .stMultiSelect > div {{
        border-radius: 8px;
        background-color: {POKEMON_COLORS['bg_card']};
    }}

    /* Progress bar */
    .stProgress > div > div {{
        background: linear-gradient(90deg, {POKEMON_COLORS['success']} 0%, #8BC34A 100%);
        border-radius: 10px;
    }}

    /* DataFrames */
    .dataframe {{
        border-radius: 8px;
        overflow: hidden;
        background-color: {POKEMON_COLORS['bg_card']};
        color: {POKEMON_COLORS['text_primary']};
    }}

    /* Text inputs */
    .stTextInput > div > div {{
        background-color: {POKEMON_COLORS['bg_card']};
        color: {POKEMON_COLORS['text_primary']};
    }}

    /* Success/Error messages */
    .stSuccess {{
        background-color: {POKEMON_COLORS['bg_card']};
        border-left-color: {POKEMON_COLORS['success']};
    }}

    .stError {{
        background-color: {POKEMON_COLORS['bg_card']};
        border-left-color: {POKEMON_COLORS['error']};
    }}

    .stWarning {{
        background-color: {POKEMON_COLORS['bg_card']};
        border-left-color: {POKEMON_COLORS['warning']};
    }}

    .stInfo {{
        background-color: {POKEMON_COLORS['bg_card']};
        border-left-color: {POKEMON_COLORS['info']};
    }}
    </style>
    """, unsafe_allow_html=True)


# ======================================================
# Reusable Components
# ======================================================

def type_badge(type_name: str, size: str = "normal") -> str:
    """Generate a styled type badge."""
    type_lower = type_name.lower()
    icon = TYPE_ICONS.get(type_lower, "")
    color = TYPE_COLORS.get(type_lower, "#999")

    sizes = {
        "small": {"padding": "4px 8px", "font": "0.75rem", "margin": "2px"},
        "normal": {"padding": "6px 12px", "font": "0.9rem", "margin": "4px"},
        "large": {"padding": "8px 16px", "font": "1.2rem", "margin": "6px"},
    }

    s = sizes.get(size, sizes["normal"])

    return f"<span style='background:{color};color:white;padding:{s['padding']};border-radius:8px;font-size:{s['font']};font-weight:600;display:inline-block;margin:{s['margin']};box-shadow:0 2px 4px rgba(0,0,0,0.2);'>{icon} {type_name.capitalize()}</span>"


def feature_card(title: str, description: str, page_link: str, icon: str = "⚡"):
    """Create a feature card with consistent styling."""
    return f"<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;height:100%;box-shadow:0 2px 8px rgba(0,0,0,0.1);border:1px solid {POKEMON_COLORS['bg_secondary']};transition:transform 0.3s ease, box-shadow 0.3s ease;' onmouseover=\"this.style.transform='translateY(-5px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.2)';\" onmouseout=\"this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)';\"><h3 style='color:{POKEMON_COLORS['secondary']};margin:0 0 15px 0;'>{icon} {title}</h3><p style='color:{POKEMON_COLORS['text_primary']};line-height:1.6;margin:0 0 15px 0;'>{description}</p><p style='color:{POKEMON_COLORS['text_secondary']};margin:0;'><strong>👉 Page: {page_link}</strong></p></div>"


def pokemon_card(pokemon, show_stats: bool = True):
    """Display a Pokémon card with sprite, types, and optionally stats."""
    st.markdown(f"### {pokemon.name}")

    # Sprite
    if pokemon.sprite_url:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(pokemon.sprite_url, width=150)

    # Types
    if pokemon.types:
        types_html = " ".join([type_badge(t, "normal") for t in pokemon.types])
        st.markdown(
            f"<div style='text-align:center;margin:10px 0;'>{types_html}</div>",
            unsafe_allow_html=True
        )

    # Stats
    if show_stats and pokemon.stats:
        st.markdown("**Statistiques**")
        col1, col2, col3 = st.columns(3)
        stats_order = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
        stats_labels = {
            "hp": "❤️ HP",
            "attack": "⚔️ Attaque",
            "defense": "🛡️ Défense",
            "sp_attack": "✨ Att.Spé",
            "sp_defense": "💫 Déf.Spé",
            "speed": "⚡ Vitesse"
        }

        for i, stat_key in enumerate(stats_order):
            stat_value = pokemon.stats.get(stat_key, 0)
            label = stats_labels.get(stat_key, stat_key.upper())

            with [col1, col2, col3][i % 3]:
                st.metric(label, int(stat_value))


def pokeball_divider():
    """Display a themed divider with Pokéball emoji and Pikachu/Eevee gradient."""
    st.markdown(f"<div style='text-align:center;margin:20px 0;'><div style='display:inline-block;background:linear-gradient(90deg, {POKEMON_COLORS['primary']} 0%, {POKEMON_COLORS['accent']} 50%, {POKEMON_COLORS['primary_alt']} 100%);height:3px;width:200px;border-radius:2px;'></div><div style='margin:10px 0;'><span style='font-size:2rem;'>⚪🔴⚪</span></div><div style='display:inline-block;background:linear-gradient(90deg, {POKEMON_COLORS['primary_alt']} 0%, {POKEMON_COLORS['accent']} 50%, {POKEMON_COLORS['primary']} 100%);height:3px;width:200px;border-radius:2px;'></div></div>", unsafe_allow_html=True)


def section_header(title: str, icon: str = "✨"):
    """Display a styled section header."""
    st.markdown(f"<div style='background:linear-gradient(135deg, {POKEMON_COLORS['bg_secondary']} 0%, {POKEMON_COLORS['bg_card']} 100%);padding:15px 20px;border-radius:12px;border-left:5px solid {POKEMON_COLORS['primary']};border-right:5px solid {POKEMON_COLORS['primary_alt']};margin:20px 0;box-shadow:0 2px 6px rgba(0,0,0,0.08);'><h2 style='margin:0;color:{POKEMON_COLORS['secondary']};'>{icon} {title}</h2></div>", unsafe_allow_html=True)


def probability_bar(probability: float, label: str = "Probabilité"):
    """Display a colored probability bar."""
    percentage = probability * 100

    # Color based on probability
    if percentage >= 70:
        color = POKEMON_COLORS['success']
        emoji = "✅"
    elif percentage >= 50:
        color = POKEMON_COLORS['warning']
        emoji = "⚖️"
    else:
        color = POKEMON_COLORS['error']
        emoji = "⚠️"

    st.markdown(f"**{emoji} {label}**")
    st.markdown(f"<div style='background:{POKEMON_COLORS['bg_secondary']};border-radius:10px;overflow:hidden;height:30px;margin:10px 0;'><div style='background:linear-gradient(90deg, {color} 0%, {color}CC 100%);width:{percentage}%;height:100%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;transition:width 0.5s ease;'>{percentage:.1f}%</div></div>", unsafe_allow_html=True)


def info_box(title: str, content: str, icon: str = "💡", color: str = "info"):
    """Display a styled info box."""
    colors = {
        "info": {"border": POKEMON_COLORS['info']},
        "success": {"border": POKEMON_COLORS['success']},
        "warning": {"border": POKEMON_COLORS['warning']},
        "error": {"border": POKEMON_COLORS['error']},
    }

    c = colors.get(color, colors["info"])

    st.markdown(f"<div style='background:{POKEMON_COLORS['bg_card']};border-left:5px solid {c['border']};border-radius:8px;padding:15px 20px;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1);'><div style='font-weight:700;font-size:1.1rem;margin-bottom:8px;color:{POKEMON_COLORS['text_primary']};'>{icon} {title}</div><div style='color:{POKEMON_COLORS['text_primary']};line-height:1.6;'>{content}</div></div>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = "⚡"):
    """Display a consistent page header."""
    subtitle_html = f"<p style='font-size:1.2rem;color:{POKEMON_COLORS['text_secondary']};margin-top:10px;'>{subtitle}</p>" if subtitle else ''
    st.markdown(f"<div style='text-align:center;padding:20px 0;background:{POKEMON_COLORS['bg_main']};border-radius:8px;'><h1 style='font-size:2.5rem;color:{POKEMON_COLORS['text_primary']};margin:0;text-shadow:2px 2px 4px rgba(0,0,0,0.1);'>{icon} {title}</h1>{subtitle_html}</div>", unsafe_allow_html=True)
    pokeball_divider()


def pikachu_eevee_mascots():
    """Display Pikachu and Eevee sprites side by side with gradient background."""
    st.markdown(f"""
    <div style='background:linear-gradient(135deg, {POKEMON_COLORS['primary']}22 0%, {POKEMON_COLORS['primary_alt']}22 100%);padding:30px;border-radius:16px;margin:20px 0;box-shadow:0 4px 12px rgba(0,0,0,0.1);'>
        <div style='display:flex;justify-content:center;align-items:center;gap:40px;flex-wrap:wrap;'>
            <div style='text-align:center;'>
                <img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png' width='150' style='filter:drop-shadow(0 4px 8px rgba(0,0,0,0.2));'/>
                <p style='margin-top:10px;font-weight:700;color:{POKEMON_COLORS['primary']};font-size:1.1rem;text-shadow:1px 1px 2px rgba(0,0,0,0.1);'>⚡ Pikachu</p>
            </div>
            <div style='text-align:center;font-size:3rem;color:{POKEMON_COLORS['accent']};'>VS</div>
            <div style='text-align:center;'>
                <img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/133.png' width='150' style='filter:drop-shadow(0 4px 8px rgba(0,0,0,0.2));'/>
                <p style='margin-top:10px;font-weight:700;color:{POKEMON_COLORS['primary_alt']};font-size:1.1rem;text-shadow:1px 1px 2px rgba(0,0,0,0.1);'>🦊 Évoli</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
