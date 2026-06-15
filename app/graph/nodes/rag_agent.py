from typing import List, Dict, Any
from app.rag.retriever import retrieve_docs

def rag_agent_node(state: dict) -> dict:
    query = state["query"]
    
    
    result = retrieve_docs(
         query,
         top_k = None, #use config default
         max_content_chars = None,
         )
         
         
    docs = result["docs"]
    debug =  result["debug"]
    
    
    

    # Attach to state
    state["retrieved_docs"] = docs

    # Update metadata
    meta = state.get("metadata", {})
    meta.update({
        "rag_docs_count": len(docs),
        "rag_debug": debug,
        "rag_agent_version": "v1_advanced",
        })
    state["metadata"] = meta
    
    return state

    return state
