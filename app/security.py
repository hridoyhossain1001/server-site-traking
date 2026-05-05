"""
Access Token Encryption — Fernet symmetric encryption ব্যবহার করে
DB-তে Facebook Access Token encrypted রাখে।

ENCRYPTION_KEY env var সেট করতে হবে। জেনারেট করতে:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
import os
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY environment variable is required.")
else:
    try:
        _fernet = Fernet(ENCRYPTION_KEY.encode())
    except ValueError as exc:
        raise RuntimeError("ENCRYPTION_KEY must be a valid Fernet key.") from exc


def encrypt_token(plaintext: str) -> str:
    """Token encrypt করে।"""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    """Token decrypt করে।"""
    try:
        return _fernet.decrypt(encrypted.encode()).decode()
    except Exception:
        # Fallback for old plaintext tokens
        return encrypted
