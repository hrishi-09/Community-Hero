"""
OTP API - Send and verify OTPs for phone verification
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.services.otp_service import create_otp, send_otp_sms

router = APIRouter()


class SendOTPRequest(BaseModel):
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp_code: str


@router.post("/send")
def send_otp(req: SendOTPRequest, db: Session = Depends(get_db)):
    phone = req.phone.strip().replace(" ", "")
    if not phone or len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    otp_code = create_otp(db, phone)
    success = send_otp_sms(phone, otp_code)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again.")

    return {"message": f"OTP sent to {phone[-4:].zfill(len(phone))} (last 4 digits shown)", "success": True}


@router.get("/pincodes")
def get_pincodes():
    """Return all Kolkata pincodes for the registration dropdown."""
    from backend.app.db.models import KOLKATA_PINCODES
    return {"pincodes": KOLKATA_PINCODES}
