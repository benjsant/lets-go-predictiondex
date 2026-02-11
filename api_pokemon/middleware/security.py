"""API key authentication middleware for FastAPI."""

import hashlib
import os
import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# API Key header configuration
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_keys() -> set:
    """
    Retrieve valid API keys from environment variables.

    Supports multiple keys separated by commas. Keys are hashed with SHA-256
    for secure in-memory storage.

    Returns:
        set: Set of valid hashed API keys

    Raises:
        RuntimeError: If API_KEYS not configured in production mode

    Environment:
        API_KEYS: Comma-separated API keys (e.g., "key1,key2,key3")
        DEV_MODE: Set to "true" to skip validation in development
    """
    keys_str = os.getenv("API_KEYS", "")
    if not keys_str:
        # DEV mode without configured API_KEYS accepts all requests
        dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        if dev_mode:
            return set()  # Skip validation in DEV mode
        raise RuntimeError("API_KEYS not configured in production")

    # Hash keys for security (never store plaintext in memory)
    return {hashlib.sha256(key.strip().encode()).hexdigest()
            for key in keys_str.split(",") if key.strip()}


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify that provided API key is valid.

    Args:
        api_key: API key provided in X-API-Key header

    Returns:
        str: Valid API key if authentication succeeds

    Raises:
        HTTPException: 403 if key is missing or invalid

    Notes:
        - In DEV mode without configured keys, bypasses validation
        - Uses constant-time comparison to prevent timing attacks
        - Returns clear error messages for better DX
    """
    # DEV mode: bypass if DEV_MODE=true and no API_KEYS configured
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    keys_str = os.getenv("API_KEYS", "")

    if dev_mode and not keys_str:
        return "dev-mode-bypass"

    # Check if API key is present
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Provide X-API-Key in header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Validate key (constant-time comparison to prevent timing attacks)
    valid_keys = get_api_keys()
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    if not any(secrets.compare_digest(api_key_hash, valid) for valid in valid_keys):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    return api_key


def generate_api_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure API key.

    Args:
        length: Key length (default: 32 characters)

    Returns:
        str: Generated API key
    """
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.

    Args:
        api_key: Plain text API key

    Returns:
        str: SHA-256 hash of the key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


# CLI script for generating keys for .env
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
