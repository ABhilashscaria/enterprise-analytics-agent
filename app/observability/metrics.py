from prometheus_client import Counter, Histogram

REQ_LAT = Histogram("copilot_request_latency_ms", "Request latency in milliseconds", ["model"],)

TOKENS = Counter("copilot_tokens_total",
                 "Total tokens used",
                 ["model", "type"],
                 )

ERRORS = Counter(
        "copilot_errors_total",
        "Total errors",
        ["stage"],
        )


def record_request_metrics(model: str | None, latency_ms: float, usage: dict):
    model = model or "unknown"
    REQ_LAT.labels(model = model).observe(latency_ms)
    TOKENS.labels(model = model, type = "prompt").inc(usage.get("prompt_tokens", 0))
    TOKENS.labels(model = model, type = "completion").inc(usage.get("completion_tokens",0))
