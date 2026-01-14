"""
Database connection and management for MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from app.core.config import MONGO_URI, DATABASE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the MongoDB database instance
database = None

async def connect_to_mongo():
    """
    Establishes connection to MongoDB using connection string from configuration.
    Creates database instance for the configured database.
    """
    global database
    try:
        # Create async MongoDB client with connection string
        client = AsyncIOMotorClient(MONGO_URI)
        # Select database from the MongoDB instance
        database = getattr(client, DATABASE_NAME)
        # Test connection by running a ping command
        await client.admin.command('ping')
        # Log successful connection
        logger.info(f"Successfully connected to MongoDB: {DATABASE_NAME}")
    except Exception as e:
        # Log any connection errors that occur
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        # Re-raise exception to prevent application from continuing with invalid connection
        raise

async def close_mongo_connection():
    """
    Closes the MongoDB connection gracefully.
    """
    global database
    try:
        # Check if database connection exists
        if database is not None:
            # Get client from database instance
            client = database.client
            # Close the client connection
            client.close()
            # Log successful disconnection
            logger.info("MongoDB connection closed")
    except Exception as e:
        # Log any errors during disconnection
        logger.error(f"Error closing MongoDB connection: {str(e)}")

def get_database():
    """
    Returns the database instance for use in other modules.
    """
    return database
