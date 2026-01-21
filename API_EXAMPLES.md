# API Examples - Let's Go PredictionDex

Ce document contient des exemples concrets d'utilisation de l'API avec des résultats réels.

## Table des Matières

1. [Exemple 1: Carapuce vs Salamèche (Type avantageux)](#exemple-1-carapuce-vs-salamèche)
2. [Exemple 2: Bulbizarre vs Salamèche (Type désavantageux)](#exemple-2-bulbizarre-vs-salamèche)
3. [Exemple 3: Pikachu vs Léviator (Électrique super efficace)](#exemple-3-pikachu-vs-léviator)
4. [Exemple 4: Détails d'un Pokémon](#exemple-4-détails-dun-pokémon)
5. [Exemple 5: Informations du Modèle ML](#exemple-5-informations-du-modèle-ml)

---

## Exemple 1: Carapuce vs Salamèche

**Contexte**: Carapuce (Type Eau) contre Salamèche (Type Feu). L'Eau est **super efficace** contre le Feu (2x).

### Requête

```bash
curl -X POST http://localhost:8000/predict/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 7,
    "pokemon_b_id": 4,
    "available_moves": ["Charge", "Pistolet à O", "Hydrocanon", "Surf"]
  }'
```

### Réponse

```json
{
    "pokemon_a_id": 7,
    "pokemon_a_name": "Carapuce",
    "pokemon_b_id": 4,
    "pokemon_b_name": "Salamèche",
    "recommended_move": "Hydrocanon",
    "win_probability": 0.9975,
    "all_moves": [
        {
            "move_name": "Hydrocanon",
            "move_type": "Eau",
            "move_power": 110,
            "effective_power": 110.0,
            "type_multiplier": 2.0,
            "stab": 1.5,
            "priority": 0,
            "score": 264.0,
            "win_probability": 0.9975,
            "predicted_winner": "A"
        },
        {
            "move_name": "Surf",
            "move_type": "Eau",
            "move_power": 90,
            "effective_power": 90.0,
            "type_multiplier": 2.0,
            "stab": 1.5,
            "priority": 0,
            "score": 270.0,
            "win_probability": 0.9938,
            "predicted_winner": "A"
        },
        {
            "move_name": "Pistolet à O",
            "move_type": "Eau",
            "move_power": 40,
            "effective_power": 40.0,
            "type_multiplier": 2.0,
            "stab": 1.5,
            "priority": 0,
            "score": 120.0,
            "win_probability": 0.8054,
            "predicted_winner": "A"
        },
        {
            "move_name": "Charge",
            "move_type": "Normal",
            "move_power": 40,
            "effective_power": 40.0,
            "type_multiplier": 1.0,
            "stab": 1.0,
            "priority": 0,
            "score": 40.0,
            "win_probability": 0.1184,
            "predicted_winner": "B"
        }
    ]
}
```

### Analyse

- **Hydrocanon est fortement recommandé** avec 99.75% de chances de victoire
- **STAB (Same Type Attack Bonus)**: 1.5x car Carapuce est de type Eau
- **Type multiplier**: 2x car Eau est super efficace contre Feu
- **Puissance effective**: 110 × 1.5 × 2.0 = 330
- Même "Charge" (Normal) a seulement 11.84% de chances de victoire à cause du désavantage défensif

---

## Exemple 2: Bulbizarre vs Salamèche

**Contexte**: Bulbizarre (Type Plante/Poison) contre Salamèche (Type Feu). Le Feu est **super efficace** contre Plante (2x), donc Bulbizarre est **désavantagé**.

### Requête

```bash
curl -X POST http://localhost:8000/predict/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "pokemon_a_id": 1,
    "pokemon_b_id": 4,
    "available_moves": ["Charge", "Fouet Lianes", "Tranch'\''Herbe", "Lance-Soleil"]
  }'
```

