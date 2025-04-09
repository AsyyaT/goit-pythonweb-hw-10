from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from src.api.authentication.schemas import (
    InfoSchema,
    LoginSchema,
    RequestEmail,
    SignUpSchema,
    Token, LoginSuccessSchema,
)
from src.mail import send_email
from src.utils import authenticate_user, get_user_id_from_token, generate_access_token, bcrypt_context
from src.conf.config import Settings, get_settings
from db import get_db
from src.domain.models import User
# from app.services.mail import send_email


logger = getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.post(
    "/sign-up",
    response_model=InfoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up for new users.",
    tags=["auth"],
)
def sign_up(
    body: SignUpSchema,
    background_tasks: BackgroundTasks,
    db: db_dependency,
    settings: Settings = Depends(get_settings),
) -> dict:
    user = db.query(User).filter(User.email == body.email).first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with such email already exists.",
        )
    user_data = body.model_dump()
    user = User(
        hashed_password=bcrypt_context.hash(user_data.pop('password')),
        **user_data
    )
    db.add(user)
    db.commit()

    background_tasks.add_task(send_email, user, settings)
    return {"message": "User is created successfully."}


@router.post(
    "/request-email",
    response_model=InfoSchema,
    status_code=status.HTTP_200_OK,
    summary="Request email confirmation.",
    tags=["auth"],
)
def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with such email does not exist.",
        )

    if user.is_confirmed:
        return {"message": "Your email is already confirmed."}
    if user:
        background_tasks.add_task(send_email, user, settings)
    return {"message": "Check your email for confirmation."}


@router.get(
    "/confirm-email/{token}",
    response_model=InfoSchema,
    status_code=status.HTTP_200_OK,
    summary="Confirm email.",
    tags=["auth"],
)
def confirmed_email(
    token: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    user_id = get_user_id_from_token(token, settings)
    query = select(User).filter(User.id == user_id)
    result = db.execute(query)
    user = result.scalars().one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error",
        )
    if user.is_confirmed:
        return {"message": "Your email is already confirmed."}

    user.is_confirmed = True
    db.commit()

    return {"message": "Your email is confirmed."}


@router.post(
    "/login",
    response_model=LoginSuccessSchema,
    summary="Login an existing user.",
    tags=["auth"],
)
def login(
    body: LoginSchema,
    db: db_dependency,
    settings: Settings = Depends(get_settings),
) -> User:

    db_user = authenticate_user(body.email, body.password, db)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to login with provided credentials.",
        )

    access_token = generate_access_token(db_user=db_user, settings=settings)
    db_user.access_token = access_token
    return db_user


@router.post("/token", response_model=Token)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency, settings: Settings = Depends(get_settings)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    token = generate_access_token(user, settings=settings)
    return {'access_token': token, 'token_type': 'bearer'}
