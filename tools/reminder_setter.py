from dotenv import load_dotenv
from tools.email_sender import send_email
from datetime import datetime
import sqlite3
import threading
import time
import os

DB_PATH = "velo.db"
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_reminder_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            message TEXT,
            remind_at TEXT,
            is_sent INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_reminder(title, message , remind_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reminders (title, message, remind_at)
        VALUES (?, ?, ?)
    """, (title, message, remind_at))
    conn.commit()
    conn.close()
    print(f"> Reminder set for {remind_at}")

def check_reminders():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, message FROM reminders
            WHERE remind_at = ? AND is_sent = 0
        """, (now,))
        rows = cursor.fetchall()
        for row in rows:
            id, title , message = row
            send_email(
                to = os.getenv("GMAIL"),
                subject = "Velo Reminder: {title}",
                body = message
            )
            cursor.execute("UPDATE reminders SET is_sent = 1 WHERE id = ?", (id,))
            print(f"> Reminder sent : {title}")
        conn.commit()
        conn.close()

def start_reminder_checker():
    thread = threading.Thread(target = check_reminders, daemon = True)
    thread.start()