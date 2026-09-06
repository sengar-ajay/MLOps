## High-level Architecture

This project serves a California Housing price prediction model via a Flask API, tracks experiments with MLflow, logs metrics to SQLite and Prometheus, and supports monitoring, drift detection, and retraining triggers. Docker Compose provides local orchestration; GitHub and GitHub Actions cover source control and CI/CD triggers on check-in.

Note: API framework is Flask (FastAPI not used).

### Diagram

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Inter, Segoe UI, Arial',
    'fontSize': '13px',
    'primaryColor': '#FFFDE7',
    'primaryTextColor': '#111827',
    'primaryBorderColor': '#111827',
    'clusterBkg': '#FFFDE7',
    'clusterBorder': '#111827',
    'lineColor': '#111827',
    'tertiaryColor': '#FFFDE7',
    'edgeLabelBackground': '#ffffff'
  },
  'flowchart': { 'nodeSpacing': 40, 'rankSpacing': 60 }
}}%%
graph TD
  classDef default stroke:#111827,stroke-width:2px,fill:#FFFDE7,color:#111827;
  %% Dev & CI/CD
  subgraph "DevOps"
    GH["GitHub Repository"]
    GHA["GitHub Actions CI/CD\n(on: push, pull_request)"]
  end

  GH -->|"code push / PR"| GHA

  %% Runtime Containers
  subgraph "Container: mlops-api (Flask)"
    API["Flask API (src/api.py)"]
    PRED["Endpoints:\n/health, /info, /schema, /predict, /predict_batch\n/monitoring/*, /logs, /metrics/api, /metrics/models, /database/*"]
    VALID["Pydantic Validation"]
  end

  subgraph "Model Serving"
    MODEL["Model: models/best_model.pkl"]
    SCALER["Scaler: data/scaler.pkl"]
    FEAT["Feature Names: data/X_train.csv"]
  end

  %% Split to keep clusters compact
  %% Place Observability cluster above the Training cluster
  subgraph "Observability"
    PROM["Prometheus (/metrics)"]
    DBLOG["SQLite logs (database/mlops_logs.db)"]
  end

  subgraph "Monitoring & Drift"
    MON["APIMonitor → reports/"]
    DRIFT["Data monitoring: drift + performance"]
    TRIGGER["Retraining trigger → triggers/*.trigger"]
  end

  subgraph "Training Pipeline (offline)"
    PREP["Data Preprocessing (src/data_preprocessing.py)"]
    TRAIN["Model Training (src/model_training.py)"]
    BEST["Best Model + Metrics →\nmodels/best_model.pkl\nmodels/best_model_metrics.json"]
  end

  subgraph "Container: mlflow-server"
    MLFLOW["MLflow Server (docker-compose)"]
  end

  subgraph "Shared Storage (volumes)"
    DATA_DIR["data/"]
    MODELS_DIR["models/"]
    MLR_DIR["mlruns/"]
    MLART_DIR["mlartifacts/"]
    REPORTS["reports/"]
    DB_DIR["database/"]
    TRIG_DIR["triggers/"]
  end

  %% Clients
  USER["User / External Client"] -->|HTTP| API
  DEMO["demo_api.py CLI"] -->|HTTP| API

  %% API internals
  API --> PRED
  API --> VALID
  VALID -->|"load"| MODEL
  VALID -->|"scale"| SCALER
  MODEL -. "features" .- FEAT

  %% Observability
  API --> PROM
  API --> DBLOG
  MON -->|"GET/POST"| API
  MON --> REPORTS

  %% Layout hint: place Training below Observability via a feedback edge
  PROM -. "observability feedback" .-> PREP
  DBLOG -. "logs/metrics" .-> PREP

  %% Monitoring & triggers
  API --> DRIFT
  DRIFT --> TRIGGER

  %% Training & registry
  PREP --> TRAIN
  TRAIN --> BEST
  TRAIN --> MLR_DIR
  TRAIN --> MLART_DIR
  MLFLOW -->|"reads/writes"| MLR_DIR
  MLFLOW -->|"reads/writes"| MLART_DIR

  %% Serving uses shared storage
  MODEL --- MODELS_DIR
  SCALER --- DATA_DIR

  %% Containers mount shared storage
  API --- DATA_DIR
  API --- MODELS_DIR
  API --- DB_DIR
  API --- REPORTS
  API --- TRIG_DIR
  MLFLOW --- MLR_DIR
  MLFLOW --- MLART_DIR

  %% CI outputs (optional)
  GHA -. "lint/test/build docker image" .-> API
  GHA -. "artifact: image / reports" .-> GH
```

### Components

- **API (Flask)**: `src/api.py` exposes `/predict`, `/predict_batch`, `/health`, `/info`, `/schema` plus monitoring and DB query endpoints. Uses Pydantic for validation, loads the best model and scaler, and emits Prometheus metrics.
- **ML Models**: Trained with `src/model_training.py`, best model stored at `models/best_model.pkl`; metrics stored at `models/best_model_metrics.json`. Individual models saved for comparison; MLflow tracks runs in `mlruns/` and artifacts in `mlartifacts/`.
- **Logging modules**: `src/database_logging.py` writes logs, API metrics, and model metrics to SQLite (`database/mlops_logs.db`). Console logging also enabled.
- **Database (SQLite)**: File-backed SQLite DB for logs/metrics: `database/mlops_logs.db`. Query via API endpoints: `/logs`, `/metrics/api`, `/metrics/models`, `/database/stats`, `/database/clear`.
- **MLflow**: Local MLflow server container (via `docker-compose.yml`) serving UI on port 5001; tracking directory `mlruns/` and artifacts `mlartifacts/` mounted as volumes.
- **Monitoring**: `src/monitoring.py` performs health checks and prediction probes, persists metrics to `reports/` and database, and generates `reports/api_monitoring_report.png` and `reports/monitoring_summary.json`.
- **Data Monitoring & Retraining**: `src/data_monitoring.py` detects drift (KS test) and performance degradation, and can write retraining triggers to `triggers/*.trigger`. Accessible via `/monitoring/*` endpoints in the API.
- **Docker**: `docker-compose.yml` defines `mlops-api` (exposes 5000) and `mlflow-server` (exposes 5001), mounting `models/`, `data/`, `mlruns/`, `mlartifacts/` as volumes.
- **GitHub**: Source control host for the repo.
- **GitHub Actions**: CI/CD flows triggered on `push` and `pull_request` to run lint/tests and optionally build images and publish artifacts. (A starter workflow can be added if desired.)
- **Clients**: `demo_api.py` CLI and any HTTP client; Postman collection available in `postman/`.

### Data Flow

1. Client sends JSON to `/predict` or `/predict_batch`.
2. API validates input (Pydantic), scales features with `data/scaler.pkl`, and predicts with `models/best_model.pkl`.
3. API logs request metrics to SQLite and emits Prometheus counters/histograms; returns prediction.
4. Monitoring jobs hit `/health` and `/predict`, saving time series and reports.
5. Data monitoring evaluates drift/performance and may create retraining trigger files.
6. Offline training pipeline preprocesses data, trains multiple models, tracks in MLflow, and writes the best model/metrics to `models/`.

### Notes

- API framework is Flask; FastAPI is not used in this project.
- Prometheus metrics are exposed at `/metrics` (scrape configuration is external to this repo).
- Docker Compose is intended for local development; deployment beyond local is not defined here.
