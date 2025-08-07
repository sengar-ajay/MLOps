#!/usr/bin/env python3
"""
Quick verification script to check if MLOps pipeline setup is correct
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import requests


def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"PASS {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"FAIL {description}: {filepath} - NOT FOUND")
        return False


def check_directory_contents(dirpath, expected_files, description):
    """Check if directory contains expected files"""
    if not os.path.exists(dirpath):
        print(f"FAIL {description}: Directory {dirpath} - NOT FOUND")
        return False

    files = os.listdir(dirpath)
    missing = [f for f in expected_files if f not in files]

    if missing:
        print(f"FAIL {description}: Missing files in {dirpath}: {missing}")
        return False
    else:
        print(f"PASS {description}: All required files present in {dirpath}")
        return True


def run_command_check(command, description):
    """Run a command and check if it succeeds"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"PASS {description}: SUCCESS")
            return True
        else:
            print(f"FAIL {description}: FAILED - {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"FAIL {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"FAIL {description}: ERROR - {str(e)}")
        return False


def check_api_endpoint(url, description, timeout=5):
    """Check if API endpoint is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"PASS {description}: {url} - Response OK")
            return True
        else:
            print(f"FAIL {description}: {url} - Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL {description}: {url} - {str(e)[:50]}")
        return False


def main():
    """Main verification function"""
    print("MLOps Pipeline Setup Verification")
    print("=" * 50)

    checks_passed = 0
    total_checks = 0

    # 1. Check Python environment
    print("\n1. Environment Checks")
    print("-" * 30)
    total_checks += 1
    if sys.version_info >= (3, 8):
        print(f"PASS Python Version: {sys.version.split()[0]}")
        checks_passed += 1
    else:
        print(f"FAIL Python Version: {sys.version.split()[0]} (Need 3.8+)")

    # 2. Check required directories and files
    print("\n2. File Structure Checks")
    print("-" * 30)

    required_files = [
        ("src/data_preprocessing.py", "Data preprocessing script"),
        ("src/model_training.py", "Model training script"),
        ("src/api.py", "API server script"),
        ("src/monitoring.py", "Monitoring script"),
        ("run_pipeline.py", "Pipeline runner"),
        ("requirements.txt", "Dependencies file"),
    ]

    for filepath, desc in required_files:
        total_checks += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1

    # 3. Check generated data files
    print("\n3. Generated Data Files")
    print("-" * 30)

    data_files = [
        "X_train.csv",
        "X_test.csv",
        "y_train.csv",
        "y_test.csv",
        "scaler.pkl",
    ]
    total_checks += 1
    if check_directory_contents("data", data_files, "Data files"):
        checks_passed += 1

    # 4. Check model files
    print("\n4. Model Files")
    print("-" * 30)

    model_files = ["best_model.pkl", "best_model_metrics.json"]
    total_checks += 1
    if check_directory_contents("models", model_files, "Model files"):
        checks_passed += 1

    # 5. Check if tests can run
    print("\n5. Testing Framework")
    print("-" * 30)

    total_checks += 1
    if run_command_check("python -m pytest --version", "Pytest installation"):
        checks_passed += 1

    # 6. Check MLflow
    print("\n6. MLflow Setup")
    print("-" * 30)

    total_checks += 1
    if run_command_check("mlflow --version", "MLflow installation"):
        checks_passed += 1

    # 7. Check if we can import key modules
    print("\n7. Python Module Imports")
    print("-" * 30)

    modules_to_check = ["pandas", "numpy", "sklearn", "flask", "mlflow", "joblib"]

    for module in modules_to_check:
        total_checks += 1
        if run_command_check(f"python -c 'import {module}'", f"Import {module}"):
            checks_passed += 1

    # 8. Try to start API briefly (optional)
    print("\n8. API Server Test (Optional)")
    print("-" * 30)

    print("INFO: Skipping API server test (requires manual start)")
    print("   To test API: python src/api.py")

    # Summary
    print("\n" + "=" * 50)
    print(f"VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"Checks Passed: {checks_passed}/{total_checks}")

    if checks_passed == total_checks:
        print("ALL CHECKS PASSED! Your MLOps pipeline is ready!")
        print("\nNext steps:")
        print("   1. Run: python run_pipeline.py")
        print("   2. Or run components individually as per guide")
    else:
        print(
            f"{total_checks - checks_passed} checks failed. Please review the issues above."
        )
        print("\nCommon fixes:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Run: python src/data_preprocessing.py")
        print("   3. Run: python src/model_training.py")

    return checks_passed == total_checks


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
