"""
Community Hero - Hyperlocal Problem Solver for Kolkata
Main entry point - run with: python app.py
"""

import os
import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("ENV", "production") == "development",
        workers=1 if os.environ.get("ENV") == "development" else 4,
    )
