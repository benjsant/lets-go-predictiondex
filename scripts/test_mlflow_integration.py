#!/usr/bin/env python3
"""
Test rapide de l'intégration MLflow
===================================

Crée un run MLflow de test pour valider l'infrastructure.

Usage:
    python scripts/test_mlflow_integration.py
"""

import sys
import os
import time
from pathlib import Path

# Ajouter le projet au path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score
except ImportError as e:
    print(f"❌ Dépendance manquante: {e}")
    print("💡 Installez les dépendances: pip install mlflow scikit-learn")
    sys.exit(1)


def test_mlflow_connection():
    """Teste la connexion à MLflow."""
    print("🔌 Test de connexion MLflow...")
    
    # Configurer l'URI de tracking
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_uri)
    
    try:
        # Tenter de créer un experiment
        experiment_name = "test_integration"
        
        # Supprimer l'experiment s'il existe déjà
        try:
            exp = mlflow.get_experiment_by_name(experiment_name)
            if exp:
                print(f"   ℹ️  Experiment '{experiment_name}' existe déjà (ID: {exp.experiment_id})")
        except:
            pass
        
        # Créer ou récupérer l'experiment
        experiment_id = mlflow.create_experiment(experiment_name) if not mlflow.get_experiment_by_name(experiment_name) else mlflow.get_experiment_by_name(experiment_name).experiment_id
        
        print(f"   ✅ Connecté à MLflow: {mlflow_uri}")
        print(f"   ✅ Experiment: {experiment_name} (ID: {experiment_id})")
        
        return True, experiment_name
    
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        print(f"\n💡 Assurez-vous que MLflow est démarré:")
        print(f"   docker-compose up -d mlflow")
        print(f"   # ou")
        print(f"   mlflow server --host 0.0.0.0 --port 5000")
        return False, None


def train_test_model():
    """Entraîne un modèle de test et log dans MLflow."""
    print("\n🤖 Entraînement d'un modèle de test...")
    
    # Générer des données synthétiques
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"   📊 Dataset: {len(X_train)} train, {len(X_test)} test")
    
    # Entraîner un modèle simple
    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=5,
        random_state=42
    )
    
    start = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start
    
    # Évaluer
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"   ⏱️  Temps d'entraînement: {training_time:.2f}s")
    print(f"   📈 Accuracy: {accuracy:.3f}")
    print(f"   📈 F1-Score: {f1:.3f}")
    
    return model, {
        "accuracy": accuracy,
        "f1_score": f1,
        "training_time": training_time,
        "n_train": len(X_train),
        "n_test": len(X_test)
    }


def log_to_mlflow(experiment_name: str, model, metrics: dict):
    """Log le modèle et les métriques dans MLflow."""
    print("\n📝 Logging dans MLflow...")
    
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run(run_name=f"test_run_{int(time.time())}"):
        # Log des paramètres
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_param("n_estimators", 50)
        mlflow.log_param("max_depth", 5)
        mlflow.log_param("test_mode", True)
        
        print(f"   ✅ Paramètres loggés")
        
        # Log des métriques
        mlflow.log_metrics({
            "accuracy": metrics["accuracy"],
            "f1_score": metrics["f1_score"],
            "training_time": metrics["training_time"]
        })
        
        print(f"   ✅ Métriques loggées")
        
        # Log du modèle
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="TestModel"
        )
        
        print(f"   ✅ Modèle loggé")
        
        # Récupérer l'ID du run
        run = mlflow.active_run()
        run_id = run.info.run_id
        
        print(f"\n   🎯 Run ID: {run_id}")
        
        return run_id


def verify_mlflow_data(experiment_name: str):
    """Vérifie que les données sont bien dans MLflow."""
    print("\n🔍 Vérification des données MLflow...")
    
    try:
        # Récupérer l'experiment
        experiment = mlflow.get_experiment_by_name(experiment_name)
        
        if not experiment:
            print(f"   ❌ Experiment '{experiment_name}' non trouvé")
            return False
        
        # Récupérer les runs
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        print(f"   ✅ Experiment ID: {experiment.experiment_id}")
        print(f"   ✅ Nombre de runs: {len(runs)}")
        
        if len(runs) > 0:
            latest_run = runs.iloc[0]
            print(f"\n   📊 Dernier run:")
            print(f"      Run ID: {latest_run['run_id']}")
            print(f"      Accuracy: {latest_run['metrics.accuracy']:.3f}")
            print(f"      F1-Score: {latest_run['metrics.f1_score']:.3f}")
            print(f"      Status: {latest_run['status']}")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la vérification: {e}")
        return False


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 70)
    print("🧪 Test d'intégration MLflow")
    print("=" * 70)
    
    # 1. Tester la connexion
    connected, experiment_name = test_mlflow_connection()
    
    if not connected:
        sys.exit(1)
    
    # 2. Entraîner un modèle de test
    try:
        model, metrics = train_test_model()
    except Exception as e:
        print(f"\n❌ Erreur lors de l'entraînement: {e}")
        sys.exit(1)
    
    # 3. Logger dans MLflow
    try:
        run_id = log_to_mlflow(experiment_name, model, metrics)
    except Exception as e:
        print(f"\n❌ Erreur lors du logging MLflow: {e}")
        print(f"\n💡 Vérifiez que MLflow est accessible:")
        print(f"   curl http://localhost:5000/health")
        sys.exit(1)
    
    # 4. Vérifier les données
    if verify_mlflow_data(experiment_name):
        print("\n" + "=" * 70)
        print("✅ Test d'intégration MLflow réussi!")
        print("=" * 70)
        print(f"\n💡 Consultez MLflow UI: http://localhost:5000")
        print(f"💡 Experiment: {experiment_name}")
        print(f"💡 Run ID: {run_id}")
        
        return 0
    else:
        print("\n❌ Échec de la vérification des données")
        return 1


if __name__ == "__main__":
    sys.exit(main())
