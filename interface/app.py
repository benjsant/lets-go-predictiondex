# /interface/app.py
import streamlit as st

st.set_page_config(
    page_title="PredictionDex",
    page_icon="⚡",
    layout="wide",
)

st.title("Pokémon Let's Go – PredictionDex")

st.markdown("""
Bienvenue sur **PredictionDex**.

👉 Utilise le menu à gauche :
- **Moves** : consulter les capacités d’un Pokémon
- **Comparaison** : choisir 4 moves et prédire le meilleur contre un adversaire
""")
