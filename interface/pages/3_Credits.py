# interface/pages/3_Credits.py
import streamlit as st

st.set_page_config(
    page_title="Credits – PredictionDex",
    page_icon="🏆",
    layout="centered",
)

st.title("🏆 Crédits et Informations du Projet")

# ======================================================
# Introduction
# ======================================================
st.markdown("""
Bienvenue sur **PredictionDex**, un projet pédagogique visant à explorer
l'univers de **Pokémon Let's Go** avec des outils de data science et d'IA.
""")

st.markdown("""
Ce projet a pour objectifs :
- Collecter et centraliser les données Pokémon (PokéAPI, Poképédia).
- Visualiser les capacités et les statistiques de chaque Pokémon.
- Simuler des combats et comparer les Pokémon à l'aide d'un modèle simple.
- Expérimenter avec **FastAPI**, **Streamlit**, **SQLAlchemy** et **MLOps**.
""")

# ======================================================
# Dépôt GitHub
# ======================================================
st.header("🔗 Dépôt GitHub")
st.markdown("""
Le code source complet du projet est disponible sur GitHub :  
[PredictionDex Repository](https://github.com/votre-utilisateur/predictiondex)

N'hésitez pas à :
- Consulter le code
- Suggérer des améliorations
- Reporter des bugs
- Forker le projet pour vos propres expérimentations
""")

# ======================================================
# Technologies utilisées
# ======================================================
st.header("💻 Technologies et Librairies")
st.markdown("""
- **Python 3.11+**
- **Streamlit** pour l'interface utilisateur
- **FastAPI** pour l'API REST
- **SQLAlchemy / PostgreSQL** pour la gestion des données
- **Requests / API client** pour l'accès aux données Pokémon
- **Pandas** pour le traitement et l'affichage tabulaire
- **Pydantic** pour les modèles et la validation
- **Docker / MLOps** pour la containerisation et l'automatisation
""")

# ======================================================
# Auteurs / Contributeurs
# ======================================================
st.header("👥 Auteurs et Contributeurs")
st.markdown("""
- **Benjamin [Nom]** – Développement principal, architecture et ML
- Collaborateurs : à compléter selon votre équipe
""")

# ======================================================
# Licence et usage
# ======================================================
st.header("📄 Licence & Utilisation")
st.markdown("""
Ce projet est destiné à un usage pédagogique et expérimental.  
Les données Pokémon utilisées proviennent de **PokéAPI** et sont utilisées
dans le respect de leurs conditions d'utilisation.
""")

# ======================================================
# Remerciements
# ======================================================
st.header("🙏 Remerciements")
st.markdown("""
Merci à :
- **PokéAPI** pour la fourniture des données Pokémon
- **Poképédia** pour les informations complémentaires
- La communauté Streamlit et FastAPI pour leur documentation et support
""")
