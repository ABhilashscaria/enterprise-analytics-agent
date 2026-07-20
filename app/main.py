from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

from app.graph.graph import analytics_graph
from app.observability.tracing import with_tracing
from app.observability.metrics import record_request_metrics, REQ_LAT, TOKENS, ERRORS
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import json
import redis.asyncio as redis
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)
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

    # Retrieve session from Redis
    session_data_str = await redis_client.get(session_id)
    if session_data_str:
        session_data = json.loads(session_data_str)
    else:
        session_data = {
            "history": [],
            "memory_summary": "",
        }

    state = {
        "query": req.query,
        "session_id": session_id,
        "history": session_data["history"],
        "memory_summary": session_data["memory_summary"],
        "metadata": {},
    }

    try:
        result, trace_id, model_name, _ = await with_tracing(analytics_graph, state)
    except Exception:
        ERRORS.labels(stage="graph").inc()
        raise

    session_data["history"].append({
        "user": req.query,
        "assistant": result["answer"],
    })

    if "memory_summary" in result:
        session_data["memory_summary"] = result["memory_summary"]

    # Save session back to Redis (expires in 24 hours)
    await redis_client.set(session_id, json.dumps(session_data), ex=86400)

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
