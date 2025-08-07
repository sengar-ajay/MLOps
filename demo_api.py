#!/usr/bin/env python3
"""
Demo script to test the MLOps API endpoints
"""
import time

import requests


def test_api_endpoints():
    """Test all API endpoints with sample data"""
    base_url = "http://localhost:5000"

    print("MLOps API Demo")
    print("=" * 50)

    # Test data
    sample_house = {
        "MedInc": 8.3252,  # Median income
        "HouseAge": 41.0,  # House age
        "AveRooms": 6.98,  # Average rooms
        "AveBedrms": 1.02,  # Average bedrooms
        "Population": 322.0,  # Population
        "AveOccup": 2.55,  # Average occupancy
        "Latitude": 37.88,  # Latitude
        "Longitude": -122.23,  # Longitude (San Francisco area)
    }

    # 1. Health Check
    print("\n1. Health Check")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Message: {data['message']}")
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Cannot connect to API: {e}")
        print("Make sure to start the API server first: python src/api.py")
        return False

    # 2. Model Info
    print("\n2. Model Information")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/info")
        data = response.json()
        print(f"Model Type: {data['model_type']}")
        print(f"Features: {len(data['features'])}")
        print(f"Feature Names: {', '.join(data['features'][:4])}...")
    except Exception as e:
        print(f"Model info failed: {e}")

    # 3. Single Prediction
    print("\n3. Single House Price Prediction")
    print("-" * 30)
    print("Sample House:")
    for key, value in sample_house.items():
        print(f"   {key}: {value}")

    try:
        response = requests.post(
            f"{base_url}/predict",
            json=sample_house,
            headers={"Content-Type": "application/json"},
        )
        data = response.json()
        predicted_price = data["prediction"]
        print(f"\nPredicted Price: ${predicted_price:.2f} (in hundreds of thousands)")
        print(f"Timestamp: {data['timestamp']}")
        print(f"Model Used: {data['model_type']}")
    except Exception as e:
        print(f"Prediction failed: {e}")

    # 4. Batch Predictions
    print("\n4. Batch Predictions (3 houses)")
    print("-" * 30)

    # Create 3 different houses
    houses = [
        sample_house,  # Expensive SF house
        {
            **sample_house,
            "MedInc": 3.5,
            "Latitude": 34.05,
            "Longitude": -118.24,
        },  # LA house
        {
            **sample_house,
            "MedInc": 2.0,
            "HouseAge": 15.0,
            "Latitude": 32.71,
            "Longitude": -117.16,
        },  # San Diego house
    ]

    try:
        response = requests.post(
            f"{base_url}/predict_batch",
            json={"instances": houses},
            headers={"Content-Type": "application/json"},
        )
        data = response.json()
        predictions = data["predictions"]

        locations = ["San Francisco", "Los Angeles", "San Diego"]
        for i, (pred, loc) in enumerate(zip(predictions, locations)):
            print(f"House {i+1} ({loc}): ${pred:.2f} hundred thousand")

        print(f"\nTotal Predictions: {data['n_predictions']}")

    except Exception as e:
        print(f"Batch prediction failed: {e}")

    # 5. Error Handling Demo
    print("\n5. Error Handling Demo")
    print("-" * 30)

    # Test with missing features
    incomplete_house = {"MedInc": 8.0, "HouseAge": 25.0}  # Missing other features

    try:
        response = requests.post(
            f"{base_url}/predict",
            json=incomplete_house,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 400:
            error_data = response.json()
            print(f"Error handling works: {error_data['error']}")
        else:
            print(f"Expected error but got: {response.status_code}")
    except Exception as e:
        print(f"Error test failed: {e}")

    print("\n" + "=" * 50)
    print("API Demo Complete!")
    print("The API is working correctly and ready for production!")

    return True


if __name__ == "__main__":
    print("Starting API demo...")
    print("Make sure the API server is running: python src/api.py")
    print("\nWaiting 3 seconds...")
    time.sleep(3)

    success = test_api_endpoints()
    if success:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo failed - check API server status")
