from groq import Groq
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

model = "openai/gpt-oss-20b"

DB_PATH = "velo.db"

SYSTEM_PROMPT = """
You are a memory agent for Velo, a business automation assistant.
You receive a conversation and compact it into 3 lines.
Keep only the most important parts.
No extra text. No bullets. Just 3 short lines.
"""

def compact_memory(conversation):
    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role" : "system" , "content" : SYSTEM_PROMPT},
            {"role" : "user" , "content" : conversation}
        ]
    )
    return response.choices[0].message.content
    


def save_memory(session_id, summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT INTO memory (session_id, summary) VALUES (?, ?)", 
                   (session_id, summary))
    
    conn.commit()
    conn.close()

def get_memory(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM memory WHERE session_id = ? ORDER BY created_at DESC LIMIT 3", 
                   (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return " ".join([r[0] for r in rows])