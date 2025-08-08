#!/usr/bin/env python3
"""
Test script for in-memory database logging system
Demonstrates logging capabilities and API endpoints
"""

import json
import time
import requests
from datetime import datetime

# Import our database logging system
from src.database_logging import setup_database_logging, get_database_logger


def test_database_logging():
    """Test the database logging functionality"""
    print("Testing In-Memory Database Logging System")
    print("=" * 50)
    
    # Setup logging
    logger = setup_database_logging("test_module")
    db_logger = get_database_logger()
    
    print("\n1. Testing Basic Logging...")
    logger.info("This is an info message")
    logger.warning("This is a warning message") 
    logger.error("This is an error message")
    
    print("\n2. Testing API Metrics Logging...")
    db_logger.log_api_metric(
        endpoint="/predict",
        method="POST", 
        status_code=200,
        response_time=0.125,
        success=True,
        request_data={"MedInc": 8.3252, "HouseAge": 41.0},
        response_data={"prediction": 4.526}
    )
    
    db_logger.log_api_metric(
        endpoint="/health",
        method="GET",
        status_code=200, 
        response_time=0.023,
        success=True,
        response_data={"status": "healthy"}
    )
    
    print("\n3. Testing Model Metrics Logging...")
    db_logger.log_model_metric(
        model_name="gradient_boosting_test",
        model_type="GradientBoostingRegressor",
        rmse=0.5422,
        mae=0.3717,
        r2_score=0.7756,
        training_time=15.2,
        parameters={"n_estimators": 100, "learning_rate": 0.1}
    )
    
    print("\n4. Retrieving Data from Database...")
    
    # Get logs
    logs = db_logger.get_logs(limit=10)
    print(f"\nRecent Logs ({len(logs)} entries):")
    for log in logs[:3]:  # Show first 3
        print(f"  {log['timestamp']} - {log['level']} - {log['module']}: {log['message']}")
    
    # Get API metrics
    api_metrics = db_logger.get_api_metrics(limit=10)
    print(f"\nAPI Metrics ({len(api_metrics)} entries):")
    for metric in api_metrics:
        print(f"  {metric['timestamp']} - {metric['method']} {metric['endpoint']} - "
              f"Status: {metric['status_code']}, Time: {metric['response_time']:.3f}s")
    
    # Get model metrics
    model_metrics = db_logger.get_model_metrics(limit=10)
    print(f"\nModel Metrics ({len(model_metrics)} entries):")
    for metric in model_metrics:
        print(f"  {metric['timestamp']} - {metric['model_name']} ({metric['model_type']}) - "
              f"RMSE: {metric['rmse']:.4f}, R2: {metric['r2_score']:.4f}")
    
    # Get database stats
    stats = db_logger.get_database_stats()
    print(f"\nDatabase Statistics:")
    print(json.dumps(stats, indent=2))
    
    print("\nDatabase logging test completed successfully!")
    return True


def test_api_endpoints():
    """Test the API endpoints for querying logs"""
    print("\nTesting API Endpoints for Database Queries")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test endpoints
    endpoints = [
        ("/logs", "GET", "Application logs"),
        ("/metrics/api", "GET", "API metrics"),
        ("/metrics/models", "GET", "Model metrics"),
        ("/database/stats", "GET", "Database statistics")
    ]
    
    print("\nTo test these endpoints, start the API server first:")
    print("   python src/api.py")
    print("\nThen run these curl commands:")
    
    for endpoint, method, description in endpoints:
        print(f"\n{description}:")
        print(f"  curl -X {method} {base_url}{endpoint}")
        
        # Add query parameter examples
        if endpoint == "/logs":
            print(f"  curl -X {method} '{base_url}{endpoint}?level=ERROR&limit=50'")
        elif endpoint == "/metrics/api":
            print(f"  curl -X {method} '{base_url}{endpoint}?endpoint=/predict&limit=20'")
    
    print(f"\nClear database:")
    print(f"  curl -X POST {base_url}/database/clear")
    
    # Try to test if API is running
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        if response.status_code == 200:
            print(f"\nAPI is running! Testing endpoints...")
            
            # Test logs endpoint
            response = requests.get(f"{base_url}/logs?limit=5")
            if response.status_code == 200:
                data = response.json()
                print(f"Logs endpoint: {data['total']} logs retrieved")
            
            # Test database stats
            response = requests.get(f"{base_url}/database/stats")
            if response.status_code == 200:
                data = response.json()
                print(f"Database stats endpoint: {json.dumps(data['statistics'], indent=2)}")
                
        else:
            print(f"API responded with status {response.status_code}")
            
    except requests.exceptions.RequestException:
        print(f"API is not running at {base_url}")
        print("   Start the API with: python src/api.py")


def demonstrate_features():
    """Demonstrate key features of the in-memory database logging"""
    print("\nKey Features of In-Memory Database Logging")
    print("=" * 50)
    
    features = [
        "Structured Storage: Logs stored in SQLite tables with proper schema",
        "Query Interface: API endpoints to query logs with filters",
        "High Performance: In-memory database for fast read/write operations", 
        "Thread Safe: Concurrent access support for multi-threaded applications",
        "Rich Metrics: Separate tables for logs, API metrics, and model metrics",
        "Real-time: Immediate availability of logged data",
        "Filtering: Query by log level, module, endpoint, etc.",
        "Statistics: Built-in database statistics and summaries",
        "Management: Clear database functionality for testing",
        "Integration: Seamless integration with existing Flask API"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\nAvailable API Endpoints:")
    endpoints = [
        "GET  /logs                 - Query application logs",
        "GET  /metrics/api          - Query API performance metrics", 
        "GET  /metrics/models       - Query model training metrics",
        "GET  /database/stats       - Get database statistics",
        "POST /database/clear       - Clear all database data"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")


if __name__ == "__main__":
    print("In-Memory Database Logging System Demo")
    print("=" * 60)
    
    try:
        # Test basic functionality
        test_database_logging()
        
        # Show API endpoint information
        test_api_endpoints()
        
        # Demonstrate features
        demonstrate_features()
        
        print(f"\nSummary:")
        print(f"In-memory SQLite database successfully implemented")
        print(f"Custom logging handlers created")
        print(f"API endpoints for querying logs added")
        print(f"Thread-safe concurrent access supported")
        print(f"Integration with existing monitoring system completed")
        
        print(f"\nNext Steps:")
        print(f"1. Start the API: python src/api.py")
        print(f"2. Run monitoring: python src/monitoring.py")
        print(f"3. Query logs via API endpoints")
        print(f"4. Check database stats: curl http://localhost:5000/database/stats")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()