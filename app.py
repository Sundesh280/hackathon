import streamlit as st
from streamlit_autorefresh import st_autorefresh
import database as db
import logic

# ---------------- Configuration ----------------
st.set_page_config(page_title="Smart Traffic System", layout="wide")
db.init_db()

# Auto-refresh every 30 seconds
st_autorefresh(interval=30 * 1000, key="datarefresh")

LOCATIONS = [
    "main road", "bic", "mahendra chowk", "traffic chowk", "hospital road", 
    "bargachi", "airport mode", "puspalal chowk", "itahari road", "college road"
]

st.title("🚦Crowd-Based Traffic Management System")

# ---------------- Sidebar: User & Reporting ----------------
st.sidebar.header("👤 BIC")
user_mode = st.sidebar.selectbox(
    "Select travel mode:",
    ["General Vehicle", "🚑 Emergency (Ambulance)", "📦 Delivery / Courier", "🚶 Pedestrian (Walking)", "🚛 Heavy Load Truck"]
)

st.sidebar.divider()
st.sidebar.header("📢 Report Traffic Issue")

with st.sidebar.form("report_form", clear_on_submit=True):
    loc_in = st.selectbox("📍 Road / Area Name", LOCATIONS)
    issue_in = st.selectbox(
        "⚠ Issue Type",
        ["Traffic Jam", "Accident", "Waterlogging", "Construction", "Clear"]
    )
    submit = st.form_submit_button("Submit Report")
    
    if submit:
        db.add_report(loc_in, issue_in)
        st.sidebar.success(f"Reported {issue_in} at {loc_in.title()}")

# --- Admin Section in Sidebar ---
st.sidebar.divider()
if st.sidebar.button("🗑 Clear All Reports (Admin Mode)"):
    import sqlite3
    conn = sqlite3.connect("traffic.db")
    conn.execute("DELETE FROM reports")
    conn.commit()
    conn.close()
    st.sidebar.warning("Database Cleared!")
    st.rerun()

# ---------------- Main Logic: Analysis ----------------
st.subheader(f"🧭 Smart Route Advice for: {user_mode}")

# 1. Fetch data from DB and process through logic.py
raw_reports = db.get_all_reports()
active_status = logic.process_active_reports(raw_reports)

# 2. Input Form
with st.form("route_form"):
    col1, col2 = st.columns(2)
    source = col1.selectbox("🚩 From (Current Location)", LOCATIONS, index=1) # Default to BIC
    destination = col2.selectbox("🏁 To (Destination)", LOCATIONS, index=2)
    check = st.form_submit_button("Analyze Best Path")

# 3. Display Results
if check:
    if source == destination:
        st.info("📍 You are already at your destination!")
    else:
        # Get risky roads based on persona logic in logic.py
        risky_roads = logic.analyze_risky_roads(user_mode, active_status)
        
        if risky_roads:
            st.warning(f"Analysis complete for {user_mode}:")
            for rd, reason in risky_roads:
                st.error(f"❌ **{rd.title()}**: Avoid due to {reason}")
            
            st.divider()
            st.info("💡 **Safe Alternative Suggestion:**")
            
            # Logic to find safe detours (excluding source, destination, and risky roads)
            risky_names = [r[0].lower() for r in risky_roads]
            safe_roads = [
                loc.title() for loc in LOCATIONS 
                if loc.lower() not in risky_names 
                and loc.lower() != source.lower() 
                and loc.lower() != destination.lower()
            ]
            
            if safe_roads:
                st.write(f"Try taking a detour via: **{', '.join(safe_roads[:3])}**")
            else:
                st.write("No alternate safe roads found. Please wait for traffic to clear.")
        else:
            st.success(f"✅ Route from **{source.title()}** to **{destination.title()}** looks optimal!")