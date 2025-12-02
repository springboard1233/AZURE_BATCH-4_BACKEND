import pandas as pd
import numpy as np

def prepare_recursive_features(last_row, steps, model, feature_columns):
    """
    Generates recursive forecasts for a specified number of steps.
    
    Args:
        last_row (pd.Series): The last known data point (with all features).
        steps (int): Number of days to forecast (e.g., 7 or 30).
        model: Trained machine learning model.
        feature_columns (list): Exact list of columns the model expects.
        
    Returns:
        list: List of forecasted values.
    """
    
    # We need to maintain a history to calculate rolling features
    # For simplicity in this stateless example, we will simulate the rolling window 
    # by assuming the 'last_row' contains the necessary current state and we update it.
    # In a production DB-backed system, we would query the last N days.
    
    # However, since we only have the 'last_row' passed in typically, 
    # we have to approximate or carry forward the rolling values 
    # OR strictly update the lags and re-calculate rolling if we had the history.
    
    # Given the constraints and the request for "Auto-generate lag + rolling features",
    # we will implement a logic that updates the LAGS based on previous predictions
    # and updates ROLLING means/stds using a sliding window approach.
    
    predictions = []
    
    # Initialize current_row
    current_row = last_row.copy()
    
    # We need a small buffer of history to calculate rolling stats dynamically.
    # Since we don't have the full history passed in, we will initialize a history buffer
    # using the lag features present in the last_row to approximate the immediate past.
    # This is a heuristic to make the recursive loop work without a database connection.
    
    # Reconstruct a pseudo-history from lags
    # usage_cpu_lag_1 is t-1
    # usage_cpu_lag_3 is t-3
    # ...
    # This is imperfect but allows us to proceed with the logic.
    
    # Let's track the predicted 'usage_cpu' to update lags.
    # We also need to update 'usage_storage' and 'users_active' if they are features.
    # For this milestone, we might assume other features stay constant or follow a simple trend,
    # OR we predict them too. The prompt implies we are forecasting CPU.
    # We will assume other dynamic features (storage, users) stay at their last known value 
    # or simple average for the sake of the CPU prediction demo, 
    # UNLESS we had models for them too. We will hold them constant for simplicity 
    # but update the CPU lags and rolling stats.
    
    # Initialize a history list for CPU usage to compute rolling stats
    # We'll seed it with the current rolling mean to start, or just the lags.
    cpu_history = [
        current_row.get('usage_cpu_lag_7', 0),
        current_row.get('usage_cpu_lag_3', 0), # approximate
        current_row.get('usage_cpu_lag_1', 0),
        current_row.get('usage_cpu', 0) # t=0
    ]
    
    # Ensure we have enough data for max rolling window (7)
    while len(cpu_history) < 7:
        cpu_history.insert(0, cpu_history[0]) 

    for _ in range(steps):
        # 1. Prepare input vector for the model
        # Ensure columns are in the exact order the model expects
        input_data = pd.DataFrame([current_row])
        
        # Handle missing columns if any (fill 0)
        for col in feature_columns:
            if col not in input_data.columns:
                input_data[col] = 0
                
        input_data = input_data[feature_columns]
        
        # 2. Predict
        pred = model.predict(input_data)[0]
        predictions.append(float(pred))
        
        # 3. Update features for next step (Recursive Logic)
        
        # Update Lags
        # lag_7 becomes what lag_6 was... but we only have specific lags.
        # We shift the history.
        
        # Add new prediction to history
        cpu_history.append(pred)
        # Keep only last 7+ needed
        if len(cpu_history) > 10: 
            cpu_history.pop(0)
            
        # Update Lag Columns in current_row
        # t is now t+1. 
        # lag_1 is the prediction we just made (t)
        # lag_3 is t-2
        # lag_7 is t-6
        
        current_row['usage_cpu_lag_1'] = cpu_history[-2] # The one we just predicted is at -1, so previous is -2? 
        # Wait, we appended pred. So pred is at [-1]. 
        # The value for the NEXT prediction (t+1):
        # lag_1 should be the value at t (which is pred)
        current_row['usage_cpu_lag_1'] = cpu_history[-1]
        
        # lag_3 (t-2) -> index -3
        current_row['usage_cpu_lag_3'] = cpu_history[-3] if len(cpu_history) >= 3 else 0
        
        # lag_7 (t-6) -> index -7
        current_row['usage_cpu_lag_7'] = cpu_history[-7] if len(cpu_history) >= 7 else 0
        
        # Update Rolling Features
        # mean_3: average of last 3
        current_row['usage_cpu_rolling_mean_3'] = np.mean(cpu_history[-3:])
        # mean_7: average of last 7
        current_row['usage_cpu_rolling_mean_7'] = np.mean(cpu_history[-7:])
        
        # std_3: std of last 3
        current_row['usage_cpu_rolling_std_3'] = np.std(cpu_history[-3:])
        # std_7: std of last 7
        current_row['usage_cpu_rolling_std_7'] = np.std(cpu_history[-7:])
        
        # Update date/time features if necessary (e.g. increment day)
        # Assuming 'day' or 'is_weekend' might change. 
        # For this snippet, we'll keep it simple as date logic can be complex without a real date object.
        
        # Update the main 'usage_cpu' for the row to the predicted value 
        # (though strictly 'usage_cpu' is the target, usually we don't feed target as input, 
        # but if the model uses it as a feature for some reason, we update it. 
        # Based on the feature list, 'usage_cpu' IS a feature? 
        # Usually target is NOT a feature. The feature list has 'usage_cpu'. 
        # If so, we update it.)
        if 'usage_cpu' in feature_columns:
            current_row['usage_cpu'] = pred
            
    return predictions
