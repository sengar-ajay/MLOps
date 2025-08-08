"""
Flask API for serving the California Housing price prediction model
"""

import logging
import os
from datetime import datetime
from typing import List, Optional

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from pydantic import BaseModel, ValidationError, Field
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_flask_exporter import PrometheusMetrics

# Import database logging
from database_logging import get_database_logger, setup_database_logging
from data_monitoring import RetrainingTrigger

# Set up database logging
logger = setup_database_logging(__name__)
db_logger = get_database_logger()


# Pydantic models for input validation
class HousingFeatures(BaseModel):
    """Pydantic model for California Housing dataset features"""

    MedInc: float = Field(..., ge=0, le=20, description="Median income in block group")
    HouseAge: float = Field(
        ..., ge=0, le=100, description="Median house age in block group"
    )
    AveRooms: float = Field(
        ..., ge=1, le=50, description="Average number of rooms per household"
    )
    AveBedrms: float = Field(
        ..., ge=0, le=10, description="Average number of bedrooms per household"
    )
    Population: float = Field(..., ge=1, le=50000, description="Block group population")
    AveOccup: float = Field(
        ..., ge=0.5, le=20, description="Average number of household members"
    )
    Latitude: float = Field(..., ge=32, le=42, description="Block group latitude")
    Longitude: float = Field(..., ge=-125, le=-114, description="Block group longitude")

    class Config:
        schema_extra = {
            "example": {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                "AveRooms": 6.984,
                "AveBedrms": 1.023,
                "Population": 322.0,
                "AveOccup": 2.555,
                "Latitude": 37.88,
                "Longitude": -122.23,
            }
        }


class BatchPredictionRequest(BaseModel):
    """Pydantic model for batch prediction requests"""

    instances: List[HousingFeatures] = Field(
        ..., min_items=1, max_items=100, description="List of housing instances"
    )


class PredictionResponse(BaseModel):
    """Pydantic model for prediction responses"""

    prediction: float
    model_type: str
    input: dict
    timestamp: str


class BatchPredictionResponse(BaseModel):
    """Pydantic model for batch prediction responses"""

    predictions: List[PredictionResponse]
    total_predictions: int
    timestamp: str


# Initialize Flask app
app = Flask(__name__)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Custom Prometheus metrics
prediction_counter = Counter(
    "ml_predictions_total", "Total number of predictions made", ["model_type", "status"]
)
prediction_duration = Histogram(
    "ml_prediction_duration_seconds", "Time spent making predictions"
)
model_accuracy = Gauge("ml_model_accuracy", "Current model accuracy score")
api_requests = Counter(
    "api_requests_total", "Total API requests", ["method", "endpoint", "status"]
)
validation_errors = Counter(
    "input_validation_errors_total", "Total input validation errors", ["error_type"]
)

# Global variables for model and scaler
model = None
scaler = None
feature_names = None

# Initialize retraining trigger
retraining_trigger = RetrainingTrigger()


def load_model_and_scaler():
    """
    Load the trained model and scaler
    """
    global model, scaler, feature_names

    try:
        # Load model
        model_path = "models/best_model.pkl"
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
        else:
            raise FileNotFoundError(f"Model file not found: {model_path}")

        # Load scaler
        scaler_path = "data/scaler.pkl"
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded from {scaler_path}")
        else:
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

        # Load feature names from training data
        feature_data_path = "data/X_train.csv"
        if os.path.exists(feature_data_path):
            sample_data = pd.read_csv(feature_data_path, nrows=1)
            feature_names = list(sample_data.columns)
            logger.info(f"Feature names loaded: {feature_names}")
        else:
            # Default California Housing feature names
            feature_names = [
                "MedInc",
                "HouseAge",
                "AveRooms",
                "AveBedrms",
                "Population",
                "AveOccup",
                "Latitude",
                "Longitude",
            ]
            logger.warning(f"Using default feature names: {feature_names}")

    except Exception as e:
        logger.error(f"Error loading model or scaler: {str(e)}")
        raise


def validate_input(data):
    """
    Validate input data format and values

    Args:
        data: Input data dictionary

    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Input must be a JSON object"

    # If feature_names is not loaded, use default
    expected_features = (
        feature_names
        if feature_names is not None
        else [
            "MedInc",
            "HouseAge",
            "AveRooms",
            "AveBedrms",
            "Population",
            "AveOccup",
            "Latitude",
            "Longitude",
        ]
    )

    # Check if all required features are present
    missing_features = set(expected_features) - set(data.keys())
    if missing_features:
        return False, f"Missing features: {list(missing_features)}"

    # Check if values are numeric
    for feature, value in data.items():
        if feature in expected_features:
            try:
                float(value)
            except (TypeError, ValueError):
                return False, f"Feature '{feature}' must be numeric, got: {value}"

    return True, ""


@app.route("/", methods=["GET"])
def home():
    """
    Home endpoint with API information
    """
    return jsonify(
        {
            "message": "California Housing Price Prediction API",
            "version": "1.0.0",
            "endpoints": {
                "/predict": "POST - Make price predictions",
                "/health": "GET - Check API health",
                "/info": "GET - Get model information",
            },
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint
    """
    try:
        # Check if model and scaler are loaded
        if model is None or scaler is None:
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "message": "Model or scaler not loaded",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                500,
            )

        return jsonify(
            {
                "status": "healthy",
                "message": "API is running and model is loaded",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/schema", methods=["GET"])
def get_schema():
    """
    Get the Pydantic schema for input validation
    """
    try:
        return jsonify(
            {
                "schema": {
                    "HousingFeatures": HousingFeatures.schema(),
                    "BatchPredictionRequest": BatchPredictionRequest.schema(),
                },
                "example": HousingFeatures.schema()["example"]
                if "example" in HousingFeatures.schema()
                else HousingFeatures.Config.schema_extra["example"],
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}")
        return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.route("/info", methods=["GET"])
def info():
    """
    Model information endpoint
    """
    try:
        model_info = {
            "model_type": type(model).__name__,
            "features": feature_names,
            "n_features": len(feature_names),
            "model_loaded": model is not None,
            "scaler_loaded": scaler is not None,
            "timestamp": datetime.now().isoformat(),
        }

        # Add model-specific parameters if available
        if hasattr(model, "get_params"):
            model_info["model_parameters"] = model.get_params()

        return jsonify(model_info)

    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """
    Prediction endpoint with Pydantic validation

    Expected input format (validated by Pydantic):
    {
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        "AveRooms": 6.98,
        "AveBedrms": 1.02,
        "Population": 322.0,
        "AveOccup": 2.55,
        "Latitude": 37.88,
        "Longitude": -122.23
    }
    """
    start_time = datetime.now()

    try:
        # Get JSON data from request
        try:
            data = request.get_json(force=True)
        except Exception:
            return (
                jsonify(
                    {
                        "error": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        if data is None:
            return (
                jsonify(
                    {
                        "error": "No JSON data provided",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Validate input using Pydantic
        try:
            validated_input = HousingFeatures(**data)
            logger.info(f"Prediction request validated: {validated_input.dict()}")
        except ValidationError as e:
            validation_errors_list = []
            for error in e.errors():
                field = error["loc"][0] if error["loc"] else "unknown"
                message = error["msg"]
                validation_errors_list.append(f"{field}: {message}")
                # Track validation errors in Prometheus
                validation_errors.labels(error_type=field).inc()

            api_requests.labels(
                method="POST", endpoint="/predict", status="validation_error"
            ).inc()

            return (
                jsonify(
                    {
                        "error": "Input validation failed",
                        "validation_errors": validation_errors_list,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Check if model is loaded
        if model is None or scaler is None or feature_names is None:
            return (
                jsonify(
                    {
                        "error": "Model not properly loaded",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                500,
            )

        # Prepare input data using validated input
        input_dict = validated_input.dict()
        input_data = pd.DataFrame([input_dict])[feature_names]

        # Scale the input
        input_scaled = scaler.transform(input_data)

        # Make prediction with timing
        with prediction_duration.time():
            prediction = model.predict(input_scaled)[0]

        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()

        # Update Prometheus metrics
        prediction_counter.labels(
            model_type=type(model).__name__, status="success"
        ).inc()
        api_requests.labels(method="POST", endpoint="/predict", status="success").inc()

        # Log API metrics to database
        db_logger.log_api_metric(
            endpoint="/predict",
            method="POST",
            status_code=200,
            response_time=response_time,
            success=True,
            request_data=input_dict,
            response_data={"prediction": float(prediction)},
        )

        # Log the prediction
        logger.info(
            f"Prediction made: {prediction} (response_time: {response_time:.3f}s)"
        )

        return jsonify(
            {
                "prediction": float(prediction),
                "input": input_dict,
                "timestamp": datetime.now().isoformat(),
                "model_type": type(model).__name__,
            }
        )

    except Exception as e:
        # Update Prometheus metrics for error
        prediction_counter.labels(
            model_type=type(model).__name__ if model else "unknown", status="error"
        ).inc()
        api_requests.labels(method="POST", endpoint="/predict", status="error").inc()

        # Log API metrics for error case
        response_time = (datetime.now() - start_time).total_seconds()
        db_logger.log_api_metric(
            endpoint="/predict",
            method="POST",
            status_code=500,
            response_time=response_time,
            success=False,
            error_message=str(e),
        )

        logger.error(f"Error making prediction: {str(e)}")
        return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.route("/predict_batch", methods=["POST"])
def predict_batch():
    """
    Batch prediction endpoint

    Expected input format:
    {
        "instances": [
            {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                ...
            },
            {
                "MedInc": 7.2574,
                "HouseAge": 21.0,
                ...
            }
        ]
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        if data is None or "instances" not in data:
            return (
                jsonify(
                    {
                        "error": "No instances provided. "
                        'Expected format: {"instances": [...]}',
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        instances = data["instances"]

        if not isinstance(instances, list) or len(instances) == 0:
            return (
                jsonify(
                    {
                        "error": "Instances must be a non-empty list",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        # Validate each instance
        predictions = []
        for i, instance in enumerate(instances):
            is_valid, error_message = validate_input(instance)
            if not is_valid:
                return (
                    jsonify(
                        {
                            "error": f"Instance {i}: {error_message}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    ),
                    400,
                )

        # Prepare input data
        input_df = pd.DataFrame(instances)[feature_names]

        # Scale the input
        input_scaled = scaler.transform(input_df)

        # Make predictions
        predictions = model.predict(input_scaled).tolist()

        logger.info(f"Batch prediction made for {len(instances)} instances")

        return jsonify(
            {
                "predictions": predictions,
                "n_predictions": len(predictions),
                "timestamp": datetime.now().isoformat(),
                "model_type": type(model).__name__,
            }
        )

    except Exception as e:
        logger.error(f"Error making batch prediction: {str(e)}")
        return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 500


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {
                "error": "Endpoint not found",
                "message": "Please check the API documentation",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "Something went wrong on the server",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        500,
    )


# Database Logging Query Endpoints


@app.route("/logs", methods=["GET"])
def get_logs():
    """
    Get logs from in-memory database

    Query parameters:
    - level: Filter by log level (INFO, WARNING, ERROR, etc.)
    - module: Filter by module name
    - limit: Maximum number of records (default: 100, max: 1000)
    """
    try:
        level = request.args.get("level")
        module = request.args.get("module")
        limit = min(int(request.args.get("limit", 100)), 1000)  # Cap at 1000

        logs = db_logger.get_logs(level=level, module=module, limit=limit)

        return jsonify(
            {
                "success": True,
                "logs": logs,
                "total": len(logs),
                "filters": {"level": level, "module": module, "limit": limit},
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/metrics/api", methods=["GET"])
def get_api_metrics():
    """
    Get API metrics from in-memory database

    Query parameters:
    - endpoint: Filter by endpoint
    - limit: Maximum number of records (default: 100, max: 1000)
    """
    try:
        endpoint = request.args.get("endpoint")
        limit = min(int(request.args.get("limit", 100)), 1000)

        metrics = db_logger.get_api_metrics(endpoint=endpoint, limit=limit)

        return jsonify(
            {
                "success": True,
                "metrics": metrics,
                "total": len(metrics),
                "filters": {"endpoint": endpoint, "limit": limit},
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving API metrics: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/metrics/models", methods=["GET"])
def get_model_metrics():
    """
    Get model training metrics from in-memory database

    Query parameters:
    - limit: Maximum number of records (default: 100, max: 1000)
    """
    try:
        limit = min(int(request.args.get("limit", 100)), 1000)

        metrics = db_logger.get_model_metrics(limit=limit)

        return jsonify(
            {
                "success": True,
                "metrics": metrics,
                "total": len(metrics),
                "filters": {"limit": limit},
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving model metrics: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/database/stats", methods=["GET"])
def get_database_stats():
    """
    Get database statistics including logs count, API metrics summary, etc.
    """
    try:
        stats = db_logger.get_database_stats()

        return jsonify(
            {
                "success": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving database stats: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/database/clear", methods=["POST"])
def clear_database():
    """
    Clear all data from the in-memory database
    WARNING: This will delete all logs and metrics!
    """
    try:
        db_logger.clear_database()
        logger.warning("Database cleared by user request")

        return jsonify(
            {
                "success": True,
                "message": "Database cleared successfully",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/monitoring/drift", methods=["POST"])
def check_data_drift():
    """
    Check for data drift in new data

    Expected input:
    {
        "data": [
            {"MedInc": 8.32, "HouseAge": 41, ...},
            {"MedInc": 7.25, "HouseAge": 35, ...}
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or "data" not in data:
            return jsonify({"error": "No data provided for drift detection"}), 400

        # Convert to DataFrame
        new_data = pd.DataFrame(data["data"])

        # Check drift
        drift_results = retraining_trigger.drift_detector.detect_drift(new_data)

        return jsonify(
            {"drift_analysis": drift_results, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        logger.error(f"Error in drift detection: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/monitoring/retraining-check", methods=["POST"])
def check_retraining_need():
    """
    Check if model retraining is needed

    Expected input:
    {
        "new_data": [{"MedInc": 8.32, ...}],
        "predictions": [4.2, 3.8, 5.1],
        "actuals": [4.1, 3.9, 5.0]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        new_data = pd.DataFrame(data.get("new_data", []))
        predictions = data.get("predictions", [])
        actuals = data.get("actuals", [])

        # Check if retraining is needed
        decision = retraining_trigger.should_retrain(
            new_data=new_data,
            predictions=predictions if predictions else None,
            actuals=actuals if actuals else None,
        )

        return jsonify(decision)

    except Exception as e:
        logger.error(f"Error checking retraining need: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/monitoring/trigger-retraining", methods=["POST"])
def trigger_model_retraining():
    """
    Manually trigger model retraining
    """
    try:
        # Trigger retraining
        result = retraining_trigger.trigger_retraining()

        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Error triggering retraining: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/monitoring/config", methods=["GET"])
def get_monitoring_config():
    """
    Get current monitoring configuration
    """
    try:
        return jsonify(
            {
                "config": retraining_trigger.config,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error getting monitoring config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/monitoring/status", methods=["GET"])
def get_monitoring_status():
    """
    Get monitoring system status
    """
    try:
        # Check if trigger files exist
        trigger_files = []
        if os.path.exists("triggers"):
            trigger_files = [
                f for f in os.listdir("triggers") if f.endswith(".trigger")
            ]

        status = {
            "monitoring_active": True,
            "drift_detection_enabled": retraining_trigger.config.get(
                "monitoring_config", {}
            ).get("enable_drift_detection", True),
            "performance_monitoring_enabled": retraining_trigger.config.get(
                "monitoring_config", {}
            ).get("enable_performance_monitoring", True),
            "automatic_retraining_enabled": retraining_trigger.config.get(
                "enable_automatic_retraining", True
            ),
            "pending_retraining_triggers": len(trigger_files),
            "trigger_files": trigger_files,
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Load model and scaler on startup
    logger.info("Starting California Housing Price Prediction API...")

    try:
        load_model_and_scaler()
        logger.info("Model and scaler loaded successfully")

        # Start the Flask app
        app.run(host="0.0.0.0", port=5000, debug=False)

    except Exception as e:
        logger.error(f"Failed to start API: {str(e)}")
        exit(1)
