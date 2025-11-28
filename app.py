from flask import Flask, jsonify
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# ---------------------------------------------------
# 1) LOAD MODELS
# ---------------------------------------------------
cpu_model = joblib.load("models/cpu_demand_model.pkl")
storage_model = joblib.load("models/storage_demand_model.pkl")

# ---------------------------------------------------
# 2) LOAD ML-READY DATASET (last N days)
# ---------------------------------------------------
df = pd.read_csv("data/processed/mlmodeltrainingdataset.csv")


# ---------------------------------------------------
# 3) RECURSIVE FORECASTING FUNCTION
# ---------------------------------------------------
def recursive_forecast(df, model, target_col, n_days=30):
    """
    Recursive ML forecasting with automatic updates for:
    - lag features (1, 3, 7)
    - rolling features (mean, std)
    - derived features (ratios)
    - date-related features (month, year, weekend)
    """

    df = df.copy()

    feature_cols = model.feature_names_in_

    # We need last 7 records for lag7 & rolling7
    history = df.tail(7).copy()
    predictions = []

    for day in range(n_days):

        last = history.iloc[-1].copy()  # last known day

        # -------------------------------------------------------
        # 1) UPDATE DATE FEATURES
        # -------------------------------------------------------
        if "month" in last:
            last["month"] = (last["month"] % 12) + 1

        if "year" in last:
            if last["month"] == 1:
                last["year"] += 1

        if "is_weekend" in last:
            last["is_weekend"] = 1 - last["is_weekend"]

        # -------------------------------------------------------
        # 2) LAG FEATURES (1, 3, 7)
        # -------------------------------------------------------
        # lag-1
        if "usage_cpu_lag_1" in last:
            last["usage_cpu_lag_1"] = history["usage_cpu"].iloc[-1]

        if "usage_storage_lag_1" in last:
            last["usage_storage_lag_1"] = history["usage_storage"].iloc[-1]

        if "users_active_lag_1" in last:
            last["users_active_lag_1"] = history["users_active"].iloc[-1]

        # lag-3
        if len(history) >= 3:
            if "usage_cpu_lag_3" in last:
                last["usage_cpu_lag_3"] = history["usage_cpu"].iloc[-3]
            if "usage_storage_lag_3" in last:
                last["usage_storage_lag_3"] = history["usage_storage"].iloc[-3]
            if "users_active_lag_3" in last:
                last["users_active_lag_3"] = history["users_active"].iloc[-3]

        # lag-7
        if len(history) >= 7:
            if "usage_cpu_lag_7" in last:
                last["usage_cpu_lag_7"] = history["usage_cpu"].iloc[-7]
            if "usage_storage_lag_7" in last:
                last["usage_storage_lag_7"] = history["usage_storage"].iloc[-7]
            if "users_active_lag_7" in last:
                last["users_active_lag_7"] = history["users_active"].iloc[-7]

        # -------------------------------------------------------
        # 3) ROLLING MEAN & STD (3-day, 7-day)
        # -------------------------------------------------------
        for col in ["usage_cpu", "usage_storage", "users_active"]:
            last3 = history[col].tail(3)
            last7 = history[col].tail(7)

            if f"{col}_rolling_mean_3" in last:
                last[f"{col}_rolling_mean_3"] = last3.mean()

            if f"{col}_rolling_mean_7" in last:
                last[f"{col}_rolling_mean_7"] = last7.mean()

            if f"{col}_rolling_std_3" in last:
                last[f"{col}_rolling_std_3"] = last3.std()

            if f"{col}_rolling_std_7" in last:
                last[f"{col}_rolling_std_7"] = last7.std()

        # -------------------------------------------------------
        # 4) DERIVED FEATURES
        # -------------------------------------------------------
        # Prevent divide-by-zero using +1e-6
        if "cpu_per_user" in last:
            last["cpu_per_user"] = last["usage_cpu_lag_1"] / (last["users_active_lag_1"] + 1e-6)

        if "storage_per_user" in last:
            last["storage_per_user"] = last["usage_storage_lag_1"] / (last["users_active_lag_1"] + 1e-6)

        if "cpu_storage_ratio" in last:
            last["cpu_storage_ratio"] = last["usage_cpu_lag_1"] / (last["usage_storage_lag_1"] + 1e-6)

        if "econ_demand_ratio" in last:
            last["econ_demand_ratio"] = last["economic_index"] / (last["cloud_market_demand"] + 1e-6)

        if "system_stress" in last:
            last["system_stress"] = (
                last["usage_cpu_lag_1"]
                + last["usage_storage_lag_1"]
                + last["users_active_lag_1"]
            )

        # -------------------------------------------------------
        # 5) PREDICT USING MODEL
        # -------------------------------------------------------
        row = last.reindex(feature_cols).values.reshape(1, -1)
        pred = model.predict(row)[0]
        predictions.append(float(pred))  # convert to python float

        # -------------------------------------------------------
        # 6) FEED PREDICTION BACK INTO SERIES
        # -------------------------------------------------------
        if target_col == "cpu":
            last["usage_cpu"] = pred
        else:
            last["usage_storage"] = pred

        history = pd.concat([history, pd.DataFrame([last])], ignore_index=True)

    return predictions


# ---------------------------------------------------
# 4) API ROUTES
# ---------------------------------------------------
@app.route("/")
def home():
    return jsonify({"message": "Azure Demand Forecasting API is running!"})


@app.route("/api/metrics", methods=["GET"])
def metrics():
    return jsonify({
        "CPU_Model": {"status": "loaded"},
        "Storage_Model": {"status": "loaded"}
    })


@app.route("/api/forecast/<service>", methods=["GET"])
def forecast(service):

    service = service.lower()

    if service == "cpu":
        model = cpu_model
        target_col = "cpu"
    elif service == "storage":
        model = storage_model
        target_col = "storage"
    else:
        return jsonify({"error": "Invalid service"}), 400

    preds = recursive_forecast(df, model, target_col, n_days=30)

    return jsonify({
        "service": service,
        "forecast_days": 30,
        "predictions": preds
    })


# ---------------------------------------------------
# 5) RUN SERVER
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

