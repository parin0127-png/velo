from dotenv import load_dotenv
from tavily import TavilyClient
import os

load_dotenv()

client = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))
def search(query):
    browser = client.search(query = query, max_results = 5)
    results = []
    for b in browser["results"]:
        results.append({
            "title" : b["title"],
            "url" : b["url"],
            "content" : b["content"]
        })
    
    return results