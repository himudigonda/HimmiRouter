import hashlib
import secrets


def generate_api_key() -> tuple[str, str]:
    """Generates a raw key for the user and a hash for the DB."""
    suffix = secrets.token_urlsafe(24)
    raw_key = f"sk-or-v1-{suffix}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """Verifies a raw key against the stored SHA-256 hash."""
    return hashlib.sha256(raw_key.encode()).hexdigest() == stored_hash
