from typing import Any, Dict
from app.config import settings

try:
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # Create a dummy decorator so the script doesn't crash if Langfuse isn't installed
    def observe(**kwargs):
        def decorator(func):
            return func
        return decorator

# Configure the context globally instead of initializing a separate client object
_tracing_enabled = False
if LANGFUSE_AVAILABLE and settings.langfuse_host and settings.langfuse_public_key and settings.langfuse_secret_key:
    langfuse_context.configure(
        host=settings.langfuse_host,
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
    )
    _tracing_enabled = True

@observe(name="analytics_copilot_request")
async def _execute_with_trace(graph, input_data: Dict[str, Any]):
    """Helper function to run the graph so it gets automatically traced."""
    result = await graph.ainvoke(input_data)
    meta = result.get("metadata", {})
    
    # Update the automatically generated trace with your graph's metadata
    langfuse_context.update_current_trace(metadata=meta)
    
    # Extract the trace ID to return it to the frontend/logs
    trace_id = langfuse_context.get_current_trace_id()
    
    # Force flush to ensure the trace is sent immediately
    langfuse_context.flush()
    
    return result, trace_id, meta.get("model_name"), meta.get("planner_version", "v0")

async def with_tracing(graph, input_data: Dict[str, Any]):
    """Wrap graph invocation in a Langfuse trace if configured."""
    if not _tracing_enabled:
        # Standard execution (No Langfuse tracing)
        result = await graph.ainvoke(input_data)
        meta = result.get("metadata", {})
        return result, None, meta.get("model_name"), meta.get("planner_version", "v0")

    # Traced execution
    return await _execute_with_trace(graph, input_data)
