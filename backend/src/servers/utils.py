import hashlib
import secrets
from typing import Tuple


def generate_agent_api_key() -> Tuple[str, str]:
    """
    Generates a secure API key with prefix 'smp_' and returns (raw_key, hashed_key).
    Raw key is shown once to user, hashed key is stored in DB.
    """
    raw_key = f"smp_{secrets.token_urlsafe(32)}"
    hashed_key = hash_api_key(raw_key)
    return raw_key, hashed_key


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
