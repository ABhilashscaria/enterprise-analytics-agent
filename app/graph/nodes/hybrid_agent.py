from app.rag.retriever import retrieve_docs
from app.graph.nodes.sql_agent import _generate_sql
from app.db.bigquery_client import execute_query


def hybrid_agent_node(state: dict) -> dict:
    """
    Hybrid SQL + RAG: retrieves definitions from docs and fetches metrics from BigQuery.
    Example: "What is bounce rate and what was our bounce rate last month?"
    """
    query = state["query"]

    # --- RAG leg: definitions / concepts ---
    rag_result = retrieve_docs(query)
    state["retrieved_docs"] = rag_result["docs"]

    # --- SQL leg: metrics / data ---
    sql, model, latency, usage = _generate_sql(
        query,
        extra_context="Extract only the metric/data question for SQL. Ignore definition parts.",
    )
    result_text, error = execute_query(sql)
    state["generated_sql"] = sql
    state["sql_result"] = result_text if not error else ""
    state["sql_error"] = error or ""

    meta = state.get("metadata", {})
    meta.update({
        "hybrid_agent_version": "v1_sql_rag",
        "rag_docs_count": len(rag_result["docs"]),
        "rag_debug": rag_result["debug"],
        "sql_model": model,
        "sql_latency_ms": latency,
        "sql_tokens": usage,
    })
    state["metadata"] = meta
    state["plan"] = "Hybrid: retrieve definition (RAG) + fetch metric (SQL)"
    return state
