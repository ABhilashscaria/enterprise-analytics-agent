from app.llm.client import call_model

SYSTEM_PROMPT = """
You are a routing agent.

Classify the query into one of:

sql
rag
chat

Rules:

sql:
- metrics
- counts
- revenue
- users
- visits
- analytics
- trends
- comparisons

rag:
- definitions
- explanations
- concepts
- documentation

chat:
- greetings
- small talk

Return ONLY:
sql
rag
chat
"""

def planner_node(state):
    query = state["query"]

    route, model, latency, usage = call_model(
        query,
        SYSTEM_PROMPT,
    )

    route = route.strip().lower()

    if route not in ["sql", "rag", "chat"]:
        route = "chat"

    state["route"] = route
    state["plan"] = f"Route query to {route}"

    meta = state.get("metadata", {})
    meta["planner_version"] = "v1_router"

    state["metadata"] = meta

    return state