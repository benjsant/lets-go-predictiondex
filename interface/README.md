# 🎮 Interface Streamlit - PredictionDex

> Application web interactive pour les prédictions de combat Pokémon

## 📋 Vue d'ensemble

Interface utilisateur Streamlit permettant de :
- Prédire l'issue de combats Pokémon
- Explorer le catalogue des Pokémon et capacités
- Visualiser les affinités de types
- Tester ses connaissances avec un quiz

## 📁 Structure

```
interface/
├── app.py                    # 🏠 Page d'accueil
├── pages/                    # Pages de l'application
│   ├── 1_Capacités.py        # Catalogue des moves
│   ├── 2_Combat_et_Prédiction.py  # Simulateur de combat
│   ├── 3_Détails_Pokémon.py  # Fiches Pokémon
│   ├── 4_Types_et_Affinités.py    # Matrice des types
│   ├── 5_Quiz_Types.py       # Quiz interactif
│   └── 6_Crédits.py          # Sources et technologies
├── services/                 # Communication API
├── formatters/               # Formatage affichage
├── utils/                    # Utilitaires (thème, cache)
├── assets/                   # Images et ressources
├── config/                   # Configuration
└── .streamlit/               # Configuration Streamlit
    └── config.toml
```

## 🚀 Utilisation

### Via Docker (recommandé)

```bash
docker compose up streamlit
# Accès: http://localhost:8502
```

### En local

```bash
cd interface
source ../.venv/bin/activate
pip install -r requirements_streamlit.txt
streamlit run app.py --server.port 8502
```

## 📱 Pages

| Page | Description | Fonctionnalités |
|------|-------------|-----------------|
| **Accueil** | Présentation du projet | Stats, features |
| **Capacités** | Catalogue des 226 moves | Filtres type/catégorie/puissance |
| **Combat & Prédiction** | Simulateur ML | Sélection Pokémon, prédiction |
| **Détails Pokémon** | Fiches détaillées | Stats, types, évolutions |
| **Types & Affinités** | Matrice 18×18 | Résistances/faiblesses |
| **Quiz Types** | Jeu éducatif | Score, progression |
| **Crédits** | Attribution | Sources, technologies |

## ⚙️ Configuration

### Variables d'environnement (`.env`)

```env
API_URL=http://localhost:8080
API_KEY=your-api-key-here
```

### Streamlit (`.streamlit/config.toml`)

```toml
[server]
port = 8502
headless = true

[theme]
primaryColor = "#FFCB05"      # Jaune Pokémon
backgroundColor = "#1a1a2e"   # Fond sombre
secondaryBackgroundColor = "#16213e"
textColor = "#FFFFFF"
```

## 🎨 Thème Pokémon

Le thème personnalisé inclut :
- Couleurs Pokémon (jaune/bleu/rouge)
- Cards avec effets de hover
- Sprites animés (Pikachu, Évoli)
- Responsive design

Fichier : `utils/pokemon_theme.py`

## 🔌 Communication API

L'interface communique avec l'API FastAPI via `services/api_client.py` :

```python
# Exemple d'appel
from services.api_client import get_prediction

result = get_prediction(
    pokemon_a_id=25,      # Pikachu
    pokemon_b_id=6,       # Dracaufeu
    move_a="Fatal-Foudre"
)
```

## 🧪 Tests

```bash
pytest tests/interface/ -v
```

## 📈 Performance

| Métrique | Valeur |
|----------|--------|
| Temps de chargement | < 1s |
| Temps de prédiction | < 500ms |
| Pages | 7 |
| Cache | Session Streamlit |
