# interface/pages/3_Credits.py
import streamlit as st
from utils.pokemon_theme import (
    POKEMON_COLORS,
    info_box,
    load_custom_css,
    page_header,
    pikachu_eevee_mascots,
    pokeball_divider,
    section_header,
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
    - Nettoyer et préparer un dataset de 898,612 combats
    - Entraîner un modèle XGBoost avec 96.24% de précision
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
    st.metric("🎮 Pokémon", "187", help="Tous les Pokémon de Kanto + formes Alola")
with col2:
    st.metric("💥 Capacités", "225", help="Toutes les attaques disponibles")
with col3:
    st.metric("⚔️ Combats simulés", "898,612", help="Dataset d'entraînement ML")
with col4:
    st.metric("✅ Précision", "96.24%", help="Accuracy du modèle XGBoost")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔢 Features", "133", help="Variables analysées par le modèle")
with col2:
    st.metric("⚡ Latence", "<500ms", help="Temps de réponse de l'API")
with col3:
    st.metric("🌈 Types", "18", help="Types élémentaires Pokémon")
with col4:
    st.metric("🎯 Affinités", "323", help="Combinaisons de types (18×18 - certaines neutres)")

pokeball_divider()

# ======================================================
# Sources de Données
# ======================================================
section_header("Sources de Données", "🔗")

col_src1, col_src2 = st.columns(2)

with col_src1:
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

with col_src2:
    info_box(
        "Pokepedia",
        """
        <strong>Pokepedia</strong> est une encyclopédie collaborative Pokémon sous licence Creative Commons CC-BY-SA.
        <br><br>
        🔗 <a href='https://www.pokepedia.fr' target='_blank' style='color:#3B4CCA;'>https://www.pokepedia.fr</a>
        <br><br>
        Données complémentaires et informations détaillées sur les capacités Let's Go.
        """,
        "📚",
        "info"
    )

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border:2px solid {POKEMON_COLORS['primary']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>📚 Pipeline ETL - 3 Sources</h4>
    <ul style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;list-style-position:outside;padding-left:20px;'>
        <li style='margin-bottom:16px;'>
            <strong>Source 1 : CSV manuels</strong>
            <ul style='list-style-type:none;padding-left:0;margin-top:6px;'>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– 187 Pokémon : noms (FR/EN), types, formes (Alola, Mega)</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– 225 capacités : noms, type, puissance, précision, PP</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– 323 affinités de types : multiplicateurs de dégâts</li>
            </ul>
        </li>
        <li style='margin-bottom:16px;'>
            <strong>Source 2 : PokéAPI REST</strong>
            <ul style='list-style-type:none;padding-left:0;margin-top:6px;'>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>Enrichissement automatique via appels HTTP GET</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– Statistiques de combat : HP, Attaque, Défense, Vitesse</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– Sprites PNG des Pokémon</li>
            </ul>
        </li>
        <li style='margin-bottom:0;'>
            <strong>Source 3 : Web Scraping Pokepedia</strong>
            <ul style='list-style-type:none;padding-left:0;margin-top:6px;'>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>Scrapy spider pour détails capacités Let's Go</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– Puissance, précision, PP, descriptions françaises</li>
            </ul>
        </li>
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
        <li>Simulation de 898,612 combats</li>
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
# Auteurs & Code Source
# ======================================================
section_header("Auteurs & Code Source", "👥")

info_box(
    "Développement Principal",
    """
    Ce projet a été développé dans le cadre d'un apprentissage des technologies
    web modernes, du Machine Learning et de l'architecture full-stack.
    <br><br>
    <strong>🎯 Objectif pédagogique:</strong> Démontrer l'intégration d'un modèle ML
    dans une application web production-ready avec Docker, API REST et interface utilisateur moderne.
    <br><br>
    📂 <strong>Code Source:</strong> <a href='https://github.com/benjsant/lets-go-predictiondex' target='_blank' style='color:#3B4CCA;'>github.com/benjsant/lets-go-predictiondex</a>
    """,
    "💡",
    "success"
)

pokeball_divider()

# ======================================================
# Protection des Données (RGPD)
# ======================================================
section_header("Protection des Données & RGPD", "🔒")

info_box(
    "Conformité RGPD",
    """
    <strong>PredictionDex est conforme au Règlement Général sur la Protection des Données (RGPD)</strong>
    car il ne collecte <strong>AUCUNE donnée personnelle</strong>.
    <br><br>
    ✅ <strong>Aucun compte utilisateur</strong> requis<br>
    ✅ <strong>Aucune donnée personnelle</strong> collectée (nom, email, adresse, etc.)<br>
    ✅ <strong>Aucun cookie de tracking</strong> ou publicité<br>
    ✅ <strong>Aucune identification</strong> des utilisateurs<br>
    ✅ <strong>Pas de revente de données</strong> - car il n'y en a pas !
    """,
    "🔒",
    "success"
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['success']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>📊 Données stockées</h4>
    <ul style='color:{POKEMON_COLORS['text_primary']};'>
        <li><strong>Base de données PostgreSQL</strong> : Uniquement données Pokémon (stats, types, capacités)</li>
        <li><strong>Aucune table utilisateur</strong> : Pas de comptes, pas d'historique personnel</li>
        <li><strong>Données de jeu uniquement</strong> : Issues de PokéAPI et Pokepedia</li>
    </ul>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['info']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>📈 Métriques techniques</h4>
    <ul style='color:{POKEMON_COLORS['text_primary']};'>
        <li><strong>Prometheus</strong> : Métriques agrégées (latence, nombre de requêtes)</li>
        <li><strong>Pas d'IP collectées</strong> : Aucune identification possible</li>
        <li><strong>Session locale</strong> : Streamlit utilise une session volatile (score quiz, sélections UI)</li>
        <li><strong>Données anonymes</strong> : Aucune possibilité de relier à une personne</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border:2px solid {POKEMON_COLORS['primary']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>🛡️ Engagement de confidentialité</h4>
    <p style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;'>
        Ce projet pédagogique <strong>ne collecte, ne stocke et ne traite aucune donnée personnelle</strong>.
        L'application fonctionne entièrement sans identification des utilisateurs.
    </p>
    <p style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;'>
        Les seules données présentes dans le système sont des <strong>statistiques de jeu Pokémon</strong>
        (HP, Attaque, Défense, etc.) et des <strong>métriques techniques agrégées</strong> pour le monitoring
        (nombre de requêtes API, temps de réponse).
    </p>
    <p style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;'>
        <strong>Aucune donnée à caractère personnel</strong> au sens de l'article 4 du RGPD n'est collectée.
        Le projet est donc <strong>naturellement conforme au RGPD</strong> par absence de traitement
        de données personnelles.
    </p>
</div>
""", unsafe_allow_html=True)

pokeball_divider()

# ======================================================
# Propriété Intellectuelle & Disclaimer
# ======================================================
section_header("Propriété Intellectuelle & Droits d'Auteur", "⚖️")

st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:25px;border-radius:12px;border:2px solid {POKEMON_COLORS['warning']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>⚠️ Disclaimer Juridique</h4>
    <p style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;'>
        <strong>Pokémon</strong> et tous les noms de personnages Pokémon sont des <strong>marques déposées</strong> de
        <strong>Nintendo</strong>, <strong>Creatures Inc.</strong> et <strong>GAME FREAK Inc.</strong>
    </p>
    <p style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;'>
        © 1995–2026 Nintendo / Creatures Inc. / GAME FREAK Inc.
    </p>
    <p style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;'>
        Ce projet est un <strong>projet pédagogique à but non lucratif</strong> développé dans le cadre d'une
        <strong>certification RNCP Concepteur Développeur d'Applications</strong> (Niveau 6).
    </p>
    <p style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;'>
        <strong>Usage éducatif protégé :</strong> Ce projet bénéficie de l'<strong>exception pédagogique</strong>
        (article L122-5 du Code de la Propriété Intellectuelle, loi DADVSI du 1er août 2006) qui autorise
        l'utilisation d'extraits d'œuvres à des fins exclusives d'illustration dans le cadre de l'enseignement
        et de la recherche.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['info']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>📚 Sources de Données Tierces</h4>
    <ul style='color:{POKEMON_COLORS['text_primary']};line-height:1.8;list-style-position:outside;padding-left:20px;'>
        <li style='margin-bottom:16px;'>
            <strong>1. CSV manuels (3 fichiers)</strong>
            <ul style='list-style-type:none;padding-left:0;margin-top:6px;'>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– 225 capacités + 187 Pokémon + 323 affinités de types</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– Compilés depuis sources communautaires Pokémon</li>
            </ul>
        </li>
        <li style='margin-bottom:16px;'>
            <strong>2. PokéAPI</strong> (pokeapi.co)
            <ul style='list-style-type:none;padding-left:0;margin-top:6px;'>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>API RESTful open-source (non affiliée à Nintendo)</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– Statistiques de combat : HP, Attaque, Défense, Vitesse</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– Sprites et images des Pokémon</li>
            </ul>
        </li>
        <li style='margin-bottom:0;'>
            <strong>3. Pokepedia</strong> (pokepedia.fr)
            <ul style='list-style-type:none;padding-left:0;margin-top:6px;'>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>Web scraping (Scrapy) – Licence CC-BY-SA</li>
                <li style='color:{POKEMON_COLORS['text_secondary']};font-size:0.85rem;line-height:1.6;'>– Détails capacités : puissance, précision, PP</li>
            </ul>
        </li>
    </ul>
    <p style='color:{POKEMON_COLORS['text_secondary']};font-size:0.9rem;margin-top:12px;'>
        <strong>⚖️ Conformité :</strong> Statistiques de jeu publiques utilisées dans un cadre strictement pédagogique.
    </p>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['success']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>🎓 Cadre Pédagogique</h4>
    <ul style='color:{POKEMON_COLORS['text_primary']};'>
        <li><strong>Objectif :</strong> Démonstration de compétences techniques (data science, ML, API)</li>
        <li><strong>Public :</strong> Jury de certification RNCP, formateurs, étudiants</li>
        <li><strong>Usage :</strong> Non-commercial, exclusivement éducatif</li>
        <li><strong>Certification :</strong> RNCP Niveau 6 "Concepteur Développeur d'Applications"</li>
    </ul>
    <p style='color:{POKEMON_COLORS['text_secondary']};font-size:0.9rem;margin-top:10px;'>
        Aucune exploitation commerciale, aucune revente, aucun profit généré.
    </p>
</div>
""", unsafe_allow_html=True)

pokeball_divider()

# ======================================================
# Licence et Utilisation
# ======================================================
section_header("Licence du Code Source", "📄")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
<div style='background:{POKEMON_COLORS['bg_card']};padding:20px;border-radius:12px;border-left:4px solid {POKEMON_COLORS['info']};'>
    <h4 style='color:{POKEMON_COLORS['secondary']};margin-top:0;'>⚖️ Usage Pédagogique</h4>
    <p style='color:{POKEMON_COLORS['text_primary']};'>
        Ce projet est destiné à un usage <strong>pédagogique et expérimental</strong>.
    </p>
    <p style='color:{POKEMON_COLORS['text_primary']};'>
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
    </p>
    <p style='color:{POKEMON_COLORS['text_primary']};'>
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
            <p><strong>📡 PokéAPI</strong> - API REST gratuite pour les données Pokémon</p>
            <p><strong>📚 Pokepedia</strong> - Encyclopédie collaborative (licence CC-BY-SA)</p>
            <p><strong>🎨 Streamlit</strong> - Framework UI incroyable</p>
            <p><strong>⚡ FastAPI</strong> - Performance et simplicité</p>
            <p><strong>🤖 XGBoost</strong> - Algorithme ML puissant</p>
            <p><strong>🐳 Docker</strong> - Facilitation du déploiement</p>
            <p><strong>🎮 Game Freak & Nintendo</strong> - Univers Pokémon</p>
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
        Données fournies par <a href='https://pokeapi.co' target='_blank' style='color:{POKEMON_COLORS['primary']};text-decoration:none;'>PokéAPI</a> et <a href='https://www.pokepedia.fr' target='_blank' style='color:{POKEMON_COLORS['primary']};text-decoration:none;'>Pokepedia</a>
    </p>
    <p style='font-size:0.85rem;'>
        🔗 <a href='https://github.com/benjsant/lets-go-predictiondex' target='_blank' style='color:{POKEMON_COLORS['primary']};text-decoration:none;'>Code source sur GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
