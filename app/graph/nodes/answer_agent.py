from app.llm.client import call_model
from app.rag.retriever import retrieve_docs

SYSTEM_PROMPT_SQL = """You are an analytics copilot. Answer using the SQL query results.
Present numbers clearly. If SQL failed, explain what went wrong.
Do not invent data not present in the results."""

SYSTEM_PROMPT_RAG = """You are an analytics copilot. Answer using retrieved documentation.
Cite concepts from the docs. If docs are insufficient, say so."""

SYSTEM_PROMPT_HYBRID = """You are an analytics copilot. The user asked for BOTH a definition and live data.
1. Explain the concept using retrieved documentation
2. Present the metric using SQL results
Keep both parts clear and labeled."""

SYSTEM_PROMPT_CHAT = """You are a friendly analytics copilot.
Use conversation history and memory. Be concise and helpful."""

ROUTE_PROMPTS = {
    "sql": SYSTEM_PROMPT_SQL,
    "rag": SYSTEM_PROMPT_RAG,
    "hybrid": SYSTEM_PROMPT_HYBRID,
    "chat": SYSTEM_PROMPT_CHAT,
}


def format_history(history):
    if not history:
        return "(no prior turns)"
    return "\n".join(
        f"User: {turn['user']}\nAssistant: {turn['assistant']}"
        for turn in history
    )


def format_docs(docs):
    if not docs:
        return "No documentation retrieved."
    lines = []
    for i, d in enumerate(docs, start=1):
        score = d.get("combined_score", d.get("score", 0))
        lines.append(f"[DOC {i} | score={score:.2f}] {d.get('text', '')}")
    return "\n".join(lines)


def answer_agent_node(state):
    query = state["query"]
    route = state.get("route", "chat")
    plan = state.get("plan", "")

    retrieved_docs = state.get("retrieved_docs", [])
    if route in ("rag", "hybrid") and not retrieved_docs:
        result = retrieve_docs(query)
        retrieved_docs = result["docs"]
        state["retrieved_docs"] = retrieved_docs

    history_text = format_history(state.get("history", []))
    memory_summary = state.get("memory_summary", "") or "(none)"
    docs_text = format_docs(retrieved_docs)

    sql_result = state.get("sql_result", "")
    generated_sql = state.get("generated_sql", "")
    sql_error = state.get("sql_error", "")

    sql_section = "No SQL executed."
    if generated_sql:
        sql_section = f"Generated SQL:\n{generated_sql}\n\n"
        if sql_error:
            sql_section += f"SQL Error: {sql_error}"
        elif sql_result:
            sql_section += f"Results:\n{sql_result}"

    prompt = f"""Route: {route}

Conversation history:
{history_text}

Long-term memory:
{memory_summary}

Retrieved documentation:
{docs_text}

SQL analytics:
{sql_section}

Plan:
{plan}

User question:
{query}

Answer the user question using the context above for this route type."""

    system = ROUTE_PROMPTS.get(route, SYSTEM_PROMPT_CHAT)
    content, model, latency, usage = call_model(prompt, system)

    state["answer"] = content

    meta = state.get("metadata", {})
    meta.update({
        "model_name": model,
        "latency_ms": latency,
        "usage": usage,
        "answer_agent_version": "v2_route_aware",
        "answer_route": route,
    })
    state["metadata"] = meta
    return state
