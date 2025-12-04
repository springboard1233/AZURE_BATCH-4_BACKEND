# ⚙️ Azure Demand Forecasting & Capacity Optimization Backend

This is the Flask backend for the Azure Demand Forecasting & Capacity Optimization System. It provides endpoints for CPU usage prediction, capacity planning, and monitoring.

## 📂 Directory Structure

Ensure your directory looks like this:

```
AZURE_BATCH-4_BACKEND/
├── Data/
│   └── mlmodeltrainingdataset.csv  # Required for training/retraining
├── Models/
│   └── cpu_demand_model.pkl        # Pre-trained model
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Setup & Installation

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    ```bash
    python app.py
    ```
    The server will start at `http://localhost:5000`.

## 🔌 API Endpoints

-   **Predict CPU Usage:** `POST /api/predict_cpu`
-   **7-Day Forecast:** `GET /api/forecast_7`
-   **30-Day Forecast:** `GET /api/forecast_30`
-   **Capacity Planning:** `POST /api/capacity_planning`
-   **Monitoring:** `GET /api/monitoring`
-   **Retrain Model:** `POST /api/retrain`

## 📝 Notes

-   **`__pycache__`**: These files are ignored by git.
-   **`check_api.py`**: A script for local testing (ignored by git).
