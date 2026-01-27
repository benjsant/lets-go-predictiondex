# interface/pages/4_Quiz_Types.py
import random

import streamlit as st
from utils.pokemon_theme import load_custom_css, page_header

from interface.services.api_client import get_type_affinities

# ======================================================
# Page Config
# ======================================================
st.set_page_config(
    page_title="Quiz des Types",
    page_icon="🎯",
    layout="centered",
)

# Load theme
load_custom_css()

# ======================================================
# Session State Initialization
# ======================================================
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_total' not in st.session_state:
    st.session_state.quiz_total = 0
if 'quiz_high_score' not in st.session_state:
    st.session_state.quiz_high_score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'last_answer_correct' not in st.session_state:
    st.session_state.last_answer_correct = None

# ======================================================
# Load Type Affinities & Types
# ======================================================


@st.cache_data(ttl=3600)
def load_types_and_affinities():
    """Load and cache types and affinities."""
    from interface.services.api_client import get_all_types

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

    return affinities


affinities = load_types_and_affinities()

# ======================================================
# Type Icons & Colors
# ======================================================
TYPE_ICONS = {
    "feu": "🔥", "eau": "💧", "plante": "🌿", "électrik": "⚡", "glace": "🧊",
    "combat": "🥊", "poison": "☠️", "sol": "⛰️", "vol": "🦅", "psy": "🔮",
    "insecte": "🐛", "roche": "🪨", "spectre": "👻", "dragon": "🐲", "ténèbres": "🌑",
    "acier": "⚙️", "fée": "🧚", "normal": "⭐"
}

TYPE_COLORS = {
    "feu": "#F08030", "eau": "#6890F0", "plante": "#78C850", "électrik": "#F8D030",
    "glace": "#98D8D8", "combat": "#C03028", "poison": "#A040A0", "sol": "#E0C068",
    "vol": "#A890F0", "psy": "#F85888", "insecte": "#A8B820", "roche": "#B8A038",
    "spectre": "#705898", "dragon": "#7038F8", "ténèbres": "#705848", "acier": "#B8B8D0",
    "fée": "#EE99AC", "normal": "#A8A878"
}

# ======================================================
# Helper Functions
# ======================================================


def generate_question():
    """Generate a random type matchup question."""
    # Filter interesting matchups (not neutral)
    interesting = [a for a in affinities if a['multiplier'] != 1.0]
    question = random.choice(interesting)

    return {
        'attacking_type': question['attacking_type'],
        'defending_type': question['defending_type'],
        'correct_multiplier': question['multiplier']
    }


def format_type_badge(type_name):
    """Format a type as a colored badge."""
    icon = TYPE_ICONS.get(type_name.lower(), "")
    color = TYPE_COLORS.get(type_name.lower(), "#999")
    return f"<span style='background:{color};color:white;padding:8px 16px;border-radius:12px;font-size:1.2rem;font-weight:600;display:inline-block;margin:4px;'>{icon} {type_name.capitalize()}</span>"


def check_answer(user_choice, correct_multiplier):
    """Check if the user's answer is correct."""
    # Map multipliers to categories
    if correct_multiplier == 0:
        correct_category = "immune"
    elif correct_multiplier < 1:
        correct_category = "weak"
    elif correct_multiplier == 1:
        correct_category = "normal"
    else:  # > 1
        correct_category = "strong"

    return user_choice == correct_category


# ======================================================
# Page Header
# ======================================================
page_header("Quiz des Types Pokémon", "Teste tes connaissances sur les affinités de types !", "🎯")
st.markdown("**Teste tes connaissances sur les affinités de types !**")

# ======================================================
# Score Display
# ======================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("✅ Score Actuel", f"{st.session_state.quiz_score}/{st.session_state.quiz_total}")
with col2:
    if st.session_state.quiz_total > 0:
        accuracy = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
        st.metric("📊 Précision", f"{accuracy:.0f}%")
    else:
        st.metric("📊 Précision", "0%")
with col3:
    st.metric("🏆 Meilleur Score", f"{st.session_state.quiz_high_score}")

st.divider()

# ======================================================
# Generate or Display Question
# ======================================================
if st.session_state.current_question is None or st.session_state.answered:
    if st.button("🎲 Nouvelle Question", type="primary", use_container_width=True):
        st.session_state.current_question = generate_question()
        st.session_state.answered = False
        st.session_state.last_answer_correct = None
        st.rerun()

if st.session_state.current_question is not None and not st.session_state.answered:
    question = st.session_state.current_question

    # Display Question
    st.markdown(f"### ❓ Question #{st.session_state.quiz_total + 1}")

    st.markdown(
        f"""
        <div style='text-align:center;padding:20px;background:#f0f2f6;border-radius:12px;margin:20px 0;'>
            <p style='font-size:1.2rem;margin-bottom:20px;'>Une attaque</p>
            {format_type_badge(question['attacking_type'])}
            <p style='font-size:1.8rem;margin:20px 0;'>⚔️</p>
            <p style='font-size:1.2rem;margin-bottom:20px;'>contre un Pokémon</p>
            {format_type_badge(question['defending_type'])}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🤔 C'est...")

    # Answer Buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🛡️ Immunisé\n(×0)", key="immune", use_container_width=True):
            is_correct = check_answer("immune", question['correct_multiplier'])
            st.session_state.quiz_total += 1
            if is_correct:
                st.session_state.quiz_score += 1
            st.session_state.answered = True
            st.session_state.last_answer_correct = is_correct
            st.rerun()

    with col2:
        if st.button("🔵 Peu efficace\n(×0.5)", key="weak", use_container_width=True):
            is_correct = check_answer("weak", question['correct_multiplier'])
            st.session_state.quiz_total += 1
            if is_correct:
                st.session_state.quiz_score += 1
            st.session_state.answered = True
            st.session_state.last_answer_correct = is_correct
            st.rerun()

    with col3:
        if st.button("⚪ Normal\n(×1)", key="normal", use_container_width=True):
            is_correct = check_answer("normal", question['correct_multiplier'])
            st.session_state.quiz_total += 1
            if is_correct:
                st.session_state.quiz_score += 1
            st.session_state.answered = True
            st.session_state.last_answer_correct = is_correct
            st.rerun()

    with col4:
        if st.button("🔴 Super efficace\n(×2 ou ×4)", key="strong", use_container_width=True):
            is_correct = check_answer("strong", question['correct_multiplier'])
            st.session_state.quiz_total += 1
            if is_correct:
                st.session_state.quiz_score += 1
            st.session_state.answered = True
            st.session_state.last_answer_correct = is_correct
            st.rerun()

# ======================================================
# Answer Feedback
# ======================================================
if st.session_state.answered and st.session_state.last_answer_correct is not None:
    question = st.session_state.current_question

    if st.session_state.last_answer_correct:
        st.success("✅ **Bravo ! Bonne réponse !**")
        st.balloons()
    else:
        st.error("❌ **Oups ! Mauvaise réponse...**")

        # Show correct answer
        mult = question['correct_multiplier']
        if mult == 0:
            correct_text = "🛡️ **Immunisé (×0)** - Aucun dégât !"
        elif mult < 1:
            correct_text = f"🔵 **Peu efficace (×{mult})** - Dégâts réduits"
        elif mult == 1:
            correct_text = "⚪ **Normal (×1)** - Dégâts standards"
        else:
            correct_text = f"🔴 **Super efficace (×{mult})** - Dégâts augmentés !"

        st.info(f"💡 La bonne réponse était : {correct_text}")

    # Update high score
    if st.session_state.quiz_score > st.session_state.quiz_high_score:
        st.session_state.quiz_high_score = st.session_state.quiz_score
        st.success("🏆 **Nouveau record !**")

    st.markdown("---")
    st.button("➡️ Question Suivante", on_click=lambda: None, type="primary", use_container_width=True)

# ======================================================
# Reset Button
# ======================================================
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Recommencer à Zéro", use_container_width=True):
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0
        st.session_state.current_question = None
        st.session_state.answered = False
        st.session_state.last_answer_correct = None
        st.rerun()

with col2:
    if st.button("🏆 Réinitialiser Record", use_container_width=True):
        st.session_state.quiz_high_score = 0
        st.rerun()

# ======================================================
# Tips Section
# ======================================================
with st.expander("💡 Astuces pour réussir"):
    st.markdown("""
    ### 🎯 Rappels importants :

    **Super efficace (×2 ou ×4) :**
    - 🔥 Feu > 🌿 Plante, 🧊 Glace, 🐛 Insecte, ⚙️ Acier
    - 💧 Eau > 🔥 Feu, ⛰️ Sol, 🪨 Roche
    - 🌿 Plante > 💧 Eau, ⛰️ Sol, 🪨 Roche
    - ⚡ Électrik > 💧 Eau, 🦅 Vol

    **Peu efficace (×0.5) :**
    - 🔥 Feu < 🔥 Feu, 💧 Eau, 🪨 Roche, 🐲 Dragon
    - 💧 Eau < 💧 Eau, 🌿 Plante, 🐲 Dragon
    - 🌿 Plante < 🔥 Feu, 🌿 Plante, ☠️ Poison, 🦅 Vol, 🐛 Insecte, 🐲 Dragon, ⚙️ Acier

    **Immunité (×0) :**
    - ⭐ Normal < 👻 Spectre
    - 🥊 Combat < 👻 Spectre
    - 👻 Spectre < ⭐ Normal
    - ⚡ Électrik < ⛰️ Sol
    - ☠️ Poison < ⚙️ Acier
    - ⛰️ Sol < 🦅 Vol
    - 🔮 Psy < 🌑 Ténèbres
    - 🐲 Dragon < 🧚 Fée

    💡 **Astuce :** Entraîne-toi régulièrement pour mémoriser les matchups !
    """)

# ======================================================
# Statistics
# ======================================================
if st.session_state.quiz_total >= 5:
    with st.expander("📊 Tes statistiques"):
        accuracy = (st.session_state.quiz_score / st.session_state.quiz_total) * 100

        st.metric("Précision globale", f"{accuracy:.1f}%")
        st.metric("Questions répondues", st.session_state.quiz_total)
        st.metric("Bonnes réponses", st.session_state.quiz_score)
        st.metric("Mauvaises réponses", st.session_state.quiz_total - st.session_state.quiz_score)

        # Performance judgment
        if accuracy >= 90:
            st.success("🏆 Expert des types ! Incroyable !")
        elif accuracy >= 75:
            st.info("🥇 Très bon ! Continue comme ça !")
        elif accuracy >= 60:
            st.warning("🥈 Pas mal ! Encore un peu d'entraînement !")
        else:
            st.error("🥉 Continue de t'entraîner, tu vas y arriver !")
