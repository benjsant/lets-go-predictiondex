"""
Platform-specific configuration for the Machine Learning pipeline.

This module automatically detects the platform (Windows/Linux/Docker) and adjusts
parallelization parameters to avoid memory issues and multiprocessing problems.

Issues addressed:
- Windows uses 'spawn' for multiprocessing (more memory-intensive than 'fork' on Linux)
- Docker Desktop on Windows has limited RAM (often 8 GB)
- Automatic n_jobs limitation based on available RAM
- Optimized garbage collector for constrained environments
"""

import gc
import multiprocessing
import os
import platform
import warnings
from typing import Dict


def is_running_in_docker() -> bool:
    """
    Detect if code is running inside a Docker container.

    Returns:
        bool: True if in Docker, False otherwise
    """
    # Method 1: Check .dockerenv file
    if os.path.exists('/.dockerenv'):
        return True

    # Method 2: Check /proc/1/cgroup
    try:
        with open('/proc/1/cgroup', 'rt', encoding='utf-8') as f:
            return 'docker' in f.read()
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def get_available_memory_gb() -> float:
    """
    Return available RAM in GB.

    Returns:
        float: Available RAM in GB
    """
    try:
        # Linux/Docker: Read /proc/meminfo
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
        # Windows: use psutil if available
        import psutil
        return psutil.virtual_memory().total / (1024**3)
    except ImportError:
        pass

    # Fallback: assume 8 GB by default
    return 8.0


def get_platform_info() -> Dict[str, any]:
    """
    Return information about the current platform.

    Returns:
        Dict with platform, cores, is_windows, is_docker, available_ram_gb
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
    Return a safe number of jobs based on platform AND available RAM.

    Args:
        max_percentage: Maximum percentage of cores to use on Windows (default: 0.5 = 50%)

    Returns:
        int: Optimized number of jobs

    Strategy:
        - Native Windows: 50% of cores (spawn is memory-intensive)
        - Docker with <10 GB RAM: 50% of cores (limited RAM)
        - Linux/Docker with >10 GB RAM: All cores (-1)
    """
    info = get_platform_info()
    cores = info['cores']
    ram_gb = info['available_ram_gb']
    is_docker = info['is_docker']

    # Native Windows: always limit
    if info['is_windows']:
        safe_jobs = max(1, min(int(cores * max_percentage), cores - 1))
        print(f"[Windows Native] n_jobs={safe_jobs}/{cores} cores (memory saving)")
        return safe_jobs

    # Docker with limited RAM (typical of Docker Desktop on Windows)
    if is_docker and ram_gb < 10:
        safe_jobs = max(1, min(int(cores * max_percentage), cores - 1))
        print(f"[Docker Limited RAM] n_jobs={safe_jobs}/{cores} cores (RAM={ram_gb:.1f}GB)")
        return safe_jobs

    # Linux or Docker with sufficient RAM
    env_label = "Docker" if is_docker else "Linux"
    print(f"[{env_label}] n_jobs=-1 (all cores, RAM={ram_gb:.1f}GB)")
    return -1


def get_safe_gridsearch_n_jobs() -> int:
    """
    Return a safe number of jobs for GridSearchCV based on platform AND RAM.

    GridSearchCV is particularly memory-intensive because it creates:
    - n_jobs parallel processes
    - cv (e.g., 3) folds per job
    - Each fold loads the complete dataset

    Returns:
        int: Optimized number of jobs for GridSearchCV
    """
    info = get_platform_info()
    cores = info['cores']
    ram_gb = info['available_ram_gb']
    is_docker = info['is_docker']

    # Native Windows or Docker with very limited RAM (<10 GB)
    if info['is_windows'] or (is_docker and ram_gb < 10):
        # Very conservative for GridSearchCV
        # Use 1/3 of cores or max 4
        safe_jobs = max(1, min(cores // 3, 4))
        return safe_jobs

    # Docker or Linux with moderate RAM (10-16 GB)
    if ram_gb < 16:
        # Moderately conservative
        return max(1, cores // 2)

    # Docker or Linux with ample RAM (>16 GB)
    # Can be more aggressive
    return max(1, cores // 2)


def configure_memory_optimization():
    """
    Configure memory optimizations for Windows.

    Actions:
        - Enable aggressive garbage collector on Windows
        - Disable certain warnings that pollute logs
        - Configure GC thresholds to free memory more often
    """
    info = get_platform_info()

    if info['is_windows']:
        # More aggressive garbage collector (more frequent collection)
        # Parameters: (threshold0, threshold1, threshold2)
        # Default: (700, 10, 10)
        # Windows: (500, 5, 5) = more aggressive collection
        gc.set_threshold(500, 5, 5)

        # Suppress UserWarning for cleaner logs
        warnings.filterwarnings('ignore', category=UserWarning)

        print("[Windows] Memory optimizations enabled (aggressive GC)")
    else:
        print("[Linux] Standard memory configuration (standard GC)")


def get_recommended_grid_type() -> str:
    """
    Return recommended GridSearch grid type based on platform and RAM.

    Returns:
        str: 'fast' for limited environments, 'extended' if RAM is sufficient
    """
    info = get_platform_info()
    ram_gb = info['available_ram_gb']

    # Native Windows or Docker with limited RAM
    if info['is_windows'] or (info['is_docker'] and ram_gb < 10):
        return 'fast'

    # Docker/Linux with moderate RAM (10-16 GB)
    if ram_gb < 16:
        return 'fast'

    # Docker/Linux with high RAM (>16 GB)
    return 'extended'


def print_platform_summary():
    """Print a summary of the platform configuration."""
    info = get_platform_info()
    safe_jobs = get_safe_n_jobs()
    grid_jobs = get_safe_gridsearch_n_jobs()

    print("\n" + "=" * 70)
    print("PLATFORM CONFIGURATION")
    print("=" * 70)
    print(f"OS: {info['platform']}")
    print(f"Python: {info['python_version']}")
    print(f"Environment: {'Docker' if info['is_docker'] else 'Native'}")
    print(f"CPU cores: {info['cores']}")
    print(f"Available RAM: {info['available_ram_gb']:.1f} GB")
    print(f"n_jobs standard: {safe_jobs}")
    print(f"n_jobs GridSearchCV: {grid_jobs}")
    print(f"Recommended grid: {get_recommended_grid_type()}")
    print("=" * 70 + "\n")


# ================================================================
# DEFAULT CONFIGURATION ON IMPORT
# ================================================================

# Automatically detect and configure on module load
PLATFORM_INFO = get_platform_info()
SAFE_N_JOBS = get_safe_n_jobs()
SAFE_GRIDSEARCH_N_JOBS = get_safe_gridsearch_n_jobs()
RECOMMENDED_GRID_TYPE = get_recommended_grid_type()

# Enable memory optimizations if on Windows
configure_memory_optimization()
