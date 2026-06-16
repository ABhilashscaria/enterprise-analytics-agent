import json
from typing import Any

from app.config import settings
from app.db.sql_validator import validate_sql


def _get_client():
    from google.cloud import bigquery

    if settings.bigquery_credentials_path:
        return bigquery.Client.from_service_account_json(
            settings.bigquery_credentials_path,
            project=settings.bigquery_project_id,
        )
    return bigquery.Client(project=settings.bigquery_project_id)


def _format_rows(rows: list[dict[str, Any]], max_rows: int) -> str:
    if not rows:
        return "Query returned 0 rows."
    truncated = rows[:max_rows]
    lines = [json.dumps(row, default=str) for row in truncated]
    header = f"Returned {len(rows)} row(s)"
    if len(rows) > max_rows:
        header += f" (showing first {max_rows})"
    return header + ":\n" + "\n".join(lines)


def _mock_execute(sql: str) -> str:
    """Deterministic mock results for local dev without GCP credentials."""
    sql_lower = sql.lower()
    if "traffic_source" in sql_lower or "traffic_sources" in sql_lower:
        return _format_rows(
            [
                {"traffic_source": "organic", "sessions": 12450, "users": 9820},
                {"traffic_source": "paid", "sessions": 8320, "users": 7100},
                {"traffic_source": "direct", "sessions": 6150, "users": 5400},
                {"traffic_source": "referral", "sessions": 2890, "users": 2450},
            ],
            settings.bigquery_max_rows,
        )
    if "order" in sql_lower or "revenue" in sql_lower or "aov" in sql_lower:
        return _format_rows(
            [
                {"month": "2025-07", "orders": 4820, "revenue": 412350.75, "avg_order_value": 85.55},
            ],
            settings.bigquery_max_rows,
        )
    if "bounce" in sql_lower:
        return _format_rows(
            [
                {"month": "2025-05", "bounce_rate": 0.42, "bounced_sessions": 5200, "total_sessions": 12380},
            ],
            settings.bigquery_max_rows,
        )
    if "device" in sql_lower or "mobile" in sql_lower or "desktop" in sql_lower:
        return _format_rows(
            [
                {"device_type": "mobile", "sessions": 18420, "users": 15200},
                {"device_type": "desktop", "sessions": 11390, "users": 9800},
            ],
            settings.bigquery_max_rows,
        )
    return _format_rows(
        [{"note": "Mock mode — configure BigQuery credentials for live data", "sql_preview": sql[:200]}],
        settings.bigquery_max_rows,
    )


def execute_query(sql: str) -> tuple[str, str | None]:
    """
    Execute validated SQL against BigQuery.
    Returns (result_text, error_message).
    """
    is_valid, err = validate_sql(sql)
    if not is_valid:
        return "", err

    if settings.bigquery_mock_mode or not settings.bigquery_project_id:
        return _mock_execute(sql), None

    try:
        client = _get_client()
        job = client.query(sql)
        rows = [dict(row) for row in job.result(max_results=settings.bigquery_max_rows)]
        return _format_rows(rows, settings.bigquery_max_rows), None
    except Exception as exc:
        return "", str(exc)
