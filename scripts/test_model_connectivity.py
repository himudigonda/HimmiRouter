#!/usr/bin/env python3
"""
test_model_connectivity.py
──────────────────────────
Tests whether each model in the HimmiRouter catalog is reachable and can
return a response. Sends a minimal "ping" prompt to every model via the
gateway's /v1/chat/completions endpoint (no API key needed if the gateway
is running in dev mode with keys stored in the DB).

Usage:
    # From repo root, with services running:
    uv run python scripts/test_model_connectivity.py

    # Target a different gateway:
    GATEWAY_URL=http://localhost:8001 uv run python scripts/test_model_connectivity.py

    # Test only a specific provider:
    FILTER_PROVIDER=Groq uv run python scripts/test_model_connectivity.py

    # Skip Ollama (local) models:
    SKIP_LOCAL=1 uv run python scripts/test_model_connectivity.py
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

# ── Config ────────────────────────────────────────────────────────────────────
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
MODELS_URL = os.getenv("MODELS_URL", f"{GATEWAY_URL}/models")
CHAT_URL = os.getenv("CHAT_URL", f"{GATEWAY_URL}/v1/chat/completions")
FILTER_PROVIDER = os.getenv("FILTER_PROVIDER", "")  # e.g. "Groq" to test only Groq
SKIP_LOCAL = os.getenv("SKIP_LOCAL", "0") == "1"
TIMEOUT = float(os.getenv("TIMEOUT", "30"))  # seconds per model
CONCURRENCY = int(os.getenv("CONCURRENCY", "4"))  # parallel requests

PING_PROMPT = "Reply with exactly one word: pong"


# ── Result dataclass ──────────────────────────────────────────────────────────
@dataclass
class ModelResult:
    slug: str
    name: str
    provider: str
    status: str  # "ok" | "error" | "timeout" | "skip"
    latency: float = 0.0  # seconds
    response: str = ""
    error: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────
def color(text: str, code: str) -> str:
    """ANSI color wrapper."""
    return f"\033[{code}m{text}\033[0m"


OK = color("✓ OK", "32")
FAIL = color("✗ ERROR", "31")
TIMEOUT_S = color("⏱ TIMEOUT", "33")
SKIP_S = color("- SKIP", "90")


async def fetch_models(client: httpx.AsyncClient) -> list[dict]:
    """Fetch the model list from the gateway."""
    resp = await client.get(MODELS_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # Support both {"models": [...]} and [...]
    if isinstance(data, list):
        return data
    return data.get("models", data.get("data", []))


async def ping_model(
    client: httpx.AsyncClient,
    model: dict,
    sem: asyncio.Semaphore,
) -> ModelResult:
    slug = model.get("slug", model.get("id", ""))
    name = model.get("name", slug)
    provider = model.get("provider", model.get("provider_name", ""))

    # Skip local Ollama models if requested
    if SKIP_LOCAL and slug.startswith("ollama/"):
        return ModelResult(
            slug=slug,
            name=name,
            provider=provider,
            status="skip",
            response="(skipped — local)",
        )

    # Filter by provider if set
    if FILTER_PROVIDER and FILTER_PROVIDER.lower() not in provider.lower():
        return ModelResult(
            slug=slug,
            name=name,
            provider=provider,
            status="skip",
            response="(filtered)",
        )

    payload = {
        "model": slug,
        "messages": [{"role": "user", "content": PING_PROMPT}],
        "max_tokens": 10,
        "stream": False,
    }

    async with sem:
        t0 = time.perf_counter()
        try:
            resp = await client.post(
                CHAT_URL,
                json=payload,
                timeout=TIMEOUT,
            )
            latency = time.perf_counter() - t0

            if resp.status_code == 200:
                body = resp.json()
                content = (
                    body.get("choices", [{}])[0].get("message", {}).get("content", "")
                    or ""
                ).strip()
                return ModelResult(
                    slug=slug,
                    name=name,
                    provider=provider,
                    status="ok",
                    latency=latency,
                    response=content,
                )
            else:
                return ModelResult(
                    slug=slug,
                    name=name,
                    provider=provider,
                    status="error",
                    latency=latency,
                    error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                )

        except httpx.TimeoutException:
            return ModelResult(
                slug=slug,
                name=name,
                provider=provider,
                status="timeout",
                latency=TIMEOUT,
                error="Request timed out",
            )
        except Exception as exc:
            return ModelResult(
                slug=slug,
                name=name,
                provider=provider,
                status="error",
                latency=time.perf_counter() - t0,
                error=str(exc)[:200],
            )


def print_result(r: ModelResult) -> None:
    if r.status == "ok":
        badge = OK
        detail = f'"{r.response}"  ({r.latency:.2f}s)'
    elif r.status == "timeout":
        badge = TIMEOUT_S
        detail = r.error
    elif r.status == "skip":
        badge = SKIP_S
        detail = r.response
    else:
        badge = FAIL
        detail = r.error

    print(f"  {badge}  [{r.provider:20s}]  {r.slug:50s}  {detail}")


def print_summary(results: list[ModelResult]) -> None:
    ok = [r for r in results if r.status == "ok"]
    errors = [r for r in results if r.status == "error"]
    timeouts = [r for r in results if r.status == "timeout"]
    skipped = [r for r in results if r.status == "skip"]

    print("\n" + "═" * 80)
    print(f"  SUMMARY  —  {len(results)} models tested")
    print("═" * 80)
    print(f"  {color(str(len(ok)),      '32')} OK")
    print(f"  {color(str(len(errors)),  '31')} ERROR")
    print(f"  {color(str(len(timeouts)),'33')} TIMEOUT")
    print(f"  {color(str(len(skipped)), '90')} SKIPPED")

    if errors or timeouts:
        print(f"\n{color('Failed models:', '31')}")
        for r in errors + timeouts:
            print(f"  • {r.slug:50s}  {r.error}")

    if ok:
        avg = sum(r.latency for r in ok) / len(ok)
        fastest = min(ok, key=lambda r: r.latency)
        slowest = max(ok, key=lambda r: r.latency)
        print(f"\n{color('Latency (successful):', '36')}")
        print(
            f"  avg {avg:.2f}s  |  fastest {fastest.slug} ({fastest.latency:.2f}s)"
            f"  |  slowest {slowest.slug} ({slowest.latency:.2f}s)"
        )

    print()


# ── Main ──────────────────────────────────────────────────────────────────────
async def main() -> int:
    print(color(f"\n🔌 HimmiRouter Model Connectivity Test", "1;36"))
    print(f"   Gateway : {GATEWAY_URL}")
    print(f"   Timeout : {TIMEOUT}s per model")
    print(f"   Workers : {CONCURRENCY} concurrent")
    if FILTER_PROVIDER:
        print(f"   Filter  : provider={FILTER_PROVIDER}")
    if SKIP_LOCAL:
        print(f"   Skipping: Ollama local models")
    print()

    async with httpx.AsyncClient() as client:
        # 1. Fetch model list
        try:
            models = await fetch_models(client)
        except Exception as exc:
            print(color(f"✗ Could not reach gateway at {MODELS_URL}: {exc}", "31"))
            print("  Make sure `just dev` is running.")
            return 1

        if not models:
            print(color("✗ No models returned from gateway.", "31"))
            return 1

        print(f"  Found {len(models)} models in catalog.\n")
        print("─" * 80)

        # 2. Ping each model
        sem = asyncio.Semaphore(CONCURRENCY)
        tasks = [ping_model(client, m, sem) for m in models]
        results: list[ModelResult] = await asyncio.gather(*tasks)

    # 3. Print results grouped by provider
    results.sort(key=lambda r: (r.provider, r.slug))
    current_provider = None
    for r in results:
        if r.provider != current_provider:
            current_provider = r.provider
            print(f"\n  {color(r.provider, '1;37')}")
        print_result(r)

    print_summary(results)

    # Exit code: 0 if all non-skipped passed, 1 otherwise
    failed = [r for r in results if r.status in ("error", "timeout")]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
