# Reports

Rapports générés automatiquement par les tests d'intégration et de validation.

## Structure

```
reports/
├── monitoring/
│   ├── validation_report.json        # Résultats détaillés (JSON)
│   ├── validation_report.html        # Rapport visuel (HTML)
│   └── integration_test_results.json # Tests d'intégration
└── validation/
    └── system_validation_report.json # Validation système complète
```

## Rapport de monitoring

Généré par `scripts/test_ci_cd_locally.py` ou le workflow GitHub Actions. Vérifie :

- **Services** : santé de l'API, PostgreSQL, Prometheus, Grafana, MLflow, Streamlit
- **Métriques Prometheus** : collecte active, endpoints exposés
- **Prédictions ML** : le modèle répond correctement, probabilités cohérentes
- **Drift detection** : le système de détection de dérive est opérationnel

Chaque vérification donne un score, le total est sur 100.

## Rapport de validation système

Généré par les tests d'intégration (`tests/integration/`). Couvre l'ensemble de la chaîne : BDD accessible, API fonctionnelle, modèle ML chargé, monitoring actif, interface Streamlit en ligne.

## Seuils recommandés

- **CI/CD** : score >= 60/100 pour passer le pipeline
- **Production** : score >= 80/100

## Génération

```bash
# En local (services Docker lancés)
python scripts/test_ci_cd_locally.py

# Via GitHub Actions (automatique sur push)
# Les rapports sont téléchargeables en artefacts du workflow
```

Ces fichiers sont gitignorés (générés à chaque exécution). La structure des dossiers est conservée via les `.gitkeep`.
