"""
Community Hero - FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.app.api import auth, issues, admin, users, otp
from backend.app.db.database import engine, Base
from backend.app.core.config import settings

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Community Hero - Kolkata",
    description="Hyperlocal Problem Solver for Kolkata Citizens",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(otp.router, prefix="/api/v1/otp", tags=["OTP"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(issues.router, prefix="/api/v1/issues", tags=["Issues"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Serve uploaded media
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve React frontend (build output)
FRONTEND_BUILD = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(FRONTEND_BUILD):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_BUILD, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        index_file = os.path.join(FRONTEND_BUILD, "index.html")
        return FileResponse(index_file)
else:
    @app.get("/")
    async def root():
        return {"message": "Community Hero API is running. Frontend not built yet."}


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Community Hero Kolkata"}
