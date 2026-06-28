"""
Admin API - Police station admins manage issues by pincode
"""

import json
import os
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.db import models
from backend.app.core.security import get_current_user, get_current_admin
from backend.app.core.config import settings

router = APIRouter()


async def save_proof(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, "proofs")
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/proofs/{filename}"


@router.get("/issues")
def admin_list_issues(
    pincode: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Issue)

    # Police admins only see their pincode
    if current_user.role == models.UserRole.police and current_user.pincode:
        query = query.filter(models.Issue.pincode == current_user.pincode)
    elif pincode:
        query = query.filter(models.Issue.pincode == pincode)

    if status:
        query = query.filter(models.Issue.status == status)
    if category:
        query = query.filter(models.Issue.category == category)

    total = query.count()
    issues = query.options(
        joinedload(models.Issue.reporter),
    ).order_by(models.Issue.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "issues": [_admin_issue_dict(i) for i in issues]
    }


@router.get("/stats")
def admin_stats(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Issue)
    if current_user.role == models.UserRole.police and current_user.pincode:
        query = query.filter(models.Issue.pincode == current_user.pincode)

    total = query.count()
    pending = query.filter(models.Issue.status == models.IssueStatus.pending).count()
    in_progress = query.filter(models.Issue.status == models.IssueStatus.in_progress).count()
    resolved = query.filter(models.Issue.status == models.IssueStatus.resolved).count()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "pincode": current_user.pincode,
        "police_station": next(
            (p["police_station"] for p in models.KOLKATA_PINCODES if p["pincode"] == current_user.pincode),
            "All Stations"
        ) if current_user.pincode else "All Stations"
    }


class StatusUpdateRequest(BaseModel):
    status: str
    note: Optional[str] = None


@router.patch("/issues/{issue_id}/status")
def update_issue_status(
    issue_id: str,
    req: StatusUpdateRequest,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Police admins can only update their pincode's issues
    if current_user.role == models.UserRole.police and issue.pincode != current_user.pincode:
        raise HTTPException(status_code=403, detail="You can only manage issues in your jurisdiction")

    valid_statuses = ["pending", "in_progress", "resolved"]
    if req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")

    old_status = issue.status.value
    issue.status = models.IssueStatus(req.status)

    action = models.IssueAction(
        issue_id=issue_id,
        admin_id=current_user.id,
        action="status_change",
        note=req.note,
        old_status=old_status,
        new_status=req.status,
    )
    db.add(action)
    db.commit()
    db.refresh(issue)

    return {"message": "Status updated", "status": issue.status.value}


@router.post("/issues/{issue_id}/resolve-proof")
async def upload_resolve_proof(
    issue_id: str,
    note: str = Form(""),
    files: List[UploadFile] = File(...),
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if current_user.role == models.UserRole.police and issue.pincode != current_user.pincode:
        raise HTTPException(status_code=403, detail="You can only manage issues in your jurisdiction")

    proof_urls = []
    for file in files:
        if file.filename:
            url = await save_proof(file)
            proof_urls.append(url)

    old_status = issue.status.value
    issue.status = models.IssueStatus.resolved

    action = models.IssueAction(
        issue_id=issue_id,
        admin_id=current_user.id,
        action="resolved_proof",
        note=note,
        proof_urls=json.dumps(proof_urls),
        old_status=old_status,
        new_status="resolved",
    )
    db.add(action)
    db.commit()

    return {"message": "Issue marked as resolved with proof", "proof_urls": proof_urls}


@router.get("/users")
def list_users(
    role: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20),
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Super admin only")

    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)

    total = query.count()
    users = query.order_by(models.User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "users": [_user_dict(u) for u in users]
    }


class CreateAdminRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    pincode: str
    role: str = "police"


@router.post("/create-admin")
def create_admin(
    req: CreateAdminRequest,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Only super admin can create admins")

    from backend.app.core.security import hash_password

    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    area = next((p["area"] for p in models.KOLKATA_PINCODES if p["pincode"] == req.pincode), None)

    user = models.User(
        name=req.name,
        email=req.email,
        phone=req.phone,
        password_hash=hash_password(req.password),
        role=models.UserRole.police if req.role == "police" else models.UserRole.admin,
        pincode=req.pincode,
        area=area,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Admin created", "user": _user_dict(user)}


def _user_dict(u: models.User) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role.value,
        "pincode": u.pincode,
        "area": u.area,
        "is_verified": u.is_verified,
        "points": u.points,
        "created_at": str(u.created_at),
    }


def _admin_issue_dict(issue: models.Issue) -> dict:
    try:
        media = json.loads(issue.media_urls) if issue.media_urls else []
    except Exception:
        media = []

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
        "reporter": {
            "id": issue.reporter.id,
            "name": issue.reporter.name,
            "phone": issue.reporter.phone,
            "email": issue.reporter.email,
        } if issue.reporter else None,
        "created_at": str(issue.created_at),
        "updated_at": str(issue.updated_at),
    }
