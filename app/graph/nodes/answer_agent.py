from app.llm.client import call_model
from app.rag.retriever import retrieve_docs
SYSTEM_PROMPT = """You are an analytics copilot with memory and retrieval.
Use the conversation history, long-term memory, and retrieved documentation
to answer the user's question. Prefer retrieved docs over guessing.
If something is not supported by the docs, be honest about uncertainty.
"""

def format_history(history):
    return "\n".join(
        f"User: {turn['user']}\nAssistant: {turn['assistant']}"
        for turn in history
    )
    
def format_docs(docs):
    if not docs:
        return "No external documents retrieved."
    lines = []
    for i, d in enumerate(docs, start=1):
        lines.append(f"[DOC {i} | score={d.get('score', 0):.2f}] {d.get('text', '')}")
    return "\n".join(lines)

def answer_agent_node(state):
    query = state["query"]
    plan = state.get("plan", "")
    
    
    retrieved_docs = state.get("retrieved_docs", [])
    if not retrieved_docs:
        retrieved_docs = retrieve_docs(query)
        state["retrieved_docs"] = retrieved_docs # Save it back to state
       
    # NEW: include memory + conversation history
    history_text = format_history(state.get("history", []))
    memory_summary = state.get("memory_summary", "")
   
    
    
    docs_text = format_docs(retrieved_docs)
    
    prompt = f"""
Conversation history:
{history_text}

Long-term memory:
{memory_summary}

Retrieved documentation:
{docs_text}

Plan:
{plan}

User:
{query}

Using ONLY the information above, answer the question.
If the answer is uncertain or not in the docs, say so explicitly.
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
