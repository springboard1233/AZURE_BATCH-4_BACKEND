def get_capacity_recommendation(forecast_demand, available_capacity, region="East US", service="Compute"):
    """
    Generates a capacity scaling recommendation based on forecast demand vs available capacity.
    
    Args:
        forecast_demand (float): The predicted demand (e.g., CPU usage or units).
        available_capacity (float): The current total capacity.
        region (str): The cloud region (e.g., "East US").
        service (str): The service type (e.g., "Compute", "Storage").
        
    Returns:
        dict: JSON-serializable dictionary with actionable recommendations.
    """
    
    # Ensure inputs are floats/ints
    forecast_demand = float(forecast_demand)
    available_capacity = float(available_capacity)
    
    diff = forecast_demand - available_capacity
    
    # Logic for recommendation text
    if diff > 0:
        # Demand exceeds capacity -> Scale UP
        # Calculate percentage increase needed
        pct_increase = (diff / available_capacity) * 100 if available_capacity > 0 else 100
        recommendation = f"Scale UP: {region} needs +{int(diff)} units (+{pct_increase:.1f}%) to meet demand."
        adjustment = f"+{int(diff)} units"
    elif diff < 0:
        # Surplus capacity -> Scale DOWN (or check if it's too much surplus)
        # Let's say if surplus is > 20% of capacity, we suggest scaling down.
        surplus = abs(diff)
        pct_surplus = (surplus / available_capacity) * 100 if available_capacity > 0 else 0
        
        if pct_surplus > 20:
            recommendation = f"Scale DOWN: {region} has excess capacity. Remove approx {int(surplus)} units."
            adjustment = f"-{int(surplus)} units"
        else:
            recommendation = "Stable: Capacity is sufficient with safe buffer."
            adjustment = "0 units"
    else:
        recommendation = "Stable: Demand matches capacity exactly."
        adjustment = "0 units"

    return {
        "region": region,
        "service": service,
        "forecast_demand": round(forecast_demand, 2),
        "available_capacity": round(available_capacity, 2),
        "recommended_adjustment": adjustment,
        "recommendation_text": recommendation # Adding a descriptive text field as well
    }
