# MLOps Pipeline for California Housing Dataset

A comprehensive MLOps pipeline implementation featuring data preprocessing, model training, API deployment, monitoring, and CI/CD automation using the California Housing dataset for regression tasks.

## Project Structure

```
Assignment/
├── src/                          # Source code
│   ├── data_preprocessing.py     # Data loading and preprocessing
│   ├── model_training.py         # ML model training with MLflow
│   ├── api.py                   # Flask REST API for model serving
│   └── monitoring.py            # API monitoring and health checks
├── tests/                       # Unit tests
│   ├── test_api.py             # API endpoint tests
│   └── test_data_preprocessing.py # Data processing tests
├── data/                        # Processed data (DVC tracked)
├── models/                      # Trained models and artifacts
├── logs/                        # Application logs
├── reports/                     # Monitoring reports and visualizations
├── mlruns/                      # MLflow experiment tracking
├── mlartifacts/                 # MLflow model artifacts
├── .github/workflows/           # CI/CD pipeline configuration
├── docker/                      # Docker configuration files
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml           # Multi-container deployment
├── run_pipeline.py              # Complete pipeline orchestrator
├── verify_setup.py              # Setup verification script
├── cleanup.py                   # Cleanup utility script
├── demo_api.py                  # API demonstration script
└── README.md                    # This documentation
```

## Technologies Used

- **Git + GitHub**: Version control and repository hosting
- **DVC**: Data version control for dataset versioning
- **MLflow**: ML experiment tracking, model versioning, and artifact storage
- **Flask**: REST API for model serving with comprehensive endpoints
- **Docker + Docker Compose**: Containerization and orchestration
- **GitHub Actions**: CI/CD pipeline automation
- **scikit-learn**: Machine learning framework (Linear Regression, Random Forest, Gradient Boosting)
- **pytest**: Unit testing framework
- **pandas + numpy**: Data manipulation and numerical computing
- **matplotlib + seaborn**: Data visualization and monitoring reports

## Quick Start

### Prerequisites

- Python 3.8+ (tested with Python 3.10)
- pip package manager
- Git

### Setup Instructions

1. **Clone and navigate to the repository:**

```bash
git clone <your-repo-url>
cd Assignment
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Verify setup:**

```bash
python verify_setup.py
```

4. **Run the complete pipeline:**

```bash
python run_pipeline.py
```

### Alternative: Individual Components

If you prefer to run components individually:

```bash
# 1. Data preprocessing
python src/data_preprocessing.py

# 2. Model training with MLflow tracking
python src/model_training.py

# 3. Start API server
python src/api.py

# 4. Run monitoring (in another terminal)
python src/monitoring.py

# 5. Run tests
pytest tests/ -v
```

## API Usage

The Flask API provides several endpoints for model interaction:

### Health Check

```bash
curl http://localhost:5000/health
```

### Model Information

```bash
curl http://localhost:5000/info
```

### Single Prediction

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.98,
    "AveBedrms": 1.02,
    "Population": 322.0,
    "AveOccup": 2.55,
    "Latitude": 37.88,
    "Longitude": -122.23
  }'
```

### Batch Predictions

```bash
curl -X POST http://localhost:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23},
      {"MedInc": 7.2574, "HouseAge": 21.0, "AveRooms": 5.64, "AveBedrms": 0.92, "Population": 2401.0, "AveOccup": 2.11, "Latitude": 39.43, "Longitude": -121.22}
    ]
  }'
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

### Manual Docker Build

```bash
docker build -t mlops-pipeline .
docker run -p 5000:5000 mlops-pipeline
```

## MLflow Tracking

Access the MLflow UI to view experiments, compare models, and manage artifacts:

```bash
mlflow ui --port 5001
# Visit http://localhost:5001
```

## Model Performance

The pipeline trains and compares multiple regression models:

- **Gradient Boosting Regressor** (Best Model)

  - RMSE: 0.5422
  - MAE: 0.3717
  - R²: 0.7756

- **Random Forest Regressor**

  - RMSE: 0.5443
  - R²: 0.7739

- **Linear Regression**
  - RMSE: 0.7456
  - R²: 0.5758

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/

# Run specific test files
pytest tests/test_api.py -v
pytest tests/test_data_preprocessing.py -v
```

## Monitoring

The pipeline includes comprehensive monitoring:

- **API Health Monitoring**: Automated health checks and performance metrics
- **Response Time Tracking**: API endpoint performance analysis
- **Success Rate Monitoring**: Request success/failure rate tracking
- **Automated Reporting**: Visual reports generated in `reports/` directory

## Cleanup

Clean up temporary files and stop processes:

```bash
python cleanup.py
```

## Project Features

### Data Pipeline

- Automated data loading from scikit-learn California Housing dataset
- Data preprocessing with train/test splitting and feature scaling
- Data version control with DVC

### Model Training

- Multiple model training and comparison
- MLflow experiment tracking with metrics and parameters
- Automated model selection and artifact storage
- Model versioning and reproducibility

### API Deployment

- RESTful Flask API with comprehensive endpoints
- Input validation and error handling
- JSON response formatting with timestamps
- Health checks and monitoring integration

### DevOps & MLOps

- Complete CI/CD pipeline with GitHub Actions
- Docker containerization with multi-stage builds
- Automated testing with pytest
- Code quality checks and coverage reporting
- Production-ready deployment configuration

### Monitoring & Observability

- API performance monitoring
- Health check endpoints
- Automated report generation
- Visual performance analytics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
