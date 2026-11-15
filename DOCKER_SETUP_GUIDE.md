# Docker Setup Guide for MLOps Project

This guide provides step-by-step instructions to set up and run the MLOps California Housing Price Prediction API on any machine using Docker.

## Prerequisites

### 1. Install Docker

Choose the installation method based on your operating system:

#### **Windows**

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the setup wizard
3. Restart your computer
4. Verify installation: `docker --version`

#### **macOS**

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Drag Docker to Applications folder
3. Launch Docker Desktop
4. Verify installation: `docker --version`

#### **Linux (Ubuntu/Debian)**

```bash
# Update package index
sudo apt-get update

# Install required packages
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
docker --version
```

#### **Linux (CentOS/RHEL)**

```bash
# Install required packages
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

### 2. Post-Installation Setup (Linux)

```bash
# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and log back in, then verify
docker run hello-world
```

## Deployment Options

### **Option 1: Pull Pre-built Image from GitHub Registry (Recommended)**

This is the fastest method as the image is already built and available:

```bash
# 1. Pull the latest image
docker pull ghcr.io/sengar-ajay/mlops:main

# 2. Run the container
docker run -d \
  --name mlops-api \
  -p 5000:5000 \
  --restart unless-stopped \
  ghcr.io/sengar-ajay/mlops:main

# 3. Verify container is running
docker ps

# 4. Check container health
docker logs mlops-api

# 5. Test the API
curl http://localhost:5000/health
```

#### **⚠️ Apple Silicon (M1/M2) Mac Issue**

If you get the error: `no matching manifest for linux/arm64/v8 in the manifest list entries`, it means the image was built for x86_64 architecture. Here are the solutions:

**Solution 1: Use Platform Flag (Quick Fix)**

```bash
# Force pull x86_64 image and run with emulation
docker pull --platform linux/amd64 ghcr.io/sengar-ajay/mlops:main
docker run -d \
  --name mlops-api \
  --platform linux/amd64 \
  -p 5000:5000 \
  --restart unless-stopped \
  ghcr.io/sengar-ajay/mlops:main
```

**Solution 2: Build Locally (Recommended for Apple Silicon)**

```bash
# Clone the repository and build for your architecture
git clone https://github.com/sengar-ajay/MLOps.git
cd MLOps
docker build -t mlops-pipeline .
docker run -d --name mlops-api -p 5000:5000 --restart unless-stopped mlops-pipeline
```

### **Option 2: Build from Source Code**

If you want to build the image locally or make modifications:

#### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/sengar-ajay/MLOps.git
cd MLOps

# Or download and extract ZIP file if you don't have git
```

#### Step 2: Build Docker Image

```bash
# Build the image
docker build -t mlops-pipeline .

# Verify image was created
docker images | grep mlops-pipeline
```

#### Step 3: Run the Container

```bash
# Run the container
docker run -d \
  --name mlops-api \
  -p 5000:5000 \
  --restart unless-stopped \
  mlops-pipeline

# Check if running
docker ps
```

### **Option 3: Using Docker Compose (Advanced)**

For more complex deployments with multiple services:

#### Step 1: Create docker-compose.yml

```yaml
version: "3.8"

services:
  mlops-api:
    image: ghcr.io/sengar-ajay/mlops:main
    container_name: mlops-api
    ports:
      - "5000:5000"
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    volumes:
      - mlops_logs:/app/logs
      - mlops_reports:/app/reports

volumes:
  mlops_logs:
  mlops_reports:
```

#### Step 2: Deploy with Docker Compose

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f mlops-api

# Stop services
docker-compose down
```

## API Testing

Once the container is running, test the API endpoints:

### Basic Health Check

```bash
# Health check
curl http://localhost:5000/health

# Expected response:
# {"message":"API is running and model is loaded","status":"healthy","timestamp":"..."}
```

### Model Information

```bash
# Get model info
curl http://localhost:5000/info

# Shows model type, features, parameters, etc.
```

### Make Predictions

```bash
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

# Expected response:
# {"prediction": 4.243..., "model_type": "GradientBoostingRegressor", ...}
```

### Batch Predictions

```bash
# Multiple predictions
curl -X POST http://localhost:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322.0, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23},
      {"MedInc": 7.2574, "HouseAge": 21.0, "AveRooms": 5.64, "AveBedrms": 0.92, "Population": 2401.0, "AveOccup": 2.11, "Latitude": 39.43, "Longitude": -121.22}
    ]
  }'
```

## Container Management

### Essential Docker Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs mlops-api

# Follow logs in real-time
docker logs -f mlops-api

# Stop container
docker stop mlops-api

# Start stopped container
docker start mlops-api

# Restart container
docker restart mlops-api

# Remove container
docker rm mlops-api

# View resource usage
docker stats mlops-api

# Execute commands inside container
docker exec -it mlops-api /bin/bash
```

### Update to Latest Version

```bash
# Pull latest image
docker pull ghcr.io/sengar-ajay/mlops:main

# Stop and remove old container
docker stop mlops-api
docker rm mlops-api

# Run new container
docker run -d \
  --name mlops-api \
  -p 5000:5000 \
  --restart unless-stopped \
  ghcr.io/sengar-ajay/mlops:main
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

```bash
# Error: port 5000 is already allocated
# Solution: Use different port
docker run -d --name mlops-api -p 5001:5000 ghcr.io/sengar-ajay/mlops:main

# Or find and stop process using port 5000
lsof -i :5000  # On macOS/Linux
netstat -ano | findstr :5000  # On Windows
```

#### 2. Container Exits Immediately

```bash
# Check container logs
docker logs mlops-api

# Run container interactively to debug
docker run -it --rm ghcr.io/sengar-ajay/mlops:main /bin/bash
```

#### 3. API Not Responding

```bash
# Check if container is healthy
docker ps

# Check container logs
docker logs mlops-api

# Test from inside container
docker exec -it mlops-api curl http://localhost:5000/health
```

#### 4. Permission Denied (Linux)

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

#### 5. Architecture Mismatch (Apple Silicon Macs)

```bash
# Error: no matching manifest for linux/arm64/v8 in the manifest list entries
# Solution 1: Use platform flag to run x86_64 image with emulation
docker pull --platform linux/amd64 ghcr.io/sengar-ajay/mlops:main
docker run -d --name mlops-api --platform linux/amd64 -p 5000:5000 ghcr.io/sengar-ajay/mlops:main

# Solution 2: Build locally for native ARM64 performance
git clone https://github.com/sengar-ajay/MLOps.git
cd MLOps
docker build -t mlops-pipeline .
docker run -d --name mlops-api -p 5000:5000 mlops-pipeline

# Check your system architecture
uname -m  # arm64 = Apple Silicon, x86_64 = Intel
```

## Production Deployment

### Security Considerations

```bash
# Run with non-root user
docker run -d \
  --name mlops-api \
  -p 5000:5000 \
  --user 1000:1000 \
  --restart unless-stopped \
  ghcr.io/sengar-ajay/mlops:main

# Limit resources
docker run -d \
  --name mlops-api \
  -p 5000:5000 \
  --memory=1g \
  --cpus=1.0 \
  --restart unless-stopped \
  ghcr.io/sengar-ajay/mlops:main
```

### Environment Variables

```bash
# Set environment variables
docker run -d \
  --name mlops-api \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  ghcr.io/sengar-ajay/mlops:main
```

### Persistent Storage

```bash
# Mount volumes for logs and reports
docker run -d \
  --name mlops-api \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/reports:/app/reports \
  --restart unless-stopped \
  ghcr.io/sengar-ajay/mlops:main
```

## API Endpoints Summary

| Endpoint         | Method | Description       |
| ---------------- | ------ | ----------------- |
| `/`              | GET    | API home page     |
| `/health`        | GET    | Health check      |
| `/info`          | GET    | Model information |
| `/predict`       | POST   | Single prediction |
| `/predict_batch` | POST   | Batch predictions |

## Support

- **Repository**: https://github.com/sengar-ajay/MLOps
- **Container Registry**: https://github.com/sengar-ajay/MLOps/pkgs/container/mlops
- **Issues**: https://github.com/sengar-ajay/MLOps/issues

## Quick Start Summary

For the fastest deployment on a new machine:

```bash
# 1. Install Docker (see installation section above)

# 2. Pull and run the container
docker pull ghcr.io/sengar-ajay/mlops:main
docker run -d --name mlops-api -p 5000:5000 --restart unless-stopped ghcr.io/sengar-ajay/mlops:main

# 3. Test the API
curl http://localhost:5000/health

# 4. Access the API at http://localhost:5000
```

That's it! Your MLOps API is now running and ready to serve predictions.
