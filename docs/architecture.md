# Architecture & Directory Tree

## Monorepo Structure

```text
.
├── apps/                   # Frontend applications
├── docs/                   # Documentation
│   └── context/            # Agent pre-frontal cortex (.md rules/memory)
├── packages/               # Shared libraries
│   ├── database/           # SQLModel models & Alembic migrations
│   └── shared/             # Security, OTel, and common utilities
├── services/               # Backend microservices
│   ├── control_plane/      # Auth, API Keys, Billing Admin
│   └── inference_gateway/  # LangGraph Router, LiteLLM Proxy
├── docker-compose.dev.yml  # Local dev stack
├── Justfile                # Command automation
└── pyproject.toml         # uv workspace definition
```

## Service Communication

- **Control Plane:** Manages persistence and admin logic.
- **Inference Gateway:** Stateless (mostly) proxy that handles the high-throughput LLM traffic and real-time billing.
- **Shared Database:** Shared by both services for atomic credit management.
