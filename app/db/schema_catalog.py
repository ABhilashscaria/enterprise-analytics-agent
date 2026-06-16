import json
from pathlib import Path
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=1)
def load_schema_catalog() -> dict:
    path = Path(settings.bigquery_schema_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def format_schema_for_prompt() -> str:
    catalog = load_schema_catalog()
    project = settings.bigquery_project_id or catalog.get("project_id", "your-gcp-project")
    dataset = settings.bigquery_dataset or catalog.get("dataset", "analytics")
    lines = [
        f"Project: {project}",
        f"Dataset: {dataset}",
        "",
        "Available tables (use fully qualified names: `project.dataset.table`):",
    ]
    for table in catalog.get("tables", []):
        fq_name = f"`{project}.{dataset}.{table['name']}`"
        lines.append(f"\nTable {fq_name}")
        lines.append(f"  Description: {table.get('description', '')}")
        lines.append("  Columns:")
        for col in table.get("columns", []):
            lines.append(
                f"    - {col['name']} ({col['type']}): {col.get('description', '')}"
            )
    return "\n".join(lines)


def allowed_table_names() -> set[str]:
    catalog = load_schema_catalog()
    project = settings.bigquery_project_id or catalog.get("project_id", "")
    dataset = settings.bigquery_dataset or catalog.get("dataset", "analytics")
    names: set[str] = set()
    for table in catalog.get("tables", []):
        t = table["name"]
        names.add(t)
        names.add(f"{dataset}.{t}")
        if project:
            names.add(f"{project}.{dataset}.{t}")
    return names
