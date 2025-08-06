#!/usr/bin/env python3
"""
Cleanup script for MLOps pipeline temporary files and logs
"""
import os
import shutil
import subprocess
import glob

def cleanup_files():
    """Clean up temporary files, logs, and cache"""
    print("Cleaning up MLOps pipeline temporary files...")
    
    # Files and directories to clean
    cleanup_items = [
        # Python cache files
        "__pycache__",
        "src/__pycache__",
        "tests/__pycache__",
        ".pytest_cache",
        
        # Log files
        "logs/api_monitor.log",
        
        # Temporary monitoring files
        "reports/monitoring_summary.json",
    ]
    
    # Patterns to clean
    patterns_to_clean = [
        "**/*.pyc",
        "**/*.pyo",
        "**/.DS_Store",
        "**/*.tmp",
        "**/*.lock",
    ]
    
    cleaned_count = 0
    
    # Clean specific files and directories
    for item in cleanup_items:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"Removed directory: {item}")
                else:
                    os.remove(item)
                    print(f"Removed file: {item}")
                cleaned_count += 1
            except Exception as e:
                print(f"Failed to remove {item}: {e}")
    
    # Clean files by pattern
    for pattern in patterns_to_clean:
        files = glob.glob(pattern, recursive=True)
        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Removed: {file}")
                    cleaned_count += 1
            except Exception as e:
                print(f"Failed to remove {file}: {e}")
    
    return cleaned_count

def stop_processes():
    """Stop any running MLOps processes"""
    print("\nStopping MLOps processes...")
    
    processes_to_stop = [
        ("mlflow ui", "MLflow UI"),
        ("python src/api.py", "API server"),
    ]
    
    stopped_count = 0
    
    for process_cmd, description in processes_to_stop:
        try:
            result = subprocess.run(
                ["pkill", "-f", process_cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Stopped {description}")
                stopped_count += 1
            else:
                print(f"No {description} processes running")
        except Exception as e:
            print(f"Failed to stop {description}: {e}")
    
    return stopped_count

def preserve_important_files():
    """List important files that should NOT be cleaned"""
    important_files = [
        "data/X_train.csv",
        "data/X_test.csv", 
        "data/y_train.csv",
        "data/y_test.csv",
        "data/scaler.pkl",
        "models/best_model.pkl",
        "models/best_model_metrics.json",
        "mlruns/",  # MLflow experiments
        "reports/api_monitoring_report.png",  # Keep the monitoring chart
    ]
    
    print("\nImportant files preserved:")
    for file in important_files:
        if os.path.exists(file):
            if os.path.isdir(file):
                size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(file)
                          for filename in filenames)
                print(f"Directory: {file}/ ({size} bytes total)")
            else:
                size = os.path.getsize(file)
                print(f"File: {file} ({size} bytes)")

def main():
    """Main cleanup function"""
    print("MLOps Pipeline Cleanup")
    print("=" * 40)
    
    # Stop processes
    stopped = stop_processes()
    
    # Clean files
    cleaned = cleanup_files()
    
    # Show preserved files
    preserve_important_files()
    
    # Summary
    print("\n" + "=" * 40)
    print("Cleanup Summary:")
    print(f"Processes stopped: {stopped}")
    print(f"Files/directories cleaned: {cleaned}")
    print("Cleanup completed!")
    
    if cleaned > 0 or stopped > 0:
        print("\nYour MLOps pipeline is now clean and ready to run!")
    else:
        print("\nEverything was already clean!")

if __name__ == "__main__":
    main()