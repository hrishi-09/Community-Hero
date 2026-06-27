"""
Authentication API - Register, Login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.app.db.database import get_db
from backend.app.db import models
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.services.otp_service import verify_otp

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    otp_code: str
    pincode: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Verify OTP first
    if not verify_otp(db, req.phone, req.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP. Please verify your phone number."
        )

    # Check email uniqueness
    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check phone uniqueness
    if db.query(models.User).filter(models.User.phone == req.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Find area from pincode
    area = None
    if req.pincode:
        for pc in models.KOLKATA_PINCODES:
            if pc["pincode"] == req.pincode:
                area = pc["area"]
                break

    user = models.User(
        name=req.name,
        email=req.email,
        phone=req.phone,
        password_hash=hash_password(req.password),
        role=models.UserRole.citizen,
        pincode=req.pincode,
        area=area,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return AuthResponse(
        access_token=token,
        user=_user_dict(user)
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.email == req.email) | (models.User.phone == req.email)
    ).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": user.id})
    return AuthResponse(
        access_token=token,
        user=_user_dict(user)
    )


def _user_dict(user: models.User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role.value,
        "pincode": user.pincode,
        "area": user.area,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "points": user.points,
        "bio": user.bio,
        "created_at": str(user.created_at),
    }
