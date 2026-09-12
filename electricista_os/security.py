"""Seguridad sin dependencias externas: JWT HS256 y hashing PBKDF2 (stdlib).

SECRET_KEY se toma de EOS_SECRET_KEY. Si no está seteada, se genera una
aleatoria por proceso: es cómodo para desarrollo, pero al reiniciar el
servidor los tokens viejos dejan de valer y el dashboard muestra "sesión
vencida" (comportamiento esperado). Para producción, setear EOS_SECRET_KEY.
"""
import os
import time
import json
import hmac
import base64
import hashlib
import secrets

SECRET_KEY = os.environ.get("EOS_SECRET_KEY") or secrets.token_hex(32)
TOKEN_HORAS = int(os.environ.get("EOS_TOKEN_HORAS", "12"))


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(seg: str) -> bytes:
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def create_token(sub: str, horas: int = TOKEN_HORAS) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + horas * 3600}
    signing_input = (_b64(json.dumps(header, separators=(",", ":")).encode())
                     + "." + _b64(json.dumps(payload, separators=(",", ":")).encode()))
    sig = _b64(hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest())
    return signing_input + "." + sig


def decode_token(token: str):
    try:
        signing_input, sig = token.rsplit(".", 1)
        expected = _b64(hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64d(signing_input.split(".", 1)[1]))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def hash_password(pw: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 120_000)
    return f"pbkdf2${salt}${dk.hex()}"


def verify_password(pw: str, stored: str) -> bool:
    try:
        _, salt, h = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 120_000)
        return hmac.compare_digest(dk.hex(), h)
    except Exception:
        return False
