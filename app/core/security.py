import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.exceptions import UnauthorizedAccess

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
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

        return {"user_id": int(user_id), "email": email}

    except jwt.ExpiredSignatureError:
        raise UnauthorizedAccess("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedAccess("Invalid token")