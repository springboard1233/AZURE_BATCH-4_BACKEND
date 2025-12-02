from datetime import datetime, timedelta

# Mock last training date (e.g., 25 days ago)
# In a real system, this would be stored in a file or DB
LAST_TRAIN_DATE = datetime.now() - timedelta(days=25)

def trigger_retraining():
    """
    Simulates the retraining pipeline.
    """
    print("🔄 RETRAINING TRIGGERED: Starting automated model retraining pipeline...")
    # Logic to call training script would go here
    # e.g., subprocess.run(["python", "train_model.py"])
    return True

def monitoring_stats(mape, last_train_date=None):
    """
    Evaluates model health based on MAPE and Data Age.
    
    Thresholds:
    - MAPE > 10% -> Drift Detected
    - Data Age > 30 Days -> Stale Model
    
    If either is true, triggers retraining.
    """
    if last_train_date is None:
        last_train_date = LAST_TRAIN_DATE
        
    status = "Model Stable"
    drift_detected = False
    retrain_triggered = False
    
    # Check Drift
    if mape > 10:
        status = "⚠ Drift Detected (High Error)"
        drift_detected = True
        
    # Check Age
    days_since_train = (datetime.now() - last_train_date).days
    if days_since_train > 30:
        status = "⚠ Model Stale (Data > 30 days old)"
        drift_detected = True # Treat age as a form of drift/staleness
        
    # Trigger Retraining if needed
    if drift_detected:
        retrain_triggered = trigger_retraining()
        status += " — Retraining Started"
        
    return {
        "accuracy_mape": float(mape),
        "days_since_retrain": days_since_train,
        "status": status,
        "drift_detected": drift_detected,
        "retrain_triggered": retrain_triggered
    }
