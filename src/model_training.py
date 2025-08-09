"""
Model training module with MLflow tracking for California Housing dataset
"""

import logging
import os

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from data_preprocessing import load_processed_data
from data_preprocessing import main as preprocess_main

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def evaluate_model(y_true, y_pred):
    """
    Evaluate model performance

    Args:
        y_true: True target values
        y_pred: Predicted values

    Returns:
        dict: Dictionary of evaluation metrics
    """
    metrics = {
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "mae": mean_absolute_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }
    return metrics


def train_linear_regression(X_train, y_train, X_test, y_test):
    """
    Train Linear Regression model
    """
    logger.info("Training Linear Regression model...")

    with mlflow.start_run(run_name="Linear_Regression"):
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Evaluate model
        metrics = evaluate_model(y_test, y_pred)

        # Log parameters
        mlflow.log_param("model_type", "Linear Regression")
        mlflow.log_param("n_features", X_train.shape[1])

        # Log metrics
        mlflow.log_metric("rmse", metrics["rmse"])
        mlflow.log_metric("mae", metrics["mae"])
        mlflow.log_metric("r2", metrics["r2"])

        # Log model
        mlflow.sklearn.log_model(model, "model")

        logger.info(
            f"Linear Regression - RMSE: {metrics['rmse']:.4f}, "
            f"MAE: {metrics['mae']:.4f}, R2: {metrics['r2']:.4f}"
        )

        return model, metrics


def train_random_forest(
    X_train, y_train, X_test, y_test, n_estimators=100, max_depth=10, random_state=42
):
    """
    Train Random Forest model
    """
    logger.info("Training Random Forest model...")

    with mlflow.start_run(run_name="Random_Forest"):
        # Train model
        model = RandomForestRegressor(
            n_estimators=n_estimators, max_depth=max_depth, random_state=random_state
        )
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Evaluate model
        metrics = evaluate_model(y_test, y_pred)

        # Log parameters
        mlflow.log_param("model_type", "Random Forest")
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("n_features", X_train.shape[1])

        # Log metrics
        mlflow.log_metric("rmse", metrics["rmse"])
        mlflow.log_metric("mae", metrics["mae"])
        mlflow.log_metric("r2", metrics["r2"])

        # Log model
        mlflow.sklearn.log_model(model, "model")

        logger.info(
            f"Random Forest - RMSE: {metrics['rmse']:.4f}, "
            f"MAE: {metrics['mae']:.4f}, R2: {metrics['r2']:.4f}"
        )

        return model, metrics


def train_gradient_boosting(
    X_train,
    y_train,
    X_test,
    y_test,
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42,
):
    """
    Train Gradient Boosting model
    """
    logger.info("Training Gradient Boosting model...")

    with mlflow.start_run(run_name="Gradient_Boosting"):
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state,
        )
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Evaluate model
        metrics = evaluate_model(y_test, y_pred)

        # Log parameters
        mlflow.log_param("model_type", "Gradient Boosting")
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("learning_rate", learning_rate)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("n_features", X_train.shape[1])

        # Log metrics
        mlflow.log_metric("rmse", metrics["rmse"])
        mlflow.log_metric("mae", metrics["mae"])
        mlflow.log_metric("r2", metrics["r2"])

        # Log model
        mlflow.sklearn.log_model(model, "model")

        logger.info(
            f"Gradient Boosting - RMSE: {metrics['rmse']:.4f}, "
            f"MAE: {metrics['mae']:.4f}, R2: {metrics['r2']:.4f}"
        )

        return model, metrics


def save_best_model(models_results, models_dir="models"):
    """
    Save the best performing model based on RMSE and generate comprehensive model comparison

    Args:
        models_results: List of (model, metrics) tuples
        models_dir: Directory to save the best model
    """
    logger.info("Selecting and saving best model...")

    # Create models directory
    os.makedirs(models_dir, exist_ok=True)

    # Save individual model metrics for comparison
    all_models_metrics = []
    model_names = ["Linear_Regression", "Random_Forest", "Gradient_Boosting"]

    for i, (model, metrics) in enumerate(models_results):
        model_name = model_names[i] if i < len(model_names) else f"Model_{i+1}"

        # Add model name and type to metrics
        enhanced_metrics = {
            "model_name": model_name,
            "model_type": type(model).__name__,
            **metrics,
        }
        all_models_metrics.append(enhanced_metrics)

        # Save individual model
        individual_model_path = os.path.join(
            models_dir, f"{model_name.lower()}_model.pkl"
        )
        joblib.dump(model, individual_model_path)
        logger.info(f"Saved {model_name} to {individual_model_path}")

    # Save all models comparison data
    comparison_path = os.path.join(models_dir, "all_models_comparison.json")
    with open(comparison_path, "w") as f:
        import json

        json.dump(all_models_metrics, f, indent=2)
    logger.info(f"All models comparison saved to {comparison_path}")

    # Find best model based on RMSE
    best_model, best_metrics = min(models_results, key=lambda x: x[1]["rmse"])
    best_model_name = model_names[models_results.index((best_model, best_metrics))]

    # Save best model
    model_path = os.path.join(models_dir, "best_model.pkl")
    joblib.dump(best_model, model_path)

    # Enhanced best model metrics with additional info
    enhanced_best_metrics = {
        **best_metrics,
        "best_model_name": best_model_name,
        "best_model_type": type(best_model).__name__,
        "training_timestamp": pd.Timestamp.now().isoformat(),
    }

    # Save enhanced metrics
    metrics_path = os.path.join(models_dir, "best_model_metrics.json")
    with open(metrics_path, "w") as f:
        import json

        json.dump(enhanced_best_metrics, f, indent=2)

    logger.info(f"Best model ({best_model_name}) saved to {model_path}")
    logger.info(
        f"Best model metrics: RMSE: {best_metrics['rmse']:.4f}, "
        f"MAE: {best_metrics['mae']:.4f}, R2: {best_metrics['r2']:.4f}"
    )

    # Print detailed comparison
    logger.info("\n" + "=" * 60)
    logger.info("DETAILED MODEL COMPARISON")
    logger.info("=" * 60)

    for metrics in sorted(all_models_metrics, key=lambda x: x["rmse"]):
        logger.info(f"\n{metrics['model_name']} ({metrics['model_type']}):")
        logger.info(f"  RMSE: {metrics['rmse']:.4f}")
        logger.info(f"  MAE:  {metrics['mae']:.4f}")
        logger.info(f"  R2:   {metrics['r2']:.4f}")

    return best_model, enhanced_best_metrics


def main():
    """
    Main training pipeline
    """
    logger.info("Starting model training pipeline...")

    # Check if processed data exists, if not, run preprocessing
    if not os.path.exists("data/X_train.csv"):
        logger.info("Processed data not found. Running data preprocessing...")
        preprocess_main()

    # Load processed data
    X_train, X_test, y_train, y_test, scaler = load_processed_data()

    # Configure MLflow for CI environment
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
        logger.info(f"MLflow tracking URI set to: {tracking_uri}")
    
    # Set MLflow experiment
    mlflow.set_experiment("California_Housing_Regression")

    # Train multiple models
    models_results = []

    # Linear Regression
    lr_model, lr_metrics = train_linear_regression(X_train, y_train, X_test, y_test)
    models_results.append((lr_model, lr_metrics))

    # Random Forest
    rf_model, rf_metrics = train_random_forest(X_train, y_train, X_test, y_test)
    models_results.append((rf_model, rf_metrics))

    # Gradient Boosting
    gb_model, gb_metrics = train_gradient_boosting(X_train, y_train, X_test, y_test)
    models_results.append((gb_model, gb_metrics))

    # Save best model
    best_model, best_metrics = save_best_model(models_results)

    logger.info("Model training pipeline completed successfully!")

    return best_model, best_metrics


if __name__ == "__main__":
    main()
