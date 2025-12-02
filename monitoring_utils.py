"""
Monitoring and Model Drift Detection Utilities
Milestone 4 - Backend Team

This module provides model health monitoring and drift detection capabilities
based on performance metrics like MAPE (Mean Absolute Percentage Error).
"""

import numpy as np


def monitoring_stats(mape, threshold=10.0):
    """
    Analyze model performance and detect drift based on MAPE.
    
    Decision Logic:
    - If MAPE <= threshold (default 10%) → Model is stable
    - If MAPE > threshold → Drift detected, retraining required
    
    Args:
        mape (float): Mean Absolute Percentage Error of the model
        threshold (float): MAPE threshold for drift detection (default: 10.0%)
    
    Returns:
        dict: Monitoring status and recommendation
            {
                "mape": float,
                "threshold": float,
                "status": str,  # "stable" or "drift_detected"
                "message": str,
                "recommendation": str
            }
    """
    
    # Determine model status
    if mape <= threshold:
        status = "stable"
        message = "✅ Model Stable"
        recommendation = "No action required. Model performance is within acceptable range."
    else:
        status = "drift_detected"
        message = "⚠️ Drift Detected — Retraining Required"
        recommendation = f"Model MAPE ({mape:.2f}%) exceeds threshold ({threshold}%). Consider retraining with recent data."
    
    return {
        "mape": round(float(mape), 2),
        "threshold": float(threshold),
        "status": status,
        "message": message,
        "recommendation": recommendation
    }


def calculate_mape(actual_values, predicted_values):
    """
    Calculate Mean Absolute Percentage Error (MAPE).
    
    Args:
        actual_values (list/array): Actual observed values
        predicted_values (list/array): Model predicted values
    
    Returns:
        float: MAPE percentage
    """
    
    actual = np.array(actual_values)
    predicted = np.array(predicted_values)
    
    # Avoid division by zero
    mask = actual != 0
    
    if not np.any(mask):
        return 0.0
    
    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
    
    return float(mape)


def comprehensive_model_health(mape, mae=None, rmse=None, r2_score=None):
    """
    Generate comprehensive model health report with multiple metrics.
    
    Args:
        mape (float): Mean Absolute Percentage Error
        mae (float, optional): Mean Absolute Error
        rmse (float, optional): Root Mean Squared Error
        r2_score (float, optional): R-squared score
    
    Returns:
        dict: Comprehensive health report
    """
    
    # Get drift status
    drift_analysis = monitoring_stats(mape)
    
    # Build comprehensive report
    health_report = {
        "drift_status": drift_analysis,
        "performance_metrics": {
            "mape": round(float(mape), 2),
        }
    }
    
    # Add optional metrics if provided
    if mae is not None:
        health_report["performance_metrics"]["mae"] = round(float(mae), 2)
    
    if rmse is not None:
        health_report["performance_metrics"]["rmse"] = round(float(rmse), 2)
    
    if r2_score is not None:
        health_report["performance_metrics"]["r2_score"] = round(float(r2_score), 4)
    
    # Overall health assessment
    if mape <= 5:
        health_grade = "Excellent"
    elif mape <= 10:
        health_grade = "Good"
    elif mape <= 15:
        health_grade = "Fair"
    else:
        health_grade = "Poor"
    
    health_report["overall_health"] = health_grade
    
    return health_report


def detect_data_drift(recent_data, historical_stats, threshold=0.2):
    """
    Detect data drift by comparing recent data statistics with historical baseline.
    
    Args:
        recent_data (array-like): Recent data samples
        historical_stats (dict): Historical statistics {"mean": float, "std": float}
        threshold (float): Relative change threshold for drift detection (default: 20%)
    
    Returns:
        dict: Data drift analysis
    """
    
    recent_array = np.array(recent_data)
    recent_mean = np.mean(recent_array)
    recent_std = np.std(recent_array)
    
    historical_mean = historical_stats.get("mean", recent_mean)
    historical_std = historical_stats.get("std", recent_std)
    
    # Calculate relative changes
    mean_change = abs(recent_mean - historical_mean) / (historical_mean + 1e-6)
    std_change = abs(recent_std - historical_std) / (historical_std + 1e-6)
    
    # Detect drift
    mean_drift = mean_change > threshold
    std_drift = std_change > threshold
    
    drift_detected = mean_drift or std_drift
    
    return {
        "drift_detected": drift_detected,
        "mean_drift": mean_drift,
        "std_drift": std_drift,
        "recent_mean": round(float(recent_mean), 2),
        "historical_mean": round(float(historical_mean), 2),
        "mean_change_percentage": round(float(mean_change * 100), 2),
        "recent_std": round(float(recent_std), 2),
        "historical_std": round(float(historical_std), 2),
        "std_change_percentage": round(float(std_change * 100), 2),
        "message": "⚠️ Data drift detected" if drift_detected else "✅ No data drift detected"
    }
