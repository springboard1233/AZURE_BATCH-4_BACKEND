# /scripts/app.py
from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

# ==============================
# Load cleaned CSV
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
data_file = os.path.join(BASE_DIR, "data", "processed", "cleaned_merged.csv")

try:
    df = pd.read_csv(data_file)
    print("✅ Data loaded successfully!")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    df = pd.DataFrame()  # fallback empty DataFrame

# ==============================
# API Endpoints
# ==============================

@app.route('/api/usage-trends', methods=['GET'])
def get_usage_trends():
    """
    Return aggregated CPU usage by date and region
    """
    if 'date' in df.columns and 'usage_cpu' in df.columns and 'region' in df.columns:
        data = df.groupby(['date', 'region'])['usage_cpu'].sum().reset_index()
        return jsonify(data.to_dict(orient='records'))
    return jsonify({"error": "Columns 'date', 'region', or 'usage_cpu' not found"})


@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    """
    Return static forecast data (placeholder)
    """
    return jsonify([
        {"date": "2025-10-25", "predicted_usage": 120},
        {"date": "2025-10-26", "predicted_usage": 130}
    ])

@app.route('/api/top-regions', methods=['GET'])
def top_regions():
    """
    Return top 5 regions by count (replace 'region' with your actual column)
    """
    if 'region' in df.columns:
        top = df['region'].value_counts().head(5).to_dict()
        return jsonify(top)
    return jsonify({"error": "Column 'region' not found"})

@app.route('/api/raw-data', methods=['GET'])
def raw_data():
    """
    Return first 100 rows as JSON
    """
    return jsonify(df.head(100).to_dict(orient='records'))

# ==============================
# Run Server
# ==============================
if __name__ == '__main__':
    app.run(debug=True)
