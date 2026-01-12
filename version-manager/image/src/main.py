"""
Version Manager Application
API server for managing application versions in PostgreSQL or SQLite database.
Set USE_POSTGRESQL=false to use SQLite for testing.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

from database import init_db
from routes import router as api_router
from swagger import get_swagger_config

# Configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12VersionManager-=")


class LoginRequest(BaseModel):
    username: str
    password: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    **get_swagger_config(),
)

# API routes
app.include_router(api_router, prefix="/v1")

# Static files for React UI
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")
if os.path.exists(UI_DIR):
    app.mount("/static", StaticFiles(directory=UI_DIR), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/auth/login")
async def login(request: LoginRequest):
    """Authenticate user with username and password."""
    if request.username == "admin" and request.password == ADMIN_PASSWORD:
        return {"success": True, "username": request.username}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/")
async def serve_ui():
    """Serve the React UI application."""
    index_path = os.path.join(UI_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "UI not available. Access API at /v1 or docs at /docs"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
