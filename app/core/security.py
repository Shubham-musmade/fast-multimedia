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
        # Decode the token. jwt.decode will raise JWTError for invalid/expired tokens.
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("user_id")
        email = payload.get("email")

        if user_id is None:
            raise UnauthorizedAccess("Invalid token payload: missing user_id")

        # Accept numeric IDs or UUID/string IDs. Convert to int only if possible.
        try:
            user_id_value = int(user_id)
        except (ValueError, TypeError):
            user_id_value = user_id
        return {
            "user_id": user_id_value,
            "user_email": email
        }

    except JWTError as e:
        raise UnauthorizedAccess(f"Invalid token: {str(e)}")
    except Exception:
        raise UnauthorizedAccess("Token validation failed")