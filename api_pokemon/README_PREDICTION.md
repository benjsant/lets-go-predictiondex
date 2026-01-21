# API Prédiction - Endpoint `/predict/best-move`

## Vue d'ensemble

L'endpoint `/predict/best-move` utilise un modèle XGBoost entraîné (94.24% accuracy) pour recommander la meilleure capacité à utiliser contre un adversaire dans Pokémon Let's Go.

## Architecture

```
Client → POST /predict/best-move
           ↓
    prediction_route.py (FastAPI route)
           ↓
    prediction_service.py (Business logic)
           ↓
    ├─→ Charge modèle ML (XGBoost + scalers)
    ├─→ Récupère données Pokémon (DB)
    ├─→ Calcule efficacité de type
    ├─→ Pour chaque move:
    │    ├─→ Prépare features (38 colonnes raw)
    │    ├─→ Apply feature engineering (133 colonnes finales)
    │    └─→ Prédit win probability
    └─→ Retourne moves classés par probabilité
```

## Endpoints

### `POST /predict/best-move`

Prédit la meilleure capacité pour le Pokémon A contre le Pokémon B.

**Request Body:**
```json
{
  "pokemon_a_id": 7,
  "pokemon_b_id": 4,
  "available_moves": ["Charge", "Pistolet à O", "Hydrocanon"]
}
```

**Response:**
```json
{
  "pokemon_a_id": 7,
  "pokemon_a_name": "Carapuce",
  "pokemon_b_id": 4,
  "pokemon_b_name": "Salamèche",
  "recommended_move": "Hydrocanon",
  "win_probability": 0.95,
  "all_moves": [
    {
      "move_name": "Hydrocanon",
      "move_type": "eau",
      "move_power": 110,
      "effective_power": 110.0,
      "type_multiplier": 2.0,
      "stab": 1.5,
      "priority": 0,
      "score": 330.0,
      "win_probability": 0.95,
      "predicted_winner": "A"
    },
    ...
  ]
}
```

### `GET /predict/model-info`

Retourne les informations sur le modèle ML chargé.

**Response:**
```json
{
  "model_type": "XGBClassifier",
  "version": "v1",
  "n_features": 133,
  "metrics": {
    "test_accuracy": 0.9424,
    "test_precision": 0.9427,
    "test_recall": 0.9421,
    "test_f1": 0.9424,
    "test_roc_auc": 0.9896
  },
  "trained_at": "2026-01-21T12:31:17",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 8,
    "learning_rate": 0.1,
    ...
  }
}
```

## Pipeline de Prédiction

### 1. Chargement du Modèle (Singleton)

```python
from api_pokemon.services import prediction_service

# Le modèle est chargé une seule fois au démarrage
model = prediction_service.prediction_model
model.load()  # Charge model, scalers, metadata
```

**Artifacts chargés:**
- `models/battle_winner_model_v1.pkl` (XGBoost, 983K)
- `models/battle_winner_scalers_v1.pkl` (2 StandardScalers, 1.7K)
- `models/battle_winner_metadata.pkl` (métadonnées, 2.8K)

### 2. Récupération des Données

```python
# Récupère Pokémon A avec stats, types, moves
pokemon_a = get_pokemon_with_details(db, pokemon_a_id)

# Récupère efficacité des types depuis la DB
type_effectiveness = load_type_effectiveness(db)
```

### 3. Sélection du Meilleur Move

Pour chaque move disponible:

```python
# Calcule le score du move contre le défenseur
score = power * stab * type_mult * (accuracy/100) + priority * 50

# STAB = Same Type Attack Bonus (1.5x si type du move = type du Pokémon)
# type_mult = Multiplicateur de type (0.25x, 0.5x, 1x, 2x, ou 4x)
# priority = Priorité du move (-5 à +2)
```

### 4. Préparation des Features

**Features raw (38 colonnes):**
- Stats A: hp, attack, defense, sp_attack, sp_defense, speed
- Stats B: hp, attack, defense, sp_attack, sp_defense, speed
- Types A: type_1, type_2
- Types B: type_1, type_2
- Move A: power, type, priority, stab, type_mult
- Move B: power, type, priority, stab, type_mult
- Computed: speed_diff, hp_diff, a_total_stats, b_total_stats, a_moves_first

### 5. Feature Engineering

**Pipeline (identique à l'entraînement):**

1. **One-hot encoding** des types → ~102 colonnes
2. **Normalisation** des stats numériques (StandardScaler #1)
3. **Création de 6 features dérivées**:
   - `stat_ratio` = a_total_stats / (b_total_stats + 1)
   - `type_advantage_diff` = a_type_mult - b_type_mult
   - `effective_power_a` = power_a × stab_a × type_mult_a
   - `effective_power_b` = power_b × stab_b × type_mult_b
   - `effective_power_diff` = effective_power_a - effective_power_b
   - `priority_advantage` = priority_a - priority_b
4. **Normalisation** des features dérivées (StandardScaler #2)

**Résultat:** 133 features finales

### 6. Prédiction

```python
# Prédit la classe (0 = B gagne, 1 = A gagne)
prediction = model.predict(features)

# Prédit les probabilités [prob_B_wins, prob_A_wins]
probabilities = model.predict_proba(features)

win_probability = probabilities[0][1]  # Prob que A gagne
```

### 7. Ranking

Les moves sont classés par `win_probability` décroissante.

## Cas d'Usage

### Recommandation pour Enfant

L'application aide un enfant à choisir la meilleure capacité:

1. L'enfant voit un adversaire en combat
2. Il sélectionne son Pokémon et l'adversaire
3. L'app affiche la liste de ses moves
4. L'API prédit la meilleure move
5. L'app affiche: "Utilise **Hydrocanon** ! (95% de chances de gagner)"

### Exemple Concret

**Situation**: Carapuce (niveau 50) contre Salamèche (niveau 50)

**Moves disponibles**: Charge, Pistolet à O, Hydrocanon

**Prédiction:**
1. **Hydrocanon** (Eau, 110 puissance)
   - STAB: 1.5x (Carapuce est type Eau)
   - Type mult: 2x (Eau super efficace contre Feu)
   - Puissance effective: 110 × 1.5 × 2 = 330
   - **Win probability: 95%**

2. **Pistolet à O** (Eau, 40 puissance)
   - Puissance effective: 40 × 1.5 × 2 = 120
   - Win probability: 75%

3. **Charge** (Normal, 40 puissance)
   - Puissance effective: 40 × 1 × 1 = 40
   - Win probability: 45%

**Recommandation**: "Utilise Hydrocanon !"

## Performance

### Latence

- **Chargement du modèle**: ~100ms (une fois au démarrage)
- **Prédiction par move**: ~50-100ms
- **Total pour 4 moves**: ~200-400ms

### Précision

- **Test Accuracy**: 94.24%
- **ROC-AUC**: 98.96%
- **F1-Score**: 94.24%

Le modèle prédit correctement le gagnant dans 94% des cas sur des matchups qu'il n'a jamais vus.

## Limites & Améliorations Futures

### Limites Actuelles

1. **Pas d'aléatoire**: Le modèle ne tient pas compte des coups critiques, miss, ou autres aléas
2. **Moves exclus**: Certains moves (Bluff, Croc Fatal, moves réactifs) sont exclus du dataset
3. **Simulation déterministe**: Le combat est simulé de manière déterministe

### Améliorations Possibles

1. **Ajout d'aléatoire**: Simuler des coups critiques et miss (post-E3)
2. **Contexte de combat**: Tenir compte des conditions météo, statuts, etc.
3. **Historique de combat**: Utiliser les moves précédents pour ajuster les prédictions
4. **Explainability**: Ajouter SHAP values pour expliquer les prédictions

## Code Examples

### Utilisation Directe du Service

```python
from api_pokemon.services import prediction_service
from core.db.session import SessionLocal

db = SessionLocal()

result = prediction_service.predict_best_move(
    db=db,
    pokemon_a_id=7,  # Carapuce
    pokemon_b_id=4,  # Salamèche
    available_moves_a=["Charge", "Pistolet à O", "Hydrocanon"]
)

print(f"Recommended: {result['recommended_move']}")
print(f"Win probability: {result['win_probability']*100:.1f}%")

db.close()
```

### Appel HTTP (curl)

```bash
curl -X POST "http://localhost:8000/predict/best-move" \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 7,
    "pokemon_b_id": 4,
    "available_moves": ["Charge", "Pistolet à O", "Hydrocanon"]
  }'
```

### Appel HTTP (Python requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/predict/best-move",
    json={
        "pokemon_a_id": 7,
        "pokemon_b_id": 4,
        "available_moves": ["Charge", "Pistolet à O", "Hydrocanon"]
    }
)

result = response.json()
print(f"Recommended: {result['recommended_move']}")
```

## Tests

Voir `test_prediction_api.py` pour les tests unitaires.

```bash
# Lancer les tests
source .venv/bin/activate
POSTGRES_HOST=localhost python test_prediction_api.py
```

## Démarrage de l'API

```bash
# Activer l'environnement
source .venv/bin/activate

# Démarrer le serveur
cd api_pokemon
uvicorn main:app --reload --port 8000
```

**Documentation interactive**: http://localhost:8000/docs

## Fichiers Clés

| Fichier | Description |
|---------|-------------|
| `api_pokemon/routes/prediction_route.py` | Définition des endpoints FastAPI |
| `api_pokemon/services/prediction_service.py` | Logique métier et ML inference |
| `api_pokemon/main.py` | Point d'entrée de l'application |
| `models/battle_winner_model_v1.pkl` | Modèle XGBoost entraîné |
| `models/battle_winner_scalers_v1.pkl` | 2 StandardScalers pour normalisation |
| `models/battle_winner_metadata.pkl` | Métadonnées du modèle |
| `test_prediction_api.py` | Tests unitaires |

## Support

Pour toute question ou bug, consulter la documentation ML dans `machine_learning/README.md`.
