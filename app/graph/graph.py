from typing import TypedDict
from langgraph.graph import StateGraph, END

# -----------------------------
# 1. DEFINE THE GRAPH STATE SCHEMA
# -----------------------------
# This tells LangGraph exactly what keys to expect and keep.
class GraphState(TypedDict, total=False):
    query: str
    session_id: str
    history: list
    memory_summary: str
    plan: str
    answer: str
    metadata: dict

# -----------------------------
# IMPORT NODES
# -----------------------------
from app.graph.nodes.planner import planner_node
from app.graph.nodes.answer_agent import answer_agent_node
from app.graph.nodes.memory_summarizer import memory_summarizer_node

# -----------------------------
# BUILD THE GRAPH
# -----------------------------
# 2. USE YOUR SCHEMA HERE INSTEAD OF 'dict'
builder = StateGraph(GraphState)

builder.add_node("planner", planner_node)
builder.add_node("memory_summarizer", memory_summarizer_node)
builder.add_node("answer_agent", answer_agent_node)

builder.set_entry_point("planner")

# Flow:
# Planner → Memory Summarizer → Answer Agent → END
builder.add_edge("planner", "memory_summarizer")
builder.add_edge("memory_summarizer", "answer_agent")
builder.add_edge("answer_agent", END)

analytics_graph = builder.compile()
