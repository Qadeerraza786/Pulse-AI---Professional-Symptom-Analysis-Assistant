"""
Database connection and management for MongoDB.
"""
# Import AsyncIOMotorClient for async MongoDB operations
from motor.motor_asyncio import AsyncIOMotorClient
# Import logging module for application logging
import logging
# Import MongoDB configuration variables
from app.core.config import MONGO_URI, DATABASE_NAME

# Configure logging - set level to INFO to see informational messages
logging.basicConfig(level=logging.INFO)
# Create logger instance for this module
logger = logging.getLogger(__name__)

# Global variable to store the MongoDB database instance
# This will be set when connection is established
database = None

# Async function to establish MongoDB connection
async def connect_to_mongo():
    """
    Establishes connection to MongoDB using connection string from configuration.
    Creates database instance for the configured database.
    """
    # Use global keyword to modify global database variable
    global database
    # Wrap connection code in try-except for error handling
    try:
        # Create async MongoDB client with connection string from config
        client = AsyncIOMotorClient(MONGO_URI)
        # Select database from the MongoDB instance using getattr
        # This is equivalent to client[DATABASE_NAME]
        database = getattr(client, DATABASE_NAME)
        # Test connection by running a ping command to admin database
        # This verifies the connection is working
        await client.admin.command('ping')
        # Log successful connection with database name
        logger.info(f"Successfully connected to MongoDB: {DATABASE_NAME}")
    # Catch any exceptions during connection
    except Exception as e:
        # Log any connection errors that occur with error message
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        # Re-raise exception to prevent application from continuing with invalid connection
        raise

# Async function to close MongoDB connection
async def close_mongo_connection():
    """
    Closes the MongoDB connection gracefully.
    """
    # Use global keyword to access global database variable
    global database
    # Wrap disconnection code in try-except for error handling
    try:
        # Check if database connection exists
        if database is not None:
            # Get client from database instance (database.client)
            client = database.client
            # Close the client connection to free resources
            client.close()
            # Log successful disconnection
            logger.info("MongoDB connection closed")
    # Catch any exceptions during disconnection
    except Exception as e:
        # Log any errors during disconnection with error message
        logger.error(f"Error closing MongoDB connection: {str(e)}")

# Function to get database instance for use in other modules
def get_database():
    """
    Returns the database instance for use in other modules.
    """
    # Return the global database variable
    return database
