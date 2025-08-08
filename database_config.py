"""
Database configuration for MLOps logging system
Switch between in-memory and persistent database
"""

import os

# Database configuration
DATABASE_CONFIG = {
    # For external DB tools access, use file-based database
    "use_persistent": True,  # Set to False for in-memory
    "db_path": "database/mlops_logs.db",
    "auto_create_dir": True
}

def get_database_path():
    """Get the appropriate database path based on configuration"""
    
    if DATABASE_CONFIG["use_persistent"]:
        db_path = DATABASE_CONFIG["db_path"]
        
        # Create directory if needed
        if DATABASE_CONFIG["auto_create_dir"]:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        return db_path
    else:
        # In-memory database
        return ":memory:"

def get_database_info():
    """Get database configuration information"""
    db_path = get_database_path()
    
    if db_path == ":memory:":
        return {
            "type": "in-memory",
            "path": ":memory:",
            "external_access": False,
            "description": "Fast in-memory database, data lost on restart"
        }
    else:
        abs_path = os.path.abspath(db_path)
        file_exists = os.path.exists(db_path)
        file_size = os.path.getsize(db_path) if file_exists else 0
        
        return {
            "type": "persistent",
            "path": db_path,
            "absolute_path": abs_path,
            "external_access": True,
            "file_exists": file_exists,
            "file_size": file_size,
            "description": "Persistent file database, accessible by external tools"
        }

if __name__ == "__main__":
    info = get_database_info()
    print("Database Configuration:")
    print(f"Type: {info['type']}")
    print(f"Path: {info['path']}")
    if info['type'] == 'persistent':
        print(f"Absolute Path: {info['absolute_path']}")
        print(f"File Exists: {info['file_exists']}")
        print(f"File Size: {info['file_size']} bytes")
    print(f"External Access: {info['external_access']}")
    print(f"Description: {info['description']}")