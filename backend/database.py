# Import motor library for asynchronous MongoDB operations
from motor.motor_asyncio import AsyncIOMotorClient
# Import os to access environment variables
import os
# Import logging for error tracking
import logging

# Configure logging to track database connection issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the MongoDB database instance
database = None

# Async function to connect to MongoDB database
async def connect_to_mongo():
    """
    Establishes connection to MongoDB using connection string from environment variables.
    Creates database instance for 'pulse_ai' database.
    """
    # Access global database variable to modify it
    global database
    try:
        # Get MongoDB connection URI from environment variable, default to localhost if not set
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        # Create async MongoDB client with connection string
        client = AsyncIOMotorClient(mongo_uri)
        # Select 'pulse_ai' database from the MongoDB instance
        database = client.pulse_ai
        # Test connection by running a ping command
        await client.admin.command('ping')
        # Log successful connection
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        # Log any connection errors that occur
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        # Re-raise exception to prevent application from continuing with invalid connection
        raise

# Async function to disconnect from MongoDB
async def close_mongo_connection():
    """
    Closes the MongoDB connection gracefully.
    """
    # Access global database variable
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

# Function to get the database instance
def get_database():
    """
    Returns the database instance for use in other modules.
    """
    # Return the global database variable
    return database
