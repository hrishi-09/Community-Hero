"""
Issues API - Create, list, upvote, comment on community issues
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.db import models
from backend.app.core.security import get_current_user, get_optional_user
from backend.app.core.config import settings

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}


async def save_upload(file: UploadFile, folder: str = "issues") -> str:
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, folder)
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{folder}/{filename}"


@router.post("/")
async def create_issue(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    pincode: str = Form(...),
    location_description: str = Form(""),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    files: List[UploadFile] = File(default=[]),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find police station for pincode
    police_station = None
    area = None
    for pc in models.KOLKATA_PINCODES:
        if pc["pincode"] == pincode:
            police_station = pc["police_station"]
            area = pc["area"]
            break

    if not police_station:
        raise HTTPException(status_code=400, detail="Invalid Kolkata pincode")

    # Upload media files
    media_urls = []
    for file in files:
        if file.filename and file.content_type:
            if file.content_type not in ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES:
                continue
            url = await save_upload(file)
            media_urls.append(url)

    issue = models.Issue(
        reporter_id=current_user.id,
        title=title,
        description=description,
        category=category,
        pincode=pincode,
        area=area,
        police_station=police_station,
        latitude=latitude,
        longitude=longitude,
        location_description=location_description,
        media_urls=json.dumps(media_urls),
        status=models.IssueStatus.pending,
    )
    db.add(issue)

    # Award points for posting
    current_user.points = (current_user.points or 0) + 10
    db.commit()
    db.refresh(issue)

    return _issue_dict(issue, current_user)


@router.get("/")
def list_issues(
    pincode: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[models.User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Issue)

    if pincode:
        query = query.filter(models.Issue.pincode == pincode)
    if category:
        query = query.filter(models.Issue.category == category)
    if status:
        query = query.filter(models.Issue.status == status)

    total = query.count()
    issues = query.options(
        joinedload(models.Issue.reporter),
        joinedload(models.Issue.upvote_records),
    ).order_by(models.Issue.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "issues": [_issue_dict(i, current_user) for i in issues]
    }


@router.get("/{issue_id}")
def get_issue(
    issue_id: str,
    current_user: Optional[models.User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    issue = db.query(models.Issue).options(
        joinedload(models.Issue.reporter),
        joinedload(models.Issue.upvote_records),
    ).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.views = (issue.views or 0) + 1
    db.commit()

    comments = db.query(models.Comment).options(
        joinedload(models.Comment.user)
    ).filter(models.Comment.issue_id == issue_id).order_by(models.Comment.created_at).all()
    actions = db.query(models.IssueAction).options(
        joinedload(models.IssueAction.admin)
    ).filter(models.IssueAction.issue_id == issue_id).order_by(models.IssueAction.created_at).all()

    result = _issue_dict(issue, current_user)
    result["comments"] = [_comment_dict(c) for c in comments]
    result["actions"] = [_action_dict(a) for a in actions]
    return result


@router.post("/{issue_id}/upvote")
def upvote_issue(
    issue_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    existing = db.query(models.IssueUpvote).filter(
        models.IssueUpvote.issue_id == issue_id,
        models.IssueUpvote.user_id == current_user.id,
    ).first()

    if existing:
        db.delete(existing)
        issue.upvotes = max(0, (issue.upvotes or 0) - 1)
        upvoted = False
    else:
        db.add(models.IssueUpvote(issue_id=issue_id, user_id=current_user.id))
        issue.upvotes = (issue.upvotes or 0) + 1
        upvoted = True

    db.commit()
    return {"upvoted": upvoted, "upvotes": issue.upvotes}


class CommentRequest(BaseModel):
    content: str


@router.post("/{issue_id}/comment")
def add_comment(
    issue_id: str,
    req: CommentRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    comment = models.Comment(
        issue_id=issue_id,
        user_id=current_user.id,
        content=req.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _comment_dict(comment)


def _issue_dict(issue: models.Issue, viewer=None) -> dict:
    try:
        media = json.loads(issue.media_urls) if issue.media_urls else []
    except Exception:
        media = []

    upvoted_by_me = False
    if viewer and hasattr(issue, 'upvote_records'):
        upvoted_by_me = any(u.user_id == viewer.id for u in issue.upvote_records)

    reporter_info = None
    if issue.reporter:
        reporter_info = {
            "id": issue.reporter.id,
            "name": issue.reporter.name,
            "avatar_url": issue.reporter.avatar_url,
            "pincode": issue.reporter.pincode,
        }

    return {
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "category": issue.category,
        "status": issue.status.value,
        "pincode": issue.pincode,
        "area": issue.area,
        "police_station": issue.police_station,
        "latitude": issue.latitude,
        "longitude": issue.longitude,
        "location_description": issue.location_description,
        "media_urls": media,
        "upvotes": issue.upvotes or 0,
        "views": issue.views or 0,
        "upvoted_by_me": upvoted_by_me,
        "reporter": reporter_info,
        "created_at": str(issue.created_at),
        "updated_at": str(issue.updated_at),
    }


def _comment_dict(c: models.Comment) -> dict:
    return {
        "id": c.id,
        "content": c.content,
        "user": {"id": c.user.id, "name": c.user.name, "avatar_url": c.user.avatar_url} if c.user else None,
        "created_at": str(c.created_at),
    }


def _action_dict(a: models.IssueAction) -> dict:
    try:
        proofs = json.loads(a.proof_urls) if a.proof_urls else []
    except Exception:
        proofs = []
    return {
        "id": a.id,
        "action": a.action,
        "note": a.note,
        "proof_urls": proofs,
        "old_status": a.old_status,
        "new_status": a.new_status,
        "admin": {"id": a.admin.id, "name": a.admin.name} if a.admin else None,
        "created_at": str(a.created_at),
    }
