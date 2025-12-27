from datetime import datetime, timedelta

def get_issue_score(issue):
    scores = {"Clear": 2, "Traffic Jam": -1, "Waterlogging": -2, "Accident": -3, "Construction": -3}
    return scores.get(issue, 0)

def process_active_reports(rows):
    active = {}
    now = datetime.now()
    for loc, issue, t in rows:
        t_obj = datetime.fromisoformat(t)
        if now - t_obj > timedelta(minutes=60): 
            continue 
        
        if loc not in active:
            active[loc] = {"score": 0, "issues": []}
        active[loc]["score"] += get_issue_score(issue)
        active[loc]["issues"].append(issue)
    return active

def analyze_risky_roads(user_mode, active_data):
    risky_roads = []
    for loc, info in active_data.items():
        primary_issue = info["issues"][-1] if info["issues"] else "Congestion"
        
        if user_mode == "🚑 Emergency (Ambulance)":
            if info["score"] < 1: risky_roads.append((loc, primary_issue))
        elif user_mode == "🚛 Heavy Load Truck":
            if any(i in info["issues"] for i in ["Waterlogging", "Construction"]):
                risky_roads.append((loc, primary_issue))
        elif user_mode == "🚶 Pedestrian (Walking)":
            if "Waterlogging" in info["issues"] and info["score"] < -3:
                risky_roads.append((loc, "Heavy Flooding"))
        else: # General Vehicle / Delivery
            if info["score"] < -1: risky_roads.append((loc, primary_issue))
            
    return risky_roads