# Figures pour Documentation

Ce dossier contient les figures et diagrammes générés pour la documentation du projet et le rapport de certification.

## 📊 Contenu

### ML Model Metrics
- `confusion_matrix.png` - Matrice de confusion du modèle v2
- `roc_curve.png` - Courbe ROC (AUC score)
- `feature_importance.png` - Top 20 features importantes
- `model_comparison_v1_v2.png` - Comparaison performances v1 vs v2

### Exploratory Data Analysis (EDA)
- `eda_stats_distribution.png` - Distribution des statistiques Pokémon
- `eda_type_distribution.png` - Distribution par type
- `eda_correlation_matrix.png` - Corrélations entre features
- `eda_battle_analysis.png` - Analyse des résultats de combats

### Architecture & Database
- `mcd_diagram.html` - Modèle Conceptuel de Données (Mermaid)
- `mcd_mermaid.md` - Source Mermaid du MCD
- `architecture_diagram.html` - Architecture Docker (Mermaid)
- `architecture_mermaid.md` - Source Mermaid de l'architecture

## 🔄 Génération

Pour regénérer toutes les figures :

```bash
python scripts/generate_report_figures.py
```

Pour générer une figure spécifique :

```bash
python scripts/generate_report_figures.py --only confusion
python scripts/generate_report_figures.py --only eda_stats
python scripts/generate_report_figures.py --only mcd
```

## 📝 Usage

Ces figures sont utilisées dans :
- `docs/RAPPORT_E1_E3_TEMPLATE.md` - Rapport de certification
- Documentation technique du projet
- Présentations et démonstrations

## ⚠️ Note

**Ces fichiers sont versionnés dans Git** car ils font partie de la documentation officielle du projet.  
Contrairement aux rapports dans `reports/` qui sont générés dynamiquement par les tests.
