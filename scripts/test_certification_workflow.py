#!/usr/bin/env python3
"""
Script de test local du workflow de certification E1/E3
Simule l'exécution GitHub Actions en local pour vérifier avant push

Usage:
    python scripts/test_certification_workflow.py
    python scripts/test_certification_workflow.py --job e1-data-validation
    python scripts/test_certification_workflow.py --job e3-c13-mlops
    python scripts/test_certification_workflow.py --all
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Couleurs ANSI
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text: str):
    """Affiche un en-tête formaté"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{BOLD}{text:^80}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")


def print_step(step: str):
    """Affiche une étape"""
    print(f"{CYAN}▶ {step}{RESET}")


def print_success(text: str):
    """Affiche un succès"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Affiche une erreur"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text: str):
    """Affiche un avertissement"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def run_command(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict] = None) -> bool:
    """Exécute une commande et retourne True si succès"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env or os.environ.copy(),
            capture_output=False,
            text=True,
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def check_prerequisites() -> bool:
    """Vérifie les prérequis"""
    print_header("VÉRIFICATION DES PRÉREQUIS")
    
    required_tools = {
        'python3': 'Python 3.11+',
        'docker': 'Docker',
        'docker-compose': 'Docker Compose (ou "docker compose")',
        'pip': 'pip',
    }
    
    all_ok = True
    for tool, name in required_tools.items():
        if subprocess.run(['which', tool], capture_output=True).returncode == 0:
            print_success(f"{name} trouvé")
        else:
            # Essayer "docker compose" si "docker-compose" n'existe pas
            if tool == 'docker-compose':
                if subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True).returncode == 0:
                    print_success(f"{name} trouvé (Docker Compose v2)")
                    continue
            print_error(f"{name} non trouvé")
            all_ok = False
    
    # Vérifier version Python
    try:
        result = subprocess.run(['python3', '--version'], 
                                capture_output=True, text=True)
        version = result.stdout.strip()
        print_success(f"Python version: {version}")
    except:
        print_error("Impossible de vérifier la version Python")
        all_ok = False
    
    return all_ok


def setup_environment() -> Dict[str, str]:
    """Configure l'environnement de test"""
    print_header("CONFIGURATION DE L'ENVIRONNEMENT")
    
    env = os.environ.copy()
    
    # Variables communes
    env_vars = {
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'letsgo_test',
        'POSTGRES_USER': 'letsgo_user',
        'POSTGRES_PASSWORD': 'letsgo_password',
        'PYTHONPATH': str(Path.cwd()),
        'DISABLE_MLFLOW_TRACKING': 'true',
        'ML_SKIP_IF_EXISTS': 'true',
    }
    
    for key, value in env_vars.items():
        env[key] = value
        print_step(f"{key}={value}")
    
    print_success("Environnement configuré")
    return env


def test_e1_data_validation(env: Dict[str, str]) -> bool:
    """Test du job E1 - Data Validation"""
    print_header("JOB E1: COLLECTE ET TRAITEMENT DES DONNÉES")
    
    steps = [
        ("E1.1 - Collecter données", 
         ["pytest", "tests/etl/", "-v", "-k", 
          "test_pokemon_fetcher or test_pokepedia_scraper", "--tb=short"]),
        
        ("E1.3 - Structure BDD", 
         ["pytest", "tests/core/db/", "-v", "--tb=short"]),
        
        ("E1.4 - Features", 
         ["pytest", "tests/ml/test_features.py", "-v", "--tb=short"]),
    ]
    
    results = []
    for step_name, cmd in steps:
        print_step(step_name)
        success = run_command(cmd, env=env)
        results.append(success)
        
        if success:
            print_success(f"{step_name} PASSÉ")
        else:
            print_warning(f"{step_name} ÉCHOUÉ (non bloquant pour test)")
    
    # Vérifier documentation
    print_step("E1.5 - Vérifier documentation")
    docs = [
        Path("etl_pokemon/README.md"),
        Path("README.md"),
    ]
    
    for doc in docs:
        if doc.exists():
            print_success(f"{doc} trouvé")
        else:
            print_warning(f"{doc} manquant")
    
    return all(results)


def test_e3_c9_api_rest(env: Dict[str, str]) -> bool:
    """Test du job C9 - API REST"""
    print_header("JOB C9: API REST EXPOSANT IA")
    
    print_step("Tester API avec IA")
    success = run_command(
        ["pytest", "tests/api/test_prediction_api.py", "-v", "--tb=short"],
        env=env
    )
    
    if success:
        print_success("Tests API passés")
    else:
        print_warning("Tests API échoués")
    
    print_step("Coverage API")
    run_command(
        ["pytest", "tests/api/", "-v", "--cov=api_pokemon", 
         "--cov-report=term-missing"],
        env=env
    )
    
    return success


def test_e3_c10_integration(env: Dict[str, str]) -> bool:
    """Test du job C10 - Intégration Application"""
    print_header("JOB C10: INTÉGRATION DANS UNE APPLICATION")
    
    print_step("Vérifier structure interface")
    interface_files = [
        Path("interface/app.py"),
        Path("interface/pages/2_Compare.py"),
        Path("interface/services/api_client.py"),
        Path("interface/services/prediction_service.py"),
    ]
    
    all_found = True
    for file in interface_files:
        if file.exists():
            print_success(f"{file} trouvé")
        else:
            print_error(f"{file} manquant")
            all_found = False
    
    print_step("Tester interface")
    success = run_command(
        ["pytest", "tests/interface/", "-v", "--tb=short"],
        env=env
    )
    
    return all_found


def test_e3_c11_monitoring(env: Dict[str, str]) -> bool:
    """Test du job C11 - Monitoring"""
    print_header("JOB C11: MONITORING DU MODÈLE IA")
    
    print_step("Vérifier infrastructure monitoring")
    monitoring_files = [
        Path("api_pokemon/monitoring/drift_detection.py"),
        Path("docker/prometheus/prometheus.yml"),
        Path("docker/grafana"),
    ]
    
    for file in monitoring_files:
        if file.exists():
            print_success(f"{file} trouvé")
        else:
            print_warning(f"{file} manquant")
    
    print_step("Tester monitoring")
    success = run_command(
        ["pytest", "tests/monitoring/", "-v", "--tb=short"],
        env=env
    )
    
    return success


def test_e3_c12_optimization(env: Dict[str, str]) -> bool:
    """Test du job C12 - Optimisation"""
    print_header("JOB C12: OPTIMISATION DU MODÈLE")
    
    print_step("Tester ML")
    success = run_command(
        ["pytest", "tests/ml/", "-v", "--tb=short"],
        env=env
    )
    
    print_step("Tester inférence")
    run_command(
        ["pytest", "tests/ml/test_model_inference.py", "-v", "--tb=short"],
        env=env
    )
    
    return success


def test_e3_c13_mlops(env: Dict[str, str]) -> bool:
    """Test du job C13 - MLOps CI/CD"""
    print_header("JOB C13: MLOPS ET CI/CD")
    
    print_step("Vérifier workflows GitHub Actions")
    workflows_dir = Path(".github/workflows")
    
    if workflows_dir.exists():
        workflows = list(workflows_dir.glob("*.yml"))
        print_success(f"{len(workflows)} workflows trouvés:")
        for workflow in workflows:
            print(f"  • {workflow.name}")
    else:
        print_error("Dossier .github/workflows/ manquant")
        return False
    
    print_step("Tester pipeline ML")
    success = run_command(
        ["pytest", "tests/ml/", "-v", "--cov=machine_learning", 
         "--cov-report=term-missing"],
        env=env
    )
    
    print_step("Vérifier artifacts ML")
    models_dir = Path("models")
    if models_dir.exists():
        models = list(models_dir.glob("*.pkl")) + list(models_dir.glob("*.json"))
        if models:
            print_success(f"{len(models)} artifacts trouvés dans models/")
        else:
            print_warning("Aucun model trouvé (normal si pas encore entraîné)")
    
    return success


def generate_report(results: Dict[str, bool]):
    """Génère un rapport final"""
    print_header("RAPPORT DE CERTIFICATION E1/E3")
    
    print(f"\n{BOLD}Résultats par job:{RESET}\n")
    
    # E1
    print(f"{BOLD}📊 BLOC E1: Collecte et Traitement des Données{RESET}")
    e1_result = results.get('e1-data-validation', False)
    status = f"{GREEN}✅ VALIDÉ{RESET}" if e1_result else f"{RED}❌ ÉCHOUÉ{RESET}"
    print(f"  E1 Data Validation: {status}\n")
    
    # E3
    print(f"{BOLD}🤖 BLOC E3: Intégration IA en Production{RESET}")
    e3_jobs = [
        ('e3-c9-api-rest', 'C9 - API REST avec IA'),
        ('e3-c10-integration', 'C10 - Intégration app'),
        ('e3-c11-monitoring', 'C11 - Monitoring IA'),
        ('e3-c12-optimization', 'C12 - Optimisation IA'),
        ('e3-c13-mlops', 'C13 - MLOps CI/CD'),
    ]
    
    for job_id, job_name in e3_jobs:
        result = results.get(job_id, False)
        status = f"{GREEN}✅ VALIDÉ{RESET}" if result else f"{RED}❌ ÉCHOUÉ{RESET}"
        print(f"  {job_name}: {status}")
    
    # Score global
    total_jobs = len(results)
    passed_jobs = sum(1 for v in results.values() if v)
    score = (passed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    print(f"\n{BOLD}🎯 Score Global:{RESET}")
    print(f"  {passed_jobs}/{total_jobs} jobs passés ({score:.1f}%)")
    
    if score >= 80:
        print(f"\n{GREEN}{BOLD}✅ PROJET PRÊT POUR CERTIFICATION{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}⚠️  AMÉLIORATIONS NÉCESSAIRES{RESET}")
    
    print(f"\n{BOLD}📚 Documentation:{RESET}")
    print("  • README.md")
    print("  • docs/certification/CI_CD_CERTIFICATION_E1_E3.md")
    print("  • docs/CERTIFICATION_E1_E3_VALIDATION.md")
    
    print(f"\n{BOLD}🔗 Prochaines étapes:{RESET}")
    if score >= 80:
        print("  1. ✅ Pousser sur GitHub")
        print("  2. ✅ Vérifier workflow GitHub Actions")
        print("  3. ✅ Télécharger rapport de certification")
        print("  4. ✅ Préparer soutenance")
    else:
        print("  1. 🔧 Corriger les tests échoués")
        print("  2. 🔄 Re-tester localement")
        print("  3. ✅ Pousser sur GitHub")


def main():
    parser = argparse.ArgumentParser(
        description="Test local du workflow de certification E1/E3"
    )
    parser.add_argument(
        '--job',
        choices=[
            'e1-data-validation',
            'e3-c9-api-rest',
            'e3-c10-integration',
            'e3-c11-monitoring',
            'e3-c12-optimization',
            'e3-c13-mlops',
            'all'
        ],
        default='all',
        help='Job spécifique à tester (défaut: all)'
    )
    
    args = parser.parse_args()
    
    print_header("TEST LOCAL WORKFLOW CERTIFICATION E1/E3")
    print(f"{BOLD}Projet:{RESET} Let's Go PredictionDex")
    print(f"{BOLD}Date:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{BOLD}Job:{RESET} {args.job}")
    
    # Vérifier prérequis
    if not check_prerequisites():
        print_error("Prérequis manquants. Installez les outils requis.")
        return 1
    
    # Setup environment
    env = setup_environment()
    
    # Exécuter les tests
    results = {}
    
    if args.job == 'all' or args.job == 'e1-data-validation':
        results['e1-data-validation'] = test_e1_data_validation(env)
    
    if args.job == 'all' or args.job == 'e3-c9-api-rest':
        results['e3-c9-api-rest'] = test_e3_c9_api_rest(env)
    
    if args.job == 'all' or args.job == 'e3-c10-integration':
        results['e3-c10-integration'] = test_e3_c10_integration(env)
    
    if args.job == 'all' or args.job == 'e3-c11-monitoring':
        results['e3-c11-monitoring'] = test_e3_c11_monitoring(env)
    
    if args.job == 'all' or args.job == 'e3-c12-optimization':
        results['e3-c12-optimization'] = test_e3_c12_optimization(env)
    
    if args.job == 'all' or args.job == 'e3-c13-mlops':
        results['e3-c13-mlops'] = test_e3_c13_mlops(env)
    
    # Générer le rapport
    generate_report(results)
    
    # Code de sortie
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
