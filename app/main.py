from fastapi import FastAPI
from pydantic import BaseModel

from app.graph.graph import analytics_graph, GraphState

# ----------------------------------------------------------
# In-memory session store (can later be moved to Redis)
# ----------------------------------------------------------
SESSION_STORE = {}

app = FastAPI(title="Analytics Copilot with Memory")


# ----------------------------------------------------------
# Request / Response Models
# ----------------------------------------------------------
class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    model_name: str | None = None
    latency_ms: float = 0.0
    metadata: dict = {}


# ----------------------------------------------------------
# Chat Endpoint (Memory Aware)
# ----------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or "default"

    # Create new session memory if not exists
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {
            "history": [],
            "memory_summary": ""
        }

    # Build memory-aware state
    state = {
        "query": req.query,
        "session_id": session_id,
        "history": SESSION_STORE[session_id]["history"],
        "memory_summary": SESSION_STORE[session_id]["memory_summary"],
        "metadata": {}
    }

    # Call LangGraph
    result = await analytics_graph.ainvoke(state)

    # -----------------------------------------------------
    # Persist updated conversational memory
    # -----------------------------------------------------
    SESSION_STORE[session_id]["history"].append({
        "user": req.query,
        "assistant": result["answer"]
    })

    if "memory_summary" in result:
        SESSION_STORE[session_id]["memory_summary"] = result["memory_summary"]

    metadata = result.get("metadata", {})

    return ChatResponse(
        answer=result.get("answer", ""),
        model_name=metadata.get("model_name"),
        latency_ms=metadata.get("latency_ms", 0),
        metadata=metadata
    )


# ----------------------------------------------------------
# Health Check
# ----------------------------------------------------------
@app.get("/healthz")
async def health():
    return {"status": "ok"}
