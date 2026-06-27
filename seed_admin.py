"""
Run once to create the first super admin account.
Usage: python seed_admin.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.app.db.database import engine, Base, SessionLocal
from backend.app.db import models
from backend.app.core.security import hash_password

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    email = "admin@communityhero.in"
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        print(f"Super admin already exists: {email}")
        db.close()
        return

    admin = models.User(
        name="Super Admin",
        email=email,
        phone="9000000000",
        password_hash=hash_password("Admin@1234"),
        role=models.UserRole.admin,
        is_verified=True,
        pincode=None,
        area="All Kolkata",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"✅ Super Admin created!")
    print(f"   Email:    {email}")
    print(f"   Password: Admin@1234")
    print(f"   ⚠️  Change the password immediately after first login!")
    db.close()

if __name__ == "__main__":
    seed()
