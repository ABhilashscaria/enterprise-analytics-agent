# 📊 Enterprise Analytics Agent

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-00a393)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20vLLM-black)

An intelligent, agentic analytics copilot designed to help non-technical business users and managers query, understand, and interact with enterprise data. 

Built with **FastAPI** and **LangGraph**, this application features dynamic LLM routing, comprehensive observability, and is optimized for ultra-fast inference using Groq (with drop-in support for local vLLM).

## 🏗 Architecture



## ✨ Key Features

* **Agentic Orchestration:** Utilizes LangGraph for structured reasoning, tool execution, and state management.
* **Dynamic LLM Routing:** A built-in heuristic router directs simple queries to smaller, lightning-fast models (e.g., Llama-3.1-8B) and complex analytical queries to heavy reasoning models (e.g., Llama-3.3-70B).
* **OpenAI-Compatible Drop-In:** Connects seamlessly to Groq's API or a local vLLM server without altering core agent logic.
* **Deep Observability:** Native integration with the Langfuse v3 SDK captures execution traces, prompt versions, and granular token usage.
* **Real-Time Metrics:** Exposes a Prometheus `/metrics` endpoint to monitor application health, model latency, and token consumption.
* **Vector Search Ready:** Configured to interface securely with Qdrant for Retrieval-Augmented Generation (RAG) and semantic search workflows.

---

## 💻 Tech Stack

* **Core Framework:** FastAPI, Uvicorn, Python 3.10+
* **AI & Orchestration:** LangGraph, LangChain Core, OpenAI Python SDK
* **Observability:** Langfuse, Prometheus Client
* **Data Layer:** Qdrant (Vector Database), Pydantic (Data Validation)

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Clone the Repository
```bash
git clone [https://github.com/yourusername/enterprise-analytics-agent.git](https://github.com/yourusername/enterprise-analytics-agent.git)
cd enterprise-analytics-agent
