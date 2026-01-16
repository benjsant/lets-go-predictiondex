#app/interface/pages/3_📜_Credits.py
import interface as st

st.set_page_config(
    page_title="Credits",
    page_icon="📜",
    layout="centered",
)

with st.sidebar:
    "[![GitHub](https://img.shields.io/badge/github-%23121011.svg?"
    "style=for-the-badge&logo=github&logoColor=white)]"
    "(https://github.com/Aurelien-L/AgentIA_TransitionEcologique.git)"

st.caption(
    "*Projet réalisé par Benjamin Santrisse. "
)
