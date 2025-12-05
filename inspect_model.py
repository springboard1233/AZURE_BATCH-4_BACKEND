import joblib
import os
import numpy as np

MODEL_PATH = os.path.join('Models', 'cpu_demand_model.pkl')

try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
    
    if hasattr(model, 'feature_names_in_'):
        print("Feature names found in model:")
        features = list(model.feature_names_in_)
        print(features)
        with open("model_features.txt", "w") as f:
            f.write(str(features))
    else:
        print("Model does not have 'feature_names_in_' attribute.")
        
except Exception as e:
    print(f"Error loading model: {e}")
