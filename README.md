# ⚙️ Azure Demand Forecasting & Capacity Optimization System

## 🚀 Milestone 4 - Backend API

A comprehensive Flask REST API for CPU demand forecasting with intelligent capacity planning, model drift monitoring, and automated reporting.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Setup Instructions](#-setup-instructions)
- [Running the Backend](#-running-the-backend)
- [API Documentation](#-api-documentation)
- [Azure Deployment](#-azure-deployment)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

✅ **Model Deployment** - Load and serve trained Random Forest CPU demand model  
✅ **Recursive Forecasting** - 7-day and 30-day forecasts with automatic feature engineering  
✅ **Capacity Planning** - Intelligent scaling recommendations (scale up/down/stable)  
✅ **Drift Detection** - Model health monitoring with MAPE-based drift detection  
✅ **Automated Reporting** - Comprehensive reports combining forecasts, capacity analysis, and model health  
✅ **CORS Enabled** - Ready for frontend integration  
✅ **Error Handling** - Robust error handling with detailed traceback

---

## 📁 Project Structure

```
AZURE_BATCH-4_BACKEND/
├── app.py                          # Main Flask application (8 endpoints)
├── forecast_utils.py               # Recursive forecasting engine
├── capacity_utils.py               # Capacity planning logic
├── monitoring_utils.py             # Drift detection & monitoring
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── Models/
│   └── cpu_demand_model.pkl       # Trained Random Forest model
└── Data/
    └── feature engineered dataset/
        └── mlmodeltrainingdataset.csv  # ML-ready training dataset
```

---

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Navigate to Project

```bash
cd AZURE_BATCH-4_BACKEND
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- Flask 3.0.0 - Web framework
- flask-cors 4.0.0 - CORS support
- pandas 2.1.4 - Data manipulation
- numpy 1.26.2 - Numerical computing
- scikit-learn 1.3.2 - Machine learning
- joblib 1.3.2 - Model serialization

### Step 4: Verify File Structure

Ensure the following files exist:
- ✅ `Models/cpu_demand_model.pkl` - Trained model file
- ✅ `Data/feature engineered dataset/mlmodeltrainingdataset.csv` - Dataset

---

## 🚀 Running the Backend

### Development Server

```bash
python app.py
```

The API will start on `http://localhost:5000`

**Expected Output:**
```
============================================================
🚀 Azure Demand Forecasting API - Starting Up...
============================================================
✅ Loaded CPU model from: Models/cpu_demand_model.pkl
✅ Loaded dataset from: Data/feature engineered dataset/mlmodeltrainingdataset.csv
   Dataset shape: (365, 44)
   Features: 44
============================================================
✅ Initialization Complete - API Ready!
============================================================
```

### Production Server (using Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:5000
```

---

### 1️⃣ **GET /** - Health Check

Check if API is running.

**Request:**
```bash
curl http://localhost:5000/
```

**Response:**
```json
{
  "status": "running",
  "message": "🚀 Azure Demand Forecasting API is running!",
  "version": "Milestone 4",
  "endpoints": {
    "health": "GET /",
    "metrics": "GET /api/metrics",
    "predict": "POST /api/predict_cpu",
    "forecast_7": "GET /api/forecast_7",
    "forecast_30": "GET /api/forecast_30",
    "capacity": "POST /api/capacity_planning",
    "monitoring": "GET /api/monitoring",
    "report": "GET /api/report"
  }
}
```

---

### 2️⃣ **GET /api/metrics** - Model Status

Get model and dataset metadata.

**Request:**
```bash
curl http://localhost:5000/api/metrics
```

**Response:**
```json
{
  "cpu_model": {
    "status": "loaded",
    "type": "RandomForestRegressor",
    "n_features": 44,
    "features": ["usage_cpu", "usage_storage", ...]
  },
  "dataset": {
    "status": "loaded",
    "shape": [365, 44],
    "rows": 365,
    "columns": 44
  }
}
```

---

### 3️⃣ **POST /api/predict_cpu** - Single Prediction

Make a single CPU demand prediction with custom input.

**Request:**
```bash
curl -X POST http://localhost:5000/api/predict_cpu \
  -H "Content-Type: application/json" \
  -d '{
    "usage_cpu": 75.5,
    "usage_storage": 82.3,
    "users_active": 1500,
    "economic_index": 105.2,
    "cloud_market_demand": 89.5,
    "holiday": 0,
    "month": 12,
    "year": 2024,
    "is_weekend": 0
  }'
```

**Note:** You can provide partial features. Missing lag/rolling features will be auto-calculated from historical data.

**Response:**
```json
{
  "prediction": 78.35,
  "input_features": {
    "usage_cpu": 75.5,
    "usage_storage": 82.3,
    ...
  }
}
```

---

### 4️⃣ **GET /api/forecast_7** - 7-Day Forecast

Get 7-day recursive CPU demand forecast.

**Request:**
```bash
curl http://localhost:5000/api/forecast_7
```

**Response:**
```json
{
  "forecast_days": 7,
  "predictions": [78.5, 79.2, 80.1, 81.5, 82.3, 83.0, 84.2]
}
```

---

### 5️⃣ **GET /api/forecast_30** - 30-Day Forecast

Get 30-day recursive CPU demand forecast.

**Request:**
```bash
curl http://localhost:5000/api/forecast_30
```

**Response:**
```json
{
  "forecast_days": 30,
  "predictions": [78.5, 79.2, ..., 95.8]
}
```

---

### 6️⃣ **POST /api/capacity_planning** - Capacity Analysis

Analyze capacity requirements and get scaling recommendations.

**Request:**
```bash
curl -X POST http://localhost:5000/api/capacity_planning \
  -H "Content-Type: application/json" \
  -d '{
    "capacity": 10000,
    "forecast_days": 7
  }'
```

**Response:**
```json
{
  "avg_forecast": 7850.5,
  "capacity": 10000,
  "utilization": 78.51,
  "status": "stable",
  "recommendation": "✅ STABLE: Current capacity is adequate, no action needed"
}
```

**Status Values:**
- `scale_up` - Utilization > 80% → Add 15% capacity
- `scale_down` - Utilization < 40% → Reduce 10% capacity
- `stable` - 40% ≤ Utilization ≤ 80% → No action needed

---

### 7️⃣ **GET /api/monitoring** - Model Health

Monitor model health and detect drift.

**Request:**
```bash
curl "http://localhost:5000/api/monitoring?mape=8.5"
```

**Response:**
```json
{
  "mape": 8.5,
  "threshold": 10.0,
  "status": "stable",
  "message": "✅ Model Stable",
  "recommendation": "No action required. Model performance is within acceptable range."
}
```

**Drift Detection:**
- MAPE ≤ 10% → ✅ Model Stable
- MAPE > 10% → ⚠️ Drift Detected - Retraining Required

---

### 8️⃣ **GET /api/report** - Comprehensive Report

Generate comprehensive automated report.

**Request:**
```bash
curl "http://localhost:5000/api/report?capacity=10000&mape=8.5"
```

**Response:**
```json
{
  "report_type": "comprehensive",
  "generated_at": "2024-12-02T21:45:00",
  "forecast_summary": {
    "days_forecasted": 7,
    "predictions": [78.5, 79.2, ...],
    "avg_forecast": 81.2,
    "min_forecast": 78.5,
    "max_forecast": 84.2,
    "trend": "increasing"
  },
  "capacity_analysis": {
    "avg_forecast": 81.2,
    "capacity": 10000,
    "utilization": 0.81,
    "status": "stable",
    "recommendation": "✅ STABLE: Current capacity is adequate"
  },
  "model_health": {
    "mape": 8.5,
    "status": "stable",
    "message": "✅ Model Stable"
  }
}
```

---

## ☁️ Azure Deployment

### Deploy to Azure App Service

#### Step 1: Install Azure CLI

```bash
# Windows (via winget)
winget install Microsoft.AzureCLI

# Mac
brew install azure-cli

# Or download from: https://aka.ms/installazurecliwindows
```

#### Step 2: Login to Azure

```bash
az login
```

#### Step 3: Create Resource Group

```bash
az group create --name azure-forecasting-rg --location eastus
```

#### Step 4: Create App Service Plan

```bash
az appservice plan create \
  --name azure-forecasting-plan \
  --resource-group azure-forecasting-rg \
  --sku B1 \
  --is-linux
```

#### Step 5: Create Web App

```bash
az webapp create \
  --resource-group azure-forecasting-rg \
  --plan azure-forecasting-plan \
  --name azure-demand-forecasting-api \
  --runtime "PYTHON:3.9"
```

#### Step 6: Configure Deployment

```bash
# Deploy from local git
az webapp deployment source config-local-git \
  --name azure-demand-forecasting-api \
  --resource-group azure-forecasting-rg
```

#### Step 7: Deploy Code

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial deployment"

# Add Azure remote and push
git remote add azure <DEPLOYMENT_URL_FROM_STEP_6>
git push azure main
```

#### Step 8: Configure Environment Variables

```bash
az webapp config appsettings set \
  --name azure-demand-forecasting-api \
  --resource-group azure-forecasting-rg \
  --settings \
    FLASK_ENV=production \
    FLASK_DEBUG=0
```

#### Step 9: Access Your API

```
https://azure-demand-forecasting-api.azurewebsites.net
```

### Alternative: Deploy via VS Code

1. Install **Azure App Service** extension
2. Right-click on `AZURE_BATCH-4_BACKEND` folder
3. Select **Deploy to Web App**
4. Follow prompts to create/select App Service

---

## 🐛 Troubleshooting

### Issue: Model file not found

**Error:** `FileNotFoundError: Models/cpu_demand_model.pkl`

**Solution:**
```bash
# Verify model exists
ls Models/cpu_demand_model.pkl

# If missing, train and save your model first
```

### Issue: Dataset not found

**Error:** `FileNotFoundError: Data/feature engineered dataset/mlmodeltrainingdataset.csv`

**Solution:**
```bash
# Verify dataset exists
ls "Data/feature engineered dataset/mlmodeltrainingdataset.csv"
```

### Issue: ImportError for flask_cors

**Error:** `ModuleNotFoundError: No module named 'flask_cors'`

**Solution:**
```bash
pip install flask-cors
```

### Issue: Feature mismatch

**Error:** `ValueError: Number of features doesn't match`

**Solution:**
Ensure your model was trained with exactly 44 features matching the schema in the user requirements.

### Issue: CORS errors in frontend

**Solution:**
CORS is already enabled via `flask-cors`. If issues persist:
```python
# In app.py, modify CORS configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

---

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review API documentation above
- Verify all files are in correct locations

---

## 📄 License

This project is part of the Azure Demand Forecasting & Capacity Optimization System - Milestone 4.

---

**🎉 Your Flask backend is now ready for Milestone 4!**
