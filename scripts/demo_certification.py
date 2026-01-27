#!/usr/bin/env python3
"""
Script de Démonstration Automatisé - Certification E1/E3
=========================================================

Ce script ouvre automatiquement tous les composants visuels
dans le navigateur et affiche les informations de démonstration.

Usage:
    # Démonstration complète
    python scripts/demo_certification.py

    # Seulement les interfaces web
    python scripts/demo_certification.py --web-only

    # Avec génération de métriques
    python scripts/demo_certification.py --generate-metrics
"""

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import List, Tuple


# Configuration URLs
URLS = {
    "streamlit": "http://localhost:8502",
    "swagger": "http://localhost:8080/docs",
    "grafana": "http://localhost:3001",
    "prometheus": "http://localhost:9091",
    "mlflow": "http://localhost:5001",
    "github_actions": "https://github.com/YOUR_USERNAME/lets-go-predictiondex/actions",
}


class DemoLauncher:
    """Lanceur automatique de démonstration."""

    def __init__(self, generate_metrics: bool = False):
        self.generate_metrics = generate_metrics
        self.services_ok = []
        self.services_failed = []

    def print_header(self, text: str, emoji: str = ""):
        """Affiche un header formaté."""
        print("\n" + "=" * 80)
        print(f"{emoji} {text}")
        print("=" * 80)

    def print_section(self, text: str, emoji: str = ""):
        """Affiche une section."""
        print(f"\n{emoji} {text}")
        print("-" * 80)

    def check_service(self, name: str, url: str) -> bool:
        """Vérifie si un service est accessible."""
        try:
            import requests
            response = requests.get(url.replace("/docs", "/health"), timeout=5)
            if response.status_code == 200:
                self.services_ok.append(name)
                return True
        except:
            pass

        self.services_failed.append(name)
        return False

    def check_docker(self) -> bool:
        """Vérifie si Docker est en cours d'exécution."""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def open_urls(self, urls: List[Tuple[str, str]]):
        """Ouvre plusieurs URLs dans le navigateur."""
        for name, url in urls:
            print(f"   Ouverture {name}...")
            time.sleep(1)
            webbrowser.open_new_tab(url)

    def display_demo_guide(self):
        """Affiche le guide de démonstration."""
        self.print_header("GUIDE DE DEMONSTRATION - CERTIFICATION E1/E3", "🎯")

        print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    TABLEAU RECAPITULATIF                             │
├─────────────────────────────────────────────────────────────────────┤
│ Composant            │ URL/Commande              │ Compétence       │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Streamlit         │ http://localhost:8502     │ C10 - Interface  │
│ 2. Swagger API       │ http://localhost:8080     │ C9 - API + IA    │
│ 3. Grafana           │ http://localhost:3001     │ C11 - Monitoring │
│ 4. Prometheus        │ http://localhost:9091     │ C11 - Métriques  │
│ 5. MLflow            │ http://localhost:5001     │ C13 - MLOps      │
│ 6. PostgreSQL        │ Via Swagger API           │ E1.3 - BDD       │
│ 7. ETL Pipeline      │ docker logs letsgo_etl    │ E1.1, E1.2       │
│ 8. ML Training       │ docker logs letsgo_ml     │ C12 - Optim IA   │
│ 9. Notebooks         │ code notebooks/           │ E1.4 - Exploit   │
│ 10. Documentation    │ README.md                 │ E1.5 - Doc       │
└─────────────────────────────────────────────────────────────────────┘
        """)

    def display_shortcuts(self):
        """Affiche les raccourcis utiles."""
        self.print_section("COMMANDES UTILES", "💡")

        print("""
# Valider la stack
python scripts/validate_docker_stack.py --verbose

# Générer métriques pour Grafana (5 min)
python scripts/generate_monitoring_data.py --mode realistic --duration 5

# Voir logs ETL (collecte données)
docker logs letsgo_etl --tail 200

# Voir logs ML (entraînement modèle)
docker logs letsgo_ml --tail 200

# Ouvrir notebooks Jupyter
code notebooks/03_training_evaluation.ipynb

# Vérifier rapport drift Evidently
ls -lh api_pokemon/monitoring/reports/
        """)

    def display_demo_order(self):
        """Affiche l'ordre de démonstration recommandé."""
        self.print_section("ORDRE DE DEMONSTRATION RECOMMANDE (30 min)", "📋")

        print("""
Phase 1: INTERFACES WEB INTERACTIVES (12 min)
  1. Streamlit (4 min) - Page Combat et Prédiction ⭐
     → Montrer prédiction ML en action
  2. Swagger API (3 min) - Endpoint /predict/best-move ⭐
     → Tester API avec JSON
  3. Grafana (3 min) - Dashboard API Performance ⭐
     → Métriques temps réel (latency, throughput)
  4. Prometheus (1 min) - Targets UP
  5. MLflow (2 min) - Experiments + Model Registry

Phase 2: COMPOSANTS BACKEND (10 min)
  6. PostgreSQL (3 min) - Via Swagger /pokemon, /types, /moves
     → Montrer 11 tables, relations FK
  7. ETL Pipeline (3 min) - Logs Docker formatés
     → 5 étapes: Init → CSV → PokéAPI → Scraping → Validation
  8. ML Training (4 min) - Logs + Notebooks
     → Dataset 898k combats → XGBoost 94.46% accuracy

Phase 3: TECHNIQUE AVANCE (8 min)
  9. Drift Detection (2 min) - Rapports HTML Evidently
  10. GitHub Actions (3 min) - 4 workflows CI/CD
  11. Documentation (3 min) - README + Diagrammes
        """)

    def display_competences_mapping(self):
        """Affiche le mapping composants → compétences."""
        self.print_section("MAPPING COMPETENCES E1/E3", "🎓")

        print("""
╔═════════════════════════════════════════════════════════════════════╗
║                        BLOC E1 - DONNEES                            ║
╠═════════════════════════════════════════════════════════════════════╣
║ E1.1 - Collecte données      │ ETL Pipeline (3 sources)             ║
║ E1.2 - Nettoyage données     │ Validation, normalisation            ║
║ E1.3 - Structurer BDD        │ PostgreSQL 11 tables 3NF             ║
║ E1.4 - Exploiter données     │ Feature engineering 133 features     ║
║ E1.5 - Documenter            │ README + docs/ + diagrammes          ║
╠═════════════════════════════════════════════════════════════════════╣
║                        BLOC E3 - IA PRODUCTION                       ║
╠═════════════════════════════════════════════════════════════════════╣
║ C9  - API REST + IA          │ FastAPI + XGBoost 94.46%             ║
║ C10 - Intégration app        │ Streamlit 8 pages                    ║
║ C11 - Monitoring IA          │ Prometheus + Grafana + Evidently     ║
║ C12 - Optimiser IA           │ XGBoost optimisé < 500ms             ║
║ C13 - MLOps CI/CD            │ MLflow + GitHub Actions              ║
╚═════════════════════════════════════════════════════════════════════╝
        """)

    def run_demo(self, web_only: bool = False):
        """Lance la démonstration complète."""
        self.print_header("LANCEMENT DEMONSTRATION CERTIFICATION E1/E3", "🚀")

        # 1. Vérifier Docker
        self.print_section("Vérification de la stack Docker", "🔍")
        if not self.check_docker():
            print("❌ Docker n'est pas en cours d'exécution")
            print("\n💡 Démarrez les services:")
            print("   python scripts/start_docker_stack.py")
            sys.exit(1)
        print("✅ Docker est actif")

        # 2. Vérifier services
        print("\nVérification des services web...")
        for name, url in URLS.items():
            if name == "github_actions":
                continue
            if self.check_service(name, url):
                print(f"   ✅ {name:20s} - {url}")
            else:
                print(f"   ❌ {name:20s} - {url}")

        # 3. Afficher guide
        self.display_demo_guide()

        # 4. Ouvrir interfaces web
        self.print_section("Ouverture des interfaces web", "🌐")
        print("\n⏳ Ouverture de 5 onglets dans le navigateur...")

        web_urls = [
            ("Streamlit", URLS["streamlit"]),
            ("Swagger API", URLS["swagger"]),
            ("Grafana", URLS["grafana"]),
            ("MLflow", URLS["mlflow"]),
            ("Prometheus", URLS["prometheus"]),
        ]

        self.open_urls(web_urls)

        print("\n✅ Interfaces web ouvertes!")

        # 5. Générer métriques (optionnel)
        if self.generate_metrics and not web_only:
            self.print_section("Génération de métriques de monitoring", "📊")
            print("\n⏳ Génération de trafic réaliste (5 min)...")
            print("   Cela va remplir les dashboards Grafana avec des données")

            try:
                subprocess.Popen(
                    [
                        "python",
                        "scripts/generate_monitoring_data.py",
                        "--mode", "realistic",
                        "--duration", "5"
                    ]
                )
                print("✅ Génération de métriques lancée en arrière-plan")
                print("   Consultez Grafana: http://localhost:3001")
            except Exception as e:
                print(f"⚠️  Impossible de lancer la génération: {e}")

        # 6. Afficher ordre démo
        if not web_only:
            self.display_demo_order()

        # 7. Afficher compétences
        self.display_competences_mapping()

        # 8. Afficher raccourcis
        self.display_shortcuts()

        # 9. Résumé final
        self.print_header("DEMONSTRATION PRETE", "✅")

        if self.services_ok:
            print(f"\n✅ {len(self.services_ok)} services accessibles:")
            for service in self.services_ok:
                print(f"   • {service}")

        if self.services_failed:
            print(f"\n⚠️  {len(self.services_failed)} services non accessibles:")
            for service in self.services_failed:
                print(f"   • {service}")
            print("\n💡 Démarrez les services manquants:")
            print("   docker-compose up -d")

        print("\n📋 CHECKLIST AVANT DEMO:")
        print("   [ ] 5 onglets navigateur ouverts")
        print("   [ ] Tous les services UP (vert)")
        print("   [ ] Métriques générées (Grafana)")
        print("   [ ] Notebooks ouverts dans VSCode")
        print("   [ ] README.md et docs/ préparés")

        print("\n🎯 PRET POUR LA CERTIFICATION !")
        print("\n💡 Guide complet: GUIDE_DEMONSTRATION_VISUELLE.md")

        print("\n" + "=" * 80 + "\n")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Lanceur automatique de démonstration E1/E3"
    )
    parser.add_argument(
        "--web-only",
        action="store_true",
        help="Ouvrir seulement les interfaces web (pas de guide complet)"
    )
    parser.add_argument(
        "--generate-metrics",
        action="store_true",
        help="Lancer génération de métriques en arrière-plan"
    )

    args = parser.parse_args()

    launcher = DemoLauncher(generate_metrics=args.generate_metrics)

    try:
        launcher.run_demo(web_only=args.web_only)
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Démonstration interrompue")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
