"""Authentication router"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    ROLE_PERMISSIONS,
    create_access_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import RefreshToken, User
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse

router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Login endpoint"""
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email).options(selectinload(User.user_roles))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException("Email o contraseña incorrectos")

    if not user.is_active:
        raise UnauthorizedException("Usuario inactivo")

    # Get user roles and permissions
    roles = []
    permissions = set()
    for user_role in user.user_roles:
        await db.refresh(user_role, ["role"])
        role_name = user_role.role.name
        roles.append(role_name)
        # Add permissions for this role
        if role_name in ROLE_PERMISSIONS:
            permissions.update(ROLE_PERMISSIONS[role_name])

    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "roles": roles,
        }
    )

    # Create refresh token
    refresh_token_str = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=7),
    )

    # Save refresh token to database
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(refresh_token)
    await db.commit()

    return LoginResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            roles=roles,
            permissions=list(permissions),
        ),
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get current user info (requires authentication - to be implemented)"""
    # This is a placeholder - will be implemented with proper authentication
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
