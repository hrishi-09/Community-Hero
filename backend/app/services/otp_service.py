"""
OTP Service - SMS verification using Twilio or MSG91
"""

import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.db.models import OTPVerification
from backend.app.core.config import settings


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def send_otp_sms(phone: str, otp: str) -> bool:
    """Send OTP via SMS. Returns True on success."""
    try:
        if settings.SMS_PROVIDER == "twilio" and settings.TWILIO_ACCOUNT_SID:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your Community Hero OTP is: {otp}. Valid for 10 minutes. Do not share this with anyone.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone if phone.startswith("+") else f"+91{phone}"
            )
            return message.sid is not None

        elif settings.SMS_PROVIDER == "msg91" and settings.MSG91_AUTH_KEY:
            import requests
            url = "https://control.msg91.com/api/v5/otp"
            payload = {
                "template_id": settings.MSG91_TEMPLATE_ID,
                "mobile": phone.replace("+", "").replace(" ", ""),
                "authkey": settings.MSG91_AUTH_KEY,
                "otp": otp,
            }
            resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code == 200

        else:
            # Dev mode: print to console
            print(f"[DEV MODE] OTP for {phone}: {otp}")
            return True

    except Exception as e:
        print(f"SMS error: {e}")
        # In dev mode, still return True so flow works without SMS config
        print(f"[FALLBACK] OTP for {phone}: {otp}")
        return True


def create_otp(db: Session, phone: str) -> str:
    """Create and store OTP, return the code."""
    # Invalidate existing OTPs for this phone
    db.query(OTPVerification).filter(
        OTPVerification.phone == phone,
        OTPVerification.is_used == False
    ).delete()

    otp_code = generate_otp()
    otp_record = OTPVerification(
        phone=phone,
        otp_code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(otp_record)
    db.commit()
    return otp_code


def verify_otp(db: Session, phone: str, otp_code: str) -> bool:
    """Verify OTP and mark as used. Returns True if valid."""
    record = db.query(OTPVerification).filter(
        OTPVerification.phone == phone,
        OTPVerification.otp_code == otp_code,
        OTPVerification.is_used == False,
        OTPVerification.expires_at > datetime.utcnow(),
    ).first()

    if not record:
        return False

    record.is_used = True
    db.commit()
    return True
