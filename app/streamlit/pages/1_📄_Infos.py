import streamlit as st

st.set_page_config(
    page_title="Informations",
    page_icon="📄",
    layout="centered",
)

with st.sidebar:
    "[![GitHub](https://img.shields.io/badge/github-%23121011.svg?"
    "style=for-the-badge&logo=github&logoColor=white)]"
    "(https://github.com/Aurelien-L/AgentIA_TransitionEcologique.git)"

st.image("img/banner_bot.png", use_container_width=True)

st.header("Présentation")
st.write(
    "Ce projet à but pédagogique vise à concevoir un assistant conversationnel intelligent..."
)
