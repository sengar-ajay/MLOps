"""
Unit tests for data preprocessing module
"""

import os
import shutil
import sys
import tempfile

import pandas as pd
import pytest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from data_preprocessing import (  # noqa: E402
    load_california_housing_data,
    load_processed_data,
    preprocess_data,
    save_processed_data,
)


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_load_california_housing_data():
    """Test loading California housing data"""
    X, y = load_california_housing_data()

    # Check data types
    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)

    # Check data shape
    assert X.shape[0] > 0
    assert X.shape[1] == 8  # California housing has 8 features
    assert len(y) == X.shape[0]

    # Check feature names
    expected_features = [
        "MedInc",
        "HouseAge",
        "AveRooms",
        "AveBedrms",
        "Population",
        "AveOccup",
        "Latitude",
        "Longitude",
    ]
    assert list(X.columns) == expected_features

    # Check target name
    assert y.name == "target"

    # Check for missing values
    assert not X.isnull().any().any()
    assert not y.isnull().any()


def test_preprocess_data():
    """Test data preprocessing function"""
    # Load test data
    X, y = load_california_housing_data()

    # Preprocess data
    X_train, X_test, y_train, y_test, scaler = preprocess_data(
        X, y, test_size=0.3, random_state=42
    )

    # Check data types
    assert isinstance(X_train, pd.DataFrame)
    assert isinstance(X_test, pd.DataFrame)
    assert isinstance(y_train, pd.Series)
    assert isinstance(y_test, pd.Series)

    # Check shapes - allow for rounding differences in train_test_split
    total_samples = len(X)
    expected_train_size = int(total_samples * 0.7)  # test_size=0.3 means train_size=0.7
    expected_test_size = total_samples - expected_train_size

    # Allow for small differences due to train_test_split rounding
    assert abs(len(X_train) - expected_train_size) <= 1
    assert abs(len(X_test) - expected_test_size) <= 1
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)

    # Check feature names are preserved
    assert list(X_train.columns) == list(X.columns)
    assert list(X_test.columns) == list(X.columns)

    # Check that data is scaled (mean should be close to 0, std close to 1)
    train_means = X_train.mean()
    train_stds = X_train.std()

    # Allow some tolerance for floating point comparison
    assert all(
        abs(mean) < 0.1 for mean in train_means
    ), f"Means not close to 0: {train_means}"
    assert all(
        abs(std - 1.0) < 0.1 for std in train_stds
    ), f"Stds not close to 1: {train_stds}"


def test_preprocess_data_different_test_size():
    """Test preprocessing with different test size"""
    X, y = load_california_housing_data()

    test_size = 0.1
    X_train, X_test, y_train, y_test, scaler = preprocess_data(
        X, y, test_size=test_size
    )

    total_samples = len(X)
    expected_test_size = int(total_samples * test_size)

    assert len(X_test) == expected_test_size
    assert len(y_test) == expected_test_size


def test_save_and_load_processed_data(temp_data_dir):
    """Test saving and loading processed data"""
    # Load and preprocess data
    X, y = load_california_housing_data()
    X_train, X_test, y_train, y_test, scaler = preprocess_data(X, y)

    # Save processed data
    save_processed_data(X_train, X_test, y_train, y_test, scaler, temp_data_dir)

    # Check files were created
    expected_files = [
        "X_train.csv",
        "X_test.csv",
        "y_train.csv",
        "y_test.csv",
        "scaler.pkl",
    ]
    for file in expected_files:
        assert os.path.exists(os.path.join(temp_data_dir, file))

    # Load processed data
    (
        X_train_loaded,
        X_test_loaded,
        y_train_loaded,
        y_test_loaded,
        scaler_loaded,
    ) = load_processed_data(temp_data_dir)

    # Check loaded data matches original (ignoring index)
    pd.testing.assert_frame_equal(
        X_train.reset_index(drop=True), X_train_loaded.reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(
        X_test.reset_index(drop=True), X_test_loaded.reset_index(drop=True)
    )
    pd.testing.assert_series_equal(
        y_train.reset_index(drop=True), y_train_loaded.reset_index(drop=True)
    )
    pd.testing.assert_series_equal(
        y_test.reset_index(drop=True), y_test_loaded.reset_index(drop=True)
    )

    # Check scaler parameters match
    assert scaler.mean_.tolist() == scaler_loaded.mean_.tolist()
    assert scaler.scale_.tolist() == scaler_loaded.scale_.tolist()


def test_reproducibility():
    """Test that preprocessing is reproducible with same random state"""
    X, y = load_california_housing_data()

    # Preprocess data twice with same random state
    X_train1, X_test1, y_train1, y_test1, scaler1 = preprocess_data(
        X, y, random_state=42
    )
    X_train2, X_test2, y_train2, y_test2, scaler2 = preprocess_data(
        X, y, random_state=42
    )

    # Results should be identical
    pd.testing.assert_frame_equal(X_train1, X_train2)
    pd.testing.assert_frame_equal(X_test1, X_test2)
    pd.testing.assert_series_equal(y_train1, y_train2)
    pd.testing.assert_series_equal(y_test1, y_test2)


def test_different_random_states():
    """Test that different random states produce different splits"""
    X, y = load_california_housing_data()

    # Preprocess data with different random states
    X_train1, X_test1, y_train1, y_test1, scaler1 = preprocess_data(
        X, y, random_state=42
    )
    X_train2, X_test2, y_train2, y_test2, scaler2 = preprocess_data(
        X, y, random_state=123
    )

    # Results should be different (at least some rows should be different)
    # We'll check if the first few rows are different
    assert not X_train1.iloc[:5].equals(X_train2.iloc[:5])


def test_scaler_transform_consistency():
    """Test that scaler transforms data consistently"""
    X, y = load_california_housing_data()
    X_train, X_test, y_train, y_test, scaler = preprocess_data(X, y)

    # Apply scaler manually to original training data
    X_train_manual = pd.DataFrame(
        scaler.transform(scaler.inverse_transform(X_train)), columns=X_train.columns
    )

    # Should be very close to the processed training data
    pd.testing.assert_frame_equal(X_train, X_train_manual, rtol=1e-10)
