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



# print(custom_decider("How is Work From?"))

# pending

