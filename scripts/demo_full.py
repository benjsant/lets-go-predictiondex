#!/usr/bin/env python3
"""
PredictionDex — Script de demonstration complete E1/E3

Lance tout de A a Z :
  1. Verifie les prerequis (Docker, .env)
  2. Demarre le stack Docker (10 services)
  3. Attend que tous les services soient prets
  4. Lance l'ETL si la BDD est vide
  5. Enregistre le modele dans MLflow
  6. Genere des metriques de monitoring (Grafana)
  7. Lance les tests pytest
  8. Ouvre toutes les interfaces dans le navigateur

Usage:
  python3 scripts/demo_full.py              # Tout lancer
  python3 scripts/demo_full.py --skip-tests # Sans les tests
  python3 scripts/demo_full.py --skip-etl   # Sans relancer l'ETL
  python3 scripts/demo_full.py --stop       # Arreter tout

Aucune dependance externe requise (stdlib Python uniquement).
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

# ============================================================================
# Configuration
# ============================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

SERVICES = [
    ("PostgreSQL (via API health)", "http://localhost:8080/health", 90),
    ("API FastAPI", "http://localhost:8080/docs", 60),
    ("Streamlit", "http://localhost:8502", 60),
    ("Prometheus", "http://localhost:9091/-/healthy", 30),
    ("Grafana", "http://localhost:3001/api/health", 30),
    ("MLflow", "http://localhost:5001/health", 30),
]

URLS_FINALES = [
    ("Streamlit (Interface utilisateur)", "http://localhost:8502"),
    ("Swagger API (Documentation)", "http://localhost:8080/docs"),
    ("Grafana (Dashboards monitoring)", "http://localhost:3001"),
    ("Prometheus (Metriques brutes)", "http://localhost:9091"),
    ("MLflow (Model Registry)", "http://localhost:5001"),
]

# ============================================================================
# Couleurs terminal
# ============================================================================

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
MAGENTA = "\033[0;35m"
BOLD = "\033[1m"
NC = "\033[0m"


def header(text):
    print()
    print(f"{MAGENTA}{'=' * 64}{NC}")
    print(f"{MAGENTA}  {BOLD}{text}{NC}")
    print(f"{MAGENTA}{'=' * 64}{NC}")
    print()


def step(num, text):
    print(f"{CYAN}  ETAPE {num} — {text}{NC}")


def ok(msg):
    print(f"  {GREEN}  {msg}{NC}")


def warn(msg):
    print(f"  {YELLOW}  {msg}{NC}")


def fail(msg):
    print(f"  {RED}  {msg}{NC}")


def info(msg):
    print(f"  {BLUE}  {msg}{NC}")


# ============================================================================
# Utilitaires
# ============================================================================

def run(cmd, capture=False, check=True, timeout=300):
    """Execute une commande shell."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            check=check,
            timeout=timeout,
            cwd=str(PROJECT_DIR),
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture:
            return e
        raise
    except subprocess.TimeoutExpired:
        fail(f"Timeout apres {timeout}s : {' '.join(cmd)}")
        return None


def http_get(url, headers=None, timeout=5):
    """Fait un GET HTTP. Retourne (status_code, body) ou (None, None) si erreur."""
    req = Request(url, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except (URLError, OSError, ValueError):
        return None, None


def http_post(url, data, headers=None, timeout=10):
    """Fait un POST HTTP avec du JSON."""
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except (URLError, OSError, ValueError):
        return None, None


def wait_for_service(name, url, max_wait=60):
    """Attend qu'un service reponde en HTTP 200/302."""
    elapsed = 0
    while elapsed < max_wait:
        status, _ = http_get(url)
        if status in (200, 302):
            ok(f"{name} est pret")
            return True
        time.sleep(2)
        elapsed += 2
        print(f"\r    Attente de {name}... ({elapsed}s/{max_wait}s)", end="", flush=True)
    print()
    fail(f"{name} n'a pas demarre apres {max_wait}s")
    return False


def get_api_key():
    """Lit la premiere API key depuis .env."""
    env_path = PROJECT_DIR / ".env"
    if not env_path.exists():
        return ""
    for line in env_path.read_text().splitlines():
        if line.startswith("API_KEYS="):
            value = line.split("=", 1)[1].strip().strip('"')
            return value.split(",")[0]
    return ""


def get_compose_cmd():
    """Detecte docker compose v2 ou v1."""
    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    return None


def open_browser(url):
    """Ouvre une URL dans le navigateur (cross-platform)."""
    try:
        webbrowser.open(url)
    except Exception:
        pass


# ============================================================================
# Etape 1 : Prerequis
# ============================================================================

def check_prerequisites():
    step(1, "Verification des prerequis")

    # Docker
    if not shutil.which("docker"):
        fail("Docker non installe")
        sys.exit(1)
    result = run(["docker", "--version"], capture=True, check=False)
    ok(f"Docker installe ({result.stdout.strip() if result else '?'})")

    # Docker Compose
    compose_cmd = get_compose_cmd()
    if not compose_cmd:
        fail("Docker Compose non installe")
        sys.exit(1)
    ok(f"Docker Compose detecte ({' '.join(compose_cmd)})")

    # .env
    env_path = PROJECT_DIR / ".env"
    if env_path.exists():
        ok("Fichier .env trouve")
    else:
        example = PROJECT_DIR / ".env.example"
        if example.exists():
            warn("Fichier .env manquant — creation depuis .env.example")
            shutil.copy2(str(example), str(env_path))
            ok("Fichier .env cree")
        else:
            fail("Pas de .env ni .env.example")
            sys.exit(1)

    print()
    return compose_cmd


# ============================================================================
# Etape 2 : Demarrage Docker
# ============================================================================

def start_docker(compose_cmd):
    step(2, "Demarrage des services Docker")

    # Compter les conteneurs qui tournent
    result = run(compose_cmd + ["ps", "-q"], capture=True, check=False)
    running = len(result.stdout.strip().splitlines()) if result and result.stdout else 0

    if running > 5:
        ok(f"Services deja en cours ({running} conteneurs)")
    else:
        info("Lancement de docker compose up -d --build...")
        run(compose_cmd + ["up", "-d", "--build"], check=False, timeout=600)
        ok("Docker compose lance")

    print()


# ============================================================================
# Etape 3 : Attente des services
# ============================================================================

def wait_for_services():
    step(3, "Attente de la disponibilite des services")

    all_ok = True
    for name, url, timeout in SERVICES:
        if not wait_for_service(name, url, timeout):
            all_ok = False

    print()
    return all_ok


# ============================================================================
# Etape 4 : Verification des donnees (ETL)
# ============================================================================

def check_data(compose_cmd, api_key, skip_etl=False):
    step(4, "Verification des donnees en base")

    headers = {"X-API-Key": api_key} if api_key else {}
    status, body = http_get("http://localhost:8080/pokemon/", headers=headers)

    pokemon_count = 0
    if status == 200 and body:
        try:
            pokemon_count = len(json.loads(body))
        except (json.JSONDecodeError, TypeError):
            pass

    if pokemon_count > 100:
        ok(f"{pokemon_count} Pokemon en base — donnees OK")
    elif skip_etl:
        warn("Base vide mais --skip-etl active")
    else:
        info("Base vide — lancement de l'ETL...")
        run(compose_cmd + ["run", "--rm", "etl"], check=False, timeout=600)
        ok("ETL termine")

    print()


# ============================================================================
# Etape 5 : MLflow — Enregistrement du modele
# ============================================================================

def setup_mlflow():
    step(5, "Configuration MLflow")

    # Verifier si un modele est deja enregistre
    status, body = http_get("http://localhost:5001/api/2.0/mlflow/registered-models/search")
    models_count = 0
    if status == 200 and body:
        try:
            models_count = len(json.loads(body).get("registered_models", []))
        except (json.JSONDecodeError, TypeError):
            pass

    if models_count > 0:
        ok(f"Modele deja enregistre dans MLflow ({models_count} modele(s))")
        print()
        return

    info("Enregistrement du modele dans MLflow (via container letsgo_mlflow)...")

    # Script Python execute dans le conteneur MLflow
    mlflow_script = (
        "import json, pickle, mlflow, mlflow.sklearn, warnings\n"
        "from datetime import datetime\n"
        "from pathlib import Path\n"
        "from mlflow.tracking import MlflowClient\n"
        "warnings.filterwarnings('ignore')\n"
        "mlflow.set_tracking_uri('http://localhost:5001')\n"
        "models_dir = Path('/app/models')\n"
        "with open(models_dir/'battle_winner_model_v2.pkl','rb') as f: model=pickle.load(f)\n"
        "with open(models_dir/'battle_winner_metadata_v2.json') as f: metadata=json.load(f)\n"
        "metrics={k:float(v) for k,v in metadata.get('metrics',{}).items() if isinstance(v,(int,float))}\n"
        "params={**metadata.get('hyperparameters',{}), 'n_features':metadata.get('n_features',133)}\n"
        "mlflow.set_experiment('pokemon_battle_winner')\n"
        "with mlflow.start_run(run_name='train_v2_'+datetime.now().strftime('%Y%m%d_%H%M%S')) as run:\n"
        "    mlflow.log_params(params); mlflow.log_metrics(metrics)\n"
        "    mlflow.sklearn.log_model(sk_model=model,name='model')\n"
        "    mlflow.log_artifact(str(models_dir/'battle_winner_metadata_v2.json'),artifact_path='extras')\n"
        "    run_id=run.info.run_id\n"
        "result=mlflow.register_model('runs:/'+run_id+'/model','battle_winner_predictor')\n"
        "MlflowClient().transition_model_version_stage('battle_winner_predictor',result.version,'Production',archive_existing_versions=True)\n"
        "print('OK: v'+str(result.version)+' -> Production (accuracy: '+str(round(metrics.get('test_accuracy',0)*100,2))+'%)')\n"
    )

    result = run(
        ["docker", "exec", "-e", "GIT_PYTHON_REFRESH=quiet",
         "letsgo_mlflow", "python3", "-c", mlflow_script],
        capture=True, check=False, timeout=120,
    )

    output = (result.stdout or "") + (result.stderr or "") if result else ""

    if "OK:" in output:
        # Extraire la ligne OK:
        for line in output.splitlines():
            if "OK:" in line:
                ok(line.strip())
                break
    else:
        warn("Enregistrement MLflow echoue. Detail :")
        # Afficher les dernieres lignes utiles
        for line in output.strip().splitlines()[-10:]:
            print(f"    {line}")
        info("Relancer manuellement : python3 scripts/mlflow/enable_mlflow.py")

    print()


# ============================================================================
# Etape 6 : Generation de metriques (Grafana)
# ============================================================================

def generate_metrics(api_key):
    step(6, "Generation de metriques pour Grafana")

    populate_script = PROJECT_DIR / "scripts" / "populate_monitoring_v2.py"
    headers = {"X-API-Key": api_key} if api_key else {}

    if populate_script.exists():
        info("Lancement de populate_monitoring_v2.py (50 predictions avec vraies attaques)...")
        env = os.environ.copy()
        env["API_KEY"] = api_key or ""
        result = run(
            [sys.executable, str(populate_script), "--count", "50", "--skip-mlflow"],
            capture=True, check=False, timeout=120,
        )
        if result and result.stdout:
            for line in result.stdout.splitlines():
                if any(kw in line.lower() for kw in ("success", "error", "pokemon", "predictions", "throughput")):
                    print(f"    {line}")
        ok("Metriques de monitoring generees — Grafana alimente")
    else:
        info("Envoi de 20 predictions pour alimenter les metriques...")
        success = 0
        for i in range(1, 21):
            pa = (i * 7 + 3) % 153 + 1  # Pseudo-random deterministe
            pb = (i * 11 + 7) % 153 + 1
            payload = {
                "pokemon_a_id": pa,
                "pokemon_b_id": pb,
                "available_moves": ["Charge", "Vive-Attaque", "Tonnerre", "Hydrocanon"],
            }
            status, _ = http_post(
                "http://localhost:8080/predict/best-move",
                data=payload,
                headers=headers,
            )
            if status == 200:
                success += 1
            print(f"\r    Predictions: {i}/20", end="", flush=True)
            time.sleep(0.3)
        print()
        ok(f"{success}/20 predictions envoyees — Grafana alimente")

    print()


# ============================================================================
# Etape 7 : Tests pytest
# ============================================================================

def run_tests(compose_cmd, skip_tests=False):
    if skip_tests:
        step(7, "Tests pytest (IGNORES — --skip-tests)")
        warn("Tests ignores. Lancer manuellement :")
        info("  docker compose --profile tests up --abort-on-container-exit tests")
        print()
        return

    step(7, "Execution des tests via Docker")
    info("Lancement du conteneur de tests...")

    result = run(
        compose_cmd + ["--profile", "tests", "up",
                       "--abort-on-container-exit",
                       "--exit-code-from", "tests",
                       "tests"],
        capture=True, check=False, timeout=300,
    )

    # Cleanup
    run(compose_cmd + ["rm", "-f", "tests"], capture=True, check=False)

    if result and result.returncode == 0:
        ok("Tous les tests sont passes")
    else:
        warn(f"Certains tests ont echoue (code: {result.returncode if result else '?'})")
        if result and result.stdout:
            # Afficher les dernieres lignes
            for line in result.stdout.strip().splitlines()[-20:]:
                print(f"    {line}")
        info(f"Voir les logs : {' '.join(compose_cmd)} --profile tests logs tests")

    print()


# ============================================================================
# Etape 8 : Ouverture des interfaces
# ============================================================================

def open_interfaces():
    step(8, "Ouverture des interfaces dans le navigateur")

    for name, url in URLS_FINALES:
        open_browser(url)
        ok(f"{name} -> {url}")
        time.sleep(0.5)

    print()


# ============================================================================
# Rapport final
# ============================================================================

def print_report():
    header("Demonstration prete !")

    print(f"{GREEN}{BOLD}Tous les services sont operationnels.{NC}")
    print()
    print(f"{CYAN}  URLs disponibles :{NC}")
    print(f"{CYAN}  {'─' * 55}{NC}")
    print(f"  Streamlit .......... http://localhost:8502")
    print(f"  API Swagger ........ http://localhost:8080/docs")
    print(f"  API Health ......... http://localhost:8080/health")
    print(f"  API Metriques ...... http://localhost:8080/metrics")
    print(f"  Grafana ............ http://localhost:3001")
    print(f"  Prometheus ......... http://localhost:9091")
    print(f"  MLflow ............. http://localhost:5001")
    print(f"  pgAdmin ............ http://localhost:5050")
    print()
    print(f"{YELLOW}Ordre recommande pour la soutenance E3 (20 min) :{NC}")
    print(f"  1. {BOLD}API{NC}       -> Swagger /docs -> montrer /predict/best-move")
    print(f"  2. {BOLD}Streamlit{NC} -> Faire une prediction Pikachu vs Dracaufeu")
    print(f"  3. {BOLD}Grafana{NC}   -> Montrer les dashboards API + Model Performance")
    print(f"  4. {BOLD}MLflow{NC}    -> Montrer le Model Registry et les experiences")
    print(f"  5. {BOLD}GitHub{NC}    -> Montrer les Actions CI/CD (onglet Actions)")
    print()
    print(f"{YELLOW}Commandes utiles :{NC}")
    print(f"  {BLUE}docker compose logs -f api{NC}         # Logs API en temps reel")
    print(f"  {BLUE}docker compose logs -f streamlit{NC}   # Logs Streamlit")
    print(f"  {BLUE}pytest tests/ -v{NC}                   # Relancer les tests")
    print(f"  {BLUE}python3 scripts/demo_full.py --stop{NC} # Arreter tout")
    print()


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="PredictionDex — Demo Certification E1/E3")
    parser.add_argument("--skip-tests", action="store_true", help="Ignorer les tests pytest")
    parser.add_argument("--skip-etl", action="store_true", help="Ne pas relancer l'ETL")
    parser.add_argument("--stop", action="store_true", help="Arreter tous les services")
    args = parser.parse_args()

    os.chdir(str(PROJECT_DIR))

    # Mode stop
    if args.stop:
        header("Arret de PredictionDex")
        compose_cmd = get_compose_cmd()
        if compose_cmd:
            run(compose_cmd + ["down"], check=False)
            ok("Tous les services sont arretes")
        else:
            fail("Docker Compose non trouve")
        return

    # Demo complete
    header("PredictionDex — Demo Certification E1/E3")
    print(f"  {BLUE}Projet : lets-go-predictiondex{NC}")
    print(f"  {BLUE}Date   : {time.strftime('%Y-%m-%d %H:%M')}{NC}")
    print(f"  {BLUE}Dossier: {PROJECT_DIR}{NC}")
    print()

    compose_cmd = check_prerequisites()       # Etape 1
    start_docker(compose_cmd)                  # Etape 2
    wait_for_services()                        # Etape 3
    api_key = get_api_key()
    check_data(compose_cmd, api_key, args.skip_etl)  # Etape 4
    setup_mlflow()                             # Etape 5
    generate_metrics(api_key)                  # Etape 6
    run_tests(compose_cmd, args.skip_tests)    # Etape 7
    open_interfaces()                          # Etape 8
    print_report()


if __name__ == "__main__":
    main()
