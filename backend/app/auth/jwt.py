"""
JWT based authentication system.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import SecurityScopes
from jose.exceptions import JWTError
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.models.user import User
from app.services.auth_service import get_user_by_username

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create an access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the token.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user
