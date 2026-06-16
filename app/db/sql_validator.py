import re

BLOCKED_KEYWORDS = re.compile(
    r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|"
    r"MERGE|CALL|EXECUTE|EXEC|REPLACE|LOAD|EXPORT|COPY)\b",
    re.IGNORECASE,
)

MULTI_STATEMENT = re.compile(r";\s*\S", re.DOTALL)


def validate_sql(sql: str) -> tuple[bool, str]:
    """Return (is_valid, error_message). Only read-only SELECT/WITH allowed."""
    cleaned = sql.strip().rstrip(";")
    if not cleaned:
        return False, "Empty SQL query"

    upper = cleaned.upper().lstrip()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False, "Only SELECT and WITH (CTE) queries are allowed"

    if BLOCKED_KEYWORDS.search(cleaned):
        return False, "Query contains blocked keywords (write/DDL operations)"

    if MULTI_STATEMENT.search(cleaned):
        return False, "Multiple SQL statements are not allowed"

    return True, ""
