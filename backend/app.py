import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from helper import custom_decider, agent_decider, call_db_server, call_cp_server
from mcp_client import chat_with_tools

load_dotenv()
frontend = os.environ['FRONTEND_URL']

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:5500"}})
CORS(app)

@app.route('/checkemail', methods=['GET'])
def checkemail():
    email = request.args.get('email', 'Guest')
    response = requests.get(f"{os.environ['DB_URL']}/checkemail?email={email}")
    
    # If the request was successful
    if response.status_code == 200:
        data = response.json()
        return jsonify(data), 200
    else:
        return jsonify({"error": "Failed to get data from Project 1"}), 500


@app.route('/askbackend', methods=['POST'])
def askbackend():
    data = request.json
    email = data.get('email')
    query = data.get('user_question')

    if email is None or query is None:
        return jsonify({"error": "Missing input values"}), 400
    
    query = query.replace("department", "team")
    
    decider = "custom"
    serviceToCall = custom_decider(query)

    if serviceToCall == "undecided":
        serviceToCall = agent_decider(query)
        decider = "agent"

        if serviceToCall == "unrelated":
            response = "Please ask queries related to the company only"
            return jsonify({"response": response}), 200

    serverResponse = "Try again after some time"
    if serviceToCall == 'db':
        data = call_db_server(email=email, query=query)

        serverResponse =  data["response"]

    if serviceToCall == 'cp':
        data = call_cp_server(query=query)
        serverResponse =  data["response"]

    if serviceToCall == 'mcp':
        serverResponse = chat_with_tools(user_message=query)

    return jsonify({
        "response": serverResponse,
        "server": serviceToCall,
        "decider": decider
    })

if __name__ == '__main__':
    app.run(debug=True, port=4000)