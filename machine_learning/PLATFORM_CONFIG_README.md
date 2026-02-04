# Configuration Multiplateforme (Windows / Linux)

## Problème résolu

Le pipeline de machine learning utilisait `n_jobs=-1` partout, ce qui causait des **problèmes de mémoire sur Windows** :

### Différences Windows vs Linux

| Aspect | Linux | Windows |
|--------|-------|---------|
| Multiprocessing | `fork` (efficace) | `spawn` (gourmand en RAM) |
| Processus fils | Partage mémoire | Copie complète de l'instance Python |
| RAM nécessaire | Modérée | **Très élevée** |
| n_jobs=-1 sûr ? | ✅ Oui | ❌ Non (risque saturation) |

### Symptômes sur Windows

- Processus qui crash sans message clair
- Consommation RAM excessive
- Lenteur extrême ou freeze
- GridSearchCV qui ne termine jamais

## Solution implémentée

### 1. Fichier `platform_config.py`

Nouveau module qui détecte automatiquement la plateforme et ajuste les paramètres :

```python
from machine_learning.platform_config import (
    SAFE_N_JOBS,              # n_jobs pour XGBoost
    SAFE_GRIDSEARCH_N_JOBS,   # n_jobs pour GridSearchCV
)
```

**Valeurs automatiques :**
- **Windows** :
  - `SAFE_N_JOBS = 6` (50% des cœurs sur PC 12 cœurs)
  - `SAFE_GRIDSEARCH_N_JOBS = 4` (33% des cœurs)
  - Garbage collector agressif activé

- **Linux** :
  - `SAFE_N_JOBS = -1` (tous les cœurs)
  - `SAFE_GRIDSEARCH_N_JOBS = -1` ou 50% selon RAM disponible

### 2. Modifications appliquées

**Fichiers modifiés :**
- ✅ `machine_learning/config.py` - Utilise `SAFE_N_JOBS` au lieu de `-1`
- ✅ `machine_learning/run_machine_learning.py` - GridSearchCV avec `SAFE_GRIDSEARCH_N_JOBS`
- ✅ `machine_learning/train_model.py` - GridSearchCV avec `SAFE_GRIDSEARCH_N_JOBS`

**Changements clés :**

```python
# AVANT (problématique sur Windows)
n_jobs: int = -1

# APRÈS (auto-ajusté)
n_jobs: int = SAFE_N_JOBS  # 6 sur Windows, -1 sur Linux
```

## Vérifier la configuration

```bash
python machine_learning/test_platform_config.py
```

**Sortie attendue sur Windows :**
```
[Windows] n_jobs=6/12 coeurs (economie memoire)
[Windows] Optimisations memoire activees (GC agressif)

OS: Windows
Cœurs CPU: 12
n_jobs standard: 6
n_jobs GridSearchCV: 4
Grille recommandée: fast
```

## Commandes recommandées

### Sur Windows (16 GB RAM)

**Option 1 : Sans GridSearch (RECOMMANDÉ)**
```bash
# Rapide, faible consommation RAM (~2-4 GB)
python machine_learning/run_machine_learning.py --mode=all
```

**Option 2 : Avec GridSearch FAST**
```bash
# Tuning modéré, consommation RAM acceptable (~4-6 GB)
python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type fast
```

**⚠️ NON RECOMMANDÉ : GridSearch EXTENDED**
```bash
# Éviter sur Windows (12-20 GB RAM requis)
# python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type extended
```

### Sur Linux (>=16 GB RAM)

**Toutes les options disponibles :**
```bash
# Pipeline complet avec tuning étendu
python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type extended
```

## Comparaison des configurations

| Configuration | Combinaisons | RAM estimée (Win) | RAM estimée (Linux) | Temps |
|---------------|--------------|-------------------|---------------------|-------|
| Sans GridSearch | 1 | ~2-4 GB | ~2-3 GB | 5-10 min |
| GridSearch FAST | 12 (2×3×2) | ~4-6 GB | ~3-4 GB | 15-30 min |
| GridSearch EXTENDED | 243 (3×3×3×3×3) | **12-20 GB** ⚠️ | ~8-12 GB | 2-4 h |

## Optimisations mémoire Windows

Le module `platform_config.py` active automatiquement sur Windows :

1. **Garbage Collector agressif**
   ```python
   gc.set_threshold(500, 5, 5)  # Au lieu de (700, 10, 10)
   ```

2. **Limitation du multiprocessing**
   - XGBoost : 50% des cœurs
   - GridSearchCV : 33% des cœurs
   - Évite la surcharge mémoire

3. **Warnings désactivés**
   ```python
   warnings.filterwarnings('ignore', category=UserWarning)
   ```

## Désactiver la détection automatique (avancé)

Si vous voulez forcer une configuration :

```python
# Dans votre script
import os
os.environ['FORCE_N_JOBS'] = '4'  # Forcer 4 jobs

# Puis importer
from machine_learning.config import XGBOOST_PARAMS
```

Ou modifier directement dans `platform_config.py` :

```python
def get_safe_n_jobs(max_percentage: float = 0.5):
    return 4  # Valeur fixe
```

## Diagnostic des problèmes

### Le script crash sans message

**Cause probable :** Manque de RAM, trop de processus parallèles

**Solution :**
```bash
# Réduire encore plus le nombre de jobs
# Modifier platform_config.py, ligne 60 :
safe_jobs = max(1, cores // 4)  # Au lieu de cores // 2
```

### GridSearchCV très lent

**Cause probable :** Trop de combinaisons ou pas assez de cœurs utilisés

**Solution :**
```bash
# Utiliser grille FAST au lieu de EXTENDED
python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type fast
```

### Erreur "Memory Error" ou "Out of Memory"

**Cause :** Dataset trop grand ou trop de processus parallèles

**Solution :**
```bash
# Réduire la taille du dataset
python machine_learning/run_machine_learning.py --mode=dataset --dataset-version v2 --scenario-type best_move

# Puis entraîner sans GridSearch
python machine_learning/run_machine_learning.py --mode=train --dataset-version v2
```

## Tests automatisés

Les tests CI/CD utilisent automatiquement la configuration optimale :

```yaml
# .github/workflows/ci.yml
- name: Run ML pipeline
  run: |
    python machine_learning/run_machine_learning.py --mode=all --grid-type fast
    # Auto-détection : fast sur CI runners (ressources limitées)
```

## Support

Si vous rencontrez des problèmes :

1. Vérifier la configuration : `python machine_learning/test_platform_config.py`
2. Vérifier la RAM disponible : Gestionnaire des tâches Windows
3. Essayer avec `--grid-type fast` ou sans `--tune-hyperparams`
4. Ouvrir une issue GitHub avec les logs complets

## Changelog

- **2026-02-04** : Ajout détection automatique Windows/Linux
- **2026-02-04** : Optimisations mémoire pour Windows
- **2026-02-04** : Tests de configuration plateforme
