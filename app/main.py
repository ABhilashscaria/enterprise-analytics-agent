from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from app.graph.graph import analytics_graph
from app.observability.tracing import with_tracing
from app.observability.metrics import record_request_metrics

app = FastAPI(title = "Enterprise Analytics Agent")


class ChatRequest(BaseModel):
    query: str
    user_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    model_name: str | None = None
    prompt_version: str | None = None
    latency_ms: float
    debug_trace_id: str | None = None
    metadata: dict | None = None


@app.post("/chat", response_model = ChatResponse)
async def chat(req: ChatRequest):
    import time

    start = time.time()
    result, trace_id, model_used, prompt_version = await with_tracing( graph = analytics_graph,
            input_data={
                "query": req.query,
                "metadata": {
                    "user_id": req.user_id,
                    "session_id": req.session_id,
                    },
                },
            )
    end = time.time()
    latency_ms = (end - start) * 1000

    metadata = result.get("metadata", {})
    usage = metadata.get("usage", {})

    record_request_metrics(model_used, latency_ms, usage)

    return ChatResponse(
            answer=result.get("answer", ""),
            model_name = model_used,
            prompt_version = prompt_version,
            latency_ms = latency_ms,
            debug_trace_id = trace_id,
            metadata=result.get("metadata", {}),
            )

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content = data, media_type = CONTENT_TYPE_LATEST)
