# MLOps Pipeline - Quick Start Guide

## One-Command Setup & Run

### Step 1: Verify Setup

```bash
python verify_setup.py
```

**Expected:** All 17 checks should pass

### Step 2: Run Complete Pipeline

```bash
python run_pipeline.py
```

**Expected:** Complete MLOps pipeline execution with all steps passing

### Step 3: Test API (Optional)

```bash
# Terminal 1: Start API
python src/api.py

# Terminal 2: Test API
python demo_api.py
```

## What to Check After Running

### Files Generated:

```bash
# Check these directories have files:
ls data/        # Should have: X_train.csv, X_test.csv, y_train.csv, y_test.csv, scaler.pkl
ls models/      # Should have: best_model.pkl, best_model_metrics.json
ls mlruns/      # Should have experiment directories
```

### Test Results:

```bash
python -m pytest tests/ -v
```

**Expected:** `21 passed, 3 warnings`

### API Endpoints:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/info
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23}'
```

### MLflow UI (Optional):

```bash
mlflow ui --port 5001
# Open: http://localhost:5001
```

## Success Indicators

| Component           | Success Indicator                                 |
| ------------------- | ------------------------------------------------- |
| **Data Processing** | Files in `data/` directory, ~16K training samples |
| **Model Training**  | Best model RMSE ~0.54, R² ~0.78                   |
| **API Server**      | Health endpoint returns "healthy" status          |
| **Unit Tests**      | All 21 tests pass                                 |
| **MLflow**          | Experiments visible in UI                         |
| **Predictions**     | API returns reasonable house prices (0.15-5.0)    |

## Quick Troubleshooting

| Problem         | Solution                                                           |
| --------------- | ------------------------------------------------------------------ |
| Missing files   | `python src/data_preprocessing.py && python src/model_training.py` |
| API won't start | `pkill -f "python src/api.py"` then restart                        |
| Tests fail      | Ensure data and model files exist first                            |
| Port 5000 busy  | Use different port or kill existing process                        |

## Expected Performance

- **Best Model:** Gradient Boosting Regressor
- **Training Time:** ~20 seconds
- **API Response Time:** <100ms
- **Memory Usage:** ~200MB
- **Disk Space:** ~50MB for all artifacts

---

**Your MLOps pipeline is production-ready!**
