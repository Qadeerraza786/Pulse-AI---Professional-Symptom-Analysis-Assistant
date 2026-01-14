"""
Entry point for running the FastAPI application.
This file imports the app from the app package and can be used with uvicorn.

Usage:
    uvicorn main:app --reload --port 8000
"""
# Import FastAPI app instance from app.main module
from app.main import app

# Define __all__ to specify what gets exported when using "from main import *"
__all__ = ["app"]
