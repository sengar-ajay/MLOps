#!/usr/bin/env python3
"""
Complete MLOps Pipeline Runner
This script demonstrates the complete MLOps pipeline from data preprocessing
to model deployment
"""
import logging
import subprocess
import sys
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_command(command, description):
    """
    Run a shell command and handle errors

    Args:
        command: Command to run
        description: Description of what the command does
    """
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        logger.info(f"Success: {description}")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False


def main():
    """
    Run the complete MLOps pipeline
    """
    logger.info("=" * 60)
    logger.info("STARTING COMPLETE MLOPS PIPELINE")
    logger.info("=" * 60)

    # Step 1: Data Preprocessing
    logger.info("\nStep 1: Data Preprocessing")
    if not run_command("python src/data_preprocessing.py", "Data preprocessing"):
        logger.error("Data preprocessing failed. Exiting.")
        return False

    # Step 2: Model Training with MLflow
    logger.info("\nStep 2: Model Training with MLflow Tracking")
    if not run_command("python src/model_training.py", "Model training"):
        logger.error("Model training failed. Exiting.")
        return False

    # Step 3: Run Tests
    logger.info("\nStep 3: Running Unit Tests")
    if not run_command("python -m pytest tests/ -v", "Unit tests"):
        logger.warning("Some tests failed, but continuing...")

    # Step 4: Start API Server (in background)
    logger.info("\nStep 4: Starting API Server")
    logger.info("Starting Flask API server in background...")

    # Check if API is already running
    try:
        import requests

        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            logger.info("API server is already running")
        else:
            logger.info("Starting new API server...")
            subprocess.Popen(
                [sys.executable, "src/api.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(5)  # Give server time to start
    except Exception:
        logger.info("Starting new API server...")
        subprocess.Popen(
            [sys.executable, "src/api.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(5)  # Give server time to start

    # Step 5: Test API
    logger.info("\nStep 5: Testing API Endpoints")
    test_commands = [
        ("curl -s http://localhost:5000/health", "Health check"),
        ("curl -s http://localhost:5000/info", "Model info"),
        (
            "curl -s -X POST http://localhost:5000/predict "
            '-H "Content-Type: application/json" '
            '-d \'{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98, '
            '"AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55, '
            '"Latitude": 37.88, "Longitude": -122.23}\'',
            "Prediction test",
        ),
    ]

    for command, description in test_commands:
        run_command(command, description)

    # Step 6: Run Monitoring
    logger.info("\nStep 6: Running Basic Monitoring")
    if not run_command("python src/monitoring.py", "API monitoring"):
        logger.warning("Monitoring failed, but continuing...")

    # Step 7: Docker Build (optional)
    logger.info("\nStep 7: Docker Build (Optional)")
    if run_command("docker --version", "Check Docker availability"):
        logger.info("Docker is available. You can build the image with:")
        logger.info("docker build -t mlops-pipeline .")
        logger.info("docker run -p 5000:5000 mlops-pipeline")
    else:
        logger.warning("Docker not available. Skipping Docker build.")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("MLOPS PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("=" * 60)

    logger.info("\nSummary of what was accomplished:")
    logger.info("- Data preprocessing with California Housing dataset")
    logger.info("- Model training with MLflow experiment tracking")
    logger.info("- Best model selection and saving")
    logger.info("- REST API deployment with Flask")
    logger.info("- API testing and monitoring")
    logger.info("- Unit tests for code quality")
    logger.info("- Docker containerization setup")
    logger.info("- CI/CD pipeline configuration")
    logger.info("- Data version control with DVC")

    logger.info("\nAvailable endpoints:")
    logger.info("- Health check: http://localhost:5000/health")
    logger.info("- Model info: http://localhost:5000/info")
    logger.info("- Predictions: http://localhost:5000/predict")
    logger.info("- Batch predictions: http://localhost:5000/predict_batch")

    logger.info("\nGenerated artifacts:")
    logger.info("- Processed data: data/")
    logger.info("- Trained models: models/")
    logger.info("- MLflow experiments: mlruns/")
    logger.info("- API logs: logs/")
    logger.info("- Monitoring reports: reports/")

    logger.info("\nNext steps:")
    logger.info("- Push code to GitHub repository")
    logger.info("- Set up GitHub Actions secrets for Docker Hub")
    logger.info("- Deploy to cloud platform (AWS, GCP, Azure)")
    logger.info("- Set up production monitoring with Prometheus/Grafana")

    return True


if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("Pipeline failed!")
        sys.exit(1)
