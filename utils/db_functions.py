import sqlite3
import pandas as pd
from datetime import date
import os

os.makedirs('data', exist_ok=True)
DB_PATH = 'data/database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Study Logs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, log_date TEXT, subject TEXT, study_hours REAL,
            sleep_hours REAL, attendance REAL, assignments REAL, consistency INTEGER,
            days_remaining INTEGER, previous_marks REAL, predicted_marks REAL
        )
    ''')
    
    # --- UPGRADE: Add new qualitative columns to study_logs dynamically ---
    new_log_columns = {
        'focus_score': 'INTEGER',
        'session_notes': 'TEXT'
    }
    
    for col_name, data_type in new_log_columns.items():
        try:
            c.execute(f'ALTER TABLE study_logs ADD COLUMN {col_name} {data_type}')
        except sqlite3.OperationalError:
            pass # Column already exists, move on
    
    # 2. Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    
    # 3. UPGRADE: Add new profile columns dynamically
    new_columns = {
        'recovery_word': 'TEXT',
        'full_name': 'TEXT',
        'institution': 'TEXT',
        'degree_major': 'TEXT',
        'current_semester': 'TEXT',
        'target_cgpa': 'REAL'
    }
    
    for col_name, data_type in new_columns.items():
        try:
            c.execute(f'ALTER TABLE users ADD COLUMN {col_name} {data_type}')
        except sqlite3.OperationalError:
            pass # Column already exists, move on
            
    conn.commit()
    conn.close()

# --- AUTHENTICATION & PROFILE FUNCTIONS ---
def register_user(username, password, recovery_word):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, recovery_word) VALUES (?, ?, ?)', (username, password, recovery_word))
        conn.commit()
        success = True
    except sqlite3.IntegrityError: 
        success = False
    conn.close()
    return success

def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def verify_recovery_word(username, recovery_word):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND LOWER(recovery_word)=LOWER(?)', (username, recovery_word))
    result = c.fetchone()
    conn.close()
    return result is not None

def reset_password(username, new_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET password=? WHERE username=?', (new_password, username))
    conn.commit()
    conn.close()

# --- GET AND UPDATE PROFILE DATA ---
def get_user_profile(username):
    """Fetches all profile data for a specific user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT full_name, institution, degree_major, current_semester, target_cgpa FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result

def update_user_profile(username, full_name, institution, degree_major, current_semester, target_cgpa):
    """Saves the user's academic profile to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE users 
        SET full_name=?, institution=?, degree_major=?, current_semester=?, target_cgpa=?
        WHERE username=?
    ''', (full_name, institution, degree_major, current_semester, target_cgpa, username))
    conn.commit()
    conn.close()

# --- STUDY LOG FUNCTIONS ---
def save_study_log(username, log_date, subject, study_hours, sleep_hours, attendance, assignments, consistency, days_remaining, prev_marks, predicted_marks, focus_score, session_notes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Updated to include focus_score and session_notes
    c.execute('''
        INSERT INTO study_logs 
        (username, log_date, subject, study_hours, sleep_hours, attendance, assignments, consistency, days_remaining, previous_marks, predicted_marks, focus_score, session_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, str(log_date), subject, study_hours, sleep_hours, attendance, assignments, consistency, days_remaining, prev_marks, predicted_marks, focus_score, session_notes))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM study_logs WHERE username=?", conn, params=(username,))
    conn.close()
    return df