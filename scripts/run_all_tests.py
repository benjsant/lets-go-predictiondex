#!/usr/bin/env python3
"""
Script d'orchestration pour exécuter tous les tests du projet VIA DOCKER
Usage: python3 scripts/run_all_tests.py [--local] [--build]

Par défaut, lance les tests dans un conteneur Docker isolé (recommandé).
"""
import os
import sys
import time
import argparse
import subprocess
import shutil

# Couleurs ANSI
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header(text):
    """Affiche un en-tête formaté"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{BOLD}{text:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Affiche un avertissement"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    """Affiche une information"""
    print(f"{CYAN}ℹ️  {text}{RESET}")

def check_docker():
    """Vérifie que Docker est disponible"""
    print_info("Vérification de Docker...")

    if not shutil.which("docker"):
        print_error("Docker n'est pas installé ou pas dans le PATH")
        return False

    # Vérifier que Docker daemon est accessible
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Docker est disponible")
            return True
        else:
            print_error("Docker daemon n'est pas accessible")
            return False
    except Exception as e:
        print_error(f"Erreur lors de la vérification Docker: {e}")
        return False

def check_docker_compose():
    """Vérifie que Docker Compose est disponible"""
    print_info("Vérification de Docker Compose...")

    # Essayer 'docker compose' (v2)
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Docker Compose v2 disponible")
            return ["docker", "compose"]
    except Exception:
        pass

    # Essayer 'docker-compose' (v1)
    if shutil.which("docker-compose"):
        print_success("Docker Compose v1 disponible")
        return ["docker-compose"]

    print_error("Docker Compose n'est pas disponible")
    return None

def check_services_running(compose_cmd):
    """Vérifie que les services principaux sont lancés"""
    print_info("Vérification des services Docker...")

    try:
        result = subprocess.run(
            compose_cmd + ["ps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Compter les services en cours
            import json
            services = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        service = json.loads(line)
                        if service.get('State') == 'running':
                            services.append(service.get('Service'))
                    except:
                        pass

            if len(services) >= 5:  # Au moins 5 services (db, api, mlflow, prometheus, grafana)
                print_success(f"{len(services)} services actifs")
                return True
            else:
                print_warning(f"Seulement {len(services)} services actifs")
                return False

    except Exception as e:
        print_warning(f"Impossible de vérifier les services: {e}")

    return False

def start_services(compose_cmd):
    """Démarre tous les services Docker"""
    print_info("Démarrage des services Docker...")
    
    # Timeout plus long en environnement CI (GitHub Actions plus lent)
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
    timeout_seconds = 600 if is_ci else 180
    
    if is_ci:
        print_info(f"Environnement CI - Timeout étendu à {timeout_seconds}s pour le build des images...")

    try:
        result = subprocess.run(
            compose_cmd + ["up", "-d"],
            timeout=timeout_seconds
        )

        if result.returncode == 0:
            print_success("Services démarrés")
            wait_time = 45 if is_ci else 30
            print_info(f"Attente de {wait_time} secondes pour que les services soient prêts...")
            time.sleep(wait_time)
            return True
        else:
            print_error("Échec du démarrage des services")
            return False

    except Exception as e:
        print_error(f"Erreur lors du démarrage: {e}")
        return False

def run_tests_in_docker(compose_cmd, build=False):
    """Lance les tests dans un conteneur Docker"""
    print_header("LANCEMENT DES TESTS VIA DOCKER")

    print_info("Configuration:")
    print(f"  - Environnement: Docker (isolé)")
    print(f"  - Build image: {'Oui' if build else 'Non (utilise cache)'}")
    print(f"  - Services requis: PostgreSQL, API, MLflow, Prometheus, Grafana")

    # Construire la commande
    cmd = compose_cmd + ["--profile", "tests", "up"]

    if build:
        cmd.append("--build")

    cmd.extend(["--abort-on-container-exit", "--exit-code-from", "tests", "tests"])

    print_info("\nLancement des tests...")
    print_info(f"Commande: {' '.join(cmd)}\n")

    try:
        # Lancer les tests (output en temps réel)
        result = subprocess.run(cmd)

        return result.returncode

    except KeyboardInterrupt:
        print_warning("\n\nTests interrompus par l'utilisateur")
        return 130
    except Exception as e:
        print_error(f"Erreur lors de l'exécution des tests: {e}")
        return 1

def run_tests_locally():
    """Lance les tests d'intégration depuis l'hôte (legacy)"""
    print_header("LANCEMENT DES TESTS DEPUIS L'HÔTE")

    print_warning("Mode local (legacy) - Peut échouer si DB Docker non accessible")
    print_info("Lancement du test système complet...")

    try:
        result = subprocess.run(
            [sys.executable, "tests/integration/test_complete_system.py"]
        )
        return result.returncode
    except Exception as e:
        print_error(f"Erreur: {e}")
        return 1

def cleanup_tests_container(compose_cmd):
    """Nettoie le conteneur de tests après exécution"""
    print_info("\nNettoyage du conteneur de tests...")

    try:
        subprocess.run(
            compose_cmd + ["rm", "-f", "tests"],
            capture_output=True,
            timeout=10
        )
        print_success("Conteneur de tests nettoyé")
    except Exception:
        pass

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Lance tous les tests via Docker (recommandé)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python3 scripts/run_all_tests.py              # Lance via Docker (cache)
  python3 scripts/run_all_tests.py --build      # Lance via Docker (rebuild)
  python3 scripts/run_all_tests.py --local      # Lance depuis l'hôte (legacy)
        """
    )

    parser.add_argument(
        "--local",
        action="store_true",
        help="Lance les tests depuis l'hôte au lieu de Docker (non recommandé)"
    )

    parser.add_argument(
        "--build",
        action="store_true",
        help="Rebuild l'image Docker des tests avant de lancer"
    )

    parser.add_argument(
        "--no-start",
        action="store_true",
        help="Ne pas démarrer les services automatiquement (suppose qu'ils tournent déjà)"
    )

    args = parser.parse_args()

    print_header("TESTS COMPLETS - Let's Go PredictionDex")

    # Mode local (legacy)
    if args.local:
        print_warning("Mode local activé (non recommandé)")
        return run_tests_locally()

    # Mode Docker (recommandé)
    print_success("Mode Docker activé (recommandé)")

    # 1. Vérifier Docker
    if not check_docker():
        print_error("\n❌ Docker n'est pas disponible")
        print_info("Installez Docker: https://docs.docker.com/get-docker/")
        return 1

    # 2. Vérifier Docker Compose
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        print_error("\n❌ Docker Compose n'est pas disponible")
        return 1

    # 3. Vérifier/Démarrer les services
    if not args.no_start:
        services_running = check_services_running(compose_cmd)

        if not services_running:
            print_warning("Services Docker non démarrés")

            # En environnement CI (GitHub Actions), démarrer automatiquement
            is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
            
            if is_ci:
                print_info("🔄 Environnement CI détecté - démarrage automatique des services...")
                if not start_services(compose_cmd):
                    print_error("\n❌ Impossible de démarrer les services")
                    return 1
            else:
                response = input(f"\n{YELLOW}Démarrer les services maintenant? (o/N): {RESET}")
                if response.lower() in ['o', 'oui', 'y', 'yes']:
                    if not start_services(compose_cmd):
                        print_error("\n❌ Impossible de démarrer les services")
                        return 1
                else:
                    print_error("\n❌ Les tests nécessitent que les services soient lancés")
                    print_info("Lancez manuellement: docker compose up -d")
                    return 1

    # 4. Lancer les tests
    exit_code = run_tests_in_docker(compose_cmd, build=args.build)

    # 5. Nettoyer
    cleanup_tests_container(compose_cmd)

    # 6. Résumé
    print_header("RÉSULTAT FINAL")

    if exit_code == 0:
        print_success("✅ TOUS LES TESTS ONT RÉUSSI")
        print_info("\nRapports disponibles dans: ./reports/")
        return 0
    else:
        print_error(f"❌ TESTS ÉCHOUÉS (code: {exit_code})")
        print_info("\nConsultez les logs ci-dessus pour plus de détails")
        return exit_code

if __name__ == "__main__":
    sys.exit(main())
