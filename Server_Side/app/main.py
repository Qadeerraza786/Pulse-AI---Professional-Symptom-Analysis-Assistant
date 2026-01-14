"""
Main FastAPI application entry point.
"""
# Import FastAPI class to create the application
from fastapi import FastAPI
# Import CORSMiddleware for handling cross-origin requests
from fastapi.middleware.cors import CORSMiddleware
# Import logging module for application logging
import logging

# Import CORS configuration from config module
from app.core.config import ALLOWED_ORIGINS
# Import database connection functions
from app.core.database import connect_to_mongo, close_mongo_connection
# Import API router with all endpoints
from app.api.routes import router

# Configure logging - set level to INFO to see informational messages
logging.basicConfig(level=logging.INFO)
# Create logger instance for this module
logger = logging.getLogger(__name__)

# Create FastAPI application instance with metadata
app = FastAPI(
    # Set application title for API documentation
    title="Pulse AI",
    # Set application description for API documentation
    description="Medical Chatbot API",
    # Set application version
    version="1.0.0"
)

# Configure CORS middleware to allow cross-origin requests
app.add_middleware(
    # Use CORSMiddleware class
    CORSMiddleware,
    # Allow requests from these origins (from config)
    allow_origins=ALLOWED_ORIGINS,
    # Allow credentials (cookies, authorization headers) in requests
    allow_credentials=True,
    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    # Allow all headers in requests
    allow_headers=["*"],
)

# Include API routes from router into the main application
app.include_router(router)

# Root endpoint - health check endpoint
@app.get("/")
# Async function to handle root endpoint requests
async def root():
    """
    Health check endpoint that returns API status.
    """
    # Return JSON response with API status
    return {"message": "Pulse AI API is running", "status": "healthy"}

# Event handlers - lifecycle events for the application
# Startup event handler - runs when application starts
@app.on_event("startup")
# Async function to handle application startup
async def startup_event():
    """
    Connects to MongoDB database when the application starts.
    """
    # Wrap startup code in try-except for error handling
    try:
        # Connect to MongoDB database
        await connect_to_mongo()
        # Log successful startup
        logger.info("Pulse AI application started successfully")
    # Catch any exceptions during startup
    except Exception as e:
        # Log error during startup
        logger.error(f"Error during startup: {str(e)}")
        # Re-raise exception to prevent application from starting with errors
        raise

# Shutdown event handler - runs when application shuts down
@app.on_event("shutdown")
# Async function to handle application shutdown
async def shutdown_event():
    """
    Closes MongoDB connection when the application shuts down.
    """
    # Wrap shutdown code in try-except for error handling
    try:
        # Close MongoDB connection gracefully
        await close_mongo_connection()
        # Log successful shutdown
        logger.info("Pulse AI application shut down successfully")
    # Catch any exceptions during shutdown
    except Exception as e:
        # Log error during shutdown
        logger.error(f"Error during shutdown: {str(e)}")
