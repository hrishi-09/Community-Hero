from datetime import datetime

from extensions import db


class User(db.Model):
    """A registered citizen. Public registration: name, phone, email, password."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    home_pincode = db.Column(db.String(6))

    reward_points = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issues = db.relationship(
        "Issue", backref="reporter", lazy=True, foreign_keys="Issue.reporter_id"
    )


class PoliceAdmin(db.Model):
    """One admin account per Kolkata pincode, representing the local police station."""

    __tablename__ = "police_admins"

    id = db.Column(db.Integer, primary_key=True)
    pincode = db.Column(db.String(6), unique=True, nullable=False, index=True)
    police_station = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Issue(db.Model):
    """A citizen-reported civic issue (pothole, water leak, streetlight, waste, etc.)."""

    __tablename__ = "issues"

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    pincode = db.Column(db.String(6), nullable=False, index=True)
    location_text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    media_filename = db.Column(db.String(255))
    media_type = db.Column(db.String(10))  # "image" or "video"

    status = db.Column(db.String(15), default="pending", nullable=False, index=True)

    resolved_by_id = db.Column(db.Integer, db.ForeignKey("police_admins.id"))
    resolved_by = db.relationship("PoliceAdmin", foreign_keys=[resolved_by_id])
    resolved_proof_filename = db.Column(db.String(255))
    resolved_at = db.Column(db.DateTime)
    reward_points_awarded = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    verifications = db.relationship(
        "IssueVerification",
        backref="issue",
        lazy=True,
        cascade="all, delete-orphan",
    )

    @property
    def verification_count(self):
        return len(self.verifications)


class IssueVerification(db.Model):
    """One citizen confirming 'I see this too' on a report -- simple community verification."""

    __tablename__ = "issue_verifications"

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("issue_id", "user_id", name="uq_issue_user_verification"),
    )
