# Engineering Rules & Standards

## 1. Python Standards

- **Runtime:** Python 3.12+ (strictly enforced).
- **Typing:** PEP 484 type hints are mandatory for all function signatures. Use `typing.Annotated` for Pydantic/SQLModel metadata.
- **Async:** Use `async/await` for all I/O (Database, LLM, Redis). No `time.sleep()`.

## 2. Framework Standards

- **FastAPI:** Use `Annotated` dependencies. Prefer `APIRouter` segmentation.
- **SQLModel:** All models must reside in `packages/database`. Use `select_in` or `joined` loading to avoid N+1 queries.
- **Pydantic V2:** Use `model_validate` and `model_dump`. Strict mode enabled for validation.

## 3. The "God Mode" Principles

- **SOLID:** Every class has one reason to change.
- **Atomic Operations:** Credit deductions must use SQL Row-Level Locking (`FOR UPDATE`).
- **Idempotency:** Payment onramps and credit updates must be idempotent.
