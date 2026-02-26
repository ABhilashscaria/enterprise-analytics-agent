from typing import TypedDict

class PlannerState(TypedDict, total=False):
    query: str
    plan: str
    metadata: dict


def planner_node(state: PlannerState) -> PlannerState:
    query = state["query"]
    #Placeholder
    plan = f"Answer the user's analytics question: '{query}' with clear concise explanation."
    metadata = state.get("metadata", {}) | {"planner_version": "v0"}

    return{
            **state,
            "plan": plan,
            "metadata": metadata,
          }
