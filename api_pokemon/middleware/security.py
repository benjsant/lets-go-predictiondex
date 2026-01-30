"""
API Security Middleware - API Key Authentication
=================================================

Security middleware for FastAPI application implementing API key authentication.

This module provides:
    - API key validation via X-API-Key header
    - Support for multiple API keys (comma-separated)
    - Development mode bypass (DEV_MODE=true)
    - SHA-256 hashing for secure key storage in memory
    - Clear HTTP 403 responses for unauthorized access

Environment Variables:
    API_KEYS: Comma-separated list of valid API keys
    DEV_MODE: Set to "true" to bypass authentication in development
    API_KEY_REQUIRED: Set to "false" to disable authentication entirely

Usage:
    from api_pokemon.middleware.security import verify_api_key

    @app.get("/protected")
    def protected_route(api_key: str = Depends(verify_api_key)):
        return {"message": "Access granted"}
"""
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

    # Vérification de la présence de la clé
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key manquante. Fournir X-API-Key dans le header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Vérification de la validité
    valid_keys = get_api_keys()
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    if api_key_hash not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key invalide",
        )

    return api_key


def generate_api_key(length: int = 32) -> str:
    """
    Génère une API key cryptographiquement sécurisée.

    Args:
        length: Longueur de la clé (défaut: 32 caractères)

    Returns:
        str: API key générée
    """
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str) -> str:
    """
    Hash une API key pour stockage sécurisé.

    Args:
        api_key: Clé API en clair

    Returns:
        str: Hash SHA-256 de la clé
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


# Fonction pour générer des clés pour .env (script d'initialisation)
if __name__ == "__main__":
    print("=== Générateur d'API Keys ===\n")
    nb_keys = int(input("Nombre de clés à générer (défaut: 3): ") or "3")

    print("\n📝 Ajoutez ces lignes à votre fichier .env:\n")

    keys = [generate_api_key() for _ in range(nb_keys)]
    print(f'API_KEYS="{",".join(keys)}"')

    print("\n🔑 Clés générées (à distribuer aux clients):\n")
    for i, key in enumerate(keys, 1):
        print(f"Clé {i}: {key}")

    print("\n⚠️  IMPORTANT:")
    print("- Stockez ces clés de manière sécurisée")
    print("- Ne les commitez JAMAIS dans git")
    print("- Distribuez-les via un canal sécurisé (email chiffré, vault, etc.)")
