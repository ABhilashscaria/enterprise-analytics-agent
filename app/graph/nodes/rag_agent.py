from typing import List, Dict, Any
from app.rag.retriever import retrieve_docs

def rag_agent_node(state: dict) -> dict:
    query = state["query"]
    # Retrieve top-k relevant docs
    docs: List[Dict[str, Any]] = retrieve_docs(query, top_k=4)

    # Attach to state
    state["retrieved_docs"] = docs

    # Update metadata
    meta = state.get("metadata", {})
    meta["rag_docs_count"] = len(docs)
    meta["rag_agent_version"] = "v0"
    state["metadata"] = meta

    return state
