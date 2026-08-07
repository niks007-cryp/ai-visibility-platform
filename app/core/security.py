import uuid
import hmac
import hashlib
import base64
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Hashes plain text password using PBKDF2-HMAC-SHA256 with random salt."""
    salt = uuid.uuid4().hex
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against stored salt$hash string."""
    try:
        salt, stored_hash = hashed_password.split("$")
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000
        ).hex()
        return hmac.compare_digest(stored_hash, computed_hash)
    except Exception:
        return False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)


def create_jwt(payload: Dict[str, Any], secret: str = SECRET_KEY) -> str:
    """Creates a signed JWT token string."""
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(',', ':')).encode('utf-8')
    payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')

    unsigned_token = f"{_base64url_encode(header_json)}.{_base64url_encode(payload_json)}"
    signature = hmac.new(
        secret.encode('utf-8'),
        unsigned_token.encode('utf-8'),
        hashlib.sha256
    ).digest()

    return f"{unsigned_token}.{_base64url_encode(signature)}"


def decode_jwt(token: str, secret: str = SECRET_KEY) -> Optional[Dict[str, Any]]:
    """Decodes and verifies a signed JWT token string."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        unsigned_token = f"{parts[0]}.{parts[1]}"
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            unsigned_token.encode('utf-8'),
            hashlib.sha256
        ).digest()

        provided_sig = _base64url_decode(parts[2])
        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        payload_bytes = _base64url_decode(parts[1])
        payload = json.loads(payload_bytes.decode('utf-8'))

        # Expiry check
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None

        return payload
    except Exception:
        return None


def create_access_token(user_id: uuid.UUID, email: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }
    return create_jwt(payload)


def create_refresh_token(user_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }
    return create_jwt(payload)
