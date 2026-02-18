# HimmiRouter (OpenRouter Clone)

HimmiRouter is a high-performance, enterprise-grade LLM Inference Gateway and Control Plane built with **FastAPI**, **LangGraph**, **Model Context Protocol (MCP)**, and **React (Shadcn UI)**.

## 🚀 Architecture

- **Inference Gateway:** Orchestrates LLM requests with LangGraph. Supports dynamic routing, atomic billing, and SSE streaming.
- **Control Plane:** Manages users, API keys, and global configuration.
- **Dashboard:** A premium React frontend built with Shadcn UI and Framer Motion for a "perfect" user experience.
- **MCP Server:** Exposes gateway tools to external agents (Claude, Cursor, etc.).
- **Instrumentation:** Deep observability via OpenTelemetry (OTel).

## 🛠️ Tech Stack

- **Backend:** Python 3.12, UV, FastAPI, LangGraph, LiteLLM, SQLModel, PostgreSQL.
- **Frontend:** React 18, Vite, TypeScript, Shadcn UI, Framer Motion, Bun.
- **Protocol:** Model Context Protocol (MCP) for agent interoperability.
- **Ops:** OpenTelemetry, Jaeger, Docker Compose.

## 🏁 Quick Start

### 1. Prerequisites
- [uv](https://github.com/astral-sh/uv)
- [bun](https://bun.sh)
- Docker (for Database and Jaeger)

### 2. Setup
```bash
# Install dependencies
uv sync
just install-frontend

# Spin up infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Run migrations & seed data
just migrate
just seed
```

### 3. Running the Services
Run each in a separate terminal:
```bash
just run-control  # port 8000
just run-gateway  # port 4000
just run-frontend # port 5173
```

## 🤖 MCP Usage

You can connect external agents to HimmiRouter via the MCP endpoint:
`http://localhost:4000/mcp/sse`

Tools available:
- `chat_with_model(api_key, model, prompt)`: Unified access to 100+ models.

## 📊 Observability

Access the Jaeger UI at `http://localhost:16686` to see granular traces for every routing node and LLM call.

---
Built with intensity by Himmi.
