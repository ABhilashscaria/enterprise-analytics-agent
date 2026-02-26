from typing import TypedDict

from app.llm.client import call_model


class AnswerState(TypedDict, total = False):
    query: str
    plan: str
    answer: str
    metadata: dict


SYSTEM_PROMPT = (
        "You are an analytics copilot. "
        "Explain concepts clearly to non-technical business users. "
        "Use short paragraphs and bullet points when helpful. "
        )

def answer_agent_node(state: AnswerState) -> AnswerState:
    query = state["query"]
    plan = state.get("plan") or f"Answer this question: {query}"

    prompt = f"Plan: {plan}\n\nUser question: {query}"
    content, model_name, latency_ms, usage = call_model(prompt = prompt, system_prompt = SYSTEM_PROMPT, temperature = 0.1,)

    metadata = state.get("metadata", {})
    metadata |= {
            "model_name": model_name,
            "latency_ms": latency_ms,
            "usage": usage,
            "anser_agent_version": "v0",
            }
    return{
            **state,
            "answer": content,
            "metadata": metadata,
            }
