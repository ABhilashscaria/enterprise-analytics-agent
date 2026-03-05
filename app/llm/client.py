import time
from typing import Tuple, Dict

from openai import OpenAI

from app.config import settings

from langchain_groq import ChatGroq

client = OpenAI(base_url = settings.llm_base_url,
                api_key = settings.llm_api_key,)

#Choose model based on complexity score

def choose_model(prompt:str, complexity_score:float | None = None) -> str:
    "Simple Heuristic model router"

    if complexity_score is None:
        complexity_score = len(prompt.split())
    if complexity_score > 80:
        return settings.large_model_name
    return settings.small_model_name

def call_model(prompt: str, system_prompt: str, temperature: float = 0.1,) -> Tuple[str, str, float, Dict[str, int]]:

    model_name = choose_model(prompt)
    start = time.time()


    resp = client.chat.completions.create( model = model_name, messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                                                                            temperature = temperature,)
    latency_ms = (time.time() - start) * 1000
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "total_tokens": resp.usage.total_tokens,
        }
    content = resp.choices[0].message.content
    return content, model_name, latency_ms , usage
                                                                                    

