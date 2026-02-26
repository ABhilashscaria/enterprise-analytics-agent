from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END

from app.graph.nodes.planner import planner_node
from app.graph.nodes.answer_agent import answer_agent_node


class GraphState(TypedDict, total=False):
    query: str
    plan: str
    answer: str
    metadata: Dict[str, Any]


builder = StateGraph(GraphState)

builder.add_node("planner", planner_node)
builder.add_node("answer_agent", answer_agent_node)

builder.set_entry_point("planner")
builder.add_edge("planner", "answer_agent")
builder.add_edge("answer_agent", END)

analytics_graph = builder.compile()
