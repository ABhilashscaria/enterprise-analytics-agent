VALID_ROUTES = ("sql", "rag", "chat", "hybrid")

ROUTE_MAP = {
    "sql": "sql_agent",
    "rag": "rag_agent",
    "chat": "chat_agent",
    "hybrid": "hybrid_agent",
}


def router_node(state: dict) -> dict:
    """
    Validates planner output and records routing decision in metadata.
    Conditional edges use state['route'] to dispatch to the correct agent.
    """
    route = state.get("route", "chat").strip().lower()
    if route not in VALID_ROUTES:
        route = "chat"
        state["plan"] = f"Invalid route — fallback to chat"

    state["route"] = route

    meta = state.get("metadata", {})
    meta["router_decision"] = route
    meta["router_version"] = "v2_agent_dispatch"
    state["metadata"] = meta
    return state
