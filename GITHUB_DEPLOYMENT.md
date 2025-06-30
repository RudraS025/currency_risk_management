# GitHub Deployment Guide

## Quick Setup for GitHub Repository: RudraS025/currency_risk_management

### 1. Initialize Git Repository (if not already done)

```bash
cd d:\Currency_Risk_Management
git init
git branch -M main
```

### 2. Create .gitignore

```bash
# Add to .gitignore (already exists in project):
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.pytest_cache/
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.idea/
.vscode/
*.egg-info/
dist/
build/

# Environment and config
.env
config_local.ini
*.xlsx
*.json
daily_*.json
daily_*.log

# Heroku
.profile
```

### 3. Add Remote Repository

```bash
git remote add origin https://github.com/RudraS025/currency_risk_management.git
```

### 4. Initial Commit and Push

```bash
git add .
git commit -m "Initial commit: Comprehensive Currency Risk Management System with forward rates, P&L analytics, and web dashboard"
git push -u origin main
```

### 5. Repository Structure

Your repository will contain:

```
currency_risk_management/
├── README.md                               # Main documentation
├── README_NEW.md                          # Detailed system overview
├── P&L_Complete_Guide.md                  # P&L calculation guide
├── CLIENT_FORWARD_RATES_IMPLEMENTATION.md # Forward rates guide
├── HEROKU_DEPLOYMENT.md                   # Heroku deployment guide
├── requirements.txt                       # Python dependencies
├── setup.py                              # Package setup
├── Procfile                              # Heroku process configuration
├── runtime.txt                           # Python version for Heroku
├── app.py                                # Flask web application
├── .env.example                          # Environment variables template
├── config.ini                            # Default configuration
├── src/currency_risk_mgmt/               # Main package
│   ├── models/                           # Data models (LC, etc.)
│   ├── data_providers/                   # Forex and forward rates
│   ├── calculators/                      # P&L and risk calculations
│   ├── reports/                          # Report generation
│   └── utils/                            # Utilities
├── examples/                             # Demo scripts
├── templates/                            # Web templates
└── docs/                                # Documentation
```

### 6. GitHub Features

- **Issues**: Track feature requests and bugs
- **Actions**: Set up CI/CD (optional)
- **Releases**: Tag versions
- **Wiki**: Additional documentation

### 7. Contributing

To contribute to the project:

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Create Pull Request

### 8. Deployment from GitHub

Both Heroku and other platforms can deploy directly from GitHub:

1. Connect your Heroku app to GitHub repository
2. Enable automatic deploys from main branch
3. Every push to main will trigger deployment
