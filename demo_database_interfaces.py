#!/usr/bin/env python3
"""
Demo script showing all available database interfaces
"""

from src.database_logging import get_database_logger, setup_database_logging
import json

def populate_sample_data():
    """Populate database with sample data"""
    print("🔄 Populating database with sample data...")
    
    # Setup logging to populate logs table
    logger = setup_database_logging("demo_module")
    db_logger = get_database_logger()
    
    # Add sample logs
    logger.info("Demo application started")
    logger.warning("This is a sample warning")
    logger.error("This is a sample error")
    logger.info("Processing user request")
    logger.info("Demo completed successfully")
    
    # Add sample API metrics
    db_logger.log_api_metric(
        endpoint="/predict",
        method="POST",
        status_code=200,
        response_time=0.156,
        success=True,
        request_data={"MedInc": 8.32, "HouseAge": 41.0},
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
    
    db_logger.log_api_metric(
        endpoint="/predict",
        method="POST",
        status_code=400,
        response_time=0.045,
        success=False,
        error_message="Missing required fields",
        request_data={"incomplete": "data"}
    )
    
    # Add sample model metrics
    db_logger.log_model_metric(
        model_name="RandomForest_Demo",
        model_type="RandomForestRegressor",
        rmse=0.5443,
        mae=0.3662,
        r2_score=0.7739,
        training_time=25.5,
        parameters={"n_estimators": 100, "max_depth": 10}
    )
    
    db_logger.log_model_metric(
        model_name="GradientBoosting_Demo", 
        model_type="GradientBoostingRegressor",
        rmse=0.5422,
        mae=0.3717,
        r2_score=0.7756,
        training_time=45.2,
        parameters={"n_estimators": 100, "learning_rate": 0.1}
    )
    
    print("✅ Sample data added to database")
    return db_logger


def demo_direct_python_interface(db_logger):
    """Demo direct Python interface"""
    print("\n" + "="*60)
    print("🐍 DIRECT PYTHON INTERFACE")
    print("="*60)
    
    # Query logs
    print("\n📝 Recent Logs:")
    logs = db_logger.get_logs(limit=5)
    for log in logs:
        print(f"  {log['timestamp']} | {log['level']:8} | {log['message']}")
    
    # Query API metrics
    print("\n📊 API Metrics:")
    api_metrics = db_logger.get_api_metrics(limit=5)
    for metric in api_metrics:
        status_icon = "✅" if metric['success'] else "❌"
        print(f"  {metric['timestamp']} | {status_icon} | {metric['method']} {metric['endpoint']} | {metric['response_time']:.3f}s")
    
    # Query model metrics
    print("\n🤖 Model Metrics:")
    model_metrics = db_logger.get_model_metrics(limit=5)
    for metric in model_metrics:
        print(f"  {metric['model_name']} | RMSE: {metric['rmse']:.4f} | R2: {metric['r2_score']:.4f}")
    
    # Database statistics
    print("\n📈 Database Statistics:")
    stats = db_logger.get_database_stats()
    print(json.dumps(stats, indent=2))


def demo_filtering_capabilities(db_logger):
    """Demo advanced filtering capabilities"""
    print("\n" + "="*60)
    print("🔍 FILTERING CAPABILITIES")
    print("="*60)
    
    # Filter logs by level
    print("\n❌ Error Logs Only:")
    error_logs = db_logger.get_logs(level="ERROR", limit=10)
    for log in error_logs:
        print(f"  {log['timestamp']} | {log['message']}")
    
    # Filter API metrics by endpoint
    print("\n🎯 /predict Endpoint Metrics:")
    predict_metrics = db_logger.get_api_metrics(endpoint="/predict", limit=10)
    for metric in predict_metrics:
        status_icon = "✅" if metric['success'] else "❌"
        print(f"  {status_icon} | Status: {metric['status_code']} | Time: {metric['response_time']:.3f}s")


def demo_curl_commands():
    """Show curl commands for API interface"""
    print("\n" + "="*60)
    print("🌐 REST API INTERFACE (curl commands)")
    print("="*60)
    
    print("\n💡 Start API server first: python src/api.py")
    print("\n📝 Query logs:")
    print("  curl http://localhost:5000/logs")
    print("  curl 'http://localhost:5000/logs?level=ERROR&limit=20'")
    
    print("\n📊 Query API metrics:")
    print("  curl http://localhost:5000/metrics/api")
    print("  curl 'http://localhost:5000/metrics/api?endpoint=/predict'")
    
    print("\n🤖 Query model metrics:")
    print("  curl http://localhost:5000/metrics/models")
    
    print("\n📈 Database statistics:")
    print("  curl http://localhost:5000/database/stats")
    
    print("\n🧹 Clear database:")
    print("  curl -X POST http://localhost:5000/database/clear")


def demo_inspector_tool():
    """Show interactive inspector tool"""
    print("\n" + "="*60)
    print("🔧 INTERACTIVE INSPECTOR TOOL")
    print("="*60)
    
    print("\n🚀 Interactive mode:")
    print("  python database_inspector.py")
    
    print("\n📊 Quick stats:")
    print("  python database_inspector.py --stats")
    
    print("\n✨ Features:")
    print("  - Browse logs with filtering")
    print("  - View API performance metrics")
    print("  - Check model training results")
    print("  - Real-time database statistics")
    print("  - Clear database option")


if __name__ == "__main__":
    print("🚀 DATABASE INTERFACES DEMONSTRATION")
    print("="*80)
    
    # Populate sample data
    db_logger = populate_sample_data()
    
    # Demo all interfaces
    demo_direct_python_interface(db_logger)
    demo_filtering_capabilities(db_logger)
    demo_curl_commands()
    demo_inspector_tool()
    
    print("\n" + "="*80)
    print("✅ ALL DATABASE INTERFACES DEMONSTRATED")
    print("="*80)
    
    print("\n🎯 Summary of Available Interfaces:")
    print("1. 🌐 REST API Endpoints (Production)")
    print("2. 🐍 Direct Python Interface (Development)")
    print("3. 🔧 Interactive Inspector Tool (Debugging)")
    print("4. 📋 Postman Collection (Testing)")
    print("5. 🧪 Test Scripts (Validation)")
    
    print("\n🔥 The database is ready for inspection!")
    print("   Try: python database_inspector.py")