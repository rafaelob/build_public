"""Autenticacao admin — hash de senhas e JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import ADMIN_JWT_SECRET, ADMIN_JWT_EXPIRY_HOURS


def hash_password(plain: str) -> str:
    """Gera hash bcrypt da senha."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int, username: str) -> tuple[str, int]:
    """Cria JWT com expiracao. Retorna (token, expires_in_seconds)."""
    expires_in = int(timedelta(hours=ADMIN_JWT_EXPIRY_HOURS).total_seconds())
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=ADMIN_JWT_EXPIRY_HOURS),
    }
    token = jwt.encode(payload, ADMIN_JWT_SECRET, algorithm="HS256")
    return token, expires_in


def decode_token(token: str) -> dict | None:
    """Decodifica JWT. Retorna payload ou None se invalido/expirado."""
    try:
        return jwt.decode(token, ADMIN_JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
