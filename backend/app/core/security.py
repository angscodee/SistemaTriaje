"""Security utilities: password hashing, JWT, RBAC"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context with Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Redis client for JWT blacklist
redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection"""
    global redis_client
    redis_client = await aioredis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )


async def close_redis() -> None:
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()


def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT access token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


async def blacklist_token(jti: str, exp: datetime) -> None:
    """Add a token to the blacklist (for logout/revocation)"""
    if not redis_client:
        return

    ttl = int((exp - datetime.utcnow()).total_seconds())
    if ttl > 0:
        await redis_client.setex(f"blacklist:{jti}", ttl, "1")


async def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted"""
    if not redis_client:
        return False

    result = await redis_client.exists(f"blacklist:{jti}")
    return result == 1


def validate_password_policy(password: str) -> tuple[bool, str]:
    """
    Validate password against policy
    Returns: (is_valid, error_message)
    """
    if len(password) < settings.password_min_length:
        return False, f"Password must be at least {settings.password_min_length} characters long"

    if settings.password_require_uppercase and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if settings.password_require_number and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    if settings.password_require_special:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, f"Password must contain at least one special character ({special_chars})"

    return True, ""


# RBAC: Permission definitions
PERMISSIONS = {
    "alerts:read": "Ver alertas",
    "alerts:write": "Crear y modificar alertas",
    "alerts:delete": "Eliminar alertas",
    "incidents:read": "Ver incidentes",
    "incidents:write": "Crear y modificar incidentes",
    "reports:read": "Ver reportes",
    "reports:generate": "Generar reportes",
    "audit:read": "Ver bitácora de auditoría",
    "users:manage": "Gestionar usuarios",
    "roles:manage": "Gestionar roles",
    "config:manage": "Gestionar configuración",
    "triage:read": "Ver resultados de triaje",
    "triage:write": "Modificar resultados de triaje",
}

# RBAC: Role to permissions mapping
ROLE_PERMISSIONS = {
    "Administrador": list(PERMISSIONS.keys()),  # All permissions
    "Analista": [
        "alerts:read",
        "alerts:write",
        "incidents:read",
        "incidents:write",
        "reports:read",
        "triage:read",
        "triage:write",
    ],
    "Gestor": [
        "alerts:read",
        "reports:read",
        "reports:generate",
    ],
    "Auditor": [
        "audit:read",
    ],
}
