from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from agents.write_agent import WriteAgent
from agents.edit_agent import EditAgent
from agents.arrange_agent import ArrangeAgent
from backend.document_loader import load_chunk_and_create_retriever

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