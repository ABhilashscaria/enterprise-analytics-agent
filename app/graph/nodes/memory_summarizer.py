from app.llm.client import call_model

SYSTEM_PROMPT = """
You are a memory summarizer.
Summarize past conversation history concisely.
Keep important facts, remove irrelevant details.
"""

def memory_summarizer_node(state):
    history = state.get("history", [])

    # Summarize only if history is long enough
    if len(history) < 4:
        return state

    # Convert history to text
    text = "\n".join([
        f"User: {turn['user']}\nAssistant: {turn['assistant']}"
        for turn in history
    ])

    prompt = f"Summarize this conversation:\n\n{text}"

    summary, model, latency, usage = call_model(prompt, SYSTEM_PROMPT)

    state["memory_summary"] = summary

    # Keep only last 2 turns (sliding window)
    state["history"] = history[-2:]

    # Update metadata
    meta = state.get("metadata", {})
    meta.update({
        "memory_summary_model": model,
        "memory_summary_tokens": usage.get("total_tokens", 0),
    })
    state["metadata"] = meta

    return state
