from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api import contacts, users
from src.api.authentication import views
from db import engine, Base
from src.conf.config import get_settings
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.domain.models import User
from src.utils import get_current_user

app = FastAPI()

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(views.router)
app.include_router(contacts.router)
app.include_router(users.router)


@limiter.limit("5/minute")
@app.get("/me")
async def get_current_user_data(request: Request, current_user: User = Depends(get_current_user)):
    return current_user
