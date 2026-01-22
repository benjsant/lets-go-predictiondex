# interface/app.py
import streamlit as st
import random
from utils.pokemon_theme import (
    load_custom_css,
    page_header,
    section_header,
    feature_card,
    info_box,
    pokeball_divider,
    pikachu_eevee_mascots,
    POKEMON_COLORS
)

st.set_page_config(
    page_title="Let's Go PredictionDex",
    page_icon="⚡",
    layout="wide",
)

# Load custom Pokemon theme
load_custom_css()

# ======================================================
# Header with Animation
# ======================================================
page_header(
    "Let's Go PredictionDex",
    "Ton assistant intelligent pour les combats Pokémon !",
    "⚡"
)

# Sprites Pikachu ET Évoli
pikachu_eevee_mascots()

# ======================================================
# Introduction
# ======================================================
info_box(
    "Bienvenue, Dresseur !",
    """
    Grâce à l'intelligence artificielle et à <strong>94.24% de précision</strong>, découvre quelle capacité
    te donnera le plus de chances de gagner tes combats !
    <br><br>
    PredictionDex analyse <strong>133 features</strong> pour prédire le résultat de chaque combat en moins de <strong>500ms</strong>.
    """,
    "🏆",
    "success"
)

# ======================================================
# Features Grid
# ======================================================
section_header("Que peux-tu faire ?", "🎯")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        feature_card(
            "Comparer & Prédire",
            "Compare deux Pokémon, choisis tes capacités, et découvre laquelle utiliser pour maximiser tes chances de victoire !",
            "Compare",
            "⚔️"
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        feature_card(
            "Combat Classique",
            "Configure ton propre combat en choisissant les deux Pokémon et leurs capacités pour une simulation personnalisée !",
            "Combat Classique",
            "🥊"
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        feature_card(
            "Quiz des Types",
            "Teste tes connaissances sur les affinités de types avec un quiz interactif et améliore-toi tour après tour !",
            "Quiz Types",
            "🎯"
        ),
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        feature_card(
            "Capacités",
            "Catalogue complet des 226 capacités avec filtres par type, catégorie et puissance. Explore toutes les attaques du jeu !",
            "Moves List",
            "💥"
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        feature_card(
            "Types",
            "Matrice complète des 18 types avec toutes les affinités (324 combinaisons). Maîtrise les forces et faiblesses !",
            "Types",
            "🌈"
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        feature_card(
            "Pokémon Detail",
            "Fiches détaillées des 188 Pokémon de Kanto avec stats, types, capacités et faiblesses !",
            "Pokemon Detail",
            "🔍"
        ),
        unsafe_allow_html=True
    )

pokeball_divider()

# ======================================================
# Quick Start Guide
# ======================================================
with st.expander("📖 Guide de Démarrage Rapide"):
    st.markdown("""
    ### 🚀 Comment utiliser PredictionDex ?

    #### 1️⃣ Pour prédire un combat:

    1. Va dans **"Compare"** (menu à gauche)
    2. Choisis **ton Pokémon** et celui de **ton adversaire**
    3. Sélectionne **jusqu'à 4 capacités** (pré-remplies avec des suggestions)
    4. Clique sur **"Prédire"** pour voir quelle capacité utiliser !

    #### 2️⃣ Pour explorer:

    - **Types**: Consulte la matrice des affinités de types (18×18)
    - **Moves List**: Parcours toutes les capacités avec filtres avancés
    - **Pokemon Detail**: Fiches détaillées de chaque Pokémon
    - **Quiz Types**: Entraîne-toi sur les affinités de types

    #### 3️⃣ Pour s'amuser:

    - **Combat Classique**: Configure ton propre combat avec movesets personnalisés
    - **Quiz Types**: Défie-toi avec des questions aléatoires sur les types

    💡 **Astuce:** Le modèle suppose que ton adversaire joue au mieux (worst-case scenario).
    Tes vraies chances peuvent être encore meilleures si l'adversaire ne joue pas optimalement !
    """)

# ======================================================
# How It Works
# ======================================================
with st.expander("🤖 Comment ça marche ?"):
    st.markdown("""
    ### 🧠 La Magie de l'Intelligence Artificielle

    PredictionDex utilise un **modèle de Machine Learning XGBoost** entraîné sur
    **34,040 combats Pokémon** simulés !

    **Ce que le modèle analyse :**

    **Pour ton Pokémon :**
    - 📊 Statistiques de base (HP, Attaque, Défense, Att. Spé, Déf. Spé, Vitesse)
    - 💥 Puissance et type de chaque capacité testée
    - ⚡ STAB (Same Type Attack Bonus = ×1.5)
    - 🎯 Multiplicateur de type contre l'adversaire
    - ⚠️ Priorité de la capacité

    **Pour le Pokémon adverse :**
    - 📊 Statistiques de base
    - 🛡️ Types (pour calculer les faiblesses)
    - 💥 **Meilleure capacité offensive** sélectionnée automatiquement
    - ⚡ STAB et multiplicateur de type

    **Processus de prédiction :**
    1. Pour chaque capacité de ton Pokémon
    2. Le modèle sélectionne la meilleure réponse de l'adversaire (worst-case)
    3. Il simule le combat avec ces deux capacités
    4. Il prédit le vainqueur et la probabilité de victoire

    **Résultat:**
    - ✅ **94.24% de précision** (prédit le bon gagnant 94 fois sur 100 !)
    - ⚡ **Temps de réponse < 500ms** (ultra-rapide !)
    - 🎯 **133 features analysées** pour chaque prédiction

    **🚀 Version 2 en développement :**
    - Possibilité de spécifier les 4 capacités exactes de l'adversaire
    - Simulation de combat plus réaliste avec movesets fixes
    """)

# ======================================================
# Fun Facts
# ======================================================
with st.expander("🎮 Le savais-tu ?"):
    st.markdown("""
    ### 💎 Fun Facts Pokémon Let's Go:

    **Contenu du jeu :**
    - 📚 **188 Pokémon** disponibles (Génération 1 de Kanto + formes Alola)
    - 💥 **226 capacités** différentes
    - 🌈 **18 types** élémentaires
    - ⚔️ **35,344 matchups** possibles entre Pokémon (188 × 188)
    - 🎯 **324 règles de types** (18 × 18 affinités)

    **Notre modèle ML :**
    - 🤖 Entraîné sur **34,040 combats** simulés
    - 📊 Analyse **133 features** différentes
    - ⚡ Répond en moins de **500ms**
    - ✅ **94.24% de précision** sur les tests
    - 🧠 Algorithme **XGBoost** optimisé pour les combats

    💡 **Statistique folle:** Avec toutes les combinaisons Pokémon × Capacités,
    il existe des **millions** de combats possibles différents !

    🎯 **Capacités les plus puissantes:**
    - Poing-Éclair : 150 de puissance
    - Ultralaser : 150 de puissance
    - Psyko : 140 de puissance (Spécial)
    """)

# ======================================================
# Version Info
# ======================================================
info_box(
    "🚀 Version 2 en développement",
    """
    La prochaine version permettra de spécifier les capacités exactes de l'adversaire
    pour des simulations encore plus précises et réalistes !
    <br><br>
    Reste connecté pour les nouvelles fonctionnalités.
    """,
    "🔮",
    "info"
)

pokeball_divider()

# ======================================================
# Footer
# ======================================================
st.markdown(f"""
<div style='text-align:center;color:{POKEMON_COLORS['text_secondary']};padding:30px 0;'>
    <p style='font-size:1.1rem;'><strong>🤖 Propulsé par XGBoost</strong></p>
    <p style='font-size:0.95rem;'>
        ⚡ Précision: <strong style='color:{POKEMON_COLORS['primary']};'>94.24%</strong> |
        Features: <strong style='color:{POKEMON_COLORS['primary']};'>133</strong> |
        Latence: <strong style='color:{POKEMON_COLORS['primary']};">&lt;500ms</strong>
    </p>
    <p style='font-size:0.9rem;margin-top:20px;'>
        Made with ❤️ pour les fans de Pokémon Let's Go Pikachu/Eevee
    </p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# Navigation Hint
# ======================================================
st.info("👈 **Utilise le menu à gauche pour commencer ton aventure !**")
