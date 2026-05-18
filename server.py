from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uuid
import os
 
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "velo.db"
COOKIE_NAME = "velo_session"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_session_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id   TEXT PRIMARY KEY,
            groq_key     TEXT,
            mistral_key  TEXT,
            tavily_key   TEXT,
            gmail        TEXT,
            gmail_pass   TEXT,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

create_session_table()

def get_session(session_id : str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def save_session(session_id, groq_key, mistral_key, tavily_key, gmail, gmail_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_sessions 
        (session_id, groq_key, mistral_key, tavily_key, gmail, gmail_pass)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, groq_key, mistral_key, tavily_key, gmail, gmail_password)
    )
    conn.commit()
    conn.close()

def load_keys_to_env(row):
    os.environ["GROQ_API_KEY"]          = row[1]
    os.environ["MISTRAL_API_KEY"]       = row[2]
    os.environ["TAVILY_API_KEY"]        = row[3]
    os.environ["GMAIL"]                 = row[4]
    os.environ["GMAIL_APP_PASSWORD"]    = row[5]

class SetupPayload(BaseModel):
    groq_key : str
    mistral_key : str
    tavily_key : str
    gmail : str
    gmail_password : str

class ChatPayload(BaseModel):
    message : str


@app.get("/" , response_class = HTMLResponse)
def index(request : Request):
    session_id = request.cookies.get(COOKIE_NAME)

    if not session_id or not get_session(session_id):
        with open("ui/velo-setup.html" , "r" , encoding = "utf-8")as f:
            return HTMLResponse(f.read())
    

    with open("ui/velo-chat.html" , "r" , encoding = "utf-8")as f:
        return HTMLResponse(f.read())


@app.post("/setup")
def setup(payload : SetupPayload , response : Response):
    try:
        session_id = str(uuid.uuid4())

        save_session(
            session_id,
            payload.groq_key,
            payload.mistral_key,
            payload.tavily_key,
            payload.gmail,
            payload.gmail_password
        )

        response.set_cookie(
            key = COOKIE_NAME,
            value = session_id,
            max_age = 30 * 24 * 60 * 60,
            httponly = False,
            samesite = "lax"
        )

        from fastapi.responses import RedirectResponse
        redirect = RedirectResponse(url = "/" , status_code = 302)
        redirect.set_cookie(
            key = COOKIE_NAME,
            value = session_id,
            max_age = 30 * 24 * 60 * 60,
            httponly = False,
            samesite = "lax" 
        )
        return redirect
    except Exception as e:
        return JSONResponse({"status" : "error" , "message" : str(e)}, status_code = 500)
    

@app.post("/chat")
def chat(payload : ChatPayload , request : Request):
    try:
        session_id = request.cookies.get(COOKIE_NAME)

        if not session_id:
            return JSONResponse({"status" : "no_session"}, status_code = 401)
        
        row = get_session(session_id)
        if not row:
            return JSONResponse({"status" : "no_session"}, status_code = 401)
        
        load_keys_to_env(row)

        from pipelines.task_pipeline import run_task

        result = run_task(payload.message , session_id)

        clean = ""
        if result :
            for line in result.split("\n"):
                line = line.strip()
                if "step" in line and "_result" in line:
                    value = line.split(":" , 1)[-1].strip()
                    if value:
                        clean += value + "\n"
                else:
                    clean += line + "\n"
            clean = clean.strip()
            clean = clean.replace("**" , "")

        return JSONResponse({"status" : "ok" , "response" : clean or "Task completed."})
    except Exception as e:
        return JSONResponse({"status" : "error" , "message" : str(e)}, status_code = 500)