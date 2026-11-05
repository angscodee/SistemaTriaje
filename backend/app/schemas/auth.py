"""Auth schemas"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response schema"""

    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshResponse(BaseModel):
    """Refresh token response schema"""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response schema"""

    id: UUID
    email: str
    full_name: str
    is_active: bool
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Forward reference resolution
LoginResponse.model_rebuild()
