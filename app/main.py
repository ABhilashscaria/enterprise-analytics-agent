from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

from app.graph.graph import analytics_graph
from app.observability.tracing import with_tracing
from app.observability.metrics import record_request_metrics, REQ_LAT, TOKENS, ERRORS
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

SESSION_STORE = {}

app = FastAPI(title="Enterprise Analytics Copilot")


class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    model_name: str | None = None
    latency_ms: float = 0.0
    route: str | None = None
    generated_sql: str | None = None
    trace_id: str | None = None
    metadata: dict = {}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or "default"

    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {
            "history": [],
            "memory_summary": "",
        }

    state = {
        "query": req.query,
        "session_id": session_id,
        "history": SESSION_STORE[session_id]["history"],
        "memory_summary": SESSION_STORE[session_id]["memory_summary"],
        "metadata": {},
    }

    try:
        result, trace_id, model_name, _ = await with_tracing(analytics_graph, state)
    except Exception:
        ERRORS.labels(stage="graph").inc()
        raise

    SESSION_STORE[session_id]["history"].append({
        "user": req.query,
        "assistant": result["answer"],
    })

    if "memory_summary" in result:
        SESSION_STORE[session_id]["memory_summary"] = result["memory_summary"]

    metadata = result.get("metadata", {})
    usage = metadata.get("usage", {})
    latency = metadata.get("latency_ms", 0.0)
    record_request_metrics(model_name, latency, usage)

    return ChatResponse(
        answer=result.get("answer", ""),
        model_name=metadata.get("model_name"),
        latency_ms=latency,
        route=result.get("route"),
        generated_sql=result.get("generated_sql"),
        trace_id=trace_id,
        metadata=metadata,
    )


@app.get("/healthz")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
