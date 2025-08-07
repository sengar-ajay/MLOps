"""
Data preprocessing module for California Housing dataset
"""

import logging
import os

import joblib
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_california_housing_data():
    """
    Load the California Housing dataset from scikit-learn
    Falls back to cached data if network access fails

    Returns:
        tuple: (X, y) features and target
    """
    logger.info("Loading California Housing dataset...")

    try:
        # Check if we should skip network access (for CI environments)
        if os.environ.get('SKIP_NETWORK_DOWNLOAD', '').lower() == 'true':
            raise RuntimeError("Network download disabled by environment variable")
            
        # Try to fetch the dataset from scikit-learn
        housing = fetch_california_housing()
        X = pd.DataFrame(housing.data, columns=housing.feature_names)
        y = pd.Series(housing.target, name="target")
        
        logger.info(f"Dataset loaded successfully. Shape: {X.shape}")
        logger.info(f"Features: {list(X.columns)}")
        
        return X, y
        
    except Exception as e:
        logger.warning(f"Failed to fetch dataset from internet: {e}")
        
        # Try to load from existing processed data files
        # Check both current directory and parent directory (for tests)
        data_dirs = ["data", "../data"]
        cached_data_found = False
        
        for data_dir in data_dirs:
            if (os.path.exists(os.path.join(data_dir, "X_train.csv")) and 
                os.path.exists(os.path.join(data_dir, "X_test.csv")) and
                os.path.exists(os.path.join(data_dir, "y_train.csv")) and 
                os.path.exists(os.path.join(data_dir, "y_test.csv"))):
                
                logger.info(f"Loading dataset from existing processed data files in {data_dir}...")
                
                # Load and combine the split data
                X_train = pd.read_csv(os.path.join(data_dir, "X_train.csv"))
                X_test = pd.read_csv(os.path.join(data_dir, "X_test.csv"))
                y_train = pd.read_csv(os.path.join(data_dir, "y_train.csv")).squeeze()
                y_test = pd.read_csv(os.path.join(data_dir, "y_test.csv")).squeeze()
                cached_data_found = True
                break
        
        if cached_data_found:
            # Combine train and test data
            X = pd.concat([X_train, X_test], ignore_index=True)
            y = pd.concat([y_train, y_test], ignore_index=True)
            y.name = "target"
            
            logger.info(f"Dataset loaded from cached files. Shape: {X.shape}")
            logger.info(f"Features: {list(X.columns)}")
            
            return X, y
        else:
            logger.error("No cached data available and cannot fetch from internet")
            raise RuntimeError(
                "Cannot load California Housing dataset: network access failed "
                "and no cached data files found"
            )


def preprocess_data(X, y, test_size=0.2, random_state=42):
    """
    Preprocess the data: split and scale

    Args:
        X: Features dataframe
        y: Target series
        test_size: Test split ratio
        random_state: Random seed for reproducibility

    Returns:
        tuple: (X_train, X_test, y_train, y_test, scaler)
    """
    logger.info("Preprocessing data...")

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Convert back to DataFrames for consistency
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)

    logger.info("Data preprocessing completed.")
    logger.info(f"Training set shape: {X_train_scaled.shape}")
    logger.info(f"Test set shape: {X_test_scaled.shape}")

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def save_processed_data(X_train, X_test, y_train, y_test, scaler, data_dir="data"):
    """
    Save processed data and scaler to files

    Args:
        X_train, X_test, y_train, y_test: Processed data splits
        scaler: Fitted StandardScaler
        data_dir: Directory to save data
    """
    logger.info("Saving processed data...")

    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Save data splits
    X_train.to_csv(os.path.join(data_dir, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(data_dir, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(data_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(data_dir, "y_test.csv"), index=False)

    # Save scaler
    joblib.dump(scaler, os.path.join(data_dir, "scaler.pkl"))

    logger.info(f"Data saved to {data_dir} directory")


def load_processed_data(data_dir="data"):
    """
    Load processed data from files

    Args:
        data_dir: Directory containing processed data

    Returns:
        tuple: (X_train, X_test, y_train, y_test, scaler)
    """
    logger.info("Loading processed data...")

    X_train = pd.read_csv(os.path.join(data_dir, "X_train.csv"))
    X_test = pd.read_csv(os.path.join(data_dir, "X_test.csv"))
    y_train = pd.read_csv(os.path.join(data_dir, "y_train.csv")).squeeze()
    y_test = pd.read_csv(os.path.join(data_dir, "y_test.csv")).squeeze()
    scaler = joblib.load(os.path.join(data_dir, "scaler.pkl"))

    logger.info("Processed data loaded successfully")

    return X_train, X_test, y_train, y_test, scaler


def main():
    """
    Main function to run data preprocessing pipeline
    """
    # Load raw data
    X, y = load_california_housing_data()

    # Preprocess data
    X_train, X_test, y_train, y_test, scaler = preprocess_data(X, y)

    # Save processed data
    save_processed_data(X_train, X_test, y_train, y_test, scaler)

    # Display basic statistics
    logger.info("\n=== Data Statistics ===")
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Test samples: {len(X_test)}")
    logger.info(f"Features: {X_train.shape[1]}")
    logger.info(f"Target range: [{y.min():.2f}, {y.max():.2f}]")
    logger.info(f"Target mean: {y.mean():.2f}")


if __name__ == "__main__":
    main()
