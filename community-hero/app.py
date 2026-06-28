"""
Community Hero — Kolkata
=========================
A hyperlocal civic-issue reporting platform, scoped to Kolkata pincodes.

Citizens: register publicly -> post issues (image/video/text + exact pincode) to
a news feed -> confirm others' reports -> earn reward points when fixed.

Police Admins: one login per pincode -> see Pending (red) / Resolved (green)
tickets for that pincode only -> resolve with photo proof -> citizen is
rewarded automatically.

Run locally:
    pip install -r requirements.txt
    export DATABASE_URL=postgresql://user:pass@localhost:5432/community_hero
    python seed.py        # creates tables + one police-admin per pincode
    python app.py

Deploy: see README.md (Render + render.yaml blueprint included).
"""

import os
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from extensions import db
from models import User, PoliceAdmin, Issue, IssueVerification
from kolkata_data import KOLKATA_PINCODES

CATEGORIES = [
    "Pothole",
    "Water Leakage",
    "Damaged Streetlight",
    "Waste Management",
    "Other Public Infrastructure",
]

PINCODE_LOOKUP = {code: (area, ps) for code, area, ps in KOLKATA_PINCODES}


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)
    db.init_app(flask_app)
    os.makedirs(flask_app.config["UPLOAD_FOLDER"], exist_ok=True)
    return flask_app


app = create_app()


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def suggest_category(description, location_text=""):
    """Lightweight keyword-based 'AI categorisation' so the MVP runs with zero
    external API keys. Swap this out for a real vision/LLM call (Gemini,
    OpenAI, etc. -- see README) to upgrade to true AI-powered categorisation."""
    text = f"{description} {location_text}".lower()
    if any(k in text for k in ["pothole", "crack", "broken road", "road damage", "sinkhole", "cave"]):
        return "Pothole"
    if any(k in text for k in ["water", "leak", "pipe", "sewage", "drain", "flood"]):
        return "Water Leakage"
    if any(k in text for k in ["light", "lamp", "dark street", "streetlight"]):
        return "Damaged Streetlight"
    if any(k in text for k in ["garbage", "waste", "trash", "dustbin", "rubbish", "litter"]):
        return "Waste Management"
    return "Other Public Infrastructure"


def allowed_file(filename):
    if "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext in Config.ALLOWED_IMAGE_EXT:
        return "image"
    if ext in Config.ALLOWED_VIDEO_EXT:
        return "video"
    return None


def save_media(file_storage):
    """Saves an uploaded file under static/uploads with a random name.

    NOTE: Render's free-tier filesystem is ephemeral -- uploaded files are
    wiped on every redeploy/restart. For production, swap this for an
    S3 / Cloudinary / Google Cloud Storage upload (see README)."""
    if not file_storage or file_storage.filename == "":
        return None, None
    media_type = allowed_file(file_storage.filename)
    if not media_type:
        return None, None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return filename, media_type


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please log in as a police station admin.", "error")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


def get_current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None


def get_current_admin():
    aid = session.get("admin_id")
    return PoliceAdmin.query.get(aid) if aid else None


@app.context_processor
def inject_globals():
    return {
        "pincodes": KOLKATA_PINCODES,
        "categories": CATEGORIES,
        "current_user": get_current_user(),
        "current_admin": get_current_admin(),
    }


# --------------------------------------------------------------------------
# Public / auth routes
# --------------------------------------------------------------------------

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if session.get("admin_id"):
        return redirect(url_for("admin_dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        home_pincode = request.form.get("home_pincode") or None

        if not all([name, phone, email, password]):
            flash("Name, phone, email and password are all required.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        clash = User.query.filter((User.email == email) | (User.phone == phone)).first()
        if clash:
            flash("An account with this email or phone number already exists.", "error")
            return render_template("register.html")

        user = User(
            name=name,
            phone=phone,
            email=email,
            password_hash=generate_password_hash(password),
            home_pincode=home_pincode,
        )
        db.session.add(user)
        db.session.commit()

        session.clear()
        session["user_id"] = user.id
        flash("Welcome to Community Hero! Your account has been created.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter(
            (User.email == identifier) | (User.phone == identifier)
        ).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        flash("Invalid email/phone or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "success")
    return redirect(url_for("index"))


# --------------------------------------------------------------------------
# Citizen app: news feed
# --------------------------------------------------------------------------

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user = get_current_user()

    if request.method == "POST":
        pincode = request.form.get("pincode", "")
        location_text = request.form.get("location_text", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "")
        media_file = request.files.get("media")

        if pincode not in PINCODE_LOOKUP:
            flash("Please select a valid Kolkata pincode from the dropdown.", "error")
            return redirect(url_for("dashboard"))
        if not description:
            flash("Please describe the issue.", "error")
            return redirect(url_for("dashboard"))

        if not category:
            category = suggest_category(description, location_text)

        filename, media_type = save_media(media_file)

        issue = Issue(
            reporter_id=user.id,
            pincode=pincode,
            location_text=location_text or PINCODE_LOOKUP[pincode][0],
            category=category,
            description=description,
            media_filename=filename,
            media_type=media_type,
        )
        db.session.add(issue)
        db.session.commit()
        flash("Issue reported. Thank you for helping your community!", "success")
        return redirect(url_for("dashboard", pincode=request.args.get("pincode", "")))

    filter_pincode = request.args.get("pincode", "")
    query = Issue.query.order_by(Issue.created_at.desc())
    if filter_pincode:
        query = query.filter_by(pincode=filter_pincode)
    issues = query.limit(100).all()

    stats = {
        "pending": Issue.query.filter_by(status="pending").count(),
        "resolved": Issue.query.filter_by(status="resolved").count(),
    }
    leaderboard = (
        User.query.filter(User.reward_points > 0)
        .order_by(User.reward_points.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        issues=issues,
        stats=stats,
        leaderboard=leaderboard,
        filter_pincode=filter_pincode,
    )


@app.route("/issue/<int:issue_id>/verify", methods=["POST"])
@login_required
def verify_issue(issue_id):
    user = get_current_user()
    issue = Issue.query.get_or_404(issue_id)
    already = IssueVerification.query.filter_by(issue_id=issue.id, user_id=user.id).first()
    if not already:
        db.session.add(IssueVerification(issue_id=issue.id, user_id=user.id))
        db.session.commit()
        flash("Thanks for confirming this issue.", "success")
    return redirect(request.referrer or url_for("dashboard"))


# --------------------------------------------------------------------------
# Police admin app: one login per pincode
# --------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = PoliceAdmin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session.clear()
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin username or password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    admin = get_current_admin()
    pending = (
        Issue.query.filter_by(pincode=admin.pincode, status="pending")
        .order_by(Issue.created_at.asc())
        .all()
    )
    resolved = (
        Issue.query.filter_by(pincode=admin.pincode, status="resolved")
        .order_by(Issue.resolved_at.desc())
        .all()
    )
    return render_template(
        "admin_dashboard.html", admin=admin, pending=pending, resolved=resolved
    )


@app.route("/admin/issue/<int:issue_id>/resolve", methods=["POST"])
@admin_required
def resolve_issue(issue_id):
    admin = get_current_admin()
    issue = Issue.query.get_or_404(issue_id)
    if issue.pincode != admin.pincode:
        abort(403)

    proof_file = request.files.get("proof")
    proof_filename, _ = save_media(proof_file)
    if not proof_filename:
        flash("Please upload a photo as proof of resolution.", "error")
        return redirect(url_for("admin_dashboard"))

    issue.status = "resolved"
    issue.resolved_by_id = admin.id
    issue.resolved_proof_filename = proof_filename
    issue.resolved_at = datetime.utcnow()
    issue.reward_points_awarded = Config.REWARD_POINTS_PER_RESOLUTION

    reporter = User.query.get(issue.reporter_id)
    if reporter:
        reporter.reward_points = (reporter.reward_points or 0) + Config.REWARD_POINTS_PER_RESOLUTION

    db.session.commit()
    flash("Issue marked resolved. Reward points credited to the citizen.", "success")
    return redirect(url_for("admin_dashboard"))


# --------------------------------------------------------------------------
# Health check (handy for Render)
# --------------------------------------------------------------------------

@app.route("/healthz")
def healthz():
    return {"status": "ok"}


# --------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
