import sqlite3

DB_PATH = "velo.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            task_type TEXT,
            result TEXT,
            status TEXT DEFAULT 'completed',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("> Tables created")

def save_task(user_input , task_type, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (user_input, task_type, result)
        VALUES (?, ?, ?)
    """, (user_input, task_type, result))

    conn.commit()
    conn.close()
