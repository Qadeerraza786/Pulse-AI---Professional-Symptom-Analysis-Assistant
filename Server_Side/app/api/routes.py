"""
API routes for chat and session management.
"""
# Import APIRouter from FastAPI to create route groups
from fastapi import APIRouter, HTTPException
# Import datetime for timestamp generation
from datetime import datetime
# Import ObjectId from bson for MongoDB document ID validation
from bson import ObjectId
# Import logging module for application logging
import logging

# Import Pydantic models for request/response validation
from app.models.schemas import (
    # PatientInput model for incoming patient data
    PatientInput,
    # ChatSession model for database storage
    ChatSession,
    # ChatSessionResponse model for API responses
    ChatSessionResponse,
    # ChatSessionUpdate model for partial updates
    ChatSessionUpdate
)
# Import database connection function
from app.core.database import get_database
# Import AI service function to generate medical responses
from app.services.ai_service import generate_medical_response

# Create logger instance for this module
logger = logging.getLogger(__name__)

# Create API router with prefix "/api" and tag "api" for API documentation
router = APIRouter(prefix="/api", tags=["api"])

# Define POST endpoint at "/chat" that returns ChatSessionResponse model
@router.post("/chat", response_model=ChatSessionResponse)
# Async function to handle chat requests with patient input
async def chat_with_ai(patient_input: PatientInput):
    """
    Receives patient input, generates AI medical response, and saves session to database.
    """
    # Wrap code in try-except for error handling
    try:
        # Get database connection instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not available
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Construct user message from patient input - start with name and problem
        user_message = f"Patient Name: {patient_input.name}\nProblem: {patient_input.problem}"
        # Add additional information if provided
        if patient_input.message:
            # Append additional message to user message
            user_message += f"\nAdditional Information: {patient_input.message}"
        
        # Generate AI response - wrap in try-except for AI service errors
        try:
            # Call AI service to generate medical response
            ai_response_text = await generate_medical_response(user_message)
            # Log successful AI response generation
            logger.info(f"AI response generated for patient: {patient_input.name}")
        # Catch any exceptions from AI service
        except Exception as e:
            # Log error from AI service
            logger.error(f"Error calling AI service: {str(e)}")
            # Raise HTTP 500 error with error message
            raise HTTPException(status_code=500, detail=str(e))
        
        # Create chat session document using Pydantic model
        chat_session = ChatSession(
            # Set patient name from input
            patient_name=patient_input.name,
            # Set problem description from input
            problem=patient_input.problem,
            # Set additional info from input (can be None)
            additional_info=patient_input.message,
            # Set AI response text
            ai_response=ai_response_text,
            # Set current UTC timestamp
            timestamp=datetime.utcnow()
        )
        
        # Save to database - convert Pydantic model to dictionary
        # Use by_alias=True to use field aliases (like "_id")
        # Use exclude_none=True to exclude None values
        session_dict = chat_session.model_dump(by_alias=True, exclude_none=True)
        # Insert document into chat_sessions collection
        result = await db.chat_sessions.insert_one(session_dict)
        # Log successful database save with inserted document ID
        logger.info(f"Chat session saved to database with ID: {result.inserted_id}")
        
        # Create response object for API response
        response_data = ChatSessionResponse(
            # Copy patient name from chat session
            patient_name=chat_session.patient_name,
            # Copy problem from chat session
            problem=chat_session.problem,
            # Copy additional info from chat session
            additional_info=chat_session.additional_info,
            # Copy AI response from chat session
            ai_response=chat_session.ai_response,
            # Copy timestamp from chat session
            timestamp=chat_session.timestamp,
            # Convert ObjectId to string for JSON serialization
            id=str(result.inserted_id)
        )
        
        # Return response data to client
        return response_data
        
    # Re-raise HTTPException to preserve status code and detail
    except HTTPException:
        raise
    # Catch any other unexpected exceptions
    except Exception as e:
        # Log unexpected error with full details
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        # Raise HTTP 500 error with error message
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Define GET endpoint at "/sessions" that returns list of ChatSessionResponse
@router.get("/sessions", response_model=list[ChatSessionResponse])
# Async function to retrieve all chat sessions
async def get_all_sessions():
    """
    Retrieves all chat sessions from the database.
    """
    # Wrap code in try-except for error handling
    try:
        # Get database connection instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not available
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Retrieve all documents, sorted by pinned status first, then by timestamp
        # Sort by pinned descending (-1) so pinned items appear first
        # Then sort by timestamp descending (-1) so newest appear first
        cursor = db.chat_sessions.find().sort([("pinned", -1), ("timestamp", -1)])
        # Convert cursor to list with maximum 100 documents
        sessions = await cursor.to_list(length=100)
        
        # Convert to response objects - initialize empty list
        response_list = []
        # Iterate through each session document
        for session in sessions:
            # Create ChatSessionResponse object from database document
            response_obj = ChatSessionResponse(
                # Get patient name from document
                patient_name=session["patient_name"],
                # Get problem from document
                problem=session["problem"],
                # Get additional info using .get() with default None
                additional_info=session.get("additional_info"),
                # Get AI response from document
                ai_response=session["ai_response"],
                # Get timestamp from document
                timestamp=session["timestamp"],
                # Convert ObjectId to string for JSON serialization
                id=str(session["_id"]),
                # Get pinned status with default False if not present
                pinned=session.get("pinned", False)
            )
            # Append response object to list
            response_list.append(response_obj)
        
        # Return list of response objects
        return response_list
        
    # Re-raise HTTPException to preserve status code and detail
    except HTTPException:
        raise
    # Catch any other unexpected exceptions
    except Exception as e:
        # Log error with details
        logger.error(f"Error retrieving sessions: {str(e)}")
        # Raise HTTP 500 error with error message
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

# Define GET endpoint at "/sessions/{session_id}" with path parameter
@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
# Async function to retrieve a specific chat session by ID
async def get_session_by_id(session_id: str):
    """
    Retrieves a specific chat session by its ID.
    """
    # Wrap code in try-except for error handling
    try:
        # Get database connection instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not available
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate that session_id is a valid MongoDB ObjectId format
        if not ObjectId.is_valid(session_id):
            # Raise HTTP 400 error for invalid ID format
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        # Find document in database by converting string ID to ObjectId
        session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
        
        # Check if session was found
        if session is None:
            # Raise HTTP 404 error if session doesn't exist
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create ChatSessionResponse object from database document
        response_obj = ChatSessionResponse(
            # Get patient name from document
            patient_name=session["patient_name"],
            # Get problem from document
            problem=session["problem"],
            # Get additional info using .get() with default None
            additional_info=session.get("additional_info"),
            # Get AI response from document
            ai_response=session["ai_response"],
            # Get timestamp from document
            timestamp=session["timestamp"],
            # Convert ObjectId to string for JSON serialization
            id=str(session["_id"]),
            # Get pinned status with default False if not present
            pinned=session.get("pinned", False)
        )
        
        # Return response object
        return response_obj
        
    # Re-raise HTTPException to preserve status code and detail
    except HTTPException:
        raise
    # Catch any other unexpected exceptions
    except Exception as e:
        # Log error with session ID and error details
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        # Raise HTTP 500 error with error message
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

# Define PATCH endpoint at "/sessions/{session_id}" for partial updates
@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
# Async function to update a chat session with partial data
async def update_session(session_id: str, updates: ChatSessionUpdate):
    """
    Updates a specific chat session by its ID.
    """
    # Wrap code in try-except for error handling
    try:
        # Get database connection instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not available
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate that session_id is a valid MongoDB ObjectId format
        if not ObjectId.is_valid(session_id):
            # Raise HTTP 400 error for invalid ID format
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        # Convert Pydantic model to dictionary, excluding None values
        updates_dict = updates.model_dump(exclude_none=True)
        # Initialize empty dictionary for MongoDB update operation
        update_dict = {}
        
        # Check if problem field is in updates
        if "problem" in updates_dict:
            # Add problem to update dictionary
            update_dict["problem"] = updates_dict["problem"]
        # Check if pinned field is in updates
        if "pinned" in updates_dict:
            # Add pinned status to update dictionary
            update_dict["pinned"] = updates_dict["pinned"]
        
        # Check if any valid updates were provided
        if not update_dict:
            # Raise HTTP 400 error if no valid updates
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        # Update document in database using $set operator
        result = await db.chat_sessions.update_one(
            # Filter to find document by ID
            {"_id": ObjectId(session_id)},
            # Update operation using $set to update specified fields
            {"$set": update_dict}
        )
        
        # Check if any document was matched
        if result.matched_count == 0:
            # Raise HTTP 404 error if session doesn't exist
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Retrieve updated document from database
        session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
        
        # Create ChatSessionResponse object from updated document
        response_obj = ChatSessionResponse(
            # Get patient name from document
            patient_name=session["patient_name"],
            # Get problem from document
            problem=session["problem"],
            # Get additional info using .get() with default None
            additional_info=session.get("additional_info"),
            # Get AI response from document
            ai_response=session["ai_response"],
            # Get timestamp from document
            timestamp=session["timestamp"],
            # Convert ObjectId to string for JSON serialization
            id=str(session["_id"]),
            # Get pinned status with default False if not present
            pinned=session.get("pinned", False)
        )
        
        # Return updated response object
        return response_obj
        
    # Re-raise HTTPException to preserve status code and detail
    except HTTPException:
        raise
    # Catch any other unexpected exceptions
    except Exception as e:
        # Log error with session ID and error details
        logger.error(f"Error updating session {session_id}: {str(e)}")
        # Raise HTTP 500 error with error message
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")

# Define DELETE endpoint at "/sessions/{session_id}" to delete a session
@router.delete("/sessions/{session_id}")
# Async function to delete a chat session by ID
async def delete_session(session_id: str):
    """
    Deletes a specific chat session by its ID.
    """
    # Wrap code in try-except for error handling
    try:
        # Get database connection instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not available
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate that session_id is a valid MongoDB ObjectId format
        if not ObjectId.is_valid(session_id):
            # Raise HTTP 400 error for invalid ID format
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        # Delete document from database by ID
        result = await db.chat_sessions.delete_one({"_id": ObjectId(session_id)})
        
        # Check if any document was deleted
        if result.deleted_count == 0:
            # Raise HTTP 404 error if session doesn't exist
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Return success message with deleted session ID
        return {"message": "Session deleted successfully", "id": session_id}
        
    # Re-raise HTTPException to preserve status code and detail
    except HTTPException:
        raise
    # Catch any other unexpected exceptions
    except Exception as e:
        # Log error with session ID and error details
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        # Raise HTTP 500 error with error message
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
