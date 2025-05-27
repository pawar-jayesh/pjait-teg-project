import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))
mcp_server = os.getenv("MCP_URL")

OPENAI_FUNCTIONS = [
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
    },
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
    }
]

def chat_with_tools(user_message):
    print(f"> User: {user_message}")

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that can use external tools via MCP."},
            {"role": "user", "content": user_message}
        ],
        functions=OPENAI_FUNCTIONS,
        function_call="auto"
    )

    msg = resp.choices[0].message

    if msg.function_call:
        fn_name = msg.function_call.name
        fn_args = json.loads(msg.function_call.arguments)
        print(f"> Tool requested: {fn_name} with {fn_args}")

        mcp_response = requests.post(mcp_server, json={
            "jsonrpc": "2.0",
            "method": "callTool",
            "params": {
                "tool": fn_name,
                "args": fn_args
            },
            "id": 1
        }).json()

        tool_result = mcp_response.get("result", {})
        print(f"> Tool result: {tool_result}")

        followup = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that can use external tools via MCP."},
                {"role": "user", "content": user_message},
                {
                    "role": "assistant",
                    "function_call": {
                        "name": fn_name,
                        "arguments": msg.function_call.arguments
                    }
                },
                {
                    "role": "function",
                    "name": fn_name,
                    "content": json.dumps(tool_result)
                }
            ]
        )
        print("> Final answer:")
        print(followup.choices[0].message.content)
        return followup.choices[0].message.content

    else:
        print("> Model reply (no tool call):")
        print(msg.content)
        return msg.content

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(chat_with_tools("What's a cucumber?"))
