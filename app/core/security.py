from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt   # Make sure you have python-jose[cryptography] installed
from app.core.config import settings
from app.core.exceptions import UnauthorizedAccess
from typing import Optional

# Optional: Keep HTTPBearer for backward compatibility / Swagger
security = HTTPBearer(auto_error=False)


async def get_current_user(request: Request) -> dict:
    """
    Extracts JWT from cookie (preferred) or Authorization header (fallback).
    """
    token: Optional[str] = None

    # 1. Try to get token from cookie (new requirement)
    token = request.cookies.get("access_token")   # You can change cookie name

    # 2. Fallback: Try Authorization header (Bearer token)
    if not token:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]

    if not token:
        raise UnauthorizedAccess("Not authenticated.")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = payload.get("user_id")
        email = payload.get("email")

        if user_id is None or email is None:
            raise UnauthorizedAccess("Invalid token payload")

        return {
            "user_id": int(user_id),
            "email": email,
            "payload": payload  # optional, for debugging
        }

    except JWTError as e:
        raise UnauthorizedAccess(f"Invalid token: {str(e)}")
    except Exception as e:
        raise UnauthorizedAccess("Token validation failed")