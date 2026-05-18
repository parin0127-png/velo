from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

client = Groq(api_key = os.getenv("GROQ_API_KEY"))

model = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
        You are an intake agent for Velo, a business automation assistant.
        Your job is to understand user input and extract only these 3 things:
        1. intent: what the user wants to do
        2. entities: important names, emails, dates mentioned
        3. task_type: one of [email, search, reminder, client, report, file, excel, dashboard]
            - use "excel" if user mentions excel, spreadsheet, xlsx
            - use "dashboard" if user mentions dashboard
            - use "report" only for PDF reports

        Reply in this exact format:
        intent: <intent>
        entities: <entities>
        task_type: <task_type>

        Keep it short. No extra text.
        """

def intake_agent(user_input):
    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role" : "system" , "content" : SYSTEM_PROMPT},
            {"role" : "user" , "content" : user_input}
        ]
    )
    result = response.choices[0].message.content
    tokens = { 
        "input" : response.usage.prompt_tokens,
        "output" : response.usage.completion_tokens,
        "total" : response.usage.total_tokens 
    }
    return result , tokens