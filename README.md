# MLOps Pipeline for California Housing Dataset

A comprehensive MLOps pipeline implementation featuring data preprocessing, model training, API deployment, monitoring, and CI/CD automation using the California Housing dataset for regression tasks.

> 📚 **Documentation**: Detailed guides and documentation are available in the [`docs/`](docs/) folder.

## Project Structure

```
MLOps/
├── src/                          # Source code
│   ├── data_preprocessing.py     # Data loading and preprocessing
│   ├── model_training.py         # ML model training with MLflow
│   ├── api.py                   # Flask REST API for model serving
│   └── monitoring.py            # API monitoring and health checks
├── tests/                       # Unit tests
│   ├── test_api.py             # API endpoint tests
│   └── test_data_preprocessing.py # Data processing tests
├── docs/                        # Documentation
│   ├── README.md               # Documentation index
│   ├── QUICK_START.md          # Quick setup guide
│   ├── PROJECT_SETUP_GUIDE.md  # Detailed setup instructions
│   ├── TESTING_GUIDE.md        # Testing documentation
│   ├── ASSIGNMENT_SUMMARY.md   # Project summary
│   └── PIPELINE_STATUS.md      # Pipeline status
├── postman/                     # API testing
│   └── Postman_Collection.json # Complete API collection
├── data/                        # Processed data (DVC tracked)
├── models/                      # Trained models and artifacts
├── logs/                        # Application logs
├── reports/                     # Monitoring reports and visualizations
├── mlruns/                      # MLflow experiment tracking
├── .github/workflows/           # CI/CD pipeline configuration
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml           # Multi-container deployment
├── run_pipeline.py              # Complete pipeline orchestrator
└── README.md                    # Main project documentation
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
git clone [https://github.com/sengar-ajay/](https://github.com/sengar-ajay/MLOps.git)
cd MLOps

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

## Quick API Usage

### Basic Examples

```bash
# Health check
curl http://localhost:5000/health

# Model information
curl http://localhost:5000/info

# Single prediction
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

# Batch predictions
curl -X POST http://localhost:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23},
      {"MedInc": 7.2574, "HouseAge": 21.0, "AveRooms": 5.64, "AveBedrms": 0.92, "Population": 2401.0, "AveOccup": 2.11, "Latitude": 39.43, "Longitude": -121.22}
    ]
  }'
```

## API Documentation

The API provides endpoints for model serving and health monitoring.

### Available Endpoints

#### Core Endpoints

- **GET /** - API home page with basic information
- **GET /health** - Health check to verify API and model status
- **GET /info** - Detailed model information and parameters

#### Predictions

- **POST /predict** - Single house price prediction
- **POST /predict_batch** - Batch predictions for multiple houses

#### Get Error Logs Only

```bash
curl "http://localhost:5000/logs?level=ERROR&limit=50"
```

#### Get Prediction Endpoint Performance

```bash
curl "http://localhost:5000/metrics/api?endpoint=/predict&limit=20"
```

### Postman Collection

A complete Postman collection with all 18 endpoints is available at:
`postman/Postman_Collection.json`

**Features:**

- Automated test scripts for each endpoint
- Request/response validation
- Error handling tests
- Sample data for all prediction endpoints
- Database query examples

**To use:**

1. Import `postman/Postman_Collection.json` into Postman
2. Set base_url variable to `http://localhost:5000`
3. Start the API server: `python src/api.py`
4. Run individual requests or the entire collection

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

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running quickly
- **[Project Setup Guide](docs/PROJECT_SETUP_GUIDE.md)** - Detailed setup instructions
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Complete testing documentation
- **[Assignment Summary](docs/ASSIGNMENT_SUMMARY.md)** - Project requirements and implementation
- **[Pipeline Status](docs/PIPELINE_STATUS.md)** - Current pipeline status

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ML Flow pipline

<img width="1604" height="784" alt="image" src="https://github.com/user-attachments/assets/29bfd73a-94e2-4fee-aa0e-3aa4f991e223" />

<img width="1724" height="837" alt="image" src="https://github.com/user-attachments/assets/29f989b3-f75d-4caa-96dd-43ac93d95f93" />
<img width="1724" height="837" alt="image" src="https://github.com/user-attachments/assets/05537200-e34d-4db3-a5f2-395b4593d2cb" />
<img width="1724" height="837" alt="image" src="https://github.com/user-attachments/assets/ebae35c4-44b3-478c-b7f8-c6dbfdfa0f2b" />
<img width="1724" height="837" alt="image" src="https://github.com/user-attachments/assets/2f31ad66-07b9-414c-ad70-cffd9bf6f867" />
