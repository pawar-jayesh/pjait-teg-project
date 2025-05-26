import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from flask import Flask, request, jsonify
import requests

load_dotenv()

open_api_key = os.environ['OPEN_AI_KEY']

def custom_decider(query):
    query = query.lower()

    # Check for keywords in the query to decide the service
    if check_if_db(query=query):
        return "db"
    elif check_if_mcp(query=query):
        return "mcp"
    elif check_if_cp(query=query):
        return "cp"
    else:
        return "undecided"

def check_if_db(query) -> bool:
    if "db" in query or "database" in query:
        return True
    
    team_keywords = ["hr", "it", "devops", "finance"]
    found_team_keywords = [keyword for keyword in team_keywords if keyword in query]

    if (found_team_keywords and "team" in query) or (found_team_keywords and "teams" in query):
        return True

    leave_keywords = ["leave", "leaves"]
    found_leave_keywords = [keyword for keyword in leave_keywords if keyword in query]

    leave_status_keywords = ["utilized", "utilised", "left", "pending", "remaining", "total", "all"]
    found_leave_status_keywords = [keyword for keyword in leave_status_keywords if keyword in query]

    if (found_leave_keywords and found_leave_status_keywords) or found_leave_keywords:
        return True

    office_keywords = ["office", "location", "locations", "offices"]
    found_office_keywords = [keyword for keyword in office_keywords if keyword in query]

    if ("in" in query or "at" in query) and found_office_keywords:
        return True
    
    return False


def check_if_mcp(query) -> bool:

    keywords = ["weather", "distance", "wiki", "wikipedia"]
    found_keywords = [keyword for keyword in keywords if keyword in query]

    wether_keywords = ["cold", "hot", "humid", "snow", "snowing", "rain", "raining", "sunny", "autumn"]
    found_wether_keywords = [keyword for keyword in wether_keywords if keyword in query]

    distance_keywords = ["kms", "miles", "kilometers", "transport", "metro", "bus"]
    found_distance_keywords = [keyword for keyword in distance_keywords if keyword in query]

    if found_keywords or found_wether_keywords or found_distance_keywords:
        return True
    
    return False


def check_if_cp(query):

    keywords = ["policy", "rule", "regulations", "events", "bonus"]
    found_keywords = [keyword for keyword in keywords if keyword in query]

    if found_keywords:
        return True
    
    if "code" in query and "of" in query and "conduct" in query:
        return True
    
    if "code" in query and "dress" in query:
        return True

    if ("work" in query and "from" in query and "home" in query) or "wfh" in query:
        return True

    if "company" in query and ("holiday" in query or "holidays" in query):
        return True

    return False


def agent_decider(query):

    chat = ChatOpenAI(
        model="gpt-4o-mini",        # Model to be chosen, example gpt-4o or gpt-3.5-turbo
        api_key = open_api_key,
        # temperature=0.9,            # 0-1: the higher the more creative model
        # max_tokens=150,           # 1-n: Limit response length
        # top_p=1.0,                # 0-1: Alternative randomness control (nucleus sampling)
        # frequency_penalty=0.0,    # 0-1: Reduce repetitive text, the lower the least repetitive it is
        # presence_penalty=0.0,     # 0-1: Encourage new topics, the lower the more new topics
    )

    messages = []
    system_context = """You are a helpful assistant for a corporation, who is response for classification.Classify the following query and provide the service to call (DB Service, Company Policy Service, or MCP Service) reply with 'db' for DB Service, 'cp' for Company Policy and 'mcp' for MCP service. if you are not sure reply 'unrelated'. Make sure you reply with one word only.

    DB Service contains User, Team, Leaves, Office Location tables.
    Company Policy Service has data related to the company like code of conduct, dress code, company policy, company events, company holidays and so on.
    MCP Service has following tools web searching, wikipidea searching and weather forecast.
    If you think, the user question is not related to the following tools eg: 'sup', 'what are you doing?' and so on reply 'unrelated'
    """
    
        
    if system_context:
        messages.append(SystemMessage(content = system_context))
    
    messages.append(HumanMessage(content = query))
    
    response = chat.invoke(messages)
    return response.content


def call_db_server(email, query):
    request = {
    "email": email,
    "user_question": query
    }

    try:
        url = f"{os.environ['DB_URL']}/askdb"
        response = requests.post(url, json=request, headers=None)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"response": "Failed to get data from DB server"}
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {"response": "Failed to get data from DB server"}

def call_cp_server(query):
    request = {
    "user_question": query
    }

    try:
        url = f"{os.environ['CP_URL']}/policy"
        response = requests.post(url, json=request, headers=None)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"response": "Failed to get data from CP server"}
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {"response": "Failed to get data from CP server"}


# print(custom_decider("How is Work From?"))
# print(agent_decider("What is happening in warsaw?"))