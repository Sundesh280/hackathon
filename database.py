import sqlite3
from datetime import datetime

DB_NAME = "traffic.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            issue TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_report(location, issue):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO reports (location, issue, time) VALUES (?, ?, ?)",
              (location.lower(), issue, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT location, issue, time FROM reports")
    data = c.fetchall()
    conn.close()
    return data