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
```

### 3. Set Up a Virtual Environment

It is highly recommended to use a virtual environment to isolate the project dependencies.

For Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

Once your virtual environment is activated, install the required Python packages:

```bash
pip install -r requirements.txt
```


###5. Configure Environment Variables

Create a file named .env in the root directory of the project. Do not commit this file to Git. Add your API keys and configuration:
Code snippet

# LLM Configuration (Groq)
LLM_BASE_URL="[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)"
LLM_API_KEY="gsk_your_groq_api_key_here"
LARGE_MODEL_NAME="llama-3.3-70b-versatile"
SMALL_MODEL_NAME="llama-3.1-8b-instant"

# Observability (Langfuse)
LANGFUSE_HOST="[https://cloud.langfuse.com](https://cloud.langfuse.com)"
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."



###6. Run the Application

Start the FastAPI local server using Uvicorn:
Bash

uvicorn app.main:app --reload
