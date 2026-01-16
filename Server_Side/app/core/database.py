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

# Global variable to store the MongoDB client instance
# This is needed to properly close the connection
mongo_client = None

# Async function to establish MongoDB connection
async def connect_to_mongo():
    """
    Establishes connection to MongoDB using connection string from configuration.
    Creates database instance for the configured database.
    Sets up indexes for better query performance.
    """
    # Use global keyword to modify global database variable
    global database, mongo_client
    # Wrap connection code in try-except for error handling
    try:
        # Create async MongoDB client with connection string from config
        # maxPoolSize: Maximum number of connections in the pool (default: 100)
        # minPoolSize: Minimum number of connections in the pool (default: 0)
        # maxIdleTimeMS: Maximum time a connection can be idle before being closed
        mongo_client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=50,
            minPoolSize=5,
            maxIdleTimeMS=45000,
            serverSelectionTimeoutMS=5000
        )
        # Select database from the MongoDB instance using getattr
        # This is equivalent to client[DATABASE_NAME]
        database = getattr(mongo_client, DATABASE_NAME)
        # Test connection by running a ping command to admin database
        # This verifies the connection is working
        await mongo_client.admin.command('ping')
        # Log successful connection with database name
        logger.info(f"Successfully connected to MongoDB: {DATABASE_NAME}")
        
        # Create indexes for better query performance
        try:
            # Create index on timestamp for faster sorting
            await database.chat_sessions.create_index("timestamp")
            # Create compound index on pinned and timestamp for faster queries
            await database.chat_sessions.create_index([("pinned", -1), ("timestamp", -1)])
            # Create index on patient_name for faster searches (if needed in future)
            await database.chat_sessions.create_index("patient_name")
            logger.info("Database indexes created successfully")
        except Exception as index_error:
            # Log index creation errors but don't fail startup
            logger.warning(f"Error creating indexes (may already exist): {str(index_error)}")
    # Catch any exceptions during connection
    except Exception as e:
        # Log any connection errors that occur with error message
        logger.error(f"Error connecting to MongoDB: {str(e)}", exc_info=True)
        # Re-raise exception to prevent application from continuing with invalid connection
        raise

# Async function to close MongoDB connection
async def close_mongo_connection():
    """
    Closes the MongoDB connection gracefully.
    """
    # Use global keyword to access global database and client variables
    global database, mongo_client
    # Wrap disconnection code in try-except for error handling
    try:
        # Check if client exists and close it
        if mongo_client is not None:
            # Close the client connection to free resources
            mongo_client.close()
            # Log successful disconnection
            logger.info("MongoDB connection closed")
            # Reset global variables
            mongo_client = None
            database = None
    # Catch any exceptions during disconnection
    except Exception as e:
        # Log any errors during disconnection with error message
        logger.error(f"Error closing MongoDB connection: {str(e)}", exc_info=True)

# Function to get database instance for use in other modules
def get_database():
    """
    Returns the database instance for use in other modules.
    """
    # Return the global database variable
    return database
