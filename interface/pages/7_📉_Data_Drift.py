# interface/pages/7_📉_Data_Drift.py
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
from utils.pokemon_theme import (
    POKEMON_COLORS,
    info_box,
    load_custom_css,
    page_header,
    section_header,
    pokeball_divider,
)

st.set_page_config(
    page_title="Data Drift – PredictionDex",
    page_icon="📉",
    layout="wide",
)

# Load theme
load_custom_css()

# ======================================================
# Header
# ======================================================
page_header(
    "Data Drift Detection",
    "Surveille les dérives de distribution des données en production",
    "📉"
)

# ======================================================
# Explication du Data Drift
# ======================================================
info_box(
    "Qu'est-ce que le Data Drift ?",
    """
    Le <strong>Data Drift</strong> se produit quand les données en production <strong>dérivent</strong>
    des données d'entraînement du modèle. Cela peut causer une <strong>dégradation des performances</strong>.
    <br><br>
    <strong>Evidently AI</strong> génère automatiquement des rapports toutes les heures ou après 1000 prédictions
    pour détecter ces changements de distribution.
    """,
    "⚠️",
    "info"
)

pokeball_divider()

# ======================================================
# Recherche des rapports
# ======================================================
drift_reports_dir = Path("/app/drift_reports")

# Check if directory exists and is accessible
if not drift_reports_dir.exists():
    st.warning("📂 Le dossier des rapports Evidently n'existe pas encore.")
    st.info("""
    **Comment générer des rapports ?**

    Les rapports sont générés automatiquement après:
    - 1000 prédictions via l'API
    - OU toutes les 1 heures

    Pour générer des données de test:
    ```bash
    python3 scripts/populate_monitoring.py
    ```
    """)
    st.stop()

# Lister tous les rapports HTML
html_reports = sorted(drift_reports_dir.glob("drift_dashboard_*.html"), reverse=True)
json_summaries = sorted(drift_reports_dir.glob("drift_summary_*.json"), reverse=True)

if not html_reports:
    st.warning("📊 Aucun rapport Evidently trouvé.")
    st.info("""
    **Les rapports seront générés automatiquement** dès que l'API aura collecté suffisamment de prédictions.

    **Pour accélérer** la génération de rapports:
    ```bash
    python3 scripts/populate_monitoring.py
    ```

    Cela génère 50 prédictions et devrait déclencher la création de rapports Evidently.
    """)
    st.stop()

# ======================================================
# Métriques du dernier rapport
# ======================================================
section_header("Vue d'Ensemble", "📊")

if json_summaries:
    # Charger le dernier rapport JSON
    latest_summary = json_summaries[0]
    try:
        with open(latest_summary, 'r') as f:
            summary_data = json.load(f)

        # Extraire les métriques
        timestamp_str = summary_data.get('timestamp', 'N/A')
        n_features = summary_data.get('n_features', 0)
        n_drifted = summary_data.get('n_drifted_features', 0)
        drift_pct = summary_data.get('share_drifted_features', 0) * 100
        dataset_drift = summary_data.get('dataset_drift', False)

        # Parse timestamp
        try:
            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            date_str = dt.strftime("%d/%m/%Y à %H:%M:%S")
        except:
            date_str = timestamp_str

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="📅 Dernier Rapport",
                value=date_str.split(' à ')[0],
                delta=date_str.split(' à ')[1] if ' à ' in date_str else None
            )

        with col2:
            st.metric(
                label="🎯 Features Analysées",
                value=f"{n_features}"
            )

        with col3:
            # Déterminer la couleur selon le drift
            drift_status = "🟢 Stable" if drift_pct < 20 else ("🟡 Attention" if drift_pct < 30 else "🔴 Critique")
            st.metric(
                label="📉 Features avec Drift",
                value=f"{n_drifted} ({drift_pct:.1f}%)",
                delta=drift_status,
                delta_color="inverse" if drift_pct > 30 else ("off" if drift_pct < 20 else "normal")
            )

        with col4:
            alert_emoji = "🔴" if dataset_drift else "✅"
            alert_text = "Drift Détecté" if dataset_drift else "Pas de Drift"
            st.metric(
                label="⚠️ Alerte Dataset",
                value=alert_text,
                delta=alert_emoji
            )

        # Recommendations based on drift
        if drift_pct > 30:
            st.error("""
            ⚠️ **Drift Critique Détecté !**

            Plus de 30% des features ont drifté. Actions recommandées:
            - 🔄 Re-entraîner le modèle avec des données récentes
            - 📊 Analyser les features qui ont le plus drifté
            - 🔍 Vérifier si les distributions ont changé dans Grafana
            """)
        elif drift_pct > 20:
            st.warning("""
            ⚠️ **Drift Modéré Détecté**

            Entre 20-30% des features ont drifté. Actions suggérées:
            - 📈 Surveiller l'évolution dans les prochains rapports
            - 📊 Vérifier la Model Confidence dans Grafana
            - 🔍 Préparer un re-entraînement si la tendance continue
            """)
        else:
            st.success("""
            ✅ **Distribution Stable**

            Moins de 20% des features ont drifté. Le modèle fonctionne dans des conditions normales.
            """)

    except Exception as e:
        st.error(f"Erreur lors du chargement du résumé: {e}")
else:
    st.info("Aucun résumé JSON trouvé. Les métriques détaillées seront disponibles après génération de rapports.")

pokeball_divider()

# ======================================================
# Sélection et Affichage du Rapport
# ======================================================
section_header("Rapports Evidently", "📄")

st.markdown(f"**{len(html_reports)} rapport(s) disponible(s)**")

# Créer une liste de noms de rapports avec dates formatées
report_options = {}
for report_path in html_reports:
    # Extraire le timestamp du nom de fichier
    # Format: drift_dashboard_20260129_153045.html
    filename = report_path.stem
    try:
        timestamp_part = filename.split('_')[-2] + '_' + filename.split('_')[-1]
        dt = datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")
        display_name = dt.strftime("📅 %d/%m/%Y à %H:%M:%S")
    except:
        display_name = filename

    report_options[display_name] = report_path

# Sélecteur de rapport
if report_options:
    selected_display_name = st.selectbox(
        "Sélectionner un rapport:",
        options=list(report_options.keys()),
        help="Rapports triés du plus récent au plus ancien"
    )

    selected_report = report_options[selected_display_name]

    # Informations sur le rapport sélectionné
    col1, col2 = st.columns([3, 1])

    with col1:
        st.info(f"📄 **Rapport sélectionné**: `{selected_report.name}`")

    with col2:
        # Bouton pour télécharger le rapport
        with open(selected_report, 'rb') as f:
            st.download_button(
                label="⬇️ Télécharger",
                data=f,
                file_name=selected_report.name,
                mime="text/html"
            )

    st.markdown("---")

    # Afficher le rapport HTML dans un iframe
    try:
        with open(selected_report, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Utiliser components.html pour afficher le rapport
        components.html(html_content, height=800, scrolling=True)

    except Exception as e:
        st.error(f"Erreur lors du chargement du rapport HTML: {e}")
        st.info("Essayez de télécharger le rapport et de l'ouvrir dans votre navigateur.")

else:
    st.warning("Aucun rapport HTML trouvé.")

# ======================================================
# Footer avec liens
# ======================================================
pokeball_divider()

st.markdown("""
### 📚 Ressources Complémentaires

- **Grafana**: Surveiller la Model Confidence en temps réel → [http://localhost:3001](http://localhost:3001)
- **MLflow**: Vérifier les performances du modèle → [http://localhost:5001](http://localhost:5001)
- **Documentation Evidently**: [https://docs.evidentlyai.com/](https://docs.evidentlyai.com/)

**💡 Astuce**: Si vous détectez un drift important, comparez les versions de modèles dans MLflow
et vérifiez les métriques de confiance dans Grafana avant de décider d'un re-entraînement.
""")
