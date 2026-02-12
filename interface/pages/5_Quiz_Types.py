# interface/pages/4_Quiz_Types.py
import random
import streamlit as st
from interface.utils.pokemon_theme import load_custom_css, page_header
from interface.services.api_client import get_type_affinities, get_all_types

# Page config
st.set_page_config(
    page_title="Quiz des Types",
    layout="centered",
)
load_custom_css()

# Session state initialization
for key, default in {
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_high_score": 0,
    "current_question": None,
    "answered": False,
    "last_answer_correct": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# Load type affinities data
@st.cache_data(ttl=3600)
def load_types_and_affinities():
    types_list = get_all_types()
    affinities_raw = get_type_affinities()
    type_map = {t['id']: t['name'] for t in types_list}

    affinities = [
        {
            "attacking_type": type_map.get(a['attacking_type_id'], 'Unknown'),
            "defending_type": type_map.get(a['defending_type_id'], 'Unknown'),
            "multiplier": float(a['multiplier'])
        }
        for a in affinities_raw
    ]
    return affinities


affinities = load_types_and_affinities()

# Type icons and colors
TYPE_ICONS = {
    "feu": "", "eau": "", "plante": "", "electrik": "", "glace": "",
    "combat": "", "poison": "", "sol": "", "vol": "", "psy": "",
    "insecte": "", "roche": "", "spectre": "", "dragon": "", "tenebres": "",
    "acier": "", "fee": "", "normal": ""
}

TYPE_COLORS = {
    "feu": "#F08030", "eau": "#6890F0", "plante": "#78C850", "electrik": "#F8D030",
    "glace": "#98D8D8", "combat": "#C03028", "poison": "#A040A0", "sol": "#E0C068",
    "vol": "#A890F0", "psy": "#F85888", "insecte": "#A8B820", "roche": "#B8A038",
    "spectre": "#705898", "dragon": "#7038F8", "tenebres": "#705848", "acier": "#B8B8D0",
    "fee": "#EE99AC", "normal": "#A8A878"
}


# Helper functions


def normalize_type(name: str) -> str:
    """Normalize type names for mapping (remove accents, lowercase)."""
    return name.lower().replace("é", "e").replace("è", "e").replace("ê", "e")


def format_type_badge(type_name: str) -> str:
    """Return a colored HTML badge for a type name."""
    key = normalize_type(type_name)
    icon = TYPE_ICONS.get(key, "")
    color = TYPE_COLORS.get(key, "#999")
    return f"<span style='background:{color};color:white;padding:8px 16px;border-radius:12px;font-size:1.2rem;font-weight:600;display:inline-block;margin:4px;'>{icon} {type_name.capitalize()}</span>"


def generate_question() -> dict:
    """Select a random non-neutral type matchup as a question."""
    interesting = [a for a in affinities if a['multiplier'] != 1.0]
    q = random.choice(interesting)
    return {
        "attacking_type": q["attacking_type"],
        "defending_type": q["defending_type"],
        "correct_multiplier": q["multiplier"]
    }


def check_answer(user_choice: str, correct_multiplier: float) -> bool:
    """Return True if user_choice matches the correct multiplier category."""
    if correct_multiplier == 0:
        correct_category = "immune"
    elif correct_multiplier < 1:
        correct_category = "weak"
    elif correct_multiplier == 1:
        correct_category = "normal"
    else:
        correct_category = "strong"
    return user_choice == correct_category


def get_feedback_text(multiplier: float) -> str:
    """Return a descriptive feedback string for the given multiplier."""
    if multiplier == 0:
        return "**Immunisé (x0)** - Aucun dégât !"
    if multiplier < 1:
        return f"**Peu efficace (x{multiplier})** - Dégâts réduits"
    if multiplier == 1:
        return "**Normal (x1)** - Dégâts standards"
    return f"**Super efficace (x{multiplier})** - Dégâts augmentés !"


def handle_answer(user_choice: str):
    """Process the user's answer and update session state."""
    is_correct = check_answer(user_choice, st.session_state.current_question['correct_multiplier'])
    st.session_state.quiz_total += 1
    if is_correct:
        st.session_state.quiz_score += 1
    st.session_state.answered = True
    st.session_state.last_answer_correct = is_correct
    st.rerun()


def new_question():
    """Generate a new quiz question and reset answer state."""
    st.session_state.current_question = generate_question()
    st.session_state.answered = False
    st.session_state.last_answer_correct = None


# Page header
page_header("Quiz des Types Pokémon", "Teste tes connaissances sur les affinités de types !")
st.markdown("**Teste tes connaissances sur les affinités de types !**")

# Score display
col1, col2, col3 = st.columns(3)
col1.metric("Score Actuel", f"{st.session_state.quiz_score}/{st.session_state.quiz_total}")
accuracy = (st.session_state.quiz_score / st.session_state.quiz_total * 100) if st.session_state.quiz_total else 0
col2.metric("Précision", f"{accuracy:.0f}%")
col3.metric("Meilleur Score", f"{st.session_state.quiz_high_score}")
st.divider()

if st.session_state.current_question is None or st.session_state.answered:
    st.button("Nouvelle Question", type="primary", use_container_width=True, on_click=new_question)

# Display question
if st.session_state.current_question and not st.session_state.answered:
    q = st.session_state.current_question
    st.markdown(f"### Question #{st.session_state.quiz_total + 1}")
    st.markdown(
        f"<div style='text-align:center;padding:20px;background:#f0f2f6;border-radius:12px;margin:20px 0;'>"
        f"<p style='font-size:1.2rem;margin-bottom:20px;'>Une attaque</p>"
        f"{format_type_badge(q['attacking_type'])}"
        f"<p style='font-size:1.8rem;margin:20px 0;'>VS</p>"
        f"<p style='font-size:1.2rem;margin-bottom:20px;'>contre un Pokémon</p>"
        f"{format_type_badge(q['defending_type'])}</div>",
        unsafe_allow_html=True
    )

    st.markdown("### C'est...")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("Immunisé\n(x0)", key="immune", use_container_width=True, on_click=handle_answer, args=("immune",))
    with col2:
        st.button(
            "Peu efficace\n(x0.5)",
            key="weak",
            use_container_width=True,
            on_click=handle_answer,
            args=(
                "weak",
            ))
    with col3:
        st.button("Normal\n(x1)", key="normal", use_container_width=True, on_click=handle_answer, args=("normal",))
    with col4:
        st.button(
            "Super efficace\n(x2 ou x4)",
            key="strong",
            use_container_width=True,
            on_click=handle_answer,
            args=(
                "strong",
            ))

# Answer feedback
if st.session_state.answered and st.session_state.last_answer_correct is not None:
    q = st.session_state.current_question
    if st.session_state.last_answer_correct:
        st.success("**Bravo ! Bonne réponse !**")
        st.balloons()
    else:
        st.error("**Oups ! Mauvaise réponse...**")
        st.info(f"La bonne réponse était : {get_feedback_text(q['correct_multiplier'])}")

    if st.session_state.quiz_score > st.session_state.quiz_high_score:
        st.session_state.quiz_high_score = st.session_state.quiz_score
        st.success("**Nouveau record !**")

# Reset buttons
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.button("Recommencer à Zéro", use_container_width=True, on_click=lambda: [st.session_state.update(
        {k: 0 if "score" in k or "total" in k else None for k in st.session_state}), st.rerun()])
with col2:
    st.button("Réinitialiser Record", use_container_width=True, on_click=lambda: [
              st.session_state.update({"quiz_high_score": 0}), st.rerun()])

# Tips and statistics
with st.expander("Astuces pour réussir"):
    st.markdown("""
    ### Rappels importants :

    **Super efficace (x2 ou x4) :**
    - Feu > Plante, Glace, Insecte, Acier
    - Eau > Feu, Sol, Roche
    - Plante > Eau, Sol, Roche
    - Électrik > Eau, Vol

    **Peu efficace (x0.5) :**
    - Feu < Feu, Eau, Roche, Dragon
    - Eau < Eau, Plante, Dragon
    - Plante < Feu, Plante, Poison, Vol, Insecte, Dragon, Acier

    **Immunité (x0) :**
    - Normal < Spectre
    - Combat < Spectre
    - Spectre < Normal
    - Électrik < Sol
    - Poison < Acier
    - Sol < Vol
    - Psy < Ténèbres
    - Dragon < Fée
    """)

if st.session_state.quiz_total >= 5:
    with st.expander("Tes statistiques"):
        accuracy = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
        st.metric("Précision globale", f"{accuracy:.1f}%")
        st.metric("Questions répondues", st.session_state.quiz_total)
        st.metric("Bonnes réponses", st.session_state.quiz_score)
        st.metric("Mauvaises réponses", st.session_state.quiz_total - st.session_state.quiz_score)
        if accuracy >= 90:
            st.success("Expert des types ! Incroyable !")
        elif accuracy >= 75:
            st.info("Très bon ! Continue comme ça !")
        elif accuracy >= 60:
            st.warning("Pas mal ! Encore un peu d'entraînement !")
        else:
            st.error("Continue de t'entraîner, tu vas y arriver !")
