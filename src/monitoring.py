"""
Basic monitoring and logging setup for the MLOps pipeline
Enhanced with in-memory database logging
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import requests

# Import our database logging system
from database_logging import get_database_logger, setup_database_logging


# Set up logging configuration
def setup_logging(log_level=logging.INFO, log_file="logs/mlops_pipeline.log"):
    """
    Set up logging configuration for the MLOps pipeline

    Args:
        log_level: Logging level
        log_file: Path to log file
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    logger = logging.getLogger(__name__)
    logger.info("Logging setup completed")
    return logger


class APIMonitor:
    """
    Monitor API performance and health
    Enhanced with database logging
    """

    def __init__(
        self, api_url="http://localhost:5000", log_file="logs/api_monitor.log"
    ):
        self.api_url = api_url
        self.logger = setup_database_logging("api_monitor")  # Use database logging
        self.db_logger = get_database_logger()  # Get database logger instance
        self.metrics = []

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health

        Returns:
            Dict containing health check results
        """
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response_time = time.time() - start_time

            health_data = {
                "timestamp": datetime.now().isoformat(),
                "status_code": response.status_code,
                "response_time": response_time,
                "is_healthy": response.status_code == 200,
            }

            if response.status_code == 200:
                health_data["response_data"] = response.json()
                self.logger.info(
                    f"Health check passed - Response time: {response_time:.3f}s"
                )
            else:
                self.logger.warning(
                    f"Health check failed - Status: {response.status_code}"
                )

            # Store in database
            self.db_logger.log_api_metric(
                endpoint="/health",
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_data=health_data.get("response_data")
            )

            self.metrics.append(health_data)
            return health_data

        except Exception as e:
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "is_healthy": False,
            }
            self.logger.error(f"Health check error: {str(e)}")
            self.metrics.append(error_data)
            return error_data

    def test_prediction(self, sample_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Test prediction endpoint

        Args:
            sample_data: Sample input data for prediction

        Returns:
            Dict containing prediction test results
        """
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/predict",
                json=sample_data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response_time = time.time() - start_time

            prediction_data = {
                "timestamp": datetime.now().isoformat(),
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 200,
            }

            if response.status_code == 200:
                prediction_data["response_data"] = response.json()
                prediction_data["prediction"] = response.json().get("prediction")
                self.logger.info(
                    f"Prediction test passed - Response time: {response_time:.3f}s"
                )
            else:
                self.logger.warning(
                    f"Prediction test failed - Status: {response.status_code}"
                )

            return prediction_data

        except Exception as e:
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
            }
            self.logger.error(f"Prediction test error: {str(e)}")
            return error_data

    def run_monitoring_cycle(
        self, duration_minutes: int = 10, interval_seconds: int = 30
    ):
        """
        Run continuous monitoring for specified duration

        Args:
            duration_minutes: How long to run monitoring
            interval_seconds: Interval between checks
        """
        self.logger.info(f"Starting monitoring cycle for {duration_minutes} minutes")

        sample_data = {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.98,
            "AveBedrms": 1.02,
            "Population": 322.0,
            "AveOccup": 2.55,
            "Latitude": 37.88,
            "Longitude": -122.23,
        }

        end_time = time.time() + (duration_minutes * 60)

        while time.time() < end_time:
            # Health check
            self.health_check()

            # Prediction test
            self.test_prediction(sample_data)

            # Wait for next cycle
            time.sleep(interval_seconds)

        self.logger.info("Monitoring cycle completed")
        self.save_metrics()

    def save_metrics(self, filename: str = "logs/api_metrics.json"):
        """
        Save collected metrics to file

        Args:
            filename: Path to save metrics
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as f:
            json.dump(self.metrics, f, indent=2)

        self.logger.info(f"Metrics saved to {filename}")

    def generate_report(self, output_dir: str = "reports"):
        """
        Generate monitoring report with visualizations

        Args:
            output_dir: Directory to save report
        """
        if not self.metrics:
            self.logger.warning("No metrics available for report generation")
            return

        os.makedirs(output_dir, exist_ok=True)

        # Convert metrics to DataFrame
        df = pd.DataFrame(self.metrics)

        if "response_time" in df.columns:
            # Response time analysis
            plt.figure(figsize=(12, 8))

            plt.subplot(2, 2, 1)
            plt.plot(df.index, df["response_time"])
            plt.title("API Response Time Over Time")
            plt.xlabel("Request Number")
            plt.ylabel("Response Time (seconds)")

            plt.subplot(2, 2, 2)
            plt.hist(df["response_time"], bins=20, alpha=0.7)
            plt.title("Response Time Distribution")
            plt.xlabel("Response Time (seconds)")
            plt.ylabel("Frequency")

            plt.subplot(2, 2, 3)
            success_rate = df["is_healthy"].mean() if "is_healthy" in df.columns else 0
            plt.bar(["Success", "Failure"], [success_rate, 1 - success_rate])
            plt.title("API Health Success Rate")
            plt.ylabel("Rate")

            plt.subplot(2, 2, 4)
            if "response_time" in df.columns:
                plt.boxplot(df["response_time"])
                plt.title("Response Time Box Plot")
                plt.ylabel("Response Time (seconds)")

            plt.tight_layout()
            plt.savefig(
                f"{output_dir}/api_monitoring_report.png", dpi=300, bbox_inches="tight"
            )
            plt.close()

            self.logger.info(
                f"Monitoring report saved to {output_dir}/api_monitoring_report.png"
            )

        # Generate summary statistics
        summary = {
            "total_requests": len(df),
            "average_response_time": (
                df["response_time"].mean() if "response_time" in df.columns else None
            ),
            "max_response_time": (
                df["response_time"].max() if "response_time" in df.columns else None
            ),
            "min_response_time": (
                df["response_time"].min() if "response_time" in df.columns else None
            ),
            "success_rate": (
                df["is_healthy"].mean() if "is_healthy" in df.columns else None
            ),
            "monitoring_period": {
                "start": df["timestamp"].min() if "timestamp" in df.columns else None,
                "end": df["timestamp"].max() if "timestamp" in df.columns else None,
            },
        }

        with open(f"{output_dir}/monitoring_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        self.logger.info(
            f"Summary statistics saved to {output_dir}/monitoring_summary.json"
        )


def main():
    """
    Main monitoring function
    """
    # Set up monitoring
    monitor = APIMonitor()

    # Run a quick health check
    print("Running API health check...")
    health = monitor.health_check()
    print(f"Health check result: {health}")

    # Test prediction
    sample_data = {
        "MedInc": 8.3252,
        "HouseAge": 41.0,
        "AveRooms": 6.98,
        "AveBedrms": 1.02,
        "Population": 322.0,
        "AveOccup": 2.55,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }

    print("Testing prediction endpoint...")
    prediction_result = monitor.test_prediction(sample_data)
    print(f"Prediction result: {prediction_result}")

    # Generate basic report
    monitor.generate_report()

    print(
        "Basic monitoring completed. Check logs/ and reports/ directories "
        "for detailed results."
    )


if __name__ == "__main__":
    main()
