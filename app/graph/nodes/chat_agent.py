from app.graph.nodes.memory_summarizer import memory_summarizer_node


def chat_agent_node(state: dict) -> dict:
    """
    Handles conversational queries: compresses long history into memory_summary
    and keeps a sliding window of recent turns for the answer agent.
    """
    state = memory_summarizer_node(state)

    meta = state.get("metadata", {})
    meta["chat_agent_version"] = "v1_memory"
    state["metadata"] = meta
    return state
