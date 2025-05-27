from jsonrpcserver import method, serve, Success, Error
from tools.t_wikipedia import search_wikipedia
from tools.t_tavily import tavily_search
from tools.t_weather import get_weather
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

@method
def listTools():
    return Success([
        {
            "name": "search_wikipedia",
            "description": "Search Wikipedia and return top-k results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 3}
                },
                "required": ["query"]
            }
        },
        {
            "name": "tavily_search",
            "description": "Search the web using Tavily API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "search_depth": {"type": "string", "default": "basic"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "units": {"type": "string", "default": "metric"}
                },
                "required": ["city"]
            }
        }
        
    ])


@method
def callTool(tool: str, args: dict):
    if tool == "search_wikipedia":
        return Success(search_wikipedia(args['query']))
    if tool == "tavily_search":
        print(f"Searching Tavily for {args['query']}")
        return Success(tavily_search(args['query']))
    if tool == "get_weather":
        return Success(get_weather(args['city']))
    return Error(1, f"Unknown tool: {tool}")



if __name__ == "__main__":
    print("MCP server running on http://localhost:5000")
    serve(port=5000)
