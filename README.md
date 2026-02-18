# HimmiRouter — Enterprise AI Workbench

> An OpenRouter-grade LLM Inference Gateway with a premium AI Workbench UI. Built with FastAPI, LangGraph, MCP, and React.

---

## ✨ What Is This?

HimmiRouter is a **full-stack AI platform** that routes LLM requests through a secure, observable, and credit-aware gateway. It ships with:

- 🧠 **AI Playground** — ChatGPT-style streaming chat interface
- 📦 **Model Library** — Browse all available models and pricing
- 🔑 **API Key Management** — Create and manage scoped keys
- 💳 **Credit System** — Atomic per-request billing with real-time balance
- 📡 **MCP Server** — Expose the gateway to external agents (Claude, Cursor, etc.)
- 🔭 **Observability** — Full OpenTelemetry traces in Jaeger

---

## 🏗️ Architecture

```mermaid
graph TD
    subgraph Frontend
        Dashboard["Dashboard Frontend<br/>(React + Vite + Shadcn UI)<br/>localhost:5173"]
    end

    subgraph Backend
        Control["Control Plane (FastAPI)<br/>port 8000<br/>• Auth (JWT)<br/>• API Key Mgmt<br/>• User Credits<br/>• Model Catalog"]
        Gateway["Inference Gateway (FastAPI + LangGraph)<br/>port 4000<br/>• Auth Node<br/>• Route Node<br/>• LLM Node<br/>• Billing Node<br/>• SSE Streaming"]
    end

    subgraph Database
        DB["PostgreSQL (port 5432)<br/>Users • ApiKeys • Models • Providers"]
    end

    Dashboard --> Control
    Dashboard --> Gateway
    Control --> DB
    Gateway --> DB
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| Backend Language | Python 3.12 via `uv` |
| API Framework | FastAPI |
| LLM Orchestration | LangGraph (stateful graph) |
| LLM Proxy | LiteLLM |
| Database ORM | SQLModel + Alembic |
| Database | PostgreSQL 15 |
| Auth | JWT (python-jose) + Argon2 hashing |
| Observability | OpenTelemetry + Jaeger |
| Agent Protocol | Model Context Protocol (MCP) |
| Frontend | React 18 + Vite + TypeScript |
| UI Components | Shadcn UI (Radix Primitives) |
| Animations | Framer Motion |
| Styling | Tailwind CSS |
| Package Manager | Bun (frontend), uv (backend) |
| Task Runner | Just |

---

## ✅ Prerequisites

Install these before anything else:

| Tool | Install |
| :--- | :--- |
| `uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `just` | `brew install just` |
| `bun` | `curl -fsSL https://bun.sh/install \| bash` |
| `docker` | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |

---

## 🚀 Setup From Scratch

### Step 1 — Clone & Configure

```bash
git clone <your-repo-url> HimmiRouter
cd HimmiRouter

# Copy environment config
cp .env.example .env
```

Edit `.env` with your values (defaults work for local dev):

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/openrouter
JWT_SECRET=super-secret-key-change-this-in-prod
API_KEY_SALT=optional-salt-for-hashing
REDIS_URL=redis://localhost:6379/0
```

### Step 2 — Start Infrastructure

```bash
# Start PostgreSQL, Redis, and Jaeger
docker compose -f docker-compose.dev.yml up -d

# Verify containers are running
docker compose -f docker-compose.dev.yml ps
```

### Step 3 — Install Python Dependencies

```bash
uv sync
```

### Step 4 — Run Database Migrations & Seed Data

```bash
# Apply all schema migrations
just migrate

# Seed models, providers, and pricing data
just seed
```

### Step 5 — Install & Build Frontend

```bash
# Generates OpenAPI clients + installs npm deps
just install-frontend
```

> **Note:** This runs `openapi-typescript-codegen` to generate typesafe API clients from the live backend specs. The Control Plane must be reachable for this step.

---

## ▶️ Running the Stack

Open **3 separate terminals** and run one command in each:

```bash
# Terminal 1 — Control Plane (Auth, Keys, Models)
just run-control
# → http://localhost:8000
# → Swagger UI: http://localhost:8000/docs

# Terminal 2 — Inference Gateway (LLM routing, billing, streaming)
just run-gateway
# → http://localhost:4000
# → Simulator Mode is ON by default (no real API keys needed)

# Terminal 3 — Dashboard Frontend
just run-frontend
# → http://localhost:5173
```

---

## 🧪 Simulator Mode

The Inference Gateway runs in **Simulator Mode** by default (`HIMMI_SIMULATOR=true` in the Justfile). This means:

- ✅ No real OpenAI/Anthropic/Google API keys needed
- ✅ Responses stream in real-time with word-by-word animation
- ✅ Credit deduction still works end-to-end
- ✅ Full auth, routing, and billing pipeline executes

To use **real models**, set `HIMMI_SIMULATOR=false` in the Justfile and add your provider API keys to `.env`:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

---

## 🖥️ Using the AI Workbench

1. **Open** `http://localhost:5173`
2. **Register** a new account (email + password)
3. **Dashboard** → Generate an API Key (give it a name like "Playground Key")
4. **Playground** → Paste your key into the API Key field
5. **Select a model** from the dropdown and start chatting
6. **Model Library** → Browse all available models and their pricing

---

## 🔑 API Reference

### Control Plane (`localhost:8000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login, get JWT token |
| `POST` | `/api-keys/create` | Create a new API key |
| `GET` | `/api-keys` | List your API keys |
| `GET` | `/models` | List all available models |
| `GET` | `/users/{user_id}` | Get user status & credits |

Full interactive docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### Inference Gateway (`localhost:4000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat endpoint |
| `GET` | `/health` | Health check |
| `GET` | `/mcp/sse` | MCP agent connection endpoint |

---

## 🤖 MCP Integration

Connect any MCP-compatible agent (Claude Desktop, Cursor, etc.) to HimmiRouter:

**Endpoint:** `http://localhost:4000/mcp/sse`

**Available Tools:**
- `chat_with_model(api_key, model, prompt)` — Route a prompt through the full billing-aware pipeline

**Example Claude Desktop config (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "himmirouter": {
      "url": "http://localhost:4000/mcp/sse"
    }
  }
}
```

---

## 🔭 Observability

Every LLM request generates full distributed traces:

- **Jaeger UI:** `http://localhost:16686`
- Traces include: `auth` → `route` → `llm` → `billing` nodes
- See token counts, latency, and errors per node

---

## 🧰 Justfile Commands

```bash
just setup           # Full first-time setup (infra + migrate + seed)
just migrate         # Run Alembic migrations
just seed            # Seed model/provider data
just run-control     # Start Control Plane (port 8000)
just run-gateway     # Start Inference Gateway (port 4000, Simulator ON)
just run-frontend    # Start Dashboard (port 5173)
just run-all         # Start all 3 services in background
just kill-all        # Stop all running background processes
just destroy         # Stop processes, down docker volumes, clean generated code
just install-frontend # Regenerate API clients + install frontend deps
just generate-spec   # Regenerate OpenAPI specs from live backend
just lint            # Run ruff linter with auto-fix
just test            # Run pytest
```

---

## 📁 Project Structure

```mermaid
graph TD
    Root([HimmiRouter/]) --> Apps[/apps/dashboard-frontend/]
    Root --> Pkgs[/packages/]
    Root --> Serv[/services/]
    Root --> Tools[docker-compose.dev.yml<br/>Justfile<br/>.env.example<br/>pyproject.toml]

    Apps --> AF[Generated Clients<br/>Components<br/>Pages]
    Pkgs --> DB[database/]
    Pkgs --> SH[shared/]
    Serv --> CP[control_plane/]
    Serv --> IG[inference_gateway/]
```

---

## 🐛 Troubleshooting

**`just migrate` fails with connection error**
→ Make sure Docker containers are running: `docker compose -f docker-compose.dev.yml up -d`

**Frontend shows blank page**
→ Run `just install-frontend` to regenerate API clients, then restart `just run-frontend`

**"Invalid or disabled API Key" in Playground**
→ Generate a new key from the Dashboard and paste the raw `sk-or-v1-...` value

**Gateway not reachable from frontend**
→ Both services must be running. Check `just run-gateway` is active on port 4000.

**Credits not updating**
→ The credit refresh happens after the stream completes. Wait for the full response.

---

*Built with intensity by Himmi. 2026.*
