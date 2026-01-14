"""
Entry point for running the FastAPI application.
This file imports the app from the app package and can be used with uvicorn.

Usage:
    uvicorn main:app --reload --port 8000
"""
from app.main import app

__all__ = ["app"]
