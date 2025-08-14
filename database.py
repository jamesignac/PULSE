import sqlite3
from typing import Optional, Dict
# Personalized Updates & Learning System for Experts (PULSE)
def init_db():
    conn = sqlite3.connect('healthcare_news.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE,
                  password TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  profession TEXT,
                  specialty TEXT,
                  preferences TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create user_sessions table for chat history
    c.execute('''CREATE TABLE IF NOT EXISTS user_sessions
                 (session_id TEXT PRIMARY KEY,
                  user_id INTEGER,
                  chat_history TEXT,
                  last_active TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

def add_user(email: str, hashed_password: str, profession: str, specialty: Optional[str] = None):
    conn = sqlite3.connect('healthcare_news.db')
    c = conn.cursor()
def add_user(email: str, hashed_password: str, first_name: str, last_name: str, profession: str, specialty: Optional[str] = None):
    conn = sqlite3.connect('healthcare_news.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password, first_name, last_name, profession, specialty) VALUES (?, ?, ?, ?, ?, ?)",
              (email, hashed_password, first_name, last_name, profession, specialty))
    conn.commit()
    conn.close()

def get_user(email: str) -> Optional[Dict]:
    conn = sqlite3.connect('healthcare_news.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0],
            'email': user[1],
            'password': user[2],
            'first_name': user[3],
            'last_name': user[4],
            'profession': user[5],
            'specialty': user[6]
        }
    return None