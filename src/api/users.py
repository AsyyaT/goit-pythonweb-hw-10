from typing import Annotated

import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from src.conf.config import get_settings
from src.domain.models import User
from src.utils import get_current_user

router = APIRouter(prefix="/users", tags=['users'], dependencies=[Depends(get_current_user)])

settings = get_settings()


cloudinary.config(
    cloud_name=settings.CLD_NAME,
    api_key=settings.CLD_API_KEY,
    api_secret=settings.CLD_API_SECRET
)


def upload_file(file: UploadFile, user_id: int, height: int, width: int) -> str:
    """Upload and crop file to Cloudinary."""
    public_id = f"RestApp/{user_id}"
    response = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    return cloudinary.CloudinaryImage(public_id).build_url(
        width=width,
        height=height,
        crop="fill",
        version=response.get("version"),
    )


@router.patch("/avatar")
async def update_avatar(
        user: Annotated[dict, Depends(get_current_user)],
        file: UploadFile = File(...),
        height: int = Query(default=250, ge=100, le=1000),
        width: int = Query(default=250, ge=100, le=1000),
        db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == user.get('id')).first()
    avatar_url = upload_file(file=file, user_id=db_user.id, height=height, width=width)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.avatar_url = avatar_url
    db.commit()
    db.refresh(db_user)

    return {"avatar_url": db_user.avatar_url}

