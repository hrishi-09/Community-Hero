"""
Users API - Profile management
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.app.db.database import get_db
from backend.app.db import models
from backend.app.core.security import get_current_user
from backend.app.core.config import settings

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    pincode: Optional[str] = None


@router.get("/me")
def get_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    issue_count = db.query(models.Issue).filter(models.Issue.reporter_id == current_user.id).count()
    resolved_count = db.query(models.Issue).filter(
        models.Issue.reporter_id == current_user.id,
        models.Issue.status == models.IssueStatus.resolved
    ).count()

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "pincode": current_user.pincode,
        "area": current_user.area,
        "avatar_url": current_user.avatar_url,
        "bio": current_user.bio,
        "points": current_user.points,
        "is_verified": current_user.is_verified,
        "created_at": str(current_user.created_at),
        "stats": {
            "total_issues": issue_count,
            "resolved_issues": resolved_count,
        }
    }


@router.patch("/me")
def update_profile(
    req: UpdateProfileRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.name:
        current_user.name = req.name
    if req.bio is not None:
        current_user.bio = req.bio
    if req.pincode:
        area = next((p["area"] for p in models.KOLKATA_PINCODES if p["pincode"] == req.pincode), None)
        current_user.pincode = req.pincode
        current_user.area = area

    db.commit()
    return {"message": "Profile updated"}


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP images allowed")

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    current_user.avatar_url = f"/uploads/avatars/{filename}"
    db.commit()
    return {"avatar_url": current_user.avatar_url}


@router.get("/me/issues")
def my_issues(
    page: int = 1,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import json
    query = db.query(models.Issue).filter(models.Issue.reporter_id == current_user.id)
    total = query.count()
    issues = query.order_by(models.Issue.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    def fmt(i):
        try:
            media = json.loads(i.media_urls) if i.media_urls else []
        except Exception:
            media = []
        return {
            "id": i.id, "title": i.title, "category": i.category,
            "status": i.status.value, "pincode": i.pincode, "area": i.area,
            "media_urls": media, "upvotes": i.upvotes or 0,
            "created_at": str(i.created_at),
        }

    return {"total": total, "issues": [fmt(i) for i in issues]}
