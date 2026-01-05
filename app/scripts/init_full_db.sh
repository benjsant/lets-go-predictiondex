#!/bin/bash
set -e

echo "⏳ Initialisation BDD..."
python app/scripts/init_db.py

echo "📄 Chargement CSV..."
python app/scripts/load_csv.py

echo "🌐 Enrichissement PokéAPI..."
python app/scripts/pokeapi_load_parallel.py

echo "✅ Base de données prête"
