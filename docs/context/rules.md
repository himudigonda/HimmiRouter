# Engineering Rules (The Bible)

1. **Async Everywhere**: Any I/O (DB, HTTP, Redis) MUST be async. 
2. **Strict Typing**: No `Any`. Use `SQLModel` and `Pydantic` for every data structure.
3. **Atomic Billing**: Credit deductions MUST use SQL `FOR UPDATE` locks.
4. **Security**: API Keys are never stored in plain text. Store SHA-256 hashes only.
5. **Observability**: Every service must be instrumented with OpenTelemetry.
