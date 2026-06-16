from app.config import settings
from app.llm.client import call_model
from app.db.schema_catalog import format_schema_for_prompt
from app.db.bigquery_client import execute_query

SQL_SYSTEM_PROMPT = """You are an expert BigQuery SQL analyst.
Generate a single read-only SQL query to answer the user's question.

Rules:
- Output ONLY the SQL query, no markdown fences or explanation
- Use only tables and columns from the schema below
- Use fully qualified table names: `project.dataset.table`
- Only SELECT or WITH ... SELECT queries
- Add LIMIT if the query could return many rows
- Use SAFE_DIVIDE for ratios
- For date filters, use CURRENT_DATE() and DATE_SUB when the user says "last week/month"
"""

RAG_DEFINITION_HINT = """
If the user also asks for a definition, focus the SQL on the metric/data portion only.
"""


def _generate_sql(query: str, extra_context: str = "") -> tuple[str, str, float, dict]:
    schema = format_schema_for_prompt()
    prompt = f"""Schema:
{schema}

{extra_context}

User question:
{query}

Write the BigQuery SQL:"""

    content, model, latency, usage = call_model(prompt, SQL_SYSTEM_PROMPT, temperature=0.0)
    sql = content.strip()
    if sql.startswith("```"):
        sql = sql.strip("`").replace("sql", "", 1).strip()
    return sql, model, latency, usage


def sql_agent_node(state: dict) -> dict:
    query = state["query"]
    extra = RAG_DEFINITION_HINT if state.get("route") == "hybrid" else ""

    sql, model, latency, usage = _generate_sql(query, extra)
    result_text, error = execute_query(sql)

    state["generated_sql"] = sql
    state["sql_result"] = result_text if not error else ""
    state["sql_error"] = error or ""

    meta = state.get("metadata", {})
    meta.update({
        "sql_agent_version": "v1_bigquery",
        "sql_model": model,
        "sql_latency_ms": latency,
        "sql_tokens": usage,
        "sql_mock_mode": settings.bigquery_mock_mode or not settings.bigquery_project_id,
    })
    state["metadata"] = meta
    return state
