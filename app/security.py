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
    logger.warning(
        "⚠️ ENCRYPTION_KEY সেট করা হয়নি! Token plaintext-এ সংরক্ষিত হবে। "
        "Production-এ অবশ্যই সেট করুন।"
    )
    _fernet = None
else:
    _fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt_token(plaintext: str) -> str:
    """Token encrypt করে। Key না থাকলে plaintext রিটার্ন করে।"""
    if _fernet is None:
        return plaintext
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    """
    Token decrypt করে। 
    Backward compatible — পুরাতন plaintext token থাকলে সেটাই রিটার্ন করে।
    """
    if _fernet is None:
        return encrypted
    try:
        return _fernet.decrypt(encrypted.encode()).decode()
    except (InvalidToken, Exception):
        # পুরাতন plaintext token — decrypt ব্যর্থ হলে as-is রিটার্ন
        return encrypted
