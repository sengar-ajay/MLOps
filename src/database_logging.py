"""
In-memory database logging system for MLOps pipeline
Uses SQLite in-memory database for storing logs and metrics
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional


class InMemoryDatabaseLogger:
    """
    In-memory SQLite database for storing logs and metrics
    Thread-safe implementation for concurrent access
    """

    def __init__(self, db_name="database/mlops_logs.db"):
        """
        Initialize in-memory database for logging

        Args:
            db_name: Database name (:memory: for in-memory, or file path for persistent)
        """
        self.db_name = db_name
        self.connection = None
        self.lock = threading.Lock()
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with self.lock:
            self.connection = sqlite3.connect(
                self.db_name,
                check_same_thread=False,
                isolation_level=None,  # Autocommit mode
            )
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access

            # Create logs table
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    module TEXT NOT NULL,
                    message TEXT NOT NULL,
                    extra_data TEXT  -- JSON string for additional data
                )
            """
            )

            # Create metrics table for API monitoring
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS api_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER,
                    response_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    request_data TEXT,  -- JSON string
                    response_data TEXT  -- JSON string
                )
            """
            )

            # Create model metrics table
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS model_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    rmse REAL,
                    mae REAL,
                    r2_score REAL,
                    training_time REAL,
                    parameters TEXT  -- JSON string
                )
            """
            )

            print("In-memory database initialized successfully")

    def log_message(
        self, level: str, module: str, message: str, extra_data: Optional[Dict] = None
    ):
        """
        Store log message in database

        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            module: Module name
            message: Log message
            extra_data: Additional data as dictionary
        """
        with self.lock:
            extra_json = json.dumps(extra_data) if extra_data else None
            self.connection.execute(
                """
                INSERT INTO logs (level, module, message, extra_data)
                VALUES (?, ?, ?, ?)
            """,
                (level, module, message, extra_json),
            )

    def log_api_metric(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        success: bool,
        error_message: Optional[str] = None,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
    ):
        """
        Store API metric in database

        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            response_time: Response time in seconds
            success: Whether request was successful
            error_message: Error message if any
            request_data: Request data
            response_data: Response data
        """
        with self.lock:
            request_json = json.dumps(request_data) if request_data else None
            response_json = json.dumps(response_data) if response_data else None

            self.connection.execute(
                """
                INSERT INTO api_metrics (endpoint, method, status_code, response_time, 
                                       success, error_message, request_data, response_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    endpoint,
                    method,
                    status_code,
                    response_time,
                    success,
                    error_message,
                    request_json,
                    response_json,
                ),
            )

    def log_model_metric(
        self,
        model_name: str,
        model_type: str,
        rmse: float,
        mae: float,
        r2_score: float,
        training_time: float,
        parameters: Optional[Dict] = None,
    ):
        """
        Store model training metric in database

        Args:
            model_name: Name of the model
            model_type: Type of model (e.g., RandomForest, LinearRegression)
            rmse: Root Mean Square Error
            mae: Mean Absolute Error
            r2_score: R-squared score
            training_time: Training time in seconds
            parameters: Model parameters
        """
        with self.lock:
            params_json = json.dumps(parameters) if parameters else None

            self.connection.execute(
                """
                INSERT INTO model_metrics (model_name, model_type, rmse, mae, 
                                         r2_score, training_time, parameters)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    model_name,
                    model_type,
                    rmse,
                    mae,
                    r2_score,
                    training_time,
                    params_json,
                ),
            )

    def get_logs(
        self,
        level: Optional[str] = None,
        module: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Retrieve logs from database

        Args:
            level: Filter by log level
            module: Filter by module
            limit: Maximum number of records to return

        Returns:
            List of log records
        """
        with self.lock:
            query = "SELECT * FROM logs WHERE 1=1"
            params = []

            if level:
                query += " AND level = ?"
                params.append(level)

            if module:
                query += " AND module = ?"
                params.append(module)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = self.connection.execute(query, params)
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            return [dict(row) for row in rows]

    def get_api_metrics(
        self, endpoint: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve API metrics from database

        Args:
            endpoint: Filter by endpoint
            limit: Maximum number of records to return

        Returns:
            List of API metric records
        """
        with self.lock:
            query = "SELECT * FROM api_metrics WHERE 1=1"
            params = []

            if endpoint:
                query += " AND endpoint = ?"
                params.append(endpoint)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = self.connection.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_model_metrics(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve model metrics from database

        Args:
            limit: Maximum number of records to return

        Returns:
            List of model metric records
        """
        with self.lock:
            cursor = self.connection.execute(
                """
                SELECT * FROM model_metrics 
                ORDER BY timestamp DESC 
                LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with database statistics
        """
        with self.lock:
            stats = {}

            # Count logs by level
            cursor = self.connection.execute(
                """
                SELECT level, COUNT(*) as count 
                FROM logs 
                GROUP BY level
            """
            )
            stats["logs_by_level"] = {
                row["level"]: row["count"] for row in cursor.fetchall()
            }

            # API metrics summary
            cursor = self.connection.execute(
                """
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(response_time) as avg_response_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests
                FROM api_metrics
            """
            )
            api_stats = cursor.fetchone()
            if api_stats:
                stats["api_metrics"] = {
                    "total_requests": api_stats["total_requests"],
                    "avg_response_time": api_stats["avg_response_time"],
                    "successful_requests": api_stats["successful_requests"],
                    "success_rate": (
                        api_stats["successful_requests"]
                        / api_stats["total_requests"]
                        * 100
                    )
                    if api_stats["total_requests"] > 0
                    else 0,
                }

            # Model metrics count
            cursor = self.connection.execute(
                "SELECT COUNT(*) as count FROM model_metrics"
            )
            stats["total_model_metrics"] = cursor.fetchone()["count"]

            return stats

    def clear_database(self):
        """Clear all data from database (useful for testing)"""
        with self.lock:
            self.connection.execute("DELETE FROM logs")
            self.connection.execute("DELETE FROM api_metrics")
            self.connection.execute("DELETE FROM model_metrics")
            print("Database cleared")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")


class DatabaseLogHandler(logging.Handler):
    """
    Custom logging handler that stores logs in the in-memory database
    """

    def __init__(self, db_logger: InMemoryDatabaseLogger):
        super().__init__()
        self.db_logger = db_logger

    def emit(self, record):
        """
        Emit a log record to the database

        Args:
            record: LogRecord instance
        """
        try:
            # Extract extra data if present
            extra_data = {}
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "message",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                ]:
                    extra_data[key] = value

            self.db_logger.log_message(
                level=record.levelname,
                module=record.name,
                message=record.getMessage(),
                extra_data=extra_data if extra_data else None,
            )
        except Exception as e:
            # Don't let logging errors crash the application
            print(f"Error in DatabaseLogHandler: {e}")


# Global database logger instance
db_logger = InMemoryDatabaseLogger()


def get_database_logger() -> InMemoryDatabaseLogger:
    """
    Get the global database logger instance

    Returns:
        InMemoryDatabaseLogger instance
    """
    return db_logger


def setup_database_logging(logger_name: Optional[str] = None) -> logging.Logger:
    """
    Setup logging to use both file and database handlers

    Args:
        logger_name: Name of the logger (if None, uses root logger)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(logger_name)

    # Remove existing handlers to avoid duplication
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Database handler
    db_handler = DatabaseLogHandler(db_logger)
    db_handler.setLevel(logging.INFO)
    logger.addHandler(db_handler)

    logger.setLevel(logging.INFO)
    logger.info("Database logging setup completed")

    return logger


if __name__ == "__main__":
    # Test the database logging system
    print("Testing in-memory database logging system...")

    # Setup logging
    logger = setup_database_logging("test_logger")

    # Test logging
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")

    # Test API metrics
    db_logger.log_api_metric(
        endpoint="/predict",
        method="POST",
        status_code=200,
        response_time=0.123,
        success=True,
        request_data={"test": "data"},
        response_data={"prediction": 1.23},
    )

    # Test model metrics
    db_logger.log_model_metric(
        model_name="test_model",
        model_type="RandomForest",
        rmse=0.5,
        mae=0.3,
        r2_score=0.8,
        training_time=10.5,
        parameters={"n_estimators": 100},
    )

    # Retrieve and display data
    print("\n=== Recent Logs ===")
    logs = db_logger.get_logs(limit=5)
    for log in logs:
        print(
            f"{log['timestamp']} - {log['level']} - {log['module']}: {log['message']}"
        )

    print("\n=== API Metrics ===")
    api_metrics = db_logger.get_api_metrics(limit=5)
    for metric in api_metrics:
        print(
            f"{metric['timestamp']} - {metric['method']} {metric['endpoint']} - "
            f"Status: {metric['status_code']}, Time: {metric['response_time']:.3f}s"
        )

    print("\n=== Model Metrics ===")
    model_metrics = db_logger.get_model_metrics(limit=5)
    for metric in model_metrics:
        print(
            f"{metric['timestamp']} - {metric['model_name']} ({metric['model_type']}) - "
            f"RMSE: {metric['rmse']:.3f}, R2: {metric['r2_score']:.3f}"
        )

    print("\n=== Database Stats ===")
    stats = db_logger.get_database_stats()
    print(json.dumps(stats, indent=2))

    print("\nIn-memory database logging system test completed!")
