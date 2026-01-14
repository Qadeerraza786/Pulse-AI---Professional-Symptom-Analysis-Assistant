"""
API routes for chat and session management.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
import logging

from app.models.schemas import (
    PatientInput,
    ChatSession,
    ChatSessionResponse,
    ChatSessionUpdate
)
from app.core.database import get_database
from app.services.ai_service import generate_medical_response

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api", tags=["api"])

@router.post("/chat", response_model=ChatSessionResponse)
async def chat_with_ai(patient_input: PatientInput):
    """
    Receives patient input, generates AI medical response, and saves session to database.
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Construct user message from patient input
        user_message = f"Patient Name: {patient_input.name}\nProblem: {patient_input.problem}"
        if patient_input.message:
            user_message += f"\nAdditional Information: {patient_input.message}"
        
        # Generate AI response
        try:
            ai_response_text = await generate_medical_response(user_message)
            logger.info(f"AI response generated for patient: {patient_input.name}")
        except Exception as e:
            logger.error(f"Error calling AI service: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
        # Create chat session document
        chat_session = ChatSession(
            patient_name=patient_input.name,
            problem=patient_input.problem,
            additional_info=patient_input.message,
            ai_response=ai_response_text,
            timestamp=datetime.utcnow()
        )
        
        # Save to database
        session_dict = chat_session.model_dump(by_alias=True, exclude_none=True)
        result = await db.chat_sessions.insert_one(session_dict)
        logger.info(f"Chat session saved to database with ID: {result.inserted_id}")
        
        # Create response object
        response_data = ChatSessionResponse(
            patient_name=chat_session.patient_name,
            problem=chat_session.problem,
            additional_info=chat_session.additional_info,
            ai_response=chat_session.ai_response,
            timestamp=chat_session.timestamp,
            id=str(result.inserted_id)
        )
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/sessions", response_model=list[ChatSessionResponse])
async def get_all_sessions():
    """
    Retrieves all chat sessions from the database.
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Retrieve all documents, sorted by pinned status first, then by timestamp
        cursor = db.chat_sessions.find().sort([("pinned", -1), ("timestamp", -1)])
        sessions = await cursor.to_list(length=100)
        
        # Convert to response objects
        response_list = []
        for session in sessions:
            response_obj = ChatSessionResponse(
                patient_name=session["patient_name"],
                problem=session["problem"],
                additional_info=session.get("additional_info"),
                ai_response=session["ai_response"],
                timestamp=session["timestamp"],
                id=str(session["_id"]),
                pinned=session.get("pinned", False)
            )
            response_list.append(response_obj)
        
        return response_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session_by_id(session_id: str):
    """
    Retrieves a specific chat session by its ID.
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        if not ObjectId.is_valid(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
        
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        response_obj = ChatSessionResponse(
            patient_name=session["patient_name"],
            problem=session["problem"],
            additional_info=session.get("additional_info"),
            ai_response=session["ai_response"],
            timestamp=session["timestamp"],
            id=str(session["_id"]),
            pinned=session.get("pinned", False)
        )
        
        return response_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_session(session_id: str, updates: ChatSessionUpdate):
    """
    Updates a specific chat session by its ID.
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        if not ObjectId.is_valid(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        updates_dict = updates.model_dump(exclude_none=True)
        update_dict = {}
        
        if "problem" in updates_dict:
            update_dict["problem"] = updates_dict["problem"]
        if "pinned" in updates_dict:
            update_dict["pinned"] = updates_dict["pinned"]
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        result = await db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
        
        response_obj = ChatSessionResponse(
            patient_name=session["patient_name"],
            problem=session["problem"],
            additional_info=session.get("additional_info"),
            ai_response=session["ai_response"],
            timestamp=session["timestamp"],
            id=str(session["_id"]),
            pinned=session.get("pinned", False)
        )
        
        return response_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Deletes a specific chat session by its ID.
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        if not ObjectId.is_valid(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        result = await db.chat_sessions.delete_one({"_id": ObjectId(session_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully", "id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
