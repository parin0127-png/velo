from openai import OpenAI
from dotenv import load_dotenv
from tools.email_sender import send_email
from tools.web_search import search
from tools.client_tracker import add_client, update_client_status
from tools.reminder_setter import add_reminder, create_reminder_table
from tools.pdf_generator import generate_pdf
from tools.file_reader import read_file
from tools.excel import generate_excel
from datetime import datetime, timedelta
import os

load_dotenv()

client = OpenAI(api_key = os.getenv("MISTRAL_API_KEY"),
            base_url = "https://api.mistral.ai/v1")
model = "mistral-large-latest"

SYSTEM_PROMPT = """
You are an executor agent for Velo, a business automation assistant.
You receive a list of steps and execute them one by one.

Reply in clean plain text only. No bullet symbols like *, **, no step labels.
Just write the final result as a short clear paragraph or numbered list like:
1. Result one
2. Result two

No markdown. No asterisks. No step1_result labels. Just clean readable text.
No extra text. Never ask questions. Just execute and report what was done.
"""

def executor(plan_result, entities, task_type , user_input):
    from tools.client_tracker import create_table
    create_table()
    tool_result = ""

    if task_type == "email":
        email = None
        for word in entities.split(","):
            word = word.strip()
            if "@" in word:
                email = word
        if email:

            email_response = client.chat.completions.create(
                model = model,
                messages = [
                    {"role" : "system" , "content" : "You are a professional business email writer. Write a short, professional email body only. No subject line. No extra text."},
                    {"role" : "user" , "content" : f"Write an email for this request: {user_input}"}
                ]
            )
            email_body = email_response.choices[0].message.content
            send_email(
                to = email,
                subject = "Follow Up - Velo",
                body = email_body
            )
            tool_result = f"Professional Email sent to {email}"
    
    elif task_type == "search":
        results = search(user_input)
        top = results[0] if results else {}
        tool_result = f"> Top results {top.get('title' , '')} - {top.get('url' , '')}"
        print(f"{tool_result}")
    
    elif task_type == "reminder":
        create_reminder_table()
        reminder_time = (datetime.now() + timedelta(hours = 1)).strftime("%Y-%m-%d %H:%M")
        add_reminder("Velo reminder" , user_input, reminder_time)
        tool_result = f"Reminder set for {reminder_time}"

    elif task_type == "client":
        name = entities.split(",")[0].strip() if entities else "Unknown"
        email = None
        for word in entities.split(","):
            if "@" in word:
                email = word.strip()
        
        if email:
            add_client(name , email , "active" , datetime.now().strftime("%Y-%m-%d"), user_input)
            tool_result = f"Client {name} added to tracker"

            email_response = client.chat.completions.create(
                model = model, 
                messages = [
                    {"role" : "system" , "content" : "You are a professional business email writer. Write a short, professional email body only. No subject line. No extra text. Sign off with 'Best regards, Velo Assistant' — never use placeholder text like [Your Name]."},
                    {"role" : "user" , "content" : f"Write an email for this request: {user_input}"}
                    ]
            )

            email_body = email_response.choices[0].message.content
            send_email(to = email, subject = "Follow up - Velo" , body = email_body)
            tool_result += f" and email sent to {email}"
        else:
            update_client_status(name, "Follow up")
            tool_result = f"Client {name} status updated"
    
    elif task_type == "report":
        generate_pdf("Velo Report" , user_input , "velo_report.pdf")
        tool_result = "Report generated as velo_report.pdf"
    
    elif task_type == "file":
        content = read_file(user_input.strip())
        tool_result = f"File read. First 100 chars: {content[:100]}"
    
    elif task_type == "excel":
        path = generate_excel()
        filename = os.path.basename(path)
        tool_result = f"Excel report ready. Download: /download/{filename}"

    elif task_type == "dashboard":
        from pipelines.output_stage import run as generate_output
        path = generate_output()
        filename = os.path.basename(path)
        tool_result = f"Dashboard ready. Download: /download/{filename}"

    user_message = f"Steps:\n{plan_result}\n\nEntities:\n{entities}\n\nTool result:\n{tool_result}"
    
    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role" : "system" , "content" : SYSTEM_PROMPT},
            {"role" : "user" , "content" : user_message}
        ]
    )
    result = response.choices[0].message.content
    tokens = {
        "input" : response.usage.prompt_tokens,
        "output" : response.usage.completion_tokens,
        "total" : response.usage.total_tokens
    }
    return result , tokens