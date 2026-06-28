import os

# Render (and most hosts) inject DATABASE_URL starting with "postgres://".
# SQLAlchemy 1.4+/2.x requires the "postgresql://" scheme, so we normalise it.
_raw_db_url = os.environ.get(
    "DATABASE_URL", "postgresql://localhost:5432/community_hero"
)
if _raw_db_url.startswith("postgres://"):
    _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me-before-deploy")

    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB per upload

    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_VIDEO_EXT = {"mp4", "mov", "webm", "avi", "mkv"}

    REWARD_POINTS_PER_RESOLUTION = 10
