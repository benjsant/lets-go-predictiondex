"""
Configuration spécifique à la plateforme pour le pipeline Machine Learning.

Ce module détecte automatiquement la plateforme (Windows/Linux/Docker) et ajuste
les paramètres de parallélisation pour éviter les problèmes de mémoire
et de multiprocessing.

Problèmes résolus:
- Windows utilise 'spawn' pour multiprocessing (plus gourmand en mémoire que 'fork' sur Linux)
- Docker Desktop sur Windows a une RAM limitée (souvent 8 GB)
- Limitation automatique de n_jobs selon RAM disponible
- Garbage collector optimisé pour environnements contraints
"""

import gc
import multiprocessing
import os
import platform
import warnings
from typing import Dict


def is_running_in_docker() -> bool:
    """
    Détecte si le code s'exécute dans un container Docker.

    Returns:
        bool: True si dans Docker, False sinon
    """
    # Méthode 1: Fichier .dockerenv
    if os.path.exists('/.dockerenv'):
        return True

    # Méthode 2: Vérifier /proc/1/cgroup
    try:
        with open('/proc/1/cgroup', 'rt', encoding='utf-8') as f:
            return 'docker' in f.read()
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def get_available_memory_gb() -> float:
    """
    Retourne la RAM disponible en GB.

    Returns:
        float: RAM disponible en GB
    """
    try:
        # Linux/Docker: Lire /proc/meminfo
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        # Format: "MemTotal:       8194801 kB"
                        kb = int(line.split()[1])
                        return kb / (1024 * 1024)  # Convert KB to GB
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    try:
        # Windows: utiliser psutil si disponible
        import psutil
        return psutil.virtual_memory().total / (1024**3)
    except ImportError:
        pass

    # Fallback: estimer à 8 GB par défaut
    return 8.0


def get_platform_info() -> Dict[str, any]:
    """
    Retourne les informations sur la plateforme actuelle.

    Returns:
        Dict avec platform, cores, is_windows, is_docker, available_ram_gb
    """
    is_docker = is_running_in_docker()
    available_ram = get_available_memory_gb()

    return {
        'platform': platform.system(),
        'is_windows': os.name == 'nt' or platform.system() == 'Windows',
        'is_linux': platform.system() == 'Linux',
        'is_docker': is_docker,
        'cores': multiprocessing.cpu_count(),
        'python_version': platform.python_version(),
        'available_ram_gb': available_ram,
    }


def get_safe_n_jobs(max_percentage: float = 0.5) -> int:
    """
    Retourne un nombre de jobs sûr selon la plateforme ET la RAM disponible.

    Args:
        max_percentage: Pourcentage maximum de cœurs à utiliser sur Windows (default: 0.5 = 50%)

    Returns:
        int: Nombre de jobs optimisé

    Strategy:
        - Windows natif: 50% des cœurs (spawn gourmand)
        - Docker avec <10 GB RAM: 50% des cœurs (RAM limitée)
        - Linux/Docker avec >10 GB RAM: Tous les cœurs (-1)
    """
    info = get_platform_info()
    cores = info['cores']
    ram_gb = info['available_ram_gb']
    is_docker = info['is_docker']

    # Windows natif: toujours limiter
    if info['is_windows']:
        safe_jobs = max(1, min(int(cores * max_percentage), cores - 1))
        print(f"[Windows Native] n_jobs={safe_jobs}/{cores} coeurs (economie memoire)")
        return safe_jobs

    # Docker avec RAM limitée (typique de Docker Desktop sur Windows)
    if is_docker and ram_gb < 10:
        safe_jobs = max(1, min(int(cores * max_percentage), cores - 1))
        print(f"[Docker Limited RAM] n_jobs={safe_jobs}/{cores} coeurs (RAM={ram_gb:.1f}GB)")
        return safe_jobs

    # Linux ou Docker avec RAM suffisante
    env_label = "Docker" if is_docker else "Linux"
    print(f"[{env_label}] n_jobs=-1 (tous les coeurs, RAM={ram_gb:.1f}GB)")
    return -1


def get_safe_gridsearch_n_jobs() -> int:
    """
    Retourne un nombre de jobs pour GridSearchCV selon la plateforme ET la RAM.

    GridSearchCV est particulièrement gourmand en mémoire car il crée:
    - n_jobs processus parallèles
    - cv (ex: 3) folds par job
    - Chaque fold charge le dataset complet

    Returns:
        int: Nombre de jobs optimisé pour GridSearchCV
    """
    info = get_platform_info()
    cores = info['cores']
    ram_gb = info['available_ram_gb']
    is_docker = info['is_docker']

    # Windows natif ou Docker avec RAM très limitée (<10 GB)
    if info['is_windows'] or (is_docker and ram_gb < 10):
        # Très conservateur pour GridSearchCV
        # Utiliser 1/3 des cœurs ou max 4
        safe_jobs = max(1, min(cores // 3, 4))
        return safe_jobs

    # Docker ou Linux avec RAM modérée (10-16 GB)
    if ram_gb < 16:
        # Modérément conservateur
        return max(1, cores // 2)

    # Docker ou Linux avec RAM importante (>16 GB)
    # Peut être plus agressif
    return max(1, cores // 2)


def configure_memory_optimization():
    """
    Configure les optimisations mémoire pour Windows.

    Actions:
        - Active garbage collector agressif sur Windows
        - Désactive certains warnings qui polluent les logs
        - Configure les seuils de GC pour libérer la mémoire plus souvent
    """
    info = get_platform_info()

    if info['is_windows']:
        # Garbage collector plus agressif (collecte plus fréquente)
        # Paramètres: (threshold0, threshold1, threshold2)
        # Par défaut: (700, 10, 10)
        # Windows: (500, 5, 5) = collecte plus agressive
        gc.set_threshold(500, 5, 5)

        # Supprime les warnings UserWarning pour log plus propre
        warnings.filterwarnings('ignore', category=UserWarning)

        print("[Windows] Optimisations memoire activees (GC agressif)")
    else:
        print("[Linux] Configuration memoire standard (GC standard)")


def get_recommended_grid_type() -> str:
    """
    Retourne le type de grille GridSearch recommandé selon la plateforme et RAM.

    Returns:
        str: 'fast' pour environnements limités, 'extended' si RAM suffisante
    """
    info = get_platform_info()
    ram_gb = info['available_ram_gb']

    # Windows natif ou Docker avec RAM limitée
    if info['is_windows'] or (info['is_docker'] and ram_gb < 10):
        return 'fast'

    # Docker/Linux avec RAM modérée (10-16 GB)
    if ram_gb < 16:
        return 'fast'

    # Docker/Linux avec RAM importante (>16 GB)
    return 'extended'


def print_platform_summary():
    """Affiche un résumé de la configuration plateforme."""
    info = get_platform_info()
    safe_jobs = get_safe_n_jobs()
    grid_jobs = get_safe_gridsearch_n_jobs()

    print("\n" + "=" * 70)
    print("CONFIGURATION PLATEFORME")
    print("=" * 70)
    print(f"OS: {info['platform']}")
    print(f"Python: {info['python_version']}")
    print(f"Environment: {'Docker' if info['is_docker'] else 'Native'}")
    print(f"Coeurs CPU: {info['cores']}")
    print(f"RAM disponible: {info['available_ram_gb']:.1f} GB")
    print(f"n_jobs standard: {safe_jobs}")
    print(f"n_jobs GridSearchCV: {grid_jobs}")
    print(f"Grille recommandee: {get_recommended_grid_type()}")
    print("=" * 70 + "\n")


# ================================================================
# CONFIGURATION PAR DÉFAUT À L'IMPORT
# ================================================================

# Détecte et configure automatiquement au chargement du module
PLATFORM_INFO = get_platform_info()
SAFE_N_JOBS = get_safe_n_jobs()
SAFE_GRIDSEARCH_N_JOBS = get_safe_gridsearch_n_jobs()
RECOMMENDED_GRID_TYPE = get_recommended_grid_type()

# Active les optimisations mémoire si Windows
configure_memory_optimization()
