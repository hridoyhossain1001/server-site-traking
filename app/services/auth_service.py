import base64
import hashlib
import hmac
import logging
import os
import secrets


PASSWORD_ITERATIONS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "210000"))
MAX_PASSWORD_ITERATIONS = int(os.getenv("MAX_PASSWORD_HASH_ITERATIONS", "600000"))
logger = logging.getLogger(__name__)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt_b64, digest_b64 = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
        if iterations > MAX_PASSWORD_ITERATIONS or iterations < 1:
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").lower() in ("true", "1", "yes")


def _is_production_env() -> bool:
    app_env = (os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or os.getenv("ENV") or "").lower()
    return app_env in ("production", "prod") or bool(os.getenv("PRIMARY_DOMAIN"))


def verify_admin_password(password: str, stored_value: str | None) -> bool:
    """Verify ADMIN_PASSWORD with a slow hash; legacy formats are blocked in production."""
    if not stored_value:
        return False

    if stored_value.startswith("pbkdf2_sha256$"):
        return verify_password(password, stored_value)

    allow_legacy = _env_flag("ALLOW_LEGACY_ADMIN_PASSWORD") and not _is_production_env()
    if not allow_legacy:
        logger.error(
            "ADMIN_PASSWORD uses a legacy format. Set it to pbkdf2_sha256$... "
            "using scripts/keys/hash_admin_password.py."
        )
        return False

    logger.warning(
        "ALLOW_LEGACY_ADMIN_PASSWORD is enabled for a non-production environment. "
        "Migrate ADMIN_PASSWORD to pbkdf2_sha256$... before deployment."
    )
    if stored_value.startswith("sha256:"):
        expected_hash = stored_value[7:]
        input_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(input_hash, expected_hash)
    return hmac.compare_digest(password, stored_value)


def new_session_token() -> str:
    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
