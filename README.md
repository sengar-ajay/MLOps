# MLOps Pipeline for California Housing Dataset

This project implements a complete MLOps pipeline for a machine learning model using the California Housing dataset.

## Project Structure

```
├── data/                   # Data directory (managed by DVC)
├── src/                   # Source code
│   ├── data_preprocessing.py
│   ├── model_training.py
│   └── api.py
├── models/                # Trained models
├── notebooks/             # Jupyter notebooks for exploration
├── tests/                 # Unit tests
├── docker/                # Docker configuration
├── .github/workflows/     # CI/CD pipeline
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── README.md             # This file
```

## Technologies Used

- **Git + GitHub**: Version control and repository hosting
- **DVC**: Data version control
- **MLflow**: ML experiment tracking and model versioning
- **Flask/FastAPI**: REST API for model serving
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline
- **scikit-learn**: Machine learning framework

## Setup Instructions

1. Clone the repository:

```bash
git clone <your-repo-url>
cd MLOps-Pipeline
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize DVC:

```bash
dvc init
```

4. Start MLflow tracking server:

```bash
mlflow server --host 0.0.0.0 --port 5000
```

## Usage

### Data Preprocessing

```bash
python src/data_preprocessing.py
```

### Model Training

```bash
python src/model_training.py
```

### API Server

```bash
python src/api.py
```

### Docker Deployment

```bash
docker build -t mlops-pipeline .
docker run -p 5000:5000 mlops-pipeline
```

## Learning Outcomes Achieved

- Use Git, DVC, and MLflow for versioning and tracking
- Package ML code into a REST API (Flask/FastAPI)
- Containerize and deploy using Docker
- Set up GitHub Actions pipeline for CI/CD
- Implement basic logging and monitoring metrics
