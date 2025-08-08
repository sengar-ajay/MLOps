#!/usr/bin/env python3
"""
Setup persistent SQLite database for external database tools access
This creates a file-based database that can be accessed by DB browsers
"""

import os
from src.database_logging import InMemoryDatabaseLogger

def create_persistent_database():
    """Create a persistent SQLite database file"""
    
    # Create database directory
    db_dir = "database"
    os.makedirs(db_dir, exist_ok=True)
    
    # Create persistent database file
    db_path = os.path.join(db_dir, "mlops_logs.db")
    
    print(f"Creating persistent database at: {db_path}")
    
    # Initialize database with file path instead of :memory:
    db_logger = InMemoryDatabaseLogger(db_name=db_path)
    
    # Add sample data for testing
    print("Adding sample data...")
    
    # Sample logs
    db_logger.log_message("INFO", "setup", "Database setup completed")
    db_logger.log_message("WARNING", "api", "High response time detected")
    db_logger.log_message("ERROR", "model", "Model training failed")
    db_logger.log_message("INFO", "api", "Prediction request processed")
    
    # Sample API metrics
    db_logger.log_api_metric(
        endpoint="/predict",
        method="POST",
        status_code=200,
        response_time=0.156,
        success=True,
        request_data={"MedInc": 8.32},
        response_data={"prediction": 4.526}
    )
    
    db_logger.log_api_metric(
        endpoint="/health", 
        method="GET",
        status_code=200,
        response_time=0.023,
        success=True
    )
    
    # Sample model metrics
    db_logger.log_model_metric(
        model_name="RandomForest_v1",
        model_type="RandomForestRegressor", 
        rmse=0.5443,
        mae=0.3662,
        r2_score=0.7739,
        training_time=25.5,
        parameters={"n_estimators": 100}
    )
    
    print(f"✅ Persistent database created: {db_path}")
    print(f"📊 Database size: {os.path.getsize(db_path)} bytes")
    
    return db_path

def show_database_tools():
    """Show available database management tools"""
    print("\n" + "="*60)
    print("🛠️  DATABASE MANAGEMENT TOOLS")
    print("="*60)
    
    tools = [
        {
            "name": "DB Browser for SQLite",
            "description": "Free, open-source SQLite database browser",
            "download": "https://sqlitebrowser.org/",
            "platforms": "Windows, macOS, Linux",
            "features": "GUI query editor, table browser, data export"
        },
        {
            "name": "SQLiteStudio", 
            "description": "Advanced SQLite database manager",
            "download": "https://sqlitestudio.pl/",
            "platforms": "Windows, macOS, Linux",
            "features": "SQL editor, data import/export, plugins"
        },
        {
            "name": "DBeaver",
            "description": "Universal database tool (supports SQLite)",
            "download": "https://dbeaver.io/",
            "platforms": "Windows, macOS, Linux",
            "features": "Professional DB management, ER diagrams"
        },
        {
            "name": "SQLite Online",
            "description": "Browser-based SQLite editor",
            "download": "https://sqliteonline.com/",
            "platforms": "Web browser",
            "features": "No installation required, online access"
        }
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. **{tool['name']}**")
        print(f"   Description: {tool['description']}")
        print(f"   Download: {tool['download']}")
        print(f"   Platforms: {tool['platforms']}")
        print(f"   Features: {tool['features']}")

def show_sample_queries():
    """Show sample SQL queries for database exploration"""
    print("\n" + "="*60) 
    print("📝 SAMPLE SQL QUERIES")
    print("="*60)
    
    queries = [
        {
            "purpose": "View all tables",
            "query": "SELECT name FROM sqlite_master WHERE type='table';"
        },
        {
            "purpose": "Get recent logs",
            "query": """
SELECT timestamp, level, module, message 
FROM logs 
ORDER BY timestamp DESC 
LIMIT 10;"""
        },
        {
            "purpose": "Count logs by level",
            "query": """
SELECT level, COUNT(*) as count 
FROM logs 
GROUP BY level 
ORDER BY count DESC;"""
        },
        {
            "purpose": "API success rate",
            "query": """
SELECT 
    endpoint,
    COUNT(*) as total_requests,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
    ROUND(AVG(response_time), 3) as avg_response_time
FROM api_metrics 
GROUP BY endpoint;"""
        },
        {
            "purpose": "Best performing models",
            "query": """
SELECT model_name, model_type, rmse, mae, r2_score
FROM model_metrics 
ORDER BY rmse ASC 
LIMIT 5;"""
        },
        {
            "purpose": "Error logs with details",
            "query": """
SELECT timestamp, module, message
FROM logs 
WHERE level = 'ERROR' 
ORDER BY timestamp DESC;"""
        }
    ]
    
    for i, query_info in enumerate(queries, 1):
        print(f"\n{i}. {query_info['purpose']}:")
        print(f"```sql{query_info['query']}```")

def show_database_schema():
    """Show the database schema"""
    print("\n" + "="*60)
    print("🏗️  DATABASE SCHEMA")
    print("="*60)
    
    print("""
📋 **logs** table:
- id (INTEGER PRIMARY KEY)
- timestamp (DATETIME) 
- level (TEXT) - INFO, WARNING, ERROR
- module (TEXT) - Module name
- message (TEXT) - Log message
- extra_data (TEXT) - JSON string

📊 **api_metrics** table:
- id (INTEGER PRIMARY KEY)
- timestamp (DATETIME)
- endpoint (TEXT) - API endpoint
- method (TEXT) - HTTP method
- status_code (INTEGER) - HTTP status
- response_time (REAL) - Response time in seconds
- success (BOOLEAN) - Success flag
- error_message (TEXT) - Error details
- request_data (TEXT) - JSON request data
- response_data (TEXT) - JSON response data

🤖 **model_metrics** table:
- id (INTEGER PRIMARY KEY) 
- timestamp (DATETIME)
- model_name (TEXT) - Model name
- model_type (TEXT) - Model type/class
- rmse (REAL) - Root Mean Square Error
- mae (REAL) - Mean Absolute Error
- r2_score (REAL) - R-squared score
- training_time (REAL) - Training time in seconds
- parameters (TEXT) - JSON model parameters
""")

if __name__ == "__main__":
    print("🗄️  PERSISTENT DATABASE SETUP")
    print("="*80)
    
    # Create persistent database
    db_path = create_persistent_database()
    
    # Show database tools
    show_database_tools()
    
    # Show database schema
    show_database_schema()
    
    # Show sample queries
    show_sample_queries()
    
    print("\n" + "="*80)
    print("✅ SETUP COMPLETE")
    print("="*80)
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Download a SQLite database tool (recommended: DB Browser for SQLite)")
    print(f"2. Open the database file: {os.path.abspath(db_path)}")
    print(f"3. Run SQL queries to explore the data")
    print(f"4. Use the sample queries provided above")
    
    print(f"\n📁 Database Location: {os.path.abspath(db_path)}")
    print(f"💾 Database Size: {os.path.getsize(db_path)} bytes")
    
    print(f"\n🔄 To keep database updated:")
    print(f"   Modify src/database_logging.py to use file path instead of :memory:")
    print(f"   Change: db_name=':memory:' to db_name='{db_path}'")