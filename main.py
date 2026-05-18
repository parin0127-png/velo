from dotenv import load_dotenv, set_key
import os

ENV_FILE = ".env"

def setup(): 
    print("[]==========================================[]")
    print("||  Welcome to Velo - AI Business Assistant ||")
    print("[]==========================================[]")
    print("First time setup. Please enter your API keys.\n")

    groq = input("> Groq api key : ").strip()
    mistral = input("> Mistral api key : ").strip()
    tavily = input("> Tavily api key : ").strip()
    gmail = input("> Enter your Gmail : ").strip()
    gmail_password = input("> Enter Gmail App Password : ").strip()

    set_key(ENV_FILE , "GROQ_API_KEY" , groq)
    set_key(ENV_FILE , "MISTRAL_API_KEY" , mistral)
    set_key(ENV_FILE , "TAVILY_API_KEY" , tavily)
    set_key(ENV_FILE , "GMAIL" , gmail)
    set_key(ENV_FILE , "GMAIL_APP_PASSWORD" , gmail_password)

    print("\n > Setup complete. Starting Velo...\n")


def is_setup_done():
    load_dotenv()
    return all([
        os.getenv("GROQ_API_KEY"),
        os.getenv("MISTRAL_API_KEY"),
        os.getenv("TAVILY_API_KEY"),
        os.getenv("GMAIL"),
        os.getenv("GMAIL_APP_PASSWORD")
    ])


def chat_loop():
    from pipelines.task_pipeline import run_task
    print("Velo is ready. Type your task below.")
    print("Type 'exit' to quit.\n")

    session_id = "session_1"

    while True:
        user_input = input("> YOU : ").strip()

        if user_input.lower() == "exit":
            print("> Goodbye ")
            break
            
        if not user_input:
            continue
    
        run_task(user_input, session_id)

def main():
    if not is_setup_done():
        setup()
    else:
        load_dotenv()
    
    chat_loop()


if __name__ == "__main__":
    main()