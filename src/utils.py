from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from passlib.exc import InvalidTokenError
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext

from db import get_db
from src.conf.config import Settings, get_settings
from src.domain.models import User
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(email: str, password: str, db):
    user = db.query(User).filter(User.email == email).first()

    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def generate_access_token(
    db_user: User,
    settings: Settings,
) -> str:
    payload = {
        "user_id": db_user.id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        "email": db_user.email,
    }
    return jwt.encode(payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_email_token(
    data: dict,
    settings: Settings,
) -> str:
    payload = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(days=settings.MAIL_EXP_DAYS)
    payload.update({"iat": datetime.now(tz=timezone.utc), "exp": expire})
    return jwt.encode(payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_user_id_from_token(token: str, settings: Settings) -> str:
    """Get user ID from JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload["user_id"]
    except (InvalidTokenError, KeyError):
        return


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], settings: Settings = Depends(get_settings)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get('email')
        user_id = payload.get('user_id')
        if not email or not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

        return {'email': email, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
