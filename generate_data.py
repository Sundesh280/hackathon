import sqlite3
import random
from datetime import datetime, timedelta

# Settings
LOCATIONS = ["main road", "bic", "mahendra chowk", "traffic chowk", "hospital road", 
             "bargachi", "airport mode", "puspalal chowk", "itahari road", "college road"]
ISSUES = ["Traffic Jam", "Accident", "Waterlogging", "Construction", "Clear"]

def generate_fake_data(num_records=150):
    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()
    
    now = datetime.now()
    
    for i in range(num_records):
        loc = random.choice(LOCATIONS)
        issue = random.choices(ISSUES, weights=[30, 10, 10, 10, 40])[0] # Mostly Clear or Jams
        
        # Random time within the last 24 hours
        random_minutes = random.randint(0, 1440)
        report_time = (now - timedelta(minutes=random_minutes)).isoformat()
        
        c.execute("INSERT INTO reports (location, issue, time) VALUES (?, ?, ?)",
                  (loc, issue, report_time))
    
    conn.commit()
    conn.close()
    print(f"Successfully added {num_records} fake reports to traffic.db!")

if __name__ == "__main__":
    generate_fake_data()