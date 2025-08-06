# 🚀 GitHub Actions CI/CD Pipeline Documentation

This directory contains automated CI/CD workflows for the MLOps project, providing comprehensive automation for testing, deployment, model training, and maintenance.

## 📋 Workflow Overview

### 🔧 [ci.yml](workflows/ci.yml) - Continuous Integration
**Triggers:** Push to `main`, `develop`, `feature/*` branches; Pull requests to `main`, `develop`

**Features:**
- ✅ Multi-version Python testing (3.9, 3.10, 3.11)
- 🧹 Code quality checks (flake8, black, isort)
- 🧪 Comprehensive test suite with coverage reporting
- 📊 Data validation and schema checks
- 🔒 Security scanning with Bandit
- ⚡ Dependency caching for faster builds

**Jobs:**
1. **test** - Runs tests across multiple Python versions
2. **data-validation** - Validates data integrity and schema
3. **security-scan** - Performs security vulnerability scanning

---

### 🚀 [cd.yml](workflows/cd.yml) - Continuous Deployment
**Triggers:** Push to `main`, tags starting with `v*`, successful CI completion

**Features:**
- 🐳 Automated Docker image building and publishing
- 🌐 Multi-environment deployment (staging → production)
- 🔍 Model validation and health checks
- 📈 Performance monitoring and reporting
- 🏷️ Semantic versioning support

**Jobs:**
1. **build-and-push-docker** - Builds and publishes container images
2. **deploy-staging** - Deploys to staging environment with validation
3. **deploy-production** - Production deployment (tag-triggered only)
4. **model-monitoring** - Post-deployment monitoring and reporting

---

### 🤖 [ml-pipeline.yml](workflows/ml-pipeline.yml) - ML Model Training & Validation
**Triggers:** Weekly schedule (Sundays 02:00 UTC), Manual dispatch, Changes to model/data files

**Features:**
- 📊 Automated data quality validation
- 🧠 Model training and hyperparameter optimization
- 📈 Performance comparison with existing models
- 🔄 Automated model versioning and artifact management
- 📝 Comprehensive training reports

**Jobs:**
1. **data-validation** - Validates data quality and completeness
2. **model-training** - Trains and validates new models
3. **model-comparison** - Compares performance with existing models
4. **notify-completion** - Sends training completion notifications

---

### 🛡️ [maintenance.yml](workflows/maintenance.yml) - Maintenance & Security
**Triggers:** Daily security scans (06:00 UTC), Weekly dependency updates (Mondays 08:00 UTC), Manual dispatch

**Features:**
- 🔒 Comprehensive security vulnerability scanning
- 📦 Automated dependency updates with testing
- 🐳 Docker image security analysis
- 📊 Performance benchmarking and monitoring
- 📋 Automated maintenance reporting

**Jobs:**
1. **security-audit** - Multi-tool security scanning (Safety, Bandit, Semgrep)
2. **dependency-update** - Automated dependency management
3. **docker-security-scan** - Container vulnerability analysis
4. **performance-monitoring** - Performance benchmarks and profiling

---

## 🔧 Setup Requirements

### 1. Repository Secrets
Configure these secrets in your GitHub repository settings:

```bash
# Container Registry (if using private registry)
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_password

# Optional: Notification webhooks
SLACK_WEBHOOK_URL=your_slack_webhook
TEAMS_WEBHOOK_URL=your_teams_webhook
```

### 2. Branch Protection Rules
Recommended branch protection for `main`:
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require pull request reviews before merging
- ✅ Dismiss stale reviews when new commits are pushed

### 3. Environment Configuration
Set up deployment environments in repository settings:
- **staging** - For pre-production testing
- **production** - For live deployments (require manual approval)

---

## 🎯 Workflow Triggers & Usage

### Automatic Triggers

| Event | Workflows | Description |
|-------|-----------|-------------|
| Push to `main` | CI, CD | Full pipeline execution |
| Push to `feature/*` | CI | Testing and validation |
| Pull Request | CI | Pre-merge validation |
| Weekly Schedule | ML Pipeline | Model retraining |
| Daily Schedule | Maintenance | Security and updates |
| Tag `v*` | CD (Production) | Production deployment |

### Manual Triggers

All workflows support manual dispatch with various options:

```bash
# Trigger model retraining
gh workflow run ml-pipeline.yml -f retrain_model=true

# Run security scan only
gh workflow run maintenance.yml -f security_scan_only=true

# Force dependency updates
gh workflow run maintenance.yml -f update_dependencies=true
```

---

## 📊 Monitoring & Reporting

### Artifacts Generated
- 📋 **Test Coverage Reports** - HTML and XML coverage reports
- 🔒 **Security Scan Results** - JSON reports from multiple scanners
- 🤖 **Model Training Reports** - Performance metrics and comparisons
- 📦 **Model Artifacts** - Trained models and preprocessors
- 🐳 **Container Images** - Tagged Docker images in registry

### Performance Metrics Tracked
- ⏱️ Model loading time
- 🚀 Prediction throughput
- 💾 Memory usage
- 🔍 Model accuracy metrics (R², RMSE, MAE)
- 🔒 Security vulnerability counts

---

## 🚨 Failure Handling

### Common Issues & Solutions

**1. Test Failures**
```bash
# Check test logs in GitHub Actions
# Run tests locally:
pytest tests/ -v --cov=src
```

**2. Model Training Failures**
```bash
# Check data validation logs
# Verify model performance thresholds in ml-pipeline.yml
```

**3. Security Scan Failures**
```bash
# Review security reports in artifacts
# Update dependencies: pip install --upgrade package_name
```

**4. Deployment Failures**
```bash
# Check health endpoint: curl -f http://localhost:5000/health
# Verify model artifacts are present
```

---

## 🔄 Customization

### Modifying Performance Thresholds
Edit thresholds in `ml-pipeline.yml`:
```yaml
# Model performance thresholds
if metrics['test_r2_score'] < 0.6:  # Adjust R² threshold
if metrics['test_rmse'] > 1.0:      # Adjust RMSE threshold
```

### Adding New Tests
1. Add test files to `tests/` directory
2. Tests are automatically discovered and run
3. Update coverage requirements in `ci.yml` if needed

### Custom Deployment Targets
1. Add new environment in repository settings
2. Create deployment job in `cd.yml`
3. Configure environment-specific variables

---

## 📈 Best Practices

### Code Quality
- ✅ Maintain test coverage above 80%
- 🧹 Use black for code formatting
- 📏 Follow flake8 linting rules
- 🔒 Address security scan findings promptly

### Model Management
- 🏷️ Use semantic versioning for model releases
- 📊 Monitor model performance metrics
- 🔄 Retrain models when data significantly changes
- 📝 Document model changes in commit messages

### Security
- 🔒 Regularly update dependencies
- 🛡️ Review security scan results
- 🐳 Scan container images for vulnerabilities
- 🔑 Rotate secrets and tokens regularly

---

## 🆘 Support & Troubleshooting

### Getting Help
1. Check workflow logs in GitHub Actions tab
2. Review artifact reports for detailed information
3. Consult this documentation for common issues
4. Use manual workflow dispatch for debugging

### Debugging Workflows
```bash
# Enable debug logging
gh workflow run workflow-name.yml --field enable_debug=true

# Download workflow artifacts
gh run download <run_id>
```

### Contact & Resources
- 📚 [GitHub Actions Documentation](https://docs.github.com/en/actions)
- 🐳 [Docker Documentation](https://docs.docker.com/)
- 🤖 [MLflow Documentation](https://mlflow.org/docs/latest/index.html)

---

## 📝 Changelog

### Version 1.0.0 (Initial Release)
- ✅ Complete CI/CD pipeline implementation
- 🤖 Automated ML model training and validation
- 🔒 Comprehensive security scanning
- 📦 Automated dependency management
- 🐳 Container-based deployment
- 📊 Performance monitoring and reporting

---

*Last updated: $(date)*
*Pipeline Status: 🟢 Active*