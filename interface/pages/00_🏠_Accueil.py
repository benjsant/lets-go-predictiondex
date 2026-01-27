"""
Page d'accueil - Présentation du projet PredictionDex
"""

import streamlit as st
import requests
from interface.config.settings import API_BASE_URL, API_KEY

st.set_page_config(
    page_title="PredictionDex - Accueil",
    page_icon="🏠",
    layout="wide"
)

# Header
st.title("🎮 Pokémon Let's Go - PredictionDex")
st.markdown("### Assistant IA pour les combats Pokémon")

st.markdown("---")

# Introduction
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## 🎯 À propos du projet
    
    **PredictionDex** est une application d'intelligence artificielle qui aide les enfants 
    à choisir le meilleur mouvement durant leurs combats Pokémon Let's Go.
    
    ### ✨ Fonctionnalités principales
    
    - 🤖 **Prédiction ML** : Modèle XGBoost entraîné sur 718,889 combats (94.24% de précision)
    - 📊 **Base de données** : 151 Pokémon de la 1ère génération avec stats complètes
    - ⚔️ **Recommandation** : Calcul du meilleur mouvement basé sur types, stats et STAB
    - 📈 **Monitoring** : Surveillance en temps réel via Prometheus & Grafana
    - 🔒 **Sécurité** : API protégée par clés API avec authentification SHA-256
    """)

with col2:
    st.info("""
    **🏆 Métriques du modèle**
    
    - Précision : **94.24%**
    - Features : **133**
    - Scénarios : **3**
    - Combats : **718,889**
    """)

st.markdown("---")

# Services disponibles
st.markdown("## 🌐 Services & Outils")

# Ligne 1 : Services principaux
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Monitoring")
    st.markdown("""
    **Grafana Dashboard**
    - Métriques temps réel
    - Performance API
    - Santé des services
    
    [🔗 Ouvrir Grafana](http://localhost:3001)
    
    *Credentials: admin / admin*
    """)
    
with col2:
    st.markdown("### 🧪 API Testing")
    st.markdown("""
    **Swagger UI**
    - Documentation interactive
    - Test des endpoints
    - Schémas OpenAPI
    
    [🔗 Voir la documentation](http://localhost:8502/📚_API_Documentation)
    """)

with col3:
    st.markdown("### 🎯 ML Tracking")
    st.markdown("""
    **MLflow**
    - Expériences ML
    - Métriques d'entraînement
    - Registre de modèles
    
    [🔗 Ouvrir MLflow](http://localhost:5001)
    """)

st.markdown("---")

# Ligne 2 : Outils techniques
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📈 Métriques brutes")
    st.markdown("""
    **Prometheus**
    - Collecte de métriques
    - Historique des données
    - Alertes configurables
    
    [🔗 Ouvrir Prometheus](http://localhost:9091)
    """)

with col2:
    st.markdown("### 🗄️ Base de données")
    st.markdown("""
    **PostgreSQL**
    - 151 Pokémon Gen 1
    - Moves complets
    - Types & affinités
    
    *Port: 5432 (interne)*
    """)

with col3:
    st.markdown("### 🔐 Sécurité")
    st.markdown("""
    **API Keys**
    - Authentification SHA-256
    - 3 clés configurées
    - Rate limiting (Traefik)
    
    *Voir `.env` pour les clés*
    """)

st.markdown("---")

# État des services
st.markdown("## 🔧 État des services")

col1, col2, col3, col4 = st.columns(4)

# Check API
with col1:
    try:
        headers = {"X-API-Key": API_KEY} if API_KEY else {}
        response = requests.get(f"{API_BASE_URL}/health", headers=headers, timeout=5)
        if response.status_code == 200:
            st.success("✅ **API**\nOpérationnelle")
        else:
            st.error("❌ **API**\nErreur")
    except Exception:
        st.error("❌ **API**\nHors ligne")

# Check Grafana
with col2:
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ **Grafana**\nOpérationnel")
        else:
            st.warning("⚠️ **Grafana**\nProblème")
    except Exception:
        st.error("❌ **Grafana**\nHors ligne")

# Check MLflow
with col3:
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ **MLflow**\nOpérationnel")
        else:
            st.warning("⚠️ **MLflow**\nProblème")
    except Exception:
        st.error("❌ **MLflow**\nHors ligne")

# Check Prometheus
with col4:
    try:
        response = requests.get("http://localhost:9091/-/healthy", timeout=5)
        if response.status_code == 200:
            st.success("✅ **Prometheus**\nOpérationnel")
        else:
            st.warning("⚠️ **Prometheus**\nProblème")
    except Exception:
        st.error("❌ **Prometheus**\nHors ligne")

st.markdown("---")

# Quick start
st.markdown("## 🚀 Démarrage rapide")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 1️⃣ Utiliser l'interface
    
    Naviguez dans le menu de gauche pour :
    - **Prédiction ML** : Obtenir la meilleure attaque
    - **Explorer Pokémon** : Consulter les stats
    - **Gestion des types** : Voir les affinités
    - **Mouvements** : Rechercher des attaques
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Consulter les métriques
    
    Surveillez votre application :
    - **Grafana** : Tableaux de bord visuels
    - **Prometheus** : Métriques détaillées
    - **MLflow** : Performances du modèle
    - **Swagger** : Tester l'API
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>PredictionDex v2.0</strong> - Projet Python IA</p>
    <p>Architecture : FastAPI + Streamlit + PostgreSQL + XGBoost + MLflow</p>
    <p>Monitoring : Prometheus + Grafana | Sécurité : API Keys + Docker Network Isolation</p>
</div>
""", unsafe_allow_html=True)
