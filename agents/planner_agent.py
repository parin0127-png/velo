from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = OpenAI(api_key = os.getenv("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1")

model = "mistral-small-latest"

SYSTEM_PROMPT = """
You are a planner agent for Velo, a business automation assistant.
You receive extracted intent, entities and task_type.
Your job is to break it into clear steps.

Reply in this exact format:
step1: <action>
step2: <action>
step3: <action>

Maximum 3 steps. No extra text. Keep each step short.
"""

def planner(intake_result):
    response = client.chat.completions.create(
        model = model, 
        messages = [
            {"role" : "system" , "content" : SYSTEM_PROMPT},
            {"role" : "user" , "content" : intake_result}
        ]
    )
    result = response.choices[0].message.content
    tokens = {
        "input" : response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
        "total": response.usage.prompt_tokens + response.usage.completion_tokens
    }
    return result , tokens