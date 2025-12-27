import joblib
import os
import pandas as pd
from datetime import datetime, timedelta

# 1. AI SETUP
# Mapping must match what was used in train_model.py
LOC_MAP = {
    "main road": 0, "bic": 1, "mahendra chowk": 2, "traffic chowk": 3, "hospital road": 4, 
    "bargachi": 5, "airport mode": 6, "puspalal chowk": 7, "itahari road": 8, "college road": 9
}

MODEL_PATH = 'traffic_model.pkl'
ai_model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

# 2. SCORING UTILITY
def get_issue_score(issue):
    """Assigns numerical weight to different traffic issues."""
    scores = {
        "Clear": 2, 
        "Traffic Jam": -1, 
        "Waterlogging": -2, 
        "Accident": -3, 
        "Construction": -3
    }
    return scores.get(issue, 0)

# 3. DATA PROCESSING (The missing function causing your error)
def process_active_reports(rows):
    """Filters database rows for recent reports and calculates location scores."""
    active = {}
    now = datetime.now()
    for loc, issue, t in rows:
        try:
            t_obj = datetime.fromisoformat(t)
        except ValueError:
            continue
            
        # Only consider reports from the last 60 minutes
        if now - t_obj > timedelta(minutes=60): 
            continue 
        
        if loc not in active:
            active[loc] = {"score": 0, "issues": []}
            
        active[loc]["score"] += get_issue_score(issue)
        active[loc]["issues"].append(issue)
    return active

# 4. AI & RULE-BASED ANALYSIS
def analyze_risky_roads(user_mode, active_data):
    """Combines AI predictions and hard-coded rules to identify dangerous roads."""
    risky_roads = []
    now = datetime.now()

    for loc, info in active_data.items():
        primary_issue = info["issues"][-1] if info["issues"] else "Congestion"
        
        # --- AI PREDICTION LAYER ---
        if ai_model and loc in LOC_MAP:
            loc_code = LOC_MAP[loc]
            # Predict (1 = Risky, 0 = Clear)
            # Input features: Hour, Day of Week (0-6), Location Code
            prediction = ai_model.predict([[now.hour, now.weekday(), loc_code]])[0] 
            if prediction == 1:
                risky_roads.append((loc, f"AI Forecast: High Risk ({primary_issue})"))
                continue # If AI flags it, we don't need to check rules

        # --- RULE-BASED FALLBACK LAYER ---
        if user_mode == "🚑 Emergency (Ambulance)":
            if info["score"] < 1: 
                risky_roads.append((loc, primary_issue))
        elif user_mode == "🚛 Heavy Load Truck":
            if any(i in info["issues"] for i in ["Waterlogging", "Construction"]):
                risky_roads.append((loc, primary_issue))
        elif user_mode == "🚶 Pedestrian (Walking)":
            if "Waterlogging" in info["issues"]:
                risky_roads.append((loc, "Flood Risk"))
        else: 
            if info["score"] < -1: 
                risky_roads.append((loc, primary_issue))
            
    return risky_roads