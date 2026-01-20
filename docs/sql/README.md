# Requêtes SQL – Extraction des données

Ces requêtes SQL permettent l’extraction des données depuis la base
relationnelle du projet Pokémon Let's Go PredictionDex.

## Objectifs
- Préparer les données pour analyse et machine learning
- Vérifier la cohérence des données importées
- Faciliter l’exploitation via l’API REST

## Choix techniques
- Utilisation de jointures explicites
- Séparation espèce / forme
- LEFT JOIN pour gérer les doubles types
- Ordonnancement par Pokédex pour cohérence métier

## Optimisations
- Index sur les clés étrangères
- Jointures ciblées
- Sélection uniquement des colonnes nécessaires
