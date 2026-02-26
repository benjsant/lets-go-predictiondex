"""API key authentication middleware for FastAPI."""

import hashlib
import os
import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_keys() -> set:
    keys_str = os.getenv("API_KEYS", "")
    if not keys_str:
        dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        if dev_mode:
            return set()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not configured: API_KEYS missing in environment",
        )

    # Hash keys for security (never store plaintext in memory)
    return {hashlib.sha256(key.strip().encode()).hexdigest()
            for key in keys_str.split(",") if key.strip()}


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Verify the X-API-Key header. Bypassed in DEV_MODE when no keys are configured."""
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    keys_str = os.getenv("API_KEYS", "")

    if dev_mode and not keys_str:
        return "dev-mode-bypass"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Provide X-API-Key in header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    valid_keys = get_api_keys()
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    if not any(secrets.compare_digest(api_key_hash, valid) for valid in valid_keys):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    return api_key


def generate_api_key(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


if __name__ == "__main__":
    print("=== API Key Generator ===")
    nb_keys = int(input("Number of keys to generate (default: 3): ") or "3")

    print("\n[CONFIG] Add these lines to your .env file:\n")

    keys = [generate_api_key() for _ in range(nb_keys)]
    print(f'API_KEYS="{",".join(keys)}"')

    print("\n[KEYS] Generated keys (distribute to clients):\n")
    for i, key in enumerate(keys, 1):
        print(f"Key {i}: {key}")

    print("\n[WARN] IMPORTANT:")
    print("- Store these keys securely")
    print("- NEVER commit them to git")
    print("- Distribute via secure channel (encrypted email, vault, etc.)")
