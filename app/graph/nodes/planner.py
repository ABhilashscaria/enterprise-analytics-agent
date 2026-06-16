from app.llm.client import call_model

SYSTEM_PROMPT = """
You are a routing agent for an enterprise analytics copilot.

Classify the user query into exactly ONE of:

sql
rag
chat
hybrid

Rules:

sql — data/metrics from the database ONLY (no definition needed):
- counts, revenue, users, visits, sessions, trends, comparisons
- "top traffic sources last week", "average order value in July"
- "mobile vs desktop sessions", "revenue by channel"

rag — definitions, explanations, concepts, documentation ONLY (no live data):
- "what is bounce rate?", "explain conversion rate"
- "how is AOV calculated?", documentation lookups

chat — greetings, small talk, general conversation:
- "hello", "thanks", "how are you"

hybrid — needs BOTH a definition/explanation AND live metric data:
- "what is bounce rate and what was ours last month?"
- "define AOV and show me July average order value"
- "explain traffic sources and show top sources last week"

Return ONLY one word: sql, rag, chat, or hybrid
"""


def planner_node(state):
    query = state["query"]

    route, model, latency, usage = call_model(query, SYSTEM_PROMPT, temperature=0.0)
    route = route.strip().lower().split()[0] if route.strip() else "chat"

    valid = {"sql", "rag", "chat", "hybrid"}
    if route not in valid:
        route = "chat"

    state["route"] = route
    state["plan"] = f"Route query to {route} agent"

    meta = state.get("metadata", {})
    meta.update({
        "planner_version": "v2_hybrid_router",
        "planner_model": model,
        "planner_latency_ms": latency,
        "planner_tokens": usage,
    })
    state["metadata"] = meta
    return state
