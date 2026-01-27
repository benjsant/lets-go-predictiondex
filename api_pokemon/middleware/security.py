"""
Middleware de sécurité pour l'API - Authentification par API Key
"""
import hashlib
import os
import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# Header pour l'API Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_keys() -> set:
    """
    Récupère les API keys valides depuis les variables d'environnement.
    Support pour plusieurs clés séparées par des virgules.

    Returns:
        set: Ensemble des API keys valides (hashées)
    """
    keys_str = os.getenv("API_KEYS", "")
    if not keys_str:
        # En mode DEV sans API_KEYS configurées, on accepte tout
        dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        if dev_mode:
            return set()  # Pas de vérification en DEV
        raise RuntimeError("API_KEYS non configurées en production")

    # Hash des clés pour sécurité (ne jamais stocker en clair en mémoire)
    return {hashlib.sha256(key.strip().encode()).hexdigest()
            for key in keys_str.split(",") if key.strip()}


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Vérifie que l'API key fournie est valide.

    Args:
        api_key: Clé API fournie dans le header X-API-Key

    Returns:
        str: API key valide

    Raises:
        HTTPException: Si la clé est manquante ou invalide
    """
    # Mode DEV : bypass si DEV_MODE=true et aucune API_KEYS configurée
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
