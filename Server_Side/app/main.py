"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import ALLOWED_ORIGINS
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Pulse AI",
    description="Medical Chatbot API",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    """
    Health check endpoint that returns API status.
    """
    return {"message": "Pulse AI API is running", "status": "healthy"}

# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Connects to MongoDB database when the application starts.
    """
    try:
        await connect_to_mongo()
        logger.info("Pulse AI application started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Closes MongoDB connection when the application shuts down.
    """
    try:
        await close_mongo_connection()
        logger.info("Pulse AI application shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
