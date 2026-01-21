"""
API routes for chat and session management.
"""
# Import APIRouter from FastAPI to create route groups
from fastapi import APIRouter, HTTPException
# Import json for JSON encoding
import json
# Import datetime for timestamp generation
from datetime import datetime, timezone
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
# Import AI service functions to generate medical responses
from app.services.ai_service import generate_medical_response
# Import text processing utility for markdown cleaning
from app.utils.text_processing import clean_markdown_formatting
# Import configuration for validation
from app.core.config import MAX_NAME_LENGTH, MAX_PROBLEM_LENGTH, MAX_MESSAGE_LENGTH

# Create logger instance for this module
logger = logging.getLogger(__name__)

# Create API router with prefix "/api" and tag "api" for API documentation
router = APIRouter(prefix="/api", tags=["api"])

# Define POST endpoint at "/chat" that returns ChatSessionResponse model
@router.post("/chat", response_model=ChatSessionResponse)
# Async function to handle chat requests with patient input
async def chat_with_ai(patient_input: PatientInput):
    """
    Receives patient input, generates AI medical response with structured session memory, and saves/updates session to database.
    Supports continuing existing conversations via session_id.
    """
    # Wrap code in try-except for error handling
    try:
        # Get database connection instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not available
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Input validation and sanitization
        # Validate and sanitize name
        patient_name = patient_input.name.strip()
        if not patient_name or len(patient_name) > MAX_NAME_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"Name must be between 1 and {MAX_NAME_LENGTH} characters"
            )
        
        # Validate and sanitize message
        patient_message = patient_input.message.strip()
        if not patient_message or len(patient_message) > MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Message must be between 1 and {MAX_MESSAGE_LENGTH} characters"
            )
        
        # Validate and sanitize problem (optional)
        patient_problem = patient_input.problem.strip() if patient_input.problem else None
        if patient_problem and len(patient_problem) > MAX_PROBLEM_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Problem description must not exceed {MAX_PROBLEM_LENGTH} characters"
            )
        
        # Construct user message from patient input - start with name and required message
        user_message = f"Patient Name: {patient_name}"
        if patient_problem:
            user_message += f"\nProblem: {patient_problem}"  # Append problem to the message
        user_message += f"\nMessage: {patient_message}"  # Append the patient message
        
        # Initialize conversation history and session variables
        conversation_history = []
        existing_session = None
        session_id = None
        
        # Check if continuing an existing session
        if patient_input.session_id:
            # Validate session ID format
            if not ObjectId.is_valid(patient_input.session_id):
                # Raise HTTP 400 error for invalid ID format
                raise HTTPException(status_code=400, detail="Invalid session ID format")
            
            # Fetch existing session from database
            existing_session = await db.chat_sessions.find_one({"_id": ObjectId(patient_input.session_id)})
            
            # Check if session exists
            if existing_session is None:
                # Raise HTTP 404 error if session doesn't exist
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Get conversation history from existing session (structured session memory)
            conversation_history = existing_session.get("messages", [])
            # Set session ID for update operation
            session_id = patient_input.session_id
            # Log that we're continuing an existing session
            logger.info(f"Continuing session {session_id} with {len(conversation_history)} previous messages")
        
        # Generate AI response with conversation history - wrap in try-except for AI service errors
        try:
            # Call AI service to generate medical response with structured session memory
            ai_response_text = await generate_medical_response(user_message, conversation_history)
            # Log successful AI response generation
            logger.info(f"AI response generated for patient: {patient_input.name} with session memory")
        # Catch any exceptions from AI service
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            # Log error from AI service with full context
            logger.error(f"Error calling AI service: {str(e)}", exc_info=True)
            # Raise HTTP 500 error with generic message (security: don't expose internal details)
            raise HTTPException(status_code=500, detail="Failed to generate AI response. Please try again.")
        
        # Add new user message to conversation history
        conversation_history.append({"role": "user", "content": user_message})
        # Add AI response to conversation history
        conversation_history.append({"role": "assistant", "content": ai_response_text})
        
        # Prepare session data
        session_data = {
            # Set patient name from input (sanitized)
            "patient_name": patient_name,
            # Set problem description from input (can be None, optional)
            "problem": patient_problem or "No specific disease mentioned",
            # Set additional info from input (required message, sanitized)
            "additional_info": patient_message,
            # Set AI response text (for backward compatibility)
            "ai_response": ai_response_text,
            # Set conversation messages array (structured session memory)
            "messages": conversation_history,
            # Set current UTC timestamp (using timezone-aware datetime)
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Save or update session in database
        if existing_session:
            # Update existing session with new messages
            await db.chat_sessions.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": session_data}
            )
            # Log successful database update
            logger.info(f"Chat session updated in database with ID: {session_id}")
            # Use existing session ID for response
            result_id = session_id
        else:
            # Insert new document into chat_sessions collection
            result = await db.chat_sessions.insert_one(session_data)
            # Log successful database save with inserted document ID
            logger.info(f"Chat session saved to database with ID: {result.inserted_id}")
            # Use new session ID for response
            result_id = str(result.inserted_id)
        
        # Create response object for API response
        response_data = ChatSessionResponse(
            # Copy patient name from session data
            patient_name=session_data["patient_name"],
            # Copy problem from session data
            problem=session_data["problem"],
            # Copy additional info from session data
            additional_info=session_data["additional_info"],
            # Copy AI response from session data
            ai_response=session_data["ai_response"],
            # Copy messages array from session data (structured session memory)
            messages=session_data["messages"],
            # Copy timestamp from session data
            timestamp=session_data["timestamp"],
            # Convert ObjectId to string for JSON serialization
            id=str(result_id)
        )
        
        # Return response data to client
        return response_data
        
    # Re-raise HTTPException to preserve status code and detail
    except HTTPException:
        raise
    # Catch any other unexpected exceptions
    except Exception as e:
        # Log unexpected error with full details (for debugging)
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        # Raise HTTP 500 error with generic message (security: don't expose internal details)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

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
        # Performance: Use compound index created in database.py
        cursor = db.chat_sessions.find().sort([("pinned", -1), ("timestamp", -1)])
        # Convert cursor to list with maximum 100 documents
        # TODO: Implement pagination for better performance with large datasets
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
                # Get messages array from document (structured session memory)
                messages=session.get("messages", []),
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
            # Get messages array from document (structured session memory)
            messages=session.get("messages", []),
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
            # Get messages array from document (structured session memory)
            messages=session.get("messages", []),
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
