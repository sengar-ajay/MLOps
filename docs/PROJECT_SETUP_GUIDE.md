# MLOps Pipeline - Complete Setup & Running Guide

## Project Overview

This is a complete MLOps pipeline for California Housing price prediction featuring:

- Data preprocessing with scikit-learn
- Model training with MLflow experiment tracking
- REST API deployment with Flask
- Unit testing with pytest
- Docker containerization
- Monitoring and logging

## Prerequisites & Environment Setup

### 1. Python Environment

```bash
# Ensure you have Python 3.10+ installed
python --version

# Activate your conda environment (if using conda)
conda activate py310
```

### 2. Required Dependencies

All dependencies are listed in `requirements.txt`. Install them:

```bash
pip install -r requirements.txt
```

### 3. Directory Structure Verification

Your project should have this structure:

```
Assignment/
├── src/
│   ├── data_preprocessing.py
│   ├── model_training.py
│   ├── api.py
│   └── monitoring.py
├── tests/
│   ├── test_api.py
│   └── test_data_preprocessing.py
├── run_pipeline.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## How to Run the Project

### Option 1: Complete Pipeline (Recommended)

Run the entire MLOps pipeline with one command:

```bash
python run_pipeline.py
```

This will execute:

1. Data preprocessing
2. Model training with MLflow tracking
3. Unit tests
4. API server deployment
5. API endpoint testing
6. Basic monitoring

### Option 2: Step-by-Step Execution

#### Step 1: Data Preprocessing

```bash
python src/data_preprocessing.py
```

**Expected Output:**

- Creates `data/` directory with processed files
- Generates: `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`, `scaler.pkl`

#### Step 2: Model Training

```bash
python src/model_training.py
```

**Expected Output:**

- Trains 3 models: Linear Regression, Random Forest, Gradient Boosting
- Creates `models/best_model.pkl` and `models/best_model_metrics.json`
- Logs experiments to `mlruns/` directory

#### Step 3: Run Tests

```bash
python -m pytest tests/ -v
```

**Expected Output:**

- All 21 tests should pass
- No critical failures

#### Step 4: Start API Server

```bash
python src/api.py
```

**Expected Output:**

- Server starts on `http://localhost:5000`
- Model and scaler loaded successfully

#### Step 5: Test API Endpoints

In a new terminal:

```bash
# Health check
curl http://localhost:5000/health

# Model info
curl http://localhost:5000/info

# Make prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23}'
```

## What to Check & Verify

### 1. Data Processing Verification

**Check these files exist:**

```bash
ls -la data/
# Should contain: X_train.csv, X_test.csv, y_train.csv, y_test.csv, scaler.pkl
```

**Verify data shapes:**

- Training data: ~16,512 samples
- Test data: ~4,128 samples
- Features: 8 columns

### 2. Model Training Verification

**Check model files:**

```bash
ls -la models/
# Should contain: best_model.pkl, best_model_metrics.json
```

**Check MLflow experiments:**

```bash
mlflow experiments search
# Should show "California_Housing_Regression" experiment
```

**Expected model performance:**

- Best model: Gradient Boosting Regressor
- RMSE: ~0.54
- R²: ~0.78

### 3. API Server Verification

**Start server and check endpoints:**

```bash
# Start server
python src/api.py

# In another terminal, test endpoints:
curl http://localhost:5000/health
# Expected: {"status": "healthy", "message": "API is running and model is loaded"}

curl http://localhost:5000/info
# Expected: Model information with features and type

curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23}'
# Expected: {"prediction": 4.243, ...}
```

### 4. Testing Verification

**Run all tests:**

```bash
python -m pytest tests/ -v
```

**Expected results:**

- 21 tests total
- All tests should PASS
- 3 warnings (sklearn feature names) are normal

### 5. MLflow UI (Optional)

**Start MLflow UI:**

```bash
mlflow ui --port 5001
```

**Access at:** http://localhost:5001

**What to check:**

- Experiments are visible
- Multiple runs with different models
- Metrics comparison (RMSE, MAE, R²)
- Model artifacts are logged

### 6. Docker Verification (Optional)

**Build and run container:**

```bash
docker build -t mlops-pipeline .
docker run -p 5000:5000 mlops-pipeline
```

## Common Issues & Troubleshooting

### Issue 1: Missing Files

**Problem:** API can't find model files
**Solution:**

```bash
python src/data_preprocessing.py
python src/model_training.py
```

### Issue 2: Port Already in Use

**Problem:** Port 5000 is busy
**Solution:**

```bash
# Kill existing processes
pkill -f "python src/api.py"
# Or use different port in api.py
```

### Issue 3: Test Failures

**Problem:** Some tests fail
**Solution:**

```bash
# Ensure all files exist
python src/data_preprocessing.py
python src/model_training.py
# Run tests again
python -m pytest tests/ -v
```

### Issue 4: MLflow Warnings

**Problem:** Malformed experiment warnings
**Solution:**

```bash
# Clean up corrupted experiment
rm -rf mlruns/0
```

## Expected Outputs Summary

### Files Generated:

```
data/
├── X_train.csv         # Training features (16,512 × 8)
├── X_test.csv          # Test features (4,128 × 8)
├── y_train.csv         # Training targets
├── y_test.csv          # Test targets
└── scaler.pkl          # Feature scaler

models/
├── best_model.pkl      # Best trained model
└── best_model_metrics.json # Model performance metrics

mlruns/
└── [experiment_dirs]   # MLflow experiment tracking

logs/
└── [log_files]         # API and monitoring logs

reports/
└── [monitoring_reports] # Performance reports
```

### API Endpoints:

- **GET** `/` - API information
- **GET** `/health` - Health check
- **GET** `/info` - Model information
- **POST** `/predict` - Single prediction
- **POST** `/predict_batch` - Batch predictions

### Performance Metrics:

- **Best Model:** Gradient Boosting Regressor
- **RMSE:** ~0.542
- **MAE:** ~0.372
- **R²:** ~0.776

## Success Criteria Checklist

- [ ] All 21 unit tests pass
- [ ] API server starts without errors
- [ ] All API endpoints respond correctly
- [ ] Model files are generated and loadable
- [ ] MLflow experiments are tracked
- [ ] Predictions are reasonable (housing prices 0.15-5.0)
- [ ] Data preprocessing completes successfully
- [ ] Docker build works (optional)

## Next Steps

1. **Production Deployment:** Deploy to cloud platform (AWS, GCP, Azure)
2. **CI/CD Setup:** Configure GitHub Actions
3. **Monitoring:** Set up Prometheus/Grafana
4. **Model Versioning:** Implement model registry
5. **Data Pipeline:** Add automated data ingestion

---

**Your MLOps pipeline is ready for production!**
