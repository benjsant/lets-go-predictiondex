# Interface Streamlit

Application web pour explorer les Pokémon et prédire l'issue de combats.

## Structure

```
interface/
├── app.py                         # Page d'accueil
├── pages/
│   ├── 1_Capacités.py             # Catalogue des moves
│   ├── 2_Combat_et_Prédiction.py  # Simulateur de combat
│   ├── 3_Détails_Pokémon.py       # Fiches Pokémon
│   ├── 4_Types_et_Affinités.py    # Matrice des types
│   ├── 5_Quiz_Types.py            # Quiz interactif
│   └── 6_Crédits.py               # Sources et technos
├── services/                      # Communication API
├── formatters/                    # Formatage affichage
├── utils/                         # Thème, cache
├── assets/                        # Images
└── .streamlit/config.toml         # Config Streamlit
```

## Lancer

```bash
# Via Docker
docker compose up streamlit
# → http://localhost:8502

# En local
cd interface
source ../.venv/bin/activate
pip install -r requirements_streamlit.txt
streamlit run app.py --server.port 8502
```

## Pages

- **Accueil** : présentation du projet, stats
- **Capacités** : catalogue des 226 moves avec filtres (type, catégorie, puissance)
- **Combat & Prédiction** : sélection de deux Pokémon, prédiction ML du meilleur move
- **Détails Pokémon** : fiches avec stats, types, évolutions
- **Types & Affinités** : matrice 18x18 des résistances/faiblesses
- **Quiz Types** : petit jeu pour tester ses connaissances
- **Crédits** : attribution des sources

## Configuration

Fichier `.env` :
```
API_URL=http://localhost:8080
API_KEY=your-api-key-here
```

Le thème Pokémon (jaune/bleu/rouge, fond sombre) est configuré dans `.streamlit/config.toml` et `utils/pokemon_theme.py`.

## Communication API

L'interface appelle l'API FastAPI via `services/api_client.py` :

```python
from services.api_client import get_prediction

result = get_prediction(
    pokemon_a_id=25,
    pokemon_b_id=6,
    move_a="Fatal-Foudre"
)
```
