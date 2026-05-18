from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()
client = OpenAI(api_key = os.getenv("MISTRAL_API_KEY"),
                base_url = "https://api.mistral.ai/v1")

model = "mistral-small-latest"

DB_PATH = "velo.db"

SYSTEM_PROMPT =  """
You are a critic agent for Velo, a business automation assistant.
You receive what the user wanted and what the executor did.
Your job is to find what went wrong and what can be improved.

Reply in this exact format:
what_went_wrong: <one line>
improvement: <one line>
lesson: <one line>

If everything went well say "none" for what_went_wrong.
No extra text.
"""

def critic(user_input, execution_result):
    message = f"User wanted:\n{user_input}\n\nWhat executor did:\n{execution_result}"

    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role" : "system" , "content" : SYSTEM_PROMPT},
            {"role" : "user" , "content" : message}
        ]
    )
    result = response.choices[0].message.content
    tokens = {
        "input": response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
        "total": response.usage.prompt_tokens + response.usage.completion_tokens
    }
    return result, tokens

def save_lesson(lesson):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT INTO lessons (lesson) VALUES (?)", (lesson,))
    conn.commit()
    conn.close()

def get_lesson():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("SELECT lesson FROM lessons ORDER BY created_at DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return "\n".join([r[0] for r in rows])