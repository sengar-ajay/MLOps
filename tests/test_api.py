"""
Unit tests for the Flask API
"""

import json
import os
import sys

import joblib
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from api import app, load_model_and_scaler  # noqa: E402


@pytest.fixture
def client():
    """Create a test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data():
    """Sample input data for testing"""
    return {
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        "AveRooms": 6.98,
        "AveBedrms": 1.02,
        "Population": 322.0,
        "AveOccup": 2.55,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }


@pytest.fixture
def setup_test_model():
    """Set up test model and scaler"""
    # Create temporary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Create a simple test model
    model = RandomForestRegressor(n_estimators=10, random_state=42)

    # Create test data
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
    X_test = pd.DataFrame(
        [[8.3252, 41.0, 6.98, 1.02, 322.0, 2.55, 37.88, -122.23]], columns=feature_names
    )
    y_test = [4.526]

    # Train model
    model.fit(X_test, y_test)

    # Create and fit scaler
    scaler = StandardScaler()
    scaler.fit(X_test)

    # Save model and scaler
    joblib.dump(model, "models/best_model.pkl")
    joblib.dump(scaler, "data/scaler.pkl")

    # Save sample training data
    X_test.to_csv("data/X_train.csv", index=False)

    yield

    # Cleanup
    if os.path.exists("models/best_model.pkl"):
        os.remove("models/best_model.pkl")
    if os.path.exists("data/scaler.pkl"):
        os.remove("data/scaler.pkl")
    if os.path.exists("data/X_train.csv"):
        os.remove("data/X_train.csv")


def test_home_endpoint(client):
    """Test the home endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert "California Housing Price Prediction API" in data["message"]


def test_health_endpoint_without_model(client):
    """Test health endpoint when model is not loaded"""
    response = client.get("/health")
    # Should return 500 if model is not loaded
    assert response.status_code == 500


def test_info_endpoint_without_model(client):
    """Test info endpoint when model is not loaded"""
    response = client.get("/info")
    # Should handle gracefully even without model
    assert response.status_code in [200, 500]


def test_predict_without_model(client, sample_data):
    """Test prediction endpoint without model loaded"""
    response = client.post(
        "/predict", data=json.dumps(sample_data), content_type="application/json"
    )
    assert response.status_code == 500


def test_predict_invalid_json(client):
    """Test prediction with invalid JSON"""
    response = client.post(
        "/predict", data="invalid json", content_type="application/json"
    )
    assert response.status_code == 400


def test_predict_missing_features(client, setup_test_model):
    """Test prediction with missing features"""
    load_model_and_scaler()

    incomplete_data = {
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        # Missing other required features
    }

    response = client.post(
        "/predict", data=json.dumps(incomplete_data), content_type="application/json"
    )
    assert response.status_code == 400


def test_predict_invalid_feature_values(client, setup_test_model):
    """Test prediction with invalid feature values"""
    load_model_and_scaler()

    invalid_data = {
        "MedInc": "not_a_number",
        "HouseAge": 41.0,
        "AveRooms": 6.98,
        "AveBedrms": 1.02,
        "Population": 322.0,
        "AveOccup": 2.55,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }

    response = client.post(
        "/predict", data=json.dumps(invalid_data), content_type="application/json"
    )
    assert response.status_code == 400


def test_batch_predict_invalid_format(client):
    """Test batch prediction with invalid format"""
    response = client.post(
        "/predict_batch",
        data=json.dumps({"wrong_key": []}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_batch_predict_empty_instances(client):
    """Test batch prediction with empty instances"""
    response = client.post(
        "/predict_batch",
        data=json.dumps({"instances": []}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_404_endpoint(client):
    """Test 404 error handling"""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


# Integration tests with model loaded
def test_health_with_model(client, setup_test_model):
    """Test health endpoint with model loaded"""
    # Load model and scaler
    load_model_and_scaler()

    response = client.get("/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"


def test_info_with_model(client, setup_test_model):
    """Test info endpoint with model loaded"""
    load_model_and_scaler()

    response = client.get("/info")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "model_type" in data
    assert "features" in data
    assert data["model_loaded"] is True


def test_predict_with_model(client, setup_test_model, sample_data):
    """Test prediction with model loaded"""
    load_model_and_scaler()

    response = client.post(
        "/predict", data=json.dumps(sample_data), content_type="application/json"
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "prediction" in data
    assert isinstance(data["prediction"], (int, float))


def test_batch_predict_with_model(client, setup_test_model, sample_data):
    """Test batch prediction with model loaded"""
    load_model_and_scaler()

    batch_data = {"instances": [sample_data, sample_data]}

    response = client.post(
        "/predict_batch", data=json.dumps(batch_data), content_type="application/json"
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "predictions" in data
    assert len(data["predictions"]) == 2
    assert all(isinstance(p, (int, float)) for p in data["predictions"])
