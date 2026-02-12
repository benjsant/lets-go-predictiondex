# interface/app.py
import streamlit as st
from interface.utils.pokemon_theme import (
    POKEMON_COLORS,
    feature_card,
    info_box,
    load_custom_css,
    page_header,
    pikachu_eevee_mascots,
    pokeball_divider,
    section_header,
)

st.set_page_config(
    page_title="Let's Go PredictionDex",
    layout="wide",
)

# Load custom Pokemon theme
load_custom_css()

# Page header with mascots
page_header(
    "Let's Go PredictionDex",
    "Ton assistant pour les combats Pokemon Let's Go !",
)

# Sprites Pikachu ET Évoli
pikachu_eevee_mascots()

info_box(
    "Bienvenue, Dresseur !",
    """
    Avec <strong>96.24% de precision</strong>, decouvre quelle capacite
    te donnera le plus de chances de gagner tes combats !
    <br><br>
    PredictionDex analyse <strong>133 features</strong> pour predire le resultat de chaque combat en moins de <strong>500ms</strong>.
    """,
    color="success"
)

# Features grid
section_header("Que peux-tu faire ?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        feature_card(
            "Comparer & Predire",
            "Compare deux Pokemon, choisis tes capacites, et decouvre laquelle utiliser pour maximiser tes chances de victoire !",
            "Compare",
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        feature_card(
            "Combat Classique",
            "Configure ton propre combat en choisissant les deux Pokemon et leurs capacites pour une simulation personnalisee !",
            "Combat Classique",
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        feature_card(
            "Quiz des Types",
            "Teste tes connaissances sur les affinites de types avec un quiz interactif et ameliore-toi tour apres tour !",
            "Quiz Types",
        ),
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        feature_card(
            "Capacites",
            "Catalogue complet des 226 capacites avec filtres par type, categorie et puissance. Explore toutes les attaques du jeu !",
            "Moves List",
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        feature_card(
            "Types",
            "Matrice complete des 18 types avec toutes les affinites (324 combinaisons). Maitrise les forces et faiblesses !",
            "Types",
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        feature_card(
            "Pokemon Detail",
            "Fiches detaillees des 188 Pokemon de Kanto avec stats, types, capacites et faiblesses !",
            "Pokemon Detail",
        ),
        unsafe_allow_html=True
    )

pokeball_divider()

# Quick start guide
with st.expander("Guide de Demarrage Rapide"):
    st.markdown("""
    ### Comment utiliser PredictionDex ?

    #### Pour predire un combat :

    1. Va dans **"Compare"** (menu a gauche)
    2. Choisis **ton Pokemon** et celui de **ton adversaire**
    3. Selectionne **jusqu'a 4 capacites** (pre-remplies avec des suggestions)
    4. Clique sur **"Predire"** pour voir quelle capacite utiliser !

    #### Pour explorer :

    - **Types** : Consulte la matrice des affinites de types (18x18)
    - **Moves List** : Parcours toutes les capacites avec filtres avances
    - **Pokemon Detail** : Fiches detaillees de chaque Pokemon
    - **Quiz Types** : Entraine-toi sur les affinites de types

    #### Pour s'amuser :

    - **Combat Classique** : Configure ton propre combat avec movesets personnalises
    - **Quiz Types** : Defie-toi avec des questions aleatoires sur les types

    **Astuce :** Le modele suppose que ton adversaire joue au mieux (worst-case scenario).
    Tes vraies chances peuvent etre encore meilleures si l'adversaire ne joue pas optimalement !
    """)

# How it works
with st.expander("Comment ca marche ?"):
    st.markdown("""
    ### Le modele de prediction

    PredictionDex utilise un **modele XGBoost** entraine sur
    **898,612 combats Pokemon** simules.

    **Ce que le modele analyse :**

    **Pour ton Pokemon :**
    - Statistiques de base (HP, Attaque, Defense, Att. Spe, Def. Spe, Vitesse)
    - Puissance et type de chaque capacite testee
    - STAB (Same Type Attack Bonus = x1.5)
    - Multiplicateur de type contre l'adversaire
    - Priorite de la capacite

    **Pour le Pokemon adverse :**
    - Statistiques de base
    - Types (pour calculer les faiblesses)
    - **Meilleure capacite offensive** selectionnee automatiquement
    - STAB et multiplicateur de type

    **Processus de prediction :**
    1. Pour chaque capacite de ton Pokemon
    2. Le modele selectionne la meilleure reponse de l'adversaire (worst-case)
    3. Il simule le combat avec ces deux capacites
    4. Il predit le vainqueur et la probabilite de victoire

    **Resultat :**
    - **96.24% de precision** (predit le bon gagnant 96 fois sur 100)
    - **Temps de reponse < 500ms**
    - **133 features analysees** pour chaque prediction
    """)

# Fun facts
with st.expander("Le savais-tu ?"):
    st.markdown("""
    ### Fun Facts Pokemon Let's Go

    **Contenu du jeu :**
    - **187 Pokemon** disponibles (Generation 1 de Kanto + formes Alola)
    - **225 capacites** differentes
    - **18 types** elementaires
    - **34,969 matchups** possibles entre Pokemon (187 x 187)
    - **323 regles de types** (18 x 18 affinites)

    **Le modele ML :**
    - Entraine sur **898,612 combats** simules
    - Analyse **133 features** differentes
    - Repond en moins de **500ms**
    - **96.24% de precision** sur les tests (v2)
    - Algorithme **XGBoost** optimise pour les combats

    **Statistique :** Avec toutes les combinaisons Pokemon x Capacites,
    il existe des **millions** de combats possibles differents !
    """)

pokeball_divider()

# Footer
st.markdown(f"""
<div style='text-align:center;color:{POKEMON_COLORS['text_secondary']};padding:30px 0;'>
    <p style='font-size:1.1rem;'><strong>Propulse par XGBoost</strong></p>
    <p style='font-size:0.95rem;'>
        Precision : <strong style='color:{POKEMON_COLORS['primary']};'>96.24%</strong> |
        Features : <strong style='color:{POKEMON_COLORS['primary']};'>133</strong> |
        Latence : <strong style='color:{POKEMON_COLORS['primary']};">&lt;500ms</strong>
    </p>
    <p style='font-size:0.9rem;margin-top:20px;'>
        Fait pour les fans de Pokemon Let's Go Pikachu/Eevee
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation hint
st.info("**Utilise le menu a gauche pour commencer ton aventure !**")
