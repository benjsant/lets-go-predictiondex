# 🗜️ Optimisation Taille Modèles ML

## 🚨 Problème

Le fichier `battle_winner_rf_v2.pkl` fait **401 MB** :
- ❌ Trop gros pour GitHub (limite 100 MB)
- ❌ Ralentit le chargement de l'API
- ❌ Consomme beaucoup de RAM

**Cause :** RandomForest stocke tous les arbres en mémoire (100 arbres × 15 niveaux de profondeur).

---

## ✅ Solutions Appliquées

### 1. **Compression avec joblib** (Réduction 5-10x)

#### Modification : `machine_learning/run_machine_learning.py`

**Avant (pickle standard) :**
```python
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
# Résultat : 401 MB
```

**Après (joblib compressé) :**
```python
import joblib

if model_type_name == 'RandomForestClassifier':
    joblib.dump(model, model_path, compress=('zlib', 9))
    # Résultat attendu : ~40-80 MB (5-10x plus petit)
else:
    # XGBoost reste en pickle (déjà compact)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
```

**Impact :**
- ✅ Fichier 5-10x plus petit
- ✅ Même précision du modèle
- ✅ Temps de chargement similaire
- ✅ Compatible pickle (fallback)

---

### 2. **Réduction Hyperparamètres RandomForest**

#### Modification : `machine_learning/run_machine_learning.py`

**Avant :**
```python
DEFAULT_RF_PARAMS = {
    'n_estimators': 100,      # 100 arbres
    'max_depth': 15,          # 15 niveaux
    'min_samples_split': 5,
    'min_samples_leaf': 2,
}
```

**Après :**
```python
DEFAULT_RF_PARAMS = {
    'n_estimators': 50,       # 50 arbres (-50%)
    'max_depth': 12,          # 12 niveaux (-20%)
    'min_samples_split': 10,  # Augmenté (moins de splits)
    'min_samples_leaf': 4,    # Augmenté (moins de feuilles)
}
```

**Impact :**
- ✅ Modèle ~2-3x plus petit
- ⚠️ Légère baisse de précision (~1-2%)
- ✅ Entraînement 2x plus rapide
- ✅ Prévient l'overfitting

---

### 3. **Compatibilité API** (Chargement joblib + pickle)

#### Modification : `api_pokemon/services/prediction_service.py`

**Ajout :**
```python
import joblib

def load(self):
    """Load model artifacts from disk (supports both formats)."""
    try:
        # Essayer joblib d'abord (compressé)
        self._model = joblib.load(model_path)
    except Exception:
        # Fallback pickle (anciens modèles)
        with open(model_path, 'rb') as f:
            self._model = pickle.load(f)
```

**Impact :**
- ✅ Compatible avec anciens modèles pickle
- ✅ Compatible avec nouveaux modèles joblib
- ✅ Pas de régression

---

## 📊 Résultats Attendus

### Taille Fichiers

| Fichier | Avant | Après | Gain |
|---------|-------|-------|------|
| `battle_winner_rf_v2.pkl` | 401 MB | ~50-80 MB | **5-8x** |
| `battle_winner_model_v2.pkl` (XGBoost) | 2.8 MB | 2.8 MB | - |
| `battle_winner_scalers_v2.pkl` | 1.7 KB | 1.7 KB | - |
| `battle_winner_metadata_v2.pkl` | 3.4 KB | 3.4 KB | - |

### Performance Modèle

| Métrique | RandomForest 100/15 | RandomForest 50/12 | Δ |
|----------|---------------------|-------------------|---|
| **Accuracy** | 94.46% | ~93.5% | -1% |
| **Taille** | 401 MB | ~60 MB | **-85%** |
| **Temps entraînement** | ~5 min | ~2.5 min | **-50%** |
| **RAM API** | 500 MB | 100 MB | **-80%** |

---

## 🚀 Comment Appliquer

### Option 1 : Re-entraîner avec Compression

```bash
# Activer venv
source .venv/bin/activate

# Re-entraîner RandomForest v2 (nouveau params + compression)
python -m machine_learning.run_machine_learning \
    --model-type random_forest \
    --version v2 \
    --dataset-version v2
```

**Durée :** ~3-5 minutes  
**Résultat :** Nouveau `battle_winner_model_v2.pkl` (~60 MB)

---

### Option 2 : Compresser Modèle Existant

```bash
# Script de compression (converti pickle → joblib)
python compress_ml_models.py --version v2
```

**Durée :** ~30 secondes  
**Résultat :** Même modèle, format compressé

---

## 🧪 Validation

### 1. Vérifier Taille
```bash
ls -lh models/battle_winner_model_v2.pkl
# Avant : 401M
# Après : ~60M
```

### 2. Tester API
```bash
# Démarrer API
docker compose up -d api

# Test prédiction
curl -X POST http://localhost:8000/api/v1/predict/battle-winner \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_1_id": 25,
    "pokemon_2_id": 6,
    "move_1_id": 85,
    "move_2_id": 52
  }'
```

**Résultat attendu :** Même prédiction qu'avant

### 3. Comparer Métriques
```bash
# Avant
cat models/battle_winner_metadata_v2.pkl | grep accuracy
# 94.46%

# Après re-entraînement
cat models/battle_winner_metadata_v2.pkl | grep accuracy
# ~93.5% (acceptable)
```

---

## 📝 Recommandations

### Quand utiliser RandomForest ?
- ✅ **Expérimentation** (notebooks, prototypes)
- ✅ **Feature importance** (analyse)
- ❌ **Production** (préférer XGBoost)

### Quand utiliser XGBoost ?
- ✅ **Production** (compact, rapide)
- ✅ **Performances similaires** à RF
- ✅ **Modèles <5 MB** (déjà compact)

**Actuel :**
- `battle_winner_model_v2.pkl` (XGBoost) = 2.8 MB ✅
- `battle_winner_rf_v2.pkl` (RandomForest) = 401 MB ❌

**Recommandation :** Utiliser XGBoost en production, garder RF pour expérimentations uniquement.

---

## 🔧 Alternative : Git LFS

Si tu veux vraiment versionner les gros fichiers :

```bash
# Installer Git LFS
sudo apt install git-lfs
git lfs install

# Tracker les .pkl
git lfs track "models/*.pkl"
git add .gitattributes

# Les .pkl seront maintenant dans Git LFS (stockage distant)
git add models/battle_winner_rf_v2.pkl
git commit -m "feat: add RF model with Git LFS"
git push
```

**Avantages :**
- ✅ Versionne les gros fichiers
- ✅ Pas de limite 100 MB

**Inconvénients :**
- ❌ Coût stockage GitHub LFS
- ❌ Complexité setup CI/CD
- ❌ Clone plus lents

---

## ✅ Checklist

- [x] Import `joblib` ajouté dans `run_machine_learning.py`
- [x] Export modèle avec compression joblib (RandomForest)
- [x] Réduction hyperparamètres RandomForest
- [x] Compatibilité chargement API (joblib + pickle fallback)
- [ ] Re-entraîner modèle avec nouvelles config
- [ ] Valider taille fichier (<100 MB)
- [ ] Tester API predictions
- [ ] Commit + push

---

## 📚 Références

- [joblib documentation](https://joblib.readthedocs.io/en/latest/persistence.html)
- [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html)
- [Git LFS](https://git-lfs.github.com/)
