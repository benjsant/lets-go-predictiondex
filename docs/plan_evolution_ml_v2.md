# Plan d'evolution PredictionDex ML v2

## 1. Contexte et objectifs
- Maintenir le scenario worst-case (moves optimaux) tout en ajoutant des scenarios avec moves fixes ou echantillonnes.
- Permettre a l'API et a l'UI de recevoir les capacites adverses explicites.
- Conserver la compatibilite avec le fonctionnement actuel et le deploiement docker-compose.

## 2. Correctifs prealables
1. Renommer ou corriger l'appel vers `etl_previous_evolution.py` dans `etl_pokemon/pipeline.py` pour garantir la fin du job ETL.
2. Verifier que `docker compose up --build` termine sans erreur (db -> etl -> ml_builder -> api -> streamlit).

## 3. Evolution du pipeline de donnees ML
1. Refactoriser `machine_learning/build_dataset_ml_v1.py` :
   - Isoler la logique de selection de moves (scenario worst-case actuel).
   - Introduire un module de generation d'ensembles de capacites adverses (tirage aleatoire, tirage pondered primes, listes predefinies).
   - Ajouter un indicateur de scenario dans le dataset (`scenario_type`).
2. Versionner le script (creer `build_dataset_ml_v2.py`) et maintenir le v1 pour compatibilite eventuelle.
3. Mettre a jour les tests ML pour couvrir chaque scenario de generation.

## 4. Entrainement modele v2
1. Adapter `train_model.py` pour charger soit le dataset v1 soit v2 selon une variable d'environnement ou argument CLI.
2. Enregistrer de nouveaux artefacts (`battle_winner_model_v2.pkl`, scalers, metadata) tout en preservant les fichiers v1.
3. Documenter les metriques par scenario (accuracy globale et par scenario_type).

## 5. Adaptation API FastAPI
1. Mettre a jour les schemas Pydantic de la route `/predict/best-move` pour accepter un champ optionnel `defender_moves: list[str] | None` et un champ `scenario_type`.
2. Dans `prediction_service.py` :
   - Charger les deux modeles (v1 par defaut, v2 si scenario explicite).
   - Si `defender_moves` est fourni, calculer les features avec ces moves et bypasser la selection worst-case.
   - Si `defender_moves` est absent, conserver le comportement v1.
   - Ajouter un chemin pour echantillonner un set aleatoire controle lorsque l'UI demande un scenario aleatoire (via `scenario_type`).
3. Exposer dans la reponse le scenario utilise et les moves adverses considers.
4. Couvrir les nouvelles branches avec des tests API (routes et services).

## 6. Interface Streamlit
1. Ajouter un formulaire pour saisir ou selectionner les capacites adverses.
2. Proposer des modes preconfigures :
   - "Worst-case" (defaut).
   - "Aleatoire controle" (tirage parmi les moves connus du Pokemon).
   - "Personalise" (saisie manuelle des 1 a 4 moves).
3. Adapter l'appel a l'API pour envoyer `scenario_type` et `defender_moves`.
4. Mettre a jour l'affichage des resultats pour expliquer le scenario et la liste des moves adverses.

## 7. Tests et validation
1. Ajouter des tests unitaires pour la selection de moves aleatoires et la gestion des scenarios dans le dataset ML.
2. Ajouter des tests d'integration sur l'API (worst-case, moves explicites, scenario aleatoire).
3. Ecrire des tests Streamlit (snapshot ou playwright) si possible pour verifier l'affichage des nouveaux champs.
4. Mettre a jour `test_all.py` pour indiquer comment tester les nouveaux modes manuellement.

## 8. Docker et CI/CD
1. Verifier que les Dockerfile n'ont pas besoin de dependances supplementaires (sinon mettre a jour `requirements.txt`).
2. Ajuster les scripts d'entree (`ml_entrypoint.py`) pour lancer le dataset v2 par defaut.
3. Adapter la pipeline CI/CD pour lancer les tests ML et API sur les deux scenarios.

## 9. Documentation
1. Mettre a jour `README_PROJET_COMPLET.md` et `RUN_MACHINE_LEARNING.md` avec la description des scenarios v2.
2. Ajouter une section "Scenarios de combat" dans l'aide Streamlit.
3. Documenter l'argumentation pedagogique (worst-case vs scenario controle) dans `E3_ACTION_PLAN.md` ou un nouveau document d'architecture.

## 10. Plan de deploiement
1. Deployer d'abord en environnement de test en conservant le modele v1 en parallele.
2. Valider les resultats avec un panel de combats reelles.
3. Mise a jour de production une fois la validation terminee.
