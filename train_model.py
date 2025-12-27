import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load data from your existing database
conn = sqlite3.connect("traffic.db")
df = pd.read_sql_query("SELECT * FROM reports", conn)
conn.close()

if len(df) < 5:
    print("Not enough data to train! Add more reports in the app first.")
else:
    # 2. Preprocess: Convert time to Hour and Day
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    df['day'] = df['time'].dt.weekday
    
    # Simple encoding for locations and issues
    df['loc_code'] = df['location'].astype('category').cat.codes
    # Target: 1 if issue is serious, 0 if clear
    df['is_risky'] = df['issue'].apply(lambda x: 1 if x != "Clear" else 0)

    # 3. Train the Model
    X = df[['hour', 'day', 'loc_code']]
    y = df['is_risky']
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    # 4. Save the "AI Brain"
    joblib.dump(model, 'traffic_model.pkl')
    print("AI Model Trained and Saved as traffic_model.pkl!")