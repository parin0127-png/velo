import sqlite3
import os

DB_PATH = "velo.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            status TEXT,
            last_contact TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()

def add_client(name, email, status, last_contact, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (name, email, status, last_contact, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, status, last_contact, notes))
    conn.commit()
    conn.close()

def get_all_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_client_status(status, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clients SET status = ? WHERE name = ?
    """, (status, name))
    conn.commit()
    conn.close()
    