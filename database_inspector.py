#!/usr/bin/env python3
"""
Interactive database inspector for in-memory database
Direct interface to query and inspect database entries
"""

from src.database_logging import get_database_logger
import json
from datetime import datetime


def inspect_database():
    """Interactive database inspection tool"""
    db_logger = get_database_logger()
    
    print("=" * 60)
    print("IN-MEMORY DATABASE INSPECTOR")
    print("=" * 60)
    
    while True:
        print("\nAvailable Commands:")
        print("1. Show all logs")
        print("2. Show logs by level (INFO, WARNING, ERROR)")
        print("3. Show API metrics")
        print("4. Show model metrics")
        print("5. Show database statistics")
        print("6. Clear database")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            show_all_logs(db_logger)
        elif choice == "2":
            show_logs_by_level(db_logger)
        elif choice == "3":
            show_api_metrics(db_logger)
        elif choice == "4":
            show_model_metrics(db_logger)
        elif choice == "5":
            show_database_stats(db_logger)
        elif choice == "6":
            clear_database(db_logger)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def show_all_logs(db_logger):
    """Show all logs from database"""
    limit = input("Enter limit (default 10): ").strip() or "10"
    try:
        limit = int(limit)
        logs = db_logger.get_logs(limit=limit)
        
        print(f"\n--- Recent {len(logs)} Logs ---")
        for log in logs:
            print(f"{log['timestamp']} | {log['level']:8} | {log['module']:15} | {log['message']}")
        
        if not logs:
            print("No logs found in database.")
            
    except ValueError:
        print("Invalid limit. Please enter a number.")


def show_logs_by_level(db_logger):
    """Show logs filtered by level"""
    level = input("Enter log level (INFO, WARNING, ERROR): ").strip().upper()
    limit = input("Enter limit (default 10): ").strip() or "10"
    
    try:
        limit = int(limit)
        logs = db_logger.get_logs(level=level, limit=limit)
        
        print(f"\n--- {level} Logs ({len(logs)} entries) ---")
        for log in logs:
            print(f"{log['timestamp']} | {log['module']:15} | {log['message']}")
        
        if not logs:
            print(f"No {level} logs found in database.")
            
    except ValueError:
        print("Invalid limit. Please enter a number.")


def show_api_metrics(db_logger):
    """Show API performance metrics"""
    endpoint = input("Enter endpoint filter (optional): ").strip() or None
    limit = input("Enter limit (default 10): ").strip() or "10"
    
    try:
        limit = int(limit)
        metrics = db_logger.get_api_metrics(endpoint=endpoint, limit=limit)
        
        print(f"\n--- API Metrics ({len(metrics)} entries) ---")
        for metric in metrics:
            success_icon = "✅" if metric['success'] else "❌"
            print(f"{metric['timestamp']} | {success_icon} | {metric['method']:4} {metric['endpoint']:15} | "
                  f"Status: {metric['status_code']} | Time: {metric['response_time']:.3f}s")
        
        if not metrics:
            print("No API metrics found in database.")
            
    except ValueError:
        print("Invalid limit. Please enter a number.")


def show_model_metrics(db_logger):
    """Show model training metrics"""
    limit = input("Enter limit (default 10): ").strip() or "10"
    
    try:
        limit = int(limit)
        metrics = db_logger.get_model_metrics(limit=limit)
        
        print(f"\n--- Model Metrics ({len(metrics)} entries) ---")
        for metric in metrics:
            print(f"{metric['timestamp']} | {metric['model_name']:20} ({metric['model_type']:15}) | "
                  f"RMSE: {metric['rmse']:.4f} | MAE: {metric['mae']:.4f} | R2: {metric['r2_score']:.4f}")
        
        if not metrics:
            print("No model metrics found in database.")
            
    except ValueError:
        print("Invalid limit. Please enter a number.")


def show_database_stats(db_logger):
    """Show comprehensive database statistics"""
    stats = db_logger.get_database_stats()
    
    print("\n--- Database Statistics ---")
    print(json.dumps(stats, indent=2))


def clear_database(db_logger):
    """Clear database with confirmation"""
    confirm = input("Are you sure you want to clear ALL database data? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        db_logger.clear_database()
        print("Database cleared successfully!")
    else:
        print("Database clear cancelled.")


def quick_stats():
    """Show quick database statistics"""
    db_logger = get_database_logger()
    stats = db_logger.get_database_stats()
    
    print("=" * 40)
    print("QUICK DATABASE STATS")
    print("=" * 40)
    
    # Logs summary
    logs_by_level = stats.get('logs_by_level', {})
    total_logs = sum(logs_by_level.values())
    print(f"Total Logs: {total_logs}")
    for level, count in logs_by_level.items():
        print(f"  {level}: {count}")
    
    # API metrics summary
    api_metrics = stats.get('api_metrics', {})
    if api_metrics:
        print(f"\nAPI Requests: {api_metrics.get('total_requests', 0)}")
        print(f"Success Rate: {api_metrics.get('success_rate', 0):.1f}%")
        avg_time = api_metrics.get('avg_response_time', 0)
        if avg_time is not None:
            print(f"Avg Response Time: {avg_time:.3f}s")
        else:
            print("Avg Response Time: N/A")
    
    # Model metrics
    model_count = stats.get('total_model_metrics', 0)
    print(f"\nModel Training Records: {model_count}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        quick_stats()
    else:
        inspect_database()