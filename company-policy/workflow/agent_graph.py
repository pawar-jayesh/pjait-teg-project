import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from agents.write_agent import WriteAgent
from agents.edit_agent import EditAgent
from agents.arrange_agent import ArrangeAgent
from document_loader import load_chunk_and_create_retriever
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.environ['BACKEND_URL']}})

class AgentState(TypedDict):
    query: str
    detailed: str
    edited: str
    final: str

retriever = load_chunk_and_create_retriever()
write_agent = WriteAgent(retriever)
edit_agent = EditAgent()
arrange_agent = ArrangeAgent()


def write_step(state: AgentState) -> AgentState:
    query = state["query"]
    detailed = write_agent.answer(query)
    return {"query": query, "detailed": detailed}

def edit_step(state: AgentState) -> AgentState:
    edited = edit_agent.edit(state["detailed"])
    return {**state, "edited": edited}

def arrange_step(state: AgentState) -> AgentState:
    final = arrange_agent.arrange([state["edited"], state["detailed"]])
    return {**state, "final": final}


workflow = StateGraph(AgentState)

workflow.add_node("WRITE", RunnableLambda(write_step))
workflow.add_node("EDIT", RunnableLambda(edit_step))
workflow.add_node("ARRANGE", RunnableLambda(arrange_step))

workflow.set_entry_point("WRITE")
workflow.add_edge("WRITE", "EDIT")
workflow.add_edge("EDIT", "ARRANGE")
workflow.add_edge("ARRANGE", END)


agent_graph = workflow.compile()

@app.route('/policy', methods=['POST'])
def askdb():
    data = request.json
    user_question = data.get('user_question')

    if user_question is None:
        return jsonify({"response": "Missing input values"}), 400

    output = agent_graph.invoke({"query": user_question})
    print("\nFinal Answer:\n")
    print(output["final"])

    result = output["final"]
    return {"response": result}

if __name__ == '__main__':
    app.run(debug=True, port=7000)