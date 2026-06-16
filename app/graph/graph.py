from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.graph.nodes.planner import planner_node
from app.graph.nodes.router import router_node, ROUTE_MAP
from app.graph.nodes.sql_agent import sql_agent_node
from app.graph.nodes.rag_agent import rag_agent_node
from app.graph.nodes.chat_agent import chat_agent_node
from app.graph.nodes.hybrid_agent import hybrid_agent_node
from app.graph.nodes.answer_agent import answer_agent_node


class GraphState(TypedDict, total=False):
    query: str
    session_id: str
    history: list
    memory_summary: str
    plan: str
    route: str
    retrieved_docs: list
    generated_sql: str
    sql_result: str
    sql_error: str
    answer: str
    metadata: dict


builder = StateGraph(GraphState)

builder.add_node("planner", planner_node)
builder.add_node("router", router_node)
builder.add_node("sql_agent", sql_agent_node)
builder.add_node("rag_agent", rag_agent_node)
builder.add_node("chat_agent", chat_agent_node)
builder.add_node("hybrid_agent", hybrid_agent_node)
builder.add_node("answer_agent", answer_agent_node)

builder.set_entry_point("planner")
builder.add_edge("planner", "router")

builder.add_conditional_edges("router", lambda state: state["route"], ROUTE_MAP)

builder.add_edge("sql_agent", "answer_agent")
builder.add_edge("rag_agent", "answer_agent")
builder.add_edge("chat_agent", "answer_agent")
builder.add_edge("hybrid_agent", "answer_agent")
builder.add_edge("answer_agent", END)

analytics_graph = builder.compile()
