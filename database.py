import sqlite3
import json
import os
from datetime import datetime
import pandas as pd
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_history.db")
def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    """Initializes the database schema if it doesn't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                classified_type TEXT NOT NULL,
                ocr_text TEXT NOT NULL,
                extracted_metadata TEXT NOT NULL,
                processing_time REAL NOT NULL,
                char_count INTEGER NOT NULL
            )
        """)
        conn.commit()
def save_scan(filename, file_type, classified_type, ocr_text, extracted_metadata, processing_time, char_count):
    """
    Saves a scan record to the database.
    extracted_metadata should be a dictionary. It will be serialized to JSON.
    """
    init_db()  # Ensure table exists
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata_json = json.dumps(extracted_metadata)
    
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO scans (timestamp, filename, file_type, classified_type, ocr_text, extracted_metadata, processing_time, char_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, filename, file_type, classified_type, ocr_text, metadata_json, processing_time, char_count))
        conn.commit()
def get_all_scans():
    """Retrieves all scan records as a pandas DataFrame."""
    init_db()
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM scans ORDER BY id DESC", conn)
    
    # Parse metadata column from JSON strings to Python dicts (if needed, but pandas reads as strings)
    # The application can deserialize metadata values on-the-fly where needed.
    return df
def delete_scan(scan_id):
    """Deletes a specific scan record by ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        conn.commit()
def clear_history():
    """Clears all scan history from the database."""
    with get_connection() as conn:
        conn.execute("DELETE FROM scans")
        conn.commit()
