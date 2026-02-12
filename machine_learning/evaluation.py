"""Model evaluation functions for Pokemon battle prediction."""

from typing import Any, Dict, List, Tuple

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_model(model: Any, X_train: pd.DataFrame, X_test: pd.DataFrame,
                   y_train: pd.Series, y_test: pd.Series,
                   model_name: str = "Model",
                   verbose: bool = True) -> Dict[str, float]:
    """Evaluate model and return performance metrics."""
    if verbose:
        print("\n" + "=" * 80)
        print(f"MODEL EVALUATION - {model_name}")
        print("=" * 80)

    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # Probabilities for ROC-AUC
    _ = model.predict_proba(X_train)[:, 1] # Train proba not used
    y_test_proba = model.predict_proba(X_test)[:, 1]

    # Calculate metrics
    metrics = {
        'model_name': model_name,
        'train_accuracy': accuracy_score(y_train, y_train_pred),
        'test_accuracy': accuracy_score(y_test, y_test_pred),
        'test_precision': precision_score(y_test, y_test_pred),
        'test_recall': recall_score(y_test, y_test_pred),
        'test_f1': f1_score(y_test, y_test_pred),
        'test_roc_auc': roc_auc_score(y_test, y_test_proba),
        'train_samples': len(y_train),
        'test_samples': len(y_test),
    }

    # Overfitting check
    overfitting = metrics['train_accuracy'] - metrics['test_accuracy']
    metrics['overfitting'] = overfitting

    if verbose:
        print("\nPERFORMANCE METRICS")
        print("-" * 80)
        print(f"Train Accuracy: {metrics['train_accuracy']:.4f}")
        print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")
        print(f"Test Precision: {metrics['test_precision']:.4f}")
        print(f"Test Recall: {metrics['test_recall']:.4f}")
        print(f"Test F1-Score: {metrics['test_f1']:.4f}")
        print(f"Test ROC-AUC: {metrics['test_roc_auc']:.4f}")
        print(f"\nOverfitting: {overfitting:.4f} ({overfitting*100:.2f}%)")

        # Classification report
        print("\n" + "-" * 80)
        print("CLASSIFICATION REPORT (Test Set)")
        print("-" * 80)
        print(classification_report(y_test, y_test_pred, target_names=['B wins', 'A wins']))

        # Confusion matrix
        print("Confusion Matrix:")
        cm = confusion_matrix(y_test, y_test_pred)
        print(cm)
        print(f"\nTrue Negatives: {cm[0, 0]}")
        print(f"False Positives: {cm[0, 1]}")
        print(f"False Negatives: {cm[1, 0]}")
        print(f"True Positives: {cm[1, 1]}")

    return metrics


def analyze_feature_importance(model: Any, feature_columns: List[str],
                               top_n: int = 20,
                               verbose: bool = True) -> pd.DataFrame:
    """Analyze and display feature importance from trained model."""
    if verbose:
        print("\n" + "=" * 80)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("=" * 80)

    # Get feature importances
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    else:
        if verbose:
            print("\nModel does not support feature_importances_")
        return pd.DataFrame()

    # Create DataFrame
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': importances
    }).sort_values('importance', ascending=False)

    if verbose:
        print(f"\nTop {top_n} Most Important Features:")
        print("-" * 80)
        for _, row in importance_df.head(top_n).iterrows():
            print(f"{row['feature']:40s} {row['importance']:.6f}")

    return importance_df


def compare_models(X_train: pd.DataFrame, X_test: pd.DataFrame,
                   y_train: pd.Series, y_test: pd.Series,
                   models_to_compare: List[str] = None,
                   verbose: bool = True) -> Tuple[Any, str, Dict]:
    """Train and compare multiple models, returning the best performing one based on test accuracy."""
    # Import here to avoid circular dependency
    from machine_learning.run_machine_learning import train_model

    if models_to_compare is None:
        models_to_compare = ['xgboost', 'random_forest']

    if verbose:
        print("\n" + "=" * 80)
        print("MODEL COMPARISON")
        print("=" * 80)
        print(f"\nComparing models: {', '.join(models_to_compare)}")

    results = []
    trained_models = {}

    for model_type in models_to_compare:
        if verbose:
            print(f"\n{'─' * 80}")
            print(f"Training {model_type}...")

        # Train model
        model = train_model(X_train, y_train, model_type=model_type, verbose=False)
        trained_models[model_type] = model

        # Evaluate model
        metrics = evaluate_model(model, X_train, X_test, y_train, y_test,
                                 model_name=model_type, verbose=False)
        results.append(metrics)

        if verbose:
            print(f"{model_type}: Test Accuracy = {metrics['test_accuracy']:.4f}")

    # Create comparison DataFrame
    results_df = pd.DataFrame(results)

    if verbose:
        print("\n" + "=" * 80)
        print("COMPARISON RESULTS")
        print("=" * 80)
        print("\n", results_df[['model_name', 'test_accuracy', 'test_f1',
              'test_roc_auc', 'overfitting']].to_string(index=False))

    # Select best model
    best_idx = results_df['test_accuracy'].idxmax()
    best_model_name = results_df.loc[best_idx, 'model_name']
    best_model = trained_models[best_model_name]

    if verbose:
        print(f"\n BEST MODEL: {best_model_name}")
        print(f" Test Accuracy: {results_df.loc[best_idx, 'test_accuracy']:.4f}")
        print(f" Test ROC-AUC: {results_df.loc[best_idx, 'test_roc_auc']:.4f}")

    return best_model, best_model_name, results_df.to_dict('records')
