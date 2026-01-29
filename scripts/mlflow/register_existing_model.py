#!/usr/bin/env python3
"""
Script pour enregistrer le modèle existant dans MLflow Model Registry
Enregistre le modèle v2 (96.24% accuracy) qui existe déjà sur disque
"""
import os
import sys
import pickle
import json
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from machine_learning.mlflow_integration import MLflowTracker, get_mlflow_tracker

# Couleurs
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"   {msg}")

def check_mlflow_connection():
    """Vérifie que MLflow est accessible"""
    import mlflow

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
    mlflow.set_tracking_uri(tracking_uri)

    try:
        # Test connection
        mlflow.search_experiments()
        print_success(f"MLflow connecté: {tracking_uri}")
        return True
    except Exception as e:
        print_error(f"MLflow non accessible: {e}")
        print_info(f"Assurez-vous que MLflow est démarré:")
        print_info(f"  docker compose ps mlflow")
        print_info(f"  curl http://localhost:5001/health")
        return False

def register_model_v2():
    """Enregistre le modèle v2 existant dans MLflow"""
    print_section("ENREGISTREMENT MODÈLE V2 DANS MLFLOW")

    # Chemins vers le modèle
    models_dir = Path(__file__).parent.parent.parent / "models"
    model_path = models_dir / "battle_winner_model_v2.pkl"
    scalers_path = models_dir / "battle_winner_scalers_v2.pkl"
    metadata_path = models_dir / "battle_winner_metadata_v2.json"

    # Vérifier que les fichiers existent
    if not model_path.exists():
        print_error(f"Modèle non trouvé: {model_path}")
        return False

    print_info(f"Chargement du modèle: {model_path}")

    # Charger le modèle
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print_success("Modèle chargé")
    except Exception as e:
        print_error(f"Erreur lors du chargement du modèle: {e}")
        return False

    # Charger les scalers
    try:
        with open(scalers_path, 'rb') as f:
            scalers = pickle.load(f)
        print_success("Scalers chargés")
    except Exception as e:
        print_error(f"Erreur lors du chargement des scalers: {e}")
        scalers = None

    # Charger les métadonnées
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print_success("Métadonnées chargées")

        # Afficher les métriques
        metrics = metadata.get('metrics', {})
        print_info(f"  - Accuracy: {metrics.get('test_accuracy', 0)*100:.2f}%")
        print_info(f"  - ROC-AUC: {metrics.get('test_roc_auc', 0)*100:.2f}%")
        print_info(f"  - F1-Score: {metrics.get('test_f1', 0)*100:.2f}%")

    except Exception as e:
        print_error(f"Erreur lors du chargement des métadonnées: {e}")
        metadata = {}

    # Créer le tracker MLflow
    print_info("\nCréation du tracker MLflow...")

    try:
        # Forcer l'activation de MLflow
        os.environ["DISABLE_MLFLOW_TRACKING"] = "false"

        tracker = get_mlflow_tracker(experiment_name="pokemon_battle_winner")

        if tracker.experiment_name is None:
            print_error("MLflow tracking est désactivé")
            print_info("Définissez DISABLE_MLFLOW_TRACKING=false")
            return False

        print_success(f"Tracker créé - Experiment: {tracker.experiment_name}")

    except Exception as e:
        print_error(f"Erreur lors de la création du tracker: {e}")
        return False

    # Démarrer un run
    run_name = f"register_existing_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print_info(f"\nDémarrage du run: {run_name}")

    try:
        tracker.start_run(run_name=run_name)
        print_success("Run démarré")
    except Exception as e:
        print_error(f"Erreur lors du démarrage du run: {e}")
        return False

    # Logger les paramètres
    print_info("\nLog des hyperparamètres...")
    try:
        params = metadata.get('hyperparameters', {})
        params['model_version'] = metadata.get('version', 'v2')
        params['dataset_version'] = metadata.get('dataset_version', 'v2')
        params['n_features'] = metadata.get('n_features', 133)

        tracker.log_params(params)
        print_success(f"{len(params)} paramètres loggés")
    except Exception as e:
        print_error(f"Erreur lors du log des paramètres: {e}")

    # Logger les métriques
    print_info("\nLog des métriques...")
    try:
        metrics_to_log = metadata.get('metrics', {})
        tracker.log_metrics(metrics_to_log)
        print_success(f"{len(metrics_to_log)} métriques loggées")
    except Exception as e:
        print_error(f"Erreur lors du log des métriques: {e}")

    # Logger le modèle
    print_info("\nLog du modèle...")
    try:
        # Préparer les metadata pour MLflow
        mlflow_metadata = {
            'model_type': metadata.get('model_type', 'XGBClassifier'),
            'version': metadata.get('version', 'v2'),
            'training_date': metadata.get('training_date'),
            'n_features': metadata.get('n_features'),
            'feature_columns': metadata.get('feature_columns', [])
        }

        tracker.log_model(
            model=model,
            artifact_path="model",
            model_type='xgboost',
            scalers=scalers,
            metadata=mlflow_metadata
        )
        print_success("Modèle loggé avec scalers et metadata")
    except Exception as e:
        print_error(f"Erreur lors du log du modèle: {e}")
        tracker.end_run()
        return False

    # Enregistrer dans Model Registry
    print_info("\nEnregistrement dans Model Registry...")
    try:
        model_name = "battle_winner_predictor"
        description = (
            f"Pokémon Battle Winner Predictor v2\n"
            f"Accuracy: {metrics.get('test_accuracy', 0)*100:.2f}%\n"
            f"ROC-AUC: {metrics.get('test_roc_auc', 0)*100:.2f}%\n"
            f"Training Date: {metadata.get('training_date', 'N/A')}\n"
            f"Features: {metadata.get('n_features', 133)}\n"
            f"Training Samples: {metrics.get('train_samples', 0):,}\n"
            f"Test Samples: {metrics.get('test_samples', 0):,}"
        )

        version_number = tracker.register_model(
            model_name=model_name,
            description=description
        )

        if version_number:
            print_success(f"Modèle enregistré: {model_name} version {version_number}")

            # Promouvoir en Production si accuracy >= 95%
            test_accuracy = metrics.get('test_accuracy', 0)
            if test_accuracy >= 0.95:
                print_info("\nPromotion en Production...")
                success = tracker.promote_to_production(model_name, version_number)
                if success:
                    print_success(f"Modèle promu en Production (Accuracy: {test_accuracy*100:.2f}%)")
                else:
                    print_error("Échec de la promotion en Production")
            else:
                print_info(f"\nAccuracy {test_accuracy*100:.2f}% < 95%, pas de promotion automatique")
                print_info(f"Pour promouvoir manuellement:")
                print_info(f"  python -c \"")
                print_info(f"  from machine_learning.mlflow_integration import MLflowTracker")
                print_info(f"  tracker = MLflowTracker('pokemon_battle_winner')")
                print_info(f"  tracker.promote_to_production('{model_name}', {version_number})")
                print_info(f"  \"")
        else:
            print_error("Échec de l'enregistrement du modèle")

    except Exception as e:
        print_error(f"Erreur lors de l'enregistrement: {e}")
        import mlflow
        mlflow.end_run()
        return False

    # Terminer le run
    import mlflow
    mlflow.end_run()
    print_success("\nRun terminé")

    return True

def verify_registration():
    """Vérifie que le modèle est bien enregistré"""
    print_section("VÉRIFICATION ENREGISTREMENT")

    try:
        tracker = get_mlflow_tracker(experiment_name="pokemon_battle_winner")

        # Lister les expériences
        import mlflow
        experiments = mlflow.search_experiments()
        print_info(f"Expériences trouvées: {len(experiments)}")
        for exp in experiments:
            print_info(f"  - {exp.name} (ID: {exp.experiment_id})")

        # Lister les modèles enregistrés
        from mlflow.tracking import MlflowClient
        client = MlflowClient()

        try:
            registered_models = client.search_registered_models()
            print_info(f"\nModèles enregistrés: {len(registered_models)}")

            for rm in registered_models:
                print_success(f"\n📦 Modèle: {rm.name}")
                print_info(f"   Description: {rm.description[:100]}...")

                # Lister les versions
                versions = client.search_model_versions(f"name='{rm.name}'")
                for mv in versions:
                    stage = mv.current_stage
                    emoji = "🏆" if stage == "Production" else "📝"
                    print_info(f"   {emoji} Version {mv.version}: Stage={stage}")

        except Exception as e:
            print_error(f"Impossible de lister les modèles: {e}")

        return True

    except Exception as e:
        print_error(f"Erreur lors de la vérification: {e}")
        return False

def main():
    print_section("ENREGISTREMENT MODÈLE V2 DANS MLFLOW")

    print_info("Ce script va:")
    print_info("  1. Charger le modèle v2 existant (96.24% accuracy)")
    print_info("  2. Créer une expérimentation MLflow")
    print_info("  3. Logger le modèle, métriques et hyperparamètres")
    print_info("  4. Enregistrer dans MLflow Model Registry")
    print_info("  5. Promouvoir en Production si accuracy >= 95%")

    # Vérifier la connexion MLflow
    if not check_mlflow_connection():
        return 1

    # Enregistrer le modèle
    if not register_model_v2():
        print_error("\n❌ ÉCHEC de l'enregistrement")
        return 1

    # Vérifier l'enregistrement
    if not verify_registration():
        print_error("\n❌ ÉCHEC de la vérification")
        return 1

    print_section("SUCCÈS")
    print_success("Modèle v2 enregistré dans MLflow!")
    print_info("\nVérifiez dans MLflow UI:")
    print_info("  http://localhost:5001")
    print_info("\nPour utiliser le modèle depuis MLflow dans l'API:")
    print_info("  Modifiez docker-compose.yml ligne 128:")
    print_info("    USE_MLFLOW_REGISTRY: \"true\"")
    print_info("  Puis redémarrez: docker compose restart api")

    return 0

if __name__ == "__main__":
    sys.exit(main())
