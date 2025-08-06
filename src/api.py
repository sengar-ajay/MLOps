"""
Flask API for serving the California Housing price prediction model
"""
import os
import numpy as np
import pandas as pd
import joblib
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variables for model and scaler
model = None
scaler = None
feature_names = None

def load_model_and_scaler():
    """
    Load the trained model and scaler
    """
    global model, scaler, feature_names
    
    try:
        # Load model
        model_path = 'models/best_model.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
        else:
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load scaler
        scaler_path = 'data/scaler.pkl'
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded from {scaler_path}")
        else:
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        
        # Load feature names from training data
        feature_data_path = 'data/X_train.csv'
        if os.path.exists(feature_data_path):
            sample_data = pd.read_csv(feature_data_path, nrows=1)
            feature_names = list(sample_data.columns)
            logger.info(f"Feature names loaded: {feature_names}")
        else:
            # Default California Housing feature names
            feature_names = [
                'MedInc', 'HouseAge', 'AveRooms', 'AveBedrms',
                'Population', 'AveOccup', 'Latitude', 'Longitude'
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
    expected_features = feature_names if feature_names is not None else [
        'MedInc', 'HouseAge', 'AveRooms', 'AveBedrms',
        'Population', 'AveOccup', 'Latitude', 'Longitude'
    ]
    
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

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint with API information
    """
    return jsonify({
        'message': 'California Housing Price Prediction API',
        'version': '1.0.0',
        'endpoints': {
            '/predict': 'POST - Make price predictions',
            '/health': 'GET - Check API health',
            '/info': 'GET - Get model information'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    try:
        # Check if model and scaler are loaded
        if model is None or scaler is None:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Model or scaler not loaded',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        return jsonify({
            'status': 'healthy',
            'message': 'API is running and model is loaded',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/info', methods=['GET'])
def info():
    """
    Model information endpoint
    """
    try:
        model_info = {
            'model_type': type(model).__name__,
            'features': feature_names,
            'n_features': len(feature_names),
            'model_loaded': model is not None,
            'scaler_loaded': scaler is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add model-specific parameters if available
        if hasattr(model, 'get_params'):
            model_info['model_parameters'] = model.get_params()
        
        return jsonify(model_info)
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint
    
    Expected input format:
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
    try:
        # Get JSON data from request
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({
                'error': 'Invalid JSON format',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        if data is None:
            return jsonify({
                'error': 'No JSON data provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Log the prediction request
        logger.info(f"Prediction request received: {data}")
        
        # Check if model is loaded
        if model is None or scaler is None or feature_names is None:
            return jsonify({
                'error': 'Model not properly loaded',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Validate input
        is_valid, error_message = validate_input(data)
        if not is_valid:
            return jsonify({
                'error': error_message,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Prepare input data
        input_data = pd.DataFrame([data])[feature_names]
        
        # Scale the input
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction = model.predict(input_scaled)[0]
        
        # Log the prediction
        logger.info(f"Prediction made: {prediction}")
        
        return jsonify({
            'prediction': float(prediction),
            'input': data,
            'timestamp': datetime.now().isoformat(),
            'model_type': type(model).__name__
        })
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/predict_batch', methods=['POST'])
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
        
        if data is None or 'instances' not in data:
            return jsonify({
                'error': 'No instances provided. Expected format: {"instances": [...]}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        instances = data['instances']
        
        if not isinstance(instances, list) or len(instances) == 0:
            return jsonify({
                'error': 'Instances must be a non-empty list',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Validate each instance
        predictions = []
        for i, instance in enumerate(instances):
            is_valid, error_message = validate_input(instance)
            if not is_valid:
                return jsonify({
                    'error': f'Instance {i}: {error_message}',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        # Prepare input data
        input_df = pd.DataFrame(instances)[feature_names]
        
        # Scale the input
        input_scaled = scaler.transform(input_df)
        
        # Make predictions
        predictions = model.predict(input_scaled).tolist()
        
        logger.info(f"Batch prediction made for {len(instances)} instances")
        
        return jsonify({
            'predictions': predictions,
            'n_predictions': len(predictions),
            'timestamp': datetime.now().isoformat(),
            'model_type': type(model).__name__
        })
        
    except Exception as e:
        logger.error(f"Error making batch prediction: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Please check the API documentation',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Load model and scaler on startup
    logger.info("Starting California Housing Price Prediction API...")
    
    try:
        load_model_and_scaler()
        logger.info("Model and scaler loaded successfully")
        
        # Start the Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start API: {str(e)}")
        exit(1)