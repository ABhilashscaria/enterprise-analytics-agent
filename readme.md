# Enterprise Analytics AI Copilot

A production-grade, multi-agent conversational AI system designed to intelligently query enterprise data warehouses (Google BigQuery) and vector document stores (Qdrant).

This repository demonstrates advanced LLMOps, stateless backend architecture, and deterministic agent orchestration.

## 🏗 System Architecture

*   **Orchestration:** LangGraph (State Machine / Multi-Agent Routing)
*   **Web Framework:** FastAPI (Async REST API)
*   **State Management:** Redis (Distributed Session Storage)
*   **Vector Database:** Qdrant (Semantic Document Search)
*   **Data Warehouse:** Google BigQuery (Structured Analytics)
*   **Observability:** Prometheus & Grafana (System Metrics), Langfuse (LLM Tracing)
*   **Infrastructure:** Docker & Docker Compose

## 🚀 Key Features

*   **Dynamic Agent Routing:** Uses LangGraph to classify user intent and route queries to specialized sub-agents (`sql_agent`, `rag_agent`, `chat_agent`), heavily mitigating hallucination risks.
*   **Stateless Scaling:** Conversational memory is completely decoupled from the application and managed in **Redis**, allowing safe horizontal scaling of the API.
*   **Dual-Layer Observability:** 
    *   *System Health:* Exposes a `/metrics` endpoint scraped by **Prometheus** for tracking API latency, token consumption, and error rates via **Grafana**.
    *   *AI Cognition:* Integrates **Langfuse** to trace graph execution, model routing, and tool calls.
*   **Containerized Environment:** Fully dockerized stack for seamless, reproducible deployments across any environment.

## 🛠 Quick Start (Docker)

Ensure you have Docker and Docker Compose installed on your system.

1.  **Configure Environment Variables:**
    Ensure your `.env` file is present in the root directory with the necessary LLM API keys (Groq/OpenAI), Langfuse credentials, and BigQuery settings.

2.  **Spin up the Infrastructure:**
    ```bash
    docker-compose up --build -d
    ```
    This single command orchestrates the entire cluster:
    *   `api`: The FastAPI application (Port 8000)
    *   `redis`: Conversational state cache (Port 6379)
    *   `qdrant`: Vector database (Port 6333)
    *   `prometheus`: Metrics scraper (Port 9090)
    *   `grafana`: Telemetry visualization (Port 3000)

3.  **Verify System Health:**
    ```bash
    curl http://localhost:8000/healthz
    ```

## 🧪 Testing the Pipeline

**1. Send a Request:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "How many organic sessions did we have in May?", "session_id": "test-session-001"}'
```

**2. Verify Redis Memory:**
Send a follow-up request using the exact same `session_id`. The API will query Redis for the historical context:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "And what about paid sessions?", "session_id": "test-session-001"}'
```

## 📊 Viewing Telemetry

*   **Grafana Dashboards:** Access `http://localhost:3000` (Login: `admin` / `admin`). Configure the Prometheus data source to point to the Docker internal network (`http://prometheus:9090`). You can immediately visualize metrics such as `copilot_tokens_total` and `copilot_request_latency_ms`.
*   **Langfuse Traces:** View the exact execution graph, latency breakdowns, and raw LLM payloads in your Langfuse Cloud dashboard.

## 🔜 Ongoing Enhancements (Roadmap)

*   [ ] Refactor BigQuery initialization to utilize a global connection pool for reduced latency.
*   [ ] Upgrade LLM client to `AsyncOpenAI` for non-blocking ASGI event loops.
*   [ ] Implement `tenacity` retry logic for graceful handling of upstream API rate limits.
