"""
One-time setup script.

    python seed.py

Does two things:
  1. Creates all database tables (if they don't already exist).
  2. Creates exactly one Police Station Admin account per Kolkata pincode
     (skips any pincode that already has an admin, so it's safe to re-run).

Generated logins are written to admin_credentials.csv in this folder:
  username = the pincode itself (e.g. "700016")
  password = a random 8-character token

Hand the relevant row to each police station. This MVP has no "change
password" screen yet -- add one before handing out real credentials.
admin_credentials.csv contains live passwords: keep it private, don't commit
it (it's already in .gitignore).
"""

import csv
import secrets

from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models import PoliceAdmin
from kolkata_data import KOLKATA_PINCODES


def run():
    with app.app_context():
        db.create_all()

        created_rows = []
        for pincode, area, police_station in KOLKATA_PINCODES:
            if PoliceAdmin.query.filter_by(pincode=pincode).first():
                continue

            password = secrets.token_urlsafe(6)
            admin = PoliceAdmin(
                pincode=pincode,
                police_station=f"{police_station} ({area}, {pincode})",
                username=pincode,
                password_hash=generate_password_hash(password),
            )
            db.session.add(admin)
            created_rows.append([pincode, admin.police_station, pincode, password])

        db.session.commit()

        if created_rows:
            with open("admin_credentials.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["pincode", "police_station", "username", "password"])
                writer.writerows(created_rows)
            print(f"Created {len(created_rows)} police-admin accounts.")
            print("Credentials saved to admin_credentials.csv -- keep this file private.")
        else:
            print("All police-admin accounts already exist. Nothing to do.")


if __name__ == "__main__":
    run()
