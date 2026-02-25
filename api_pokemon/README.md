# API Prédiction

L'endpoint principal est `POST /predict/best-move`. Il utilise un modèle XGBoost pour recommander la meilleure capacité à utiliser contre un adversaire dans Pokémon Let's Go.

## Comment ça marche

```
Client → POST /predict/best-move
  → prediction_route.py (route FastAPI)
  → prediction_service.py (logique métier)
    ├─ Charge le modèle ML (XGBoost + scalers)
    ├─ Récupère les données Pokémon depuis la BDD
    ├─ Calcule l'efficacité de type
    ├─ Pour chaque move : prépare les features, prédit la proba de victoire
    └─ Retourne les moves classés par probabilité
```

## Endpoints

### `POST /predict/best-move`

Prédit la meilleure capacité pour le Pokémon A contre le Pokémon B.

```json
// Request
{
  "pokemon_a_id": 7,
  "pokemon_b_id": 4,
  "available_moves": ["Charge", "Pistolet à O", "Hydrocanon"],
  "available_moves_b": null
}
```

- `pokemon_a_id` / `pokemon_b_id` : IDs des Pokémon attaquant et défenseur
- `available_moves` : moves dispo pour A (optionnel, sinon tous les moves appris)
- `available_moves_b` : moves connus de B (optionnel). Si omis, B utilise son meilleur move offensif par défaut. Permet une prédiction plus précise quand on connaît les capacités de l'adversaire.

```json
// Response
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
    }
  ]
}
```

### `GET /predict/model-info`

Retourne les infos du modèle ML chargé (type, version, nombre de features, métriques, hyperparamètres).

## Pipeline de prédiction

1. **Chargement du modèle** (singleton, une fois au démarrage) : charge `model.pkl`, `scalers.pkl` et `metadata.pkl` depuis `models/`.

2. **Récupération des données** : Pokémon A avec ses stats/types/moves, et la matrice d'efficacité des types.

3. **Score de chaque move** : `power * stab * type_mult * (accuracy/100) + priority * 50`. Le STAB (Same Type Attack Bonus) donne x1.5 si le type du move correspond au type du Pokémon.

4. **Feature engineering** (identique à l'entraînement) :
   - One-hot encoding des types (~102 colonnes)
   - Normalisation des stats (StandardScaler)
   - 6 features dérivées : stat_ratio, type_advantage_diff, effective_power_a/b, effective_power_diff, priority_advantage
   - Normalisation des features dérivées (2e StandardScaler)
   - Résultat : 135 features

5. **Prédiction** : `model.predict_proba()` donne la probabilité que A gagne. Les moves sont classés par proba décroissante.

## Exemple

Carapuce vs Salamèche avec Charge, Pistolet à O et Hydrocanon :

- **Hydrocanon** : 110 x 1.5 STAB x 2.0 type = 330, ~95% de victoire
- **Pistolet à O** : 40 x 1.5 x 2.0 = 120, ~75%
- **Charge** : 40 x 1 x 1 = 40, ~45%

Si on connaît les moves de Salamèche (`available_moves_b: ["Flammèche", "Charge"]`), la prédiction est plus fine car elle simule le combat avec ces moves précis au lieu d'assumer que B joue son meilleur move.

## Lancer l'API

```bash
source .venv/bin/activate
cd api_pokemon
uvicorn main:app --reload --port 8000
```

Doc interactive : http://localhost:8000/docs

## Fichiers

| Fichier | Rôle |
|---------|------|
| `routes/prediction_route.py` | Endpoints FastAPI |
| `services/prediction_service.py` | Logique métier + inférence ML |
| `main.py` | Point d'entrée |
