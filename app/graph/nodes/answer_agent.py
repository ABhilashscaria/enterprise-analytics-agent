from app.llm.client import call_model

SYSTEM_PROMPT = """You are an analytics copilot with memory.
Use the conversation history and long-term memory to respond.
If the user's identity or preferences were mentioned earlier, remember them.
"""

def format_history(history):
    return "\n".join(
        f"User: {turn['user']}\nAssistant: {turn['assistant']}"
        for turn in history
    )

def answer_agent_node(state):
    query = state["query"]
    plan = state.get("plan", "")

    # NEW: include memory + conversation history
    history_text = format_history(state.get("history", []))
    memory_summary = state.get("memory_summary", "")

    prompt = f"""
Conversation history:
{history_text}

Long-term memory:
{memory_summary}

Plan:
{plan}

User:
{query}

Answer based ONLY on the above memory + history + user query.
"""

    content, model, latency, usage = call_model(prompt, SYSTEM_PROMPT)

    state["answer"] = content

    meta = state.get("metadata", {})
    meta.update({
        "model_name": model,
        "latency_ms": latency,
        "usage": usage,
        "answer_agent_version": "v1-memory"
    })
    state["metadata"] = meta

    return state
