#!/usr/bin/env python3
"""
Simple test script to verify workflow components work locally
This helps identify issues before running in GitHub Actions
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_python_environment():
    """Test if Python environment is properly set up"""
    print("Testing Python environment...")
    
    try:
        import pandas as pd
        import numpy as np
        import sklearn
        import joblib
        print(f"  Python: {sys.version}")
        print(f"  Pandas: {pd.__version__}")
        print(f"  NumPy: {np.__version__}")
        print(f"  Scikit-learn: {sklearn.__version__}")
        print("  SUCCESS: All required packages available")
        return True
    except ImportError as e:
        print(f"  ERROR: Missing package - {e}")
        return False

def test_project_structure():
    """Test if required project files exist"""
    print("\nTesting project structure...")
    
    required_files = [
        'src/api.py',
        'src/data_preprocessing.py', 
        'src/model_training.py',
        'requirements.txt',
        'Dockerfile'
    ]
    
    required_dirs = [
        'src/',
        'tests/',
        'data/',
        'models/',
        '.github/workflows/'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  SUCCESS: {file_path} exists")
        else:
            print(f"  ERROR: {file_path} missing")
            all_good = False
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  SUCCESS: {dir_path} exists")
        else:
            print(f"  ERROR: {dir_path} missing")
            all_good = False
    
    return all_good

def test_workflow_syntax():
    """Test if workflow files have valid YAML syntax"""
    print("\nTesting workflow syntax...")
    
    try:
        result = subprocess.run([
            sys.executable, '.github/validate-workflows.py'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("  SUCCESS: All workflow files have valid syntax")
            return True
        else:
            print("  ERROR: Workflow syntax issues found:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"  ERROR: Could not validate workflows - {e}")
        return False

def test_basic_imports():
    """Test if core modules can be imported"""
    print("\nTesting core module imports...")
    
    test_imports = [
        'src.api',
        'src.data_preprocessing', 
        'src.model_training'
    ]
    
    # Add src to Python path temporarily
    sys.path.insert(0, 'src')
    
    all_good = True
    for module in test_imports:
        try:
            # Try importing without executing
            module_name = module.split('.')[-1]
            __import__(module_name)
            print(f"  SUCCESS: {module} imports successfully")
        except Exception as e:
            print(f"  ERROR: {module} import failed - {e}")
            all_good = False
    
    sys.path.pop(0)  # Remove src from path
    return all_good

def test_data_files():
    """Test if data files exist and are readable"""
    print("\nTesting data files...")
    
    data_files = [
        'data/X_train.csv',
        'data/X_test.csv', 
        'data/y_train.csv',
        'data/y_test.csv'
    ]
    
    all_good = True
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                print(f"  SUCCESS: {file_path} - Shape: {df.shape}")
            except Exception as e:
                print(f"  ERROR: {file_path} - Cannot read: {e}")
                all_good = False
        else:
            print(f"  WARNING: {file_path} not found (may be generated during pipeline)")
    
    return all_good

def test_model_files():
    """Test if model files exist and are loadable"""
    print("\nTesting model files...")
    
    model_files = [
        'models/best_model.pkl',
        'data/scaler.pkl'
    ]
    
    all_good = True
    for file_path in model_files:
        if os.path.exists(file_path):
            try:
                import joblib
                model = joblib.load(file_path)
                print(f"  SUCCESS: {file_path} loads successfully")
            except Exception as e:
                print(f"  ERROR: {file_path} - Cannot load: {e}")
                all_good = False
        else:
            print(f"  INFO: {file_path} not found (will be generated during training)")
    
    return all_good

def test_docker_build():
    """Test if Docker can build the image"""
    print("\nTesting Docker build...")
    
    try:
        # Check if Docker is available
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("  INFO: Docker not available - skipping Docker tests")
            return True
        
        print("  Docker available - testing build...")
        
        # Test Docker build (dry run)
        result = subprocess.run([
            'docker', 'build', '--dry-run', '-t', 'test-mlops', '.'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  SUCCESS: Dockerfile syntax is valid")
            return True
        else:
            print("  ERROR: Docker build issues:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("  INFO: Docker not installed - skipping Docker tests")
        return True
    except Exception as e:
        print(f"  ERROR: Docker test failed - {e}")
        return False

def generate_test_report(results):
    """Generate a test report"""
    print("\n" + "="*60)
    print("WORKFLOW READINESS TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nTest Results:")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\nSUCCESS: All tests passed! Your workflows should run successfully.")
        return True
    else:
        print("\nWARNING: Some tests failed. Fix these issues before running workflows.")
        return False

def main():
    """Run all tests"""
    print("GitHub Actions Workflow Readiness Test")
    print("="*60)
    
    tests = {
        'Python Environment': test_python_environment,
        'Project Structure': test_project_structure,
        'Workflow Syntax': test_workflow_syntax,
        'Module Imports': test_basic_imports,
        'Data Files': test_data_files,
        'Model Files': test_model_files,
        'Docker Build': test_docker_build
    }
    
    results = {}
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = False
    
    success = generate_test_report(results)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())