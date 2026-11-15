"""
Data Monitoring and Model Retraining Trigger System
Monitors data drift, performance degradation, and triggers retraining
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from database_logging import get_database_logger, setup_database_logging

# Setup logging
logger = setup_database_logging(__name__)
db_logger = get_database_logger()


class DataDriftDetector:
    """Detect data drift using statistical tests"""

    def __init__(self, reference_data_path: str = "data/X_train.csv"):
        self.reference_data_path = reference_data_path
        self.reference_data = None
        self.load_reference_data()

    def load_reference_data(self):
        """Load reference training data for comparison"""
        try:
            if os.path.exists(self.reference_data_path):
                self.reference_data = pd.read_csv(self.reference_data_path)
                logger.info(f"Reference data loaded: {self.reference_data.shape}")
            else:
                logger.warning(f"Reference data not found: {self.reference_data_path}")
        except Exception as e:
            logger.error(f"Error loading reference data: {e}")

    def detect_drift(self, new_data: pd.DataFrame, threshold: float = 0.05) -> Dict:
        """
        Detect data drift using Kolmogorov-Smirnov test

        Args:
            new_data: New incoming data
            threshold: P-value threshold for drift detection

        Returns:
            Dictionary with drift detection results
        """
        if self.reference_data is None:
            return {"error": "Reference data not available"}

        drift_results = {
            "timestamp": datetime.now().isoformat(),
            "total_features": len(new_data.columns),
            "drifted_features": [],
            "drift_scores": {},
            "overall_drift": False,
        }

        try:
            for column in new_data.columns:
                if column in self.reference_data.columns:
                    # Kolmogorov-Smirnov test
                    ks_statistic, p_value = stats.ks_2samp(
                        self.reference_data[column].dropna(), new_data[column].dropna()
                    )

                    drift_results["drift_scores"][column] = {
                        "ks_statistic": float(ks_statistic),
                        "p_value": float(p_value),
                        "drifted": bool(p_value < threshold),
                    }

                    if p_value < threshold:
                        drift_results["drifted_features"].append(column)

            # Overall drift if more than 20% of features show drift
            drift_threshold = 0.2 * len(new_data.columns)
            drift_results["overall_drift"] = (
                len(drift_results["drifted_features"]) > drift_threshold
            )

            logger.info(
                f"Drift detection completed. Drifted features: {len(drift_results['drifted_features'])}"
            )

        except Exception as e:
            logger.error(f"Error in drift detection: {e}")
            drift_results["error"] = str(e)

        return drift_results


class ModelPerformanceMonitor:
    """Monitor model performance and detect degradation"""

    def __init__(self, performance_threshold: float = 0.1):
        self.performance_threshold = performance_threshold
        self.baseline_metrics = self.load_baseline_metrics()

    def load_baseline_metrics(self) -> Optional[Dict]:
        """Load baseline model metrics"""
        try:
            metrics_path = "models/best_model_metrics.json"
            if os.path.exists(metrics_path):
                with open(metrics_path, "r") as f:
                    metrics = json.load(f)
                logger.info(
                    f"Baseline metrics loaded: RMSE={metrics.get('rmse', 'N/A')}"
                )
                return metrics
        except Exception as e:
            logger.error(f"Error loading baseline metrics: {e}")
        return None

    def evaluate_current_performance(
        self, predictions: List[float], actuals: List[float]
    ) -> Dict:
        """
        Evaluate current model performance

        Args:
            predictions: Model predictions
            actuals: Actual values

        Returns:
            Dictionary with performance metrics
        """
        try:
            rmse = np.sqrt(mean_squared_error(actuals, predictions))
            mae = mean_absolute_error(actuals, predictions)
            r2 = r2_score(actuals, predictions)

            performance_metrics = {
                "timestamp": datetime.now().isoformat(),
                "rmse": float(rmse),
                "mae": float(mae),
                "r2": float(r2),
                "n_samples": len(predictions),
            }

            # Check for performance degradation
            if self.baseline_metrics:
                rmse_degradation = (
                    rmse - self.baseline_metrics["rmse"]
                ) / self.baseline_metrics["rmse"]
                r2_degradation = (
                    self.baseline_metrics["r2"] - r2
                ) / self.baseline_metrics["r2"]

                performance_metrics.update(
                    {
                        "rmse_degradation": float(rmse_degradation),
                        "r2_degradation": float(r2_degradation),
                        "performance_degraded": rmse_degradation
                        > self.performance_threshold
                        or r2_degradation > self.performance_threshold,
                    }
                )

            # Log performance metrics to database
            db_logger.log_model_metric(
                model_name="current_model_performance",
                model_type="performance_monitoring",
                rmse=rmse,
                mae=mae,
                r2_score=r2,
                training_time=0,
                parameters={"monitoring": True, "n_samples": len(predictions)},
            )

            logger.info(f"Performance evaluation: RMSE={rmse:.4f}, R2={r2:.4f}")
            return performance_metrics

        except Exception as e:
            logger.error(f"Error evaluating performance: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


class RetrainingTrigger:
    """Determine when model retraining should be triggered"""

    def __init__(self, config_path: str = "monitoring/retraining_config.json"):
        self.config = self.load_config(config_path)
        self.drift_detector = DataDriftDetector()
        self.performance_monitor = ModelPerformanceMonitor()

    def load_config(self, config_path: str) -> Dict:
        """Load retraining configuration"""
        default_config = {
            "drift_threshold": 0.05,
            "performance_threshold": 0.1,
            "min_samples_for_retraining": 100,
            "max_days_since_last_training": 30,
            "enable_automatic_retraining": True,
        }

        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                logger.info(f"Retraining config loaded from {config_path}")
                return {**default_config, **config}
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")

        return default_config

    def should_retrain(
        self,
        new_data: pd.DataFrame,
        predictions: List[float] = None,
        actuals: List[float] = None,
    ) -> Dict:
        """
        Determine if model should be retrained

        Args:
            new_data: New data for drift detection
            predictions: Recent predictions (optional)
            actuals: Actual values for performance evaluation (optional)

        Returns:
            Dictionary with retraining recommendation
        """
        retraining_decision = {
            "timestamp": datetime.now().isoformat(),
            "should_retrain": False,
            "reasons": [],
            "drift_analysis": None,
            "performance_analysis": None,
            "data_volume_check": None,
        }

        try:
            # 1. Check data drift
            if len(new_data) > 0:
                drift_results = self.drift_detector.detect_drift(
                    new_data, self.config["drift_threshold"]
                )
                retraining_decision["drift_analysis"] = drift_results

                if drift_results.get("overall_drift", False):
                    retraining_decision["reasons"].append("Data drift detected")
                    retraining_decision["should_retrain"] = True

            # 2. Check performance degradation
            if predictions and actuals and len(predictions) == len(actuals):
                performance_results = (
                    self.performance_monitor.evaluate_current_performance(
                        predictions, actuals
                    )
                )
                retraining_decision["performance_analysis"] = performance_results

                if performance_results.get("performance_degraded", False):
                    retraining_decision["reasons"].append(
                        "Performance degradation detected"
                    )
                    retraining_decision["should_retrain"] = True

            # 3. Check data volume
            data_volume_check = {
                "new_samples": len(new_data),
                "min_required": self.config["min_samples_for_retraining"],
                "sufficient_data": len(new_data)
                >= self.config["min_samples_for_retraining"],
            }
            retraining_decision["data_volume_check"] = data_volume_check

            if not data_volume_check["sufficient_data"]:
                retraining_decision["reasons"].append(
                    "Insufficient new data for retraining"
                )

            # 4. Check time since last training
            try:
                if os.path.exists("models/best_model_metrics.json"):
                    with open("models/best_model_metrics.json", "r") as f:
                        metrics = json.load(f)
                        last_training = datetime.fromisoformat(
                            metrics.get(
                                "training_timestamp", datetime.now().isoformat()
                            )
                        )
                        days_since_training = (datetime.now() - last_training).days

                        if (
                            days_since_training
                            > self.config["max_days_since_last_training"]
                        ):
                            retraining_decision["reasons"].append(
                                f"Model is {days_since_training} days old"
                            )
                            retraining_decision["should_retrain"] = True
            except Exception as e:
                logger.warning(f"Could not check last training time: {e}")

            # Final decision
            if (
                retraining_decision["should_retrain"]
                and not self.config["enable_automatic_retraining"]
            ):
                retraining_decision["should_retrain"] = False
                retraining_decision["reasons"].append(
                    "Automatic retraining is disabled"
                )

            # Log decision to database
            db_logger.log_message(
                level="INFO",
                module="retraining_trigger",
                message=f"Retraining decision: {retraining_decision['should_retrain']}",
                extra_data={
                    "reasons": retraining_decision["reasons"],
                    "config": self.config,
                },
            )

            logger.info(
                f"Retraining decision: {retraining_decision['should_retrain']}, Reasons: {retraining_decision['reasons']}"
            )

        except Exception as e:
            logger.error(f"Error in retraining decision: {e}")
            retraining_decision["error"] = str(e)

        return retraining_decision

    def trigger_retraining(self) -> Dict:
        """
        Trigger model retraining process

        Returns:
            Dictionary with retraining status
        """
        try:
            logger.info("Triggering model retraining...")

            # Create retraining trigger file
            trigger_file = "triggers/retrain_model.trigger"
            os.makedirs("triggers", exist_ok=True)

            trigger_data = {
                "timestamp": datetime.now().isoformat(),
                "triggered_by": "automated_monitoring",
                "status": "pending",
            }

            with open(trigger_file, "w") as f:
                json.dump(trigger_data, f, indent=2)

            # Log retraining trigger
            db_logger.log_message(
                level="INFO",
                module="retraining_trigger",
                message="Model retraining triggered",
                extra_data=trigger_data,
            )

            logger.info(f"Retraining trigger created: {trigger_file}")

            return {
                "status": "success",
                "trigger_file": trigger_file,
                "timestamp": datetime.now().isoformat(),
                "message": "Retraining process initiated",
            }

        except Exception as e:
            logger.error(f"Error triggering retraining: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Main function for testing the monitoring system"""
    logger.info("Starting data monitoring system test...")

    # Initialize retraining trigger
    trigger = RetrainingTrigger()

    # Test with sample data
    try:
        # Load some test data
        if os.path.exists("data/X_test.csv"):
            test_data = pd.read_csv("data/X_test.csv").head(50)  # Use first 50 rows

            # Test retraining decision
            decision = trigger.should_retrain(test_data)
            print(f"Retraining Decision: {json.dumps(decision, indent=2)}")

            # If retraining is recommended, trigger it
            if decision["should_retrain"]:
                result = trigger.trigger_retraining()
                print(f"Retraining Trigger Result: {json.dumps(result, indent=2)}")
        else:
            logger.warning("Test data not found")

    except Exception as e:
        logger.error(f"Error in monitoring system test: {e}")


if __name__ == "__main__":
    main()
