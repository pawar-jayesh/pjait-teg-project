import os
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def tavily_search(query: str, search_depth: str = "basic"):
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY not found in .env"}

    response = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
        json={"query": query, "search_depth": search_depth}
    )

    if response.status_code != 200:
        return {"error": f"Tavily API error {response.status_code}", "details": response.text}

    return response.json().get("results", [])
