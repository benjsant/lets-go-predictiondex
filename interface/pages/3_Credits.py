# interface/pages/3_Credits.py
import streamlit as st
from utils.pokemon_theme import (
    load_custom_css,
    page_header,
    section_header,
    info_box,
    pokeball_divider,
    pikachu_eevee_mascots,
    POKEMON_COLORS
)

st.set_page_config(
    page_title="Credits – PredictionDex",
    page_icon="🏆",
    layout="wide",
)

# Load theme
load_custom_css()

# ======================================================
# Header
# ======================================================
page_header(
    "Crédits & Informations",
    "Découvre les technologies et données derrière PredictionDex",
    "🏆"
)

# ======================================================
# Introduction avec mascots
# ======================================================
pikachu_eevee_mascots()

info_box(
    "À Propos du Projet",
    """
    <strong>PredictionDex</strong> est un projet pédagogique qui combine l'univers
    de <strong>Pokémon Let's Go Pikachu/Eevee</strong> avec le Machine Learning et
    la data science moderne.
    <br><br>
    Ce projet démontre comment créer une application full-stack avec API REST,
    modèle ML, et interface utilisateur interactive pour prédire les combats Pokémon.
    """,
    "🎮",
    "info"
)

# ======================================================
# Objectifs du Projet
# ======================================================
section_header("Objectifs du Projet", "🎯")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Data Science
    - Collecter et centraliser les données Pokémon
    - Nettoyer et préparer un dataset de 34,040 combats
    - Entraîner un modèle XGBoost avec 94.24% de précision
    - Analyser 133 features pour chaque prédiction
    """)

with col2:
    st.markdown("""
    ### 💻 Développement
    - Architecture full-stack moderne
    - API REST avec FastAPI
    - Interface utilisateur avec Streamlit
    - Containerisation avec Docker
    - Base de données PostgreSQL
    """)

pokeball_divider()

# ======================================================
# Technologies utilisées
# ======================================================
section_header("Technologies & Librairies", "💻")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['primary']};'>
        <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>🐍 Backend</h4>
        <ul style='color:{POKEMON_COLORS['text_primary']};'>
            <li><strong>Python 3.11+</strong></li>
            <li><strong>FastAPI</strong> - API REST</li>
            <li><strong>SQLAlchemy</strong> - ORM</li>
            <li><strong>PostgreSQL</strong> - Base de données</li>
            <li><strong>Pydantic</strong> - Validation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['primary_alt']};'>
        <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>🤖 Machine Learning</h4>
        <ul style='color:{POKEMON_COLORS['text_primary']};'>
            <li><strong>XGBoost</strong> - Modèle ML</li>
            <li><strong>Scikit-learn</strong> - Preprocessing</li>
            <li><strong>Pandas</strong> - Data manipulation</li>
            <li><strong>NumPy</strong> - Calculs numériques</li>
            <li><strong>Joblib</strong> - Serialization</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['accent']};'>
        <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>🎨 Frontend</h4>
        <ul style='color:{POKEMON_COLORS['text_primary']};'>
            <li><strong>Streamlit</strong> - UI Framework</li>
            <li><strong>HTML/CSS</strong> - Styling custom</li>
            <li><strong>Requests</strong> - API client</li>
            <li><strong>Docker</strong> - Containerisation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

pokeball_divider()

# ======================================================
# Statistiques du Projet
# ======================================================
section_header("Statistiques du Projet", "📈")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎮 Pokémon", "188", help="Tous les Pokémon de Kanto + formes Alola")
with col2:
    st.metric("💥 Capacités", "226", help="Toutes les attaques disponibles")
with col3:
    st.metric("⚔️ Combats simulés", "34,040", help="Dataset d'entraînement ML")
with col4:
    st.metric("✅ Précision", "94.24%", help="Accuracy du modèle XGBoost")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔢 Features", "133", help="Variables analysées par le modèle")
with col2:
    st.metric("⚡ Latence", "<500ms", help="Temps de réponse de l'API")
with col3:
    st.metric("🌈 Types", "18", help="Types élémentaires Pokémon")
with col4:
    st.metric("🎯 Affinités", "324", help="Combinaisons de types (18×18)")

pokeball_divider()

# ======================================================
# Sources de Données
# ======================================================
section_header("Sources de Données", "🔗")

info_box(
    "PokéAPI",
    """
    <strong>PokéAPI</strong> est une API RESTful complète et gratuite pour les données Pokémon.
    <br><br>
    🔗 <a href='https://pokeapi.co' target='_blank' style='color:#3B4CCA;'>https://pokeapi.co</a>
    <br><br>
    Toutes les statistiques, types, capacités et sprites proviennent de cette source.
    """,
    "📡",
    "info"
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border:2px solid {POKEMON_COLORS['primary']};'>
        <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>📚 Données collectées</h4>
        <ul style='color:{POKEMON_COLORS['text_primary']};'>
            <li>Statistiques de base (HP, Attaque, Défense, etc.)</li>
            <li>Types primaires et secondaires</li>
            <li>Movesets (capacités apprises)</li>
            <li>Sprites officiels</li>
            <li>Affinités de types</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border:2px solid {POKEMON_COLORS['primary_alt']};'>
        <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>⚙️ Traitements appliqués</h4>
        <ul style='color:{POKEMON_COLORS['text_primary']};'>
            <li>Normalisation des noms (français)</li>
            <li>Calcul des dégâts avec formule Let's Go</li>
            <li>Génération de features ML</li>
            <li>Simulation de 34,040 combats</li>
            <li>Entraînement XGBoost</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

pokeball_divider()

# ======================================================
# Architecture du Projet
# ======================================================
section_header("Architecture Technique", "🏗️")

st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_secondary']};padding:25px;border-radius:12px;'>
    <div style='text-align:center;'>
        <h3 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>Stack Full-Stack</h3>
        <div style='display:flex;justify-content:center;align-items:center;gap:30px;margin:20px 0;flex-wrap:wrap;'>
            <div style='background:{POKEMON_COLORS['bg_card']};padding:15px 25px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.1);'>
                <div style='font-size:2rem;'>🎨</div>
                <strong style='color:{POKEMON_COLORS['primary']};'>Streamlit UI</strong>
            </div>
            <div style='font-size:2rem;color:{POKEMON_COLORS['text_secondary']};'>→</div>
            <div style='background:{POKEMON_COLORS['bg_card']};padding:15px 25px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.1);'>
                <div style='font-size:2rem;'>⚡</div>
                <strong style='color:{POKEMON_COLORS['accent']};'>FastAPI</strong>
            </div>
            <div style='font-size:2rem;color:{POKEMON_COLORS['text_secondary']};'>→</div>
            <div style='background:{POKEMON_COLORS['bg_card']};padding:15px 25px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.1);'>
                <div style='font-size:2rem;'>🗄️</div>
                <strong style='color:{POKEMON_COLORS['secondary']};'>PostgreSQL</strong>
            </div>
        </div>
        <div style='margin-top:20px;'>
            <div style='background:{POKEMON_COLORS['bg_card']};padding:15px 25px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.1);display:inline-block;'>
                <div style='font-size:2rem;'>🤖</div>
                <strong style='color:{POKEMON_COLORS['primary_alt']};'>XGBoost Model</strong>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

pokeball_divider()

# ======================================================
# Auteurs
# ======================================================
section_header("Auteurs & Contributeurs", "👥")

info_box(
    "Développement Principal",
    """
    Ce projet a été développé dans le cadre d'un apprentissage des technologies
    web modernes, du Machine Learning et de l'architecture full-stack.
    <br><br>
    <strong>🎯 Objectif pédagogique:</strong> Démontrer l'intégration d'un modèle ML
    dans une application web production-ready avec Docker, API REST et interface utilisateur moderne.
    """,
    "💡",
    "success"
)

pokeball_divider()

# ======================================================
# Licence et Utilisation
# ======================================================
section_header("Licence & Utilisation", "📄")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['info']};'>
        <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>⚖️ Usage Pédagogique</h4>
        <p style='color:{POKEMON_COLORS['text_primary']};'>
        Ce projet est destiné à un usage <strong>pédagogique et expérimental</strong>.
        <br><br>
        Les données Pokémon proviennent de <strong>PokéAPI</strong> et sont utilisées
        dans le respect de leurs conditions d'utilisation.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['success']};'>
        <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>🎓 Open Source</h4>
        <p style='color:{POKEMON_COLORS['text_primary']};'>
        Le code source peut être consulté, forké et adapté pour
        vos propres projets d'apprentissage.
        <br><br>
        N'hésitez pas à expérimenter et à partager vos améliorations !
        </p>
    </div>
    """, unsafe_allow_html=True)

pokeball_divider()

# ======================================================
# Remerciements
# ======================================================
section_header("Remerciements", "🙏")

st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:30px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);'>
    <div style='text-align:center;'>
        <h3 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>Un grand merci à :</h3>
        <div style='margin:20px 0;color:{POKEMON_COLORS['text_primary']};line-height:2;'>
            <p><strong>📡 PokéAPI</strong> - Pour la fourniture gratuite des données Pokémon</p>
            <p><strong>🎨 Streamlit</strong> - Pour leur framework UI incroyable</p>
            <p><strong>⚡ FastAPI</strong> - Pour leur performance et simplicité</p>
            <p><strong>🤖 XGBoost</strong> - Pour leur algorithme ML puissant</p>
            <p><strong>🐳 Docker</strong> - Pour faciliter le déploiement</p>
            <p><strong>🎮 Game Freak & Nintendo</strong> - Pour l'univers Pokémon</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

pokeball_divider()

# ======================================================
# Footer
# ======================================================
st.markdown(f"""
<div style='text-align:center;color:{POKEMON_COLORS['text_secondary']};padding:30px 0;'>
    <p style='font-size:1.1rem;'><strong>⚡ PredictionDex</strong></p>
    <p style='font-size:0.95rem;'>
        Made with ❤️ pour les fans de Pokémon Let's Go Pikachu/Eevee
    </p>
    <p style='font-size:0.85rem;margin-top:15px;'>
        Données fournies par <a href='https://pokeapi.co' target='_blank' style='color:{POKEMON_COLORS['primary']};text-decoration:none;'>PokéAPI</a>
    </p>
</div>
""", unsafe_allow_html=True)
