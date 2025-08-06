# GitHub Actions Pipeline Testing Guide

This guide provides step-by-step instructions to test all the GitHub Actions workflows we've established.

## Testing Overview

Our pipeline includes 4 main workflows:
- **CI (Continuous Integration)** - Tests, linting, validation
- **CD (Continuous Deployment)** - Docker builds, deployments  
- **ML Pipeline** - Model training and validation
- **Maintenance** - Security scans, dependency updates

## 1. Testing CI Workflow

### Automatic Triggers
The CI workflow runs on:
- Push to `main`, `develop`, `feature/*` branches
- Pull requests to `main`, `develop`

### Test Steps:

#### A. Test with Current Push (Already Done)
```bash
# We just pushed to feature/enhancement, which should trigger CI
# Check GitHub Actions tab in your repository to see the workflow running
```

#### B. Create a Test Change
```bash
# Make a small change to trigger another CI run
echo "# Testing CI Pipeline" >> TEST_CI.md
git add TEST_CI.md
git commit -m "test: Add test file to trigger CI workflow"
git push origin feature/enhancement
```

#### C. Expected CI Results
The CI workflow should:
- Run tests on Python 3.9, 3.10, 3.11
- Perform linting with flake8
- Check code formatting with black
- Validate data schema
- Generate test coverage reports
- Run security scans

## 2. Testing Manual Workflow Triggers

### Using GitHub Web Interface

1. **Go to your GitHub repository**
2. **Click "Actions" tab**
3. **Select a workflow** (e.g., "ML Model Training & Validation")
4. **Click "Run workflow" button**
5. **Fill in parameters and click "Run workflow"**

### Using GitHub CLI (if installed)

```bash
# Test ML Pipeline manually
gh workflow run ml-pipeline.yml -f retrain_model=true

# Test Maintenance workflow
gh workflow run maintenance.yml -f security_scan_only=true

# Test with different parameters
gh workflow run ml-pipeline.yml -f data_validation_only=true
```

## 3. Testing CD Workflow

The CD workflow has multiple stages:

### A. Test Docker Build (Staging)
```bash
# CD triggers on push to main, so let's merge our feature branch
git checkout main
git pull origin main
git merge feature/enhancement
git push origin main
```

### B. Test Production Deployment
```bash
# Create a version tag to trigger production deployment
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Expected CD Results
- Docker image built and pushed to GitHub Container Registry
- Staging deployment with health checks
- Production deployment (only on tags)
- Model validation tests
- Deployment reports generated

## 4. Testing ML Pipeline Workflow

### A. Manual Trigger Test
```bash
# Using GitHub CLI
gh workflow run ml-pipeline.yml -f retrain_model=true

# Or trigger by modifying data files
echo "# Data change to trigger ML pipeline" >> data/README.md
git add data/README.md
git commit -m "test: Trigger ML pipeline with data change"
git push origin main
```

### B. Scheduled Test
The ML pipeline runs weekly on Sundays at 02:00 UTC. To test scheduling:
- Wait for the scheduled run, or
- Manually trigger using the web interface

### Expected ML Pipeline Results
- Data validation checks
- Model training execution
- Performance comparison with existing models
- Model artifacts uploaded
- Training reports generated

## 5. Testing Maintenance Workflow

### A. Manual Security Scan
```bash
# Trigger security scan only
gh workflow run maintenance.yml -f security_scan_only=true
```

### B. Manual Dependency Update
```bash
# Trigger dependency updates
gh workflow run maintenance.yml -f update_dependencies=true
```

### Expected Maintenance Results
- Security vulnerability reports
- Dependency update analysis
- Docker image security scans
- Performance benchmarks
- Maintenance reports

## 6. Monitoring Test Results

### A. GitHub Actions Interface
1. Go to repository → Actions tab
2. Click on workflow runs to see details
3. Check job logs for success/failure
4. Download artifacts (reports, coverage, etc.)

### B. Check Workflow Status
```bash
# List recent workflow runs
gh run list

# Get details of specific run
gh run view [RUN_ID]

# Download artifacts
gh run download [RUN_ID]
```

## 7. Testing Specific Components

### A. Test Model Loading (Local)
```bash
# Verify model files exist and can be loaded
python -c "
import joblib
import os

if os.path.exists('models/best_model.pkl'):
    model = joblib.load('models/best_model.pkl')
    print('Model loaded successfully')
else:
    print('Model file not found - run model training first')
"
```

### B. Test API Health Check (Local)
```bash
# Start API locally
python src/api.py &
API_PID=$!

# Wait and test health endpoint
sleep 5
curl -f http://localhost:5000/health

# Stop API
kill $API_PID
```

### C. Test Data Validation (Local)
```bash
# Run data preprocessing validation
python src/data_preprocessing.py --validate-only
```

## 8. Troubleshooting Common Issues

### A. Workflow Fails Due to Missing Files
```bash
# Ensure required files exist
ls -la models/
ls -la data/

# If missing, run the pipeline locally first
python run_pipeline.py
```

### B. Docker Build Fails
```bash
# Test Docker build locally
docker build -t test-mlops .
docker run --rm test-mlops python -c "print('Container works')"
```

### C. Security Scan Failures
```bash
# Run security tools locally
pip install bandit safety
bandit -r src/
safety check
```

## 9. Expected Artifacts

After successful workflow runs, you should see these artifacts:

### CI Workflow Artifacts
- Test coverage reports (HTML/XML)
- Security scan results (JSON)
- Linting reports

### CD Workflow Artifacts  
- Docker images in GitHub Container Registry
- Deployment reports (Markdown)
- Health check results

### ML Pipeline Artifacts
- Trained model files (.pkl)
- Model metrics (JSON)
- Training reports (Markdown)
- Performance comparison reports

### Maintenance Artifacts
- Security vulnerability reports
- Dependency analysis reports
- Performance benchmark results

## 10. Validation Checklist

Use this checklist to verify your pipeline is working correctly:

### CI Workflow ✓
- [ ] Workflow triggers on push to feature branch
- [ ] Tests run on multiple Python versions
- [ ] Linting and formatting checks pass
- [ ] Security scans complete
- [ ] Artifacts are generated and uploaded

### CD Workflow ✓
- [ ] Docker image builds successfully
- [ ] Image pushed to container registry
- [ ] Staging deployment completes
- [ ] Health checks pass
- [ ] Production deployment works (on tags)

### ML Pipeline ✓
- [ ] Data validation runs successfully
- [ ] Model training completes
- [ ] Model metrics are within thresholds
- [ ] Model artifacts are uploaded
- [ ] Performance comparison works

### Maintenance Workflow ✓
- [ ] Security scans run without errors
- [ ] Dependency checks complete
- [ ] Performance benchmarks execute
- [ ] Reports are generated

## 11. Next Steps

After testing:

1. **Review all workflow logs** for any warnings or issues
2. **Check artifact quality** - ensure reports are meaningful
3. **Adjust thresholds** if needed (model performance, security, etc.)
4. **Set up notifications** for workflow failures
5. **Create branch protection rules** requiring CI success
6. **Document any custom configurations** for your team

## 12. Monitoring Commands

Keep these commands handy for ongoing monitoring:

```bash
# Check workflow status
gh run list --limit 10

# View specific workflow
gh workflow view ci.yml

# Download latest artifacts
gh run download $(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')

# Check repository secrets
gh secret list
```

---

**Note**: The first workflow runs might take longer as GitHub Actions sets up the environment and caches dependencies. Subsequent runs will be faster due to caching.