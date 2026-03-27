import os
import sys

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

from rag.vector_store import retrieve_docs

# Ensure Agents directory is in sys.path for imports to work
sys.path.insert(0, os.path.dirname(__file__))

from router_agent import route_question

load_dotenv()


class AgentState(TypedDict):
    question: str
    route: str
    answer: str


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


def router_node(state: AgentState):
    question = state["question"]
    route = route_question(question)
    print(f"Router selected: {route}")
    return {"route": route}

def rag_agent(state: AgentState):
    question = state["question"]

    context = retrieve_docs(question)

    prompt = f"""
Answer the question using the context below.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return {"answer": response.content}


def general_agent(state: AgentState):
    question = state["question"]

    response = llm.invoke(question)

    return {"answer": response.content}


def route_decision(state: AgentState):
    return state["route"]


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("rag_agent", rag_agent)
    workflow.add_node("general_agent", general_agent)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "rag": "rag_agent",
            "general": "general_agent"
        }
    )

    workflow.add_edge("rag_agent", END)
    workflow.add_edge("general_agent", END)

    return workflow.compile()