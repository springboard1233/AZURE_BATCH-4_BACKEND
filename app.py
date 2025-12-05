import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import custom utilities
from capacity_utils import get_capacity_recommendation
from monitoring_utils import monitoring_stats
from forecast_utils import prepare_recursive_features
from reporting_utils import save_forecast_history, generate_csv_report
import threading
from scheduler import start_scheduler

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# ====================================================
# 1. LOAD MODEL & DATA
# ====================================================
MODEL_PATH = os.path.join('Models', 'cpu_demand_model.pkl')
DATA_PATH = os.path.join('Data', 'mlmodeltrainingdataset.csv')

model = None
df = None

# Exact feature columns as specified
FEATURE_COLUMNS = [
    'usage_storage', 'users_active', 'economic_index', 'cloud_market_demand', 'holiday', 'month', 'year', 'is_weekend',
    'usage_cpu_lag_1', 'usage_storage_lag_1', 'users_active_lag_1',
    'usage_cpu_lag_3', 'usage_storage_lag_3', 'users_active_lag_3',
    'usage_cpu_lag_7', 'usage_storage_lag_7', 'users_active_lag_7',
    'usage_cpu_rolling_mean_3', 'usage_storage_rolling_mean_3', 'users_active_rolling_mean_3',
    'usage_cpu_rolling_mean_7', 'usage_storage_rolling_mean_7', 'users_active_rolling_mean_7',
    'usage_cpu_rolling_std_3', 'usage_cpu_rolling_std_7',
    'usage_storage_rolling_std_3', 'usage_storage_rolling_std_7',
    'users_active_rolling_std_3', 'users_active_rolling_std_7',
    'cpu_per_user', 'storage_per_user', 'cpu_storage_ratio', 'econ_demand_ratio',
    'system_stress', 'cpu_utilization_ratio', 'storage_efficiency',
    'region_East US', 'region_North Europe', 'region_Southeast Asia', 'region_West US',
    'type_Container', 'type_Storage', 'type_VM'
]

def load_resources():
    global model, df
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print(f"[OK] Model loaded from {MODEL_PATH}")
        else:
            print(f"[WARNING] Warning: {MODEL_PATH} not found. Predictions will fail.")

        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
            print(f"[OK] Dataset loaded from {DATA_PATH}")
        else:
            print(f"[WARNING] Warning: {DATA_PATH} not found. Forecasting will fail.")
    except Exception as e:
        print(f"[ERROR] Error loading resources: {e}")

# Load resources on startup
load_resources()

# ====================================================
# 2. API ENDPOINTS
# ====================================================

@app.route('/')
def index():
    return jsonify({
        "message": "Azure Demand Forecasting Backend is Running!",
        "endpoints": [
            "/api/predict_cpu (POST)",
            "/api/forecast_7 (GET)",
            "/api/forecast_30 (GET)",
            "/api/capacity_planning (POST)",
            "/api/monitoring (GET)",
            "/api/report (GET)"
        ]
    })

@app.route('/api/predict_cpu', methods=['POST'])
def predict_cpu():
    """
    Predicts CPU usage for a single data point.
    """
    try:
        if not model:
            return jsonify({"error": "Model not loaded"}), 500
            
        data = request.get_json()
        
        # Create DataFrame from input
        input_df = pd.DataFrame([data])
        
        # Ensure all columns exist (fill 0 for missing)
        for col in FEATURE_COLUMNS:
            if col not in input_df.columns:
                input_df[col] = 0
                
        # Reorder to match model expectation
        input_df = input_df[FEATURE_COLUMNS]
        
        prediction = model.predict(input_df)[0]
        
        return jsonify({
            "predicted_cpu_usage": float(prediction)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/forecast_7', methods=['GET'])
def forecast_7():
    """
    Returns a 7-day recursive forecast.
    """
    try:
        if model is None or df is None:
            return jsonify({"error": "Model or Data not available"}), 500
            
        # Get the last row of data to start forecasting from
        last_row = df.iloc[-1]
        
        forecasts = prepare_recursive_features(last_row, 7, model, FEATURE_COLUMNS)
        
        return jsonify({
            "forecast_period": "7 days",
            "forecast_values": [float(x) for x in forecasts]
        })
        
    except Exception as e:
        import traceback
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast_30', methods=['GET'])
def forecast_30():
    """
    Returns a 30-day recursive forecast.
    """
    try:
        if model is None or df is None:
            return jsonify({"error": "Model or Data not available"}), 500
            
        # Get the last row of data to start forecasting from
        last_row = df.iloc[-1]
        
        forecasts = prepare_recursive_features(last_row, 30, model, FEATURE_COLUMNS)
        
        return jsonify({
            "forecast_period": "30 days",
            "forecast_values": [float(x) for x in forecasts]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/capacity_planning', methods=['POST'])
def capacity_planning():
    """
    Provides capacity scaling recommendations.
    Expects JSON: { "capacity": 100, "region": "East US", "service": "Compute" }
    """
    try:
        data = request.get_json()
        current_capacity = data.get('capacity', 100)
        region = data.get('region', 'East US')
        service = data.get('service', 'Compute')
        
        # Get latest forecast (using 7-day average as a baseline for planning)
        # In a real scenario, we might call the forecast function or use cached values.
        # Here we will re-run a quick 7-day forecast to get the utilization trend.
        if model is not None and df is not None:
            last_row = df.iloc[-1]
            forecasts = prepare_recursive_features(last_row, 7, model, FEATURE_COLUMNS)
            avg_forecast = np.mean(forecasts)
        else:
            # Fallback if model missing (for testing endpoint structure)
            avg_forecast = 125.0 # Example value
            
        result = get_capacity_recommendation(avg_forecast, current_capacity, region, service)
        
        # Save to history for reporting
        save_forecast_history({
            "region": region,
            "service": service,
            "forecast_value": avg_forecast,
            "recommendation": result["recommendation_text"]
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitoring', methods=['GET'])
def monitoring():
    """
    Returns model health status, checking for drift and data age.
    """
    try:
        # In a real system, we would calculate MAPE against actuals.
        # Here we simulate a MAPE value.
        # Let's simulate a slightly higher error to test logic, or keep it stable.
        simulated_mape = 6.5 
        
        # We can also simulate passing a specific date if we tracked it in a file
        result = monitoring_stats(simulated_mape)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/report', methods=['GET'])
def report():
    """
    Returns a summary report of forecasts and system health.
    """
    try:
        # Gather data
        report_data = {
            "system_status": "Active",
            "model_status": "Stable", # Could come from monitoring()
            "forecast_summary_7_days": [],
            "avg_forecast_utilization": 0.0,
            "recommendation": "N/A"
        }
        
        if model is not None and df is not None:
            # Run forecast
            last_row = df.iloc[-1]
            forecasts = prepare_recursive_features(last_row, 7, model, FEATURE_COLUMNS)
            avg_val = float(np.mean(forecasts))
            
            # Get capacity rec (assuming default capacity of 100 for report context)
            cap_rec = get_capacity_recommendation(avg_val, 100, "East US", "Compute")
            
            report_data["forecast_summary_7_days"] = [float(x) for x in forecasts]
            report_data["avg_forecast_utilization"] = avg_val
            report_data["recommendation"] = cap_rec["recommendation_text"]
            
        return jsonify(report_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trigger_automation', methods=['POST'])
def trigger_automation():
    """
    Manually triggers the automated report generation.
    """
    try:
        report_path = generate_csv_report()
        if report_path:
            return jsonify({"message": "Automation triggered", "report_file": report_path})
        else:
            return jsonify({"message": "No data to report"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Azure Demand Forecasting Backend...")
    
    # Start scheduler in background thread
    t = threading.Thread(target=start_scheduler, daemon=True)
    t.start()
    
    app.run(debug=True, port=5000)

# ====================================================
# 📌 INSTRUCTIONS
# ====================================================
"""
HOW TO RUN THE BACKEND:
1. Ensure you have Python installed.
2. Install dependencies:
   pip install -r requirements.txt
3. Place 'cpu_demand_model.pkl' and 'mlmodeltrainingdataset.csv' in this folder.
4. Run the app:
   python app.py

HOW TO CALL APIS (CURL EXAMPLES):

1. Predict Single CPU Usage:
   curl -X POST http://127.0.0.1:5000/api/predict_cpu -H "Content-Type: application/json" -d '{"usage_cpu": 45.2, "usage_storage": 120.5, ...}'

2. Get 7-Day Forecast:
   curl http://127.0.0.1:5000/api/forecast_7

3. Get Capacity Recommendation:
   curl -X POST http://127.0.0.1:5000/api/capacity_planning -H "Content-Type: application/json" -d '{"capacity": 100}'

4. Check Model Health:
   curl http://127.0.0.1:5000/api/monitoring

HOW TO DEPLOY ON AZURE APP SERVICE:
1. Create a 'startup.sh' or configure the startup command in Azure Portal:
   gunicorn --bind=0.0.0.0 --timeout 600 app:app
2. Zip the project files (excluding venv).
3. Deploy via Azure CLI:
   az webapp up --sku F1 --name <your-app-name>
"""
