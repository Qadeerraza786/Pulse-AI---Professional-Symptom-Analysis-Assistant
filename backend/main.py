# Import FastAPI framework for creating REST API
from fastapi import FastAPI, HTTPException
# Import CORS middleware to allow cross-origin requests from React frontend
from fastapi.middleware.cors import CORSMiddleware
# Import database connection functions
from database import connect_to_mongo, close_mongo_connection, get_database
# Import Pydantic schemas for request/response validation
from schemas import PatientInput, ChatSession, ChatSessionResponse, ChatSessionUpdate, ChatSessionUpdate
# Import OpenAI library for AI integration
from openai import AsyncOpenAI
# Import os to access environment variables
import os
# Import dotenv to load environment variables from .env file
from dotenv import load_dotenv
# Import logging for error tracking
import logging
# Import datetime for timestamp generation
from datetime import datetime
# Import bson ObjectId for MongoDB document IDs
from bson import ObjectId
# Import re for regular expressions (used in markdown cleaning)
import re

# Load environment variables from .env file
load_dotenv()

# Configure logging to track application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(title="Pulse AI", description="Medical Chatbot API", version="1.0.0")

# Configure CORS middleware to allow React frontend to make requests
app.add_middleware(
    # Use CORSMiddleware to handle cross-origin requests
    CORSMiddleware,
    # Allow requests from React development server (localhost:3000) and production domains
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    # Allow credentials (cookies, authorization headers) to be sent
    allow_credentials=True,
    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    # Allow all headers in requests
    allow_headers=["*"],
)

# Initialize Groq (OpenAI-compatible) client with API key from environment variable
# Get Groq API key from environment, raise error if not found
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    # Log error if API key is missing
    logger.error("GROQ_API_KEY environment variable is not set")
    # Raise exception to prevent application from running without API key
    raise ValueError("GROQ_API_KEY environment variable is required")
# Create async OpenAI-compatible client instance pointing to Groq's API endpoint
openai_client = AsyncOpenAI(
    # Use Groq API key for authentication
    api_key=groq_api_key,
    # Use Groq's OpenAI-compatible base URL
    base_url="https://api.groq.com/openai/v1",
)

# Function to clean markdown formatting from AI response
def clean_markdown_formatting(text: str) -> str:
    """
    Removes markdown formatting from text to ensure clean, plain text output.
    """
    if not text:
        # Return empty string if text is None or empty
        return ""
    # Remove markdown headers (###, ##, #)
    text = text.replace("### ", "").replace("## ", "").replace("# ", "")
    # Remove bold markdown (**text**)
    text = text.replace("**", "")
    # Remove markdown bullet points (-, *, •)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Remove leading markdown bullet points and extra spaces
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
            # Remove bullet point but keep the text
            cleaned_lines.append(stripped[2:].strip())
        elif stripped.startswith("-") or stripped.startswith("*") or stripped.startswith("•"):
            # Handle single character bullets
            cleaned_lines.append(stripped[1:].strip())
        else:
            # Keep line as is if no bullet point
            cleaned_lines.append(line)
    # Join lines back together
    text = "\n".join(cleaned_lines)
    # Remove multiple consecutive newlines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace
    return text.strip()

# Strict system prompt that defines Pulse AI's persona and behavior
SYSTEM_PROMPT = """You are Pulse AI, a professional medical doctor providing clinical guidance. Speak like a real doctor - concise, direct, and clinical.

CRITICAL RULES:
1. You MUST ONLY answer questions related to health, symptoms, medicine, medical conditions, or wellness.
2. You MUST REFUSE to answer any questions about politics, coding, sports, general knowledge, or any non-medical topics.
3. If asked a non-medical question, politely redirect: "I'm Pulse AI, a medical assistant. I can only help with health-related questions. How can I assist you with your health today?"

RESPONSE STYLE (CRITICAL - STRICTLY FOLLOW):
- Write like a doctor speaking to a patient - direct, concise, and professional
- Use short sentences and brief paragraphs (2-3 sentences max per paragraph)
- Be clinical but clear - avoid lengthy explanations
- Structure your response in clear sections separated by line breaks
- DO NOT write long, rambling paragraphs
- DO NOT use markdown formatting (no ###, **, -, etc.)

RESPONSE STRUCTURE:
1. Brief acknowledgment (1 sentence)
2. Clinical assessment (2-3 short sentences about likely diagnosis)
3. Recommendations (concise list of actions, medications, home remedies - use line breaks, not bullets)
4. Warning signs to watch for (1-2 sentences)
5. Disclaimer (1 sentence)

Example format (follow this concise style):
"Based on your symptoms, this appears to be [diagnosis]. The [symptom] you're experiencing is likely due to [brief explanation].

I recommend [specific action 1]. You can also try [home remedy]. For pain relief, consider [medication name] at [dosage], but follow package instructions.

Seek immediate medical attention if you experience [warning sign 1] or [warning sign 2].

This is informational only and not a substitute for professional medical evaluation. Please consult a healthcare provider for proper diagnosis and treatment."

Keep responses under 200 words. Be direct, professional, and doctor-like - not conversational or lengthy."""

# Event handler that runs when FastAPI application starts
@app.on_event("startup")
async def startup_event():
    """
    Connects to MongoDB database when the application starts.
    """
    try:
        # Call function to establish MongoDB connection
        await connect_to_mongo()
        # Log successful startup
        logger.info("Pulse AI application started successfully")
    except Exception as e:
        # Log any errors during startup
        logger.error(f"Error during startup: {str(e)}")
        # Re-raise exception to prevent application from starting with invalid connection
        raise

# Event handler that runs when FastAPI application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    """
    Closes MongoDB connection when the application shuts down.
    """
    try:
        # Call function to close MongoDB connection gracefully
        await close_mongo_connection()
        # Log successful shutdown
        logger.info("Pulse AI application shut down successfully")
    except Exception as e:
        # Log any errors during shutdown
        logger.error(f"Error during shutdown: {str(e)}")

# Root endpoint to verify API is running
@app.get("/")
async def root():
    """
    Health check endpoint that returns API status.
    """
    # Return JSON response with API status
    return {"message": "Pulse AI API is running", "status": "healthy"}

# POST endpoint to handle patient input and generate AI response
@app.post("/api/chat", response_model=ChatSessionResponse)
async def chat_with_ai(patient_input: PatientInput):
    """
    Receives patient input, generates AI medical response, and saves session to database.
    """
    try:
        # Get database instance from global variable
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not connected
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Construct user message from patient input
        # Start with patient's name and problem
        user_message = f"Patient Name: {patient_input.name}\nProblem: {patient_input.problem}"
        # Add additional information if provided
        if patient_input.message:
            # Append optional message to user message
            user_message += f"\nAdditional Information: {patient_input.message}"
        
        # Generate AI response using OpenAI API
        try:
            # Create chat completion request to Groq API (OpenAI-compatible)
            response = await openai_client.chat.completions.create(
                # Specify Groq model to use (llama-3.3-70b-versatile is the recommended replacement for deprecated llama-3.1-70b-versatile)
                model="llama-3.3-70b-versatile",
                # Provide system prompt to define AI behavior
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                # Set temperature for response randomness (lower for more direct, clinical responses)
                temperature=0.3,
                # Set maximum tokens in response (reduced for concise, doctor-like responses)
                max_tokens=400
            )
            # Extract AI response text from API response
            ai_response_text = response.choices[0].message.content
            # Clean any markdown formatting from the response
            ai_response_text = clean_markdown_formatting(ai_response_text)
            # Log successful AI response generation
            logger.info(f"AI response generated for patient: {patient_input.name}")
        except Exception as e:
            # Log error if OpenAI API call fails
            logger.error(f"Error calling OpenAI API: {str(e)}")
            # Raise HTTP 500 error with descriptive message
            raise HTTPException(status_code=500, detail=f"Error generating AI response: {str(e)}")
        
        # Create chat session document for database
        chat_session = ChatSession(
            # Set patient name from input
            patient_name=patient_input.name,
            # Set problem from input
            problem=patient_input.problem,
            # Set additional info from input (can be None)
            additional_info=patient_input.message,
            # Set AI response text
            ai_response=ai_response_text,
            # Set timestamp to current UTC time
            timestamp=datetime.utcnow()
        )
        
        # Convert Pydantic model to dictionary for MongoDB insertion (Pydantic v2 uses model_dump)
        session_dict = chat_session.model_dump(by_alias=True, exclude_none=True)
        # Insert document into 'chat_sessions' collection
        result = await db.chat_sessions.insert_one(session_dict)
        # Log successful database insertion
        logger.info(f"Chat session saved to database with ID: {result.inserted_id}")
        
        # Create response object with session data
        response_data = ChatSessionResponse(
            # Set patient name
            patient_name=chat_session.patient_name,
            # Set problem
            problem=chat_session.problem,
            # Set additional info
            additional_info=chat_session.additional_info,
            # Set AI response
            ai_response=chat_session.ai_response,
            # Set timestamp
            timestamp=chat_session.timestamp,
            # Convert ObjectId to string for JSON response
            id=str(result.inserted_id)
        )
        
        # Return response data (automatically converted to JSON by FastAPI)
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        # Raise HTTP 500 error for unexpected exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# GET endpoint to retrieve all chat sessions from database
@app.get("/api/sessions", response_model=list[ChatSessionResponse])
async def get_all_sessions():
    """
    Retrieves all chat sessions from the database.
    """
    try:
        # Get database instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not connected
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Retrieve all documents from 'chat_sessions' collection
        # Sort by pinned status first (pinned chats first), then by timestamp in descending order (newest first)
        cursor = db.chat_sessions.find().sort([("pinned", -1), ("timestamp", -1)])
        # Convert cursor to list of documents
        sessions = await cursor.to_list(length=100)
        
        # Create list to store response objects
        response_list = []
        # Iterate through each session document
        for session in sessions:
            # Create ChatSessionResponse object from document
            response_obj = ChatSessionResponse(
                # Set patient name from document
                patient_name=session["patient_name"],
                # Set problem from document
                problem=session["problem"],
                # Set additional info from document (can be None)
                additional_info=session.get("additional_info"),
                # Set AI response from document
                ai_response=session["ai_response"],
                # Set timestamp from document
                timestamp=session["timestamp"],
                # Convert ObjectId to string for JSON
                id=str(session["_id"]),
                # Set pinned status from document (default to False if not present)
                pinned=session.get("pinned", False)
            )
            # Add response object to list
            response_list.append(response_obj)
        
        # Return list of chat sessions
        return response_list
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Error retrieving sessions: {str(e)}")
        # Raise HTTP 500 error
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

# GET endpoint to retrieve a specific chat session by ID
@app.get("/api/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session_by_id(session_id: str):
    """
    Retrieves a specific chat session by its ID.
    """
    try:
        # Get database instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not connected
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate that session_id is a valid ObjectId format
        if not ObjectId.is_valid(session_id):
            # Raise HTTP 400 error for invalid ID format
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        # Find document in 'chat_sessions' collection by ObjectId
        session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
        
        # Check if session was found
        if session is None:
            # Raise HTTP 404 error if session not found
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create ChatSessionResponse object from document
        response_obj = ChatSessionResponse(
            # Set patient name from document
            patient_name=session["patient_name"],
            # Set problem from document
            problem=session["problem"],
            # Set additional info from document
            additional_info=session.get("additional_info"),
            # Set AI response from document
            ai_response=session["ai_response"],
            # Set timestamp from document
            timestamp=session["timestamp"],
            # Convert ObjectId to string
            id=str(session["_id"]),
            # Set pinned status from document (default to False if not present)
            pinned=session.get("pinned", False)
        )
        
        # Return response object
        return response_obj
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        # Raise HTTP 500 error
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

# PATCH endpoint to update a chat session (rename, pin, etc.)
@app.patch("/api/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_session(session_id: str, updates: ChatSessionUpdate):
    """
    Updates a specific chat session by its ID.
    """
    try:
        # Get database instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not connected
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate that session_id is a valid ObjectId format
        if not ObjectId.is_valid(session_id):
            # Raise HTTP 400 error for invalid ID format
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        # Convert Pydantic model to dictionary, excluding None values
        updates_dict = updates.model_dump(exclude_none=True)
        
        # Prepare update dictionary (only include fields that are provided)
        update_dict = {}
        # Check if problem (rename) is in updates
        if "problem" in updates_dict:
            # Add problem to update dictionary
            update_dict["problem"] = updates_dict["problem"]
        # Check if pinned status is in updates
        if "pinned" in updates_dict:
            # Add pinned status to update dictionary
            update_dict["pinned"] = updates_dict["pinned"]
        
        # Check if there are any updates to apply
        if not update_dict:
            # Raise HTTP 400 error if no valid updates provided
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        # Update document in 'chat_sessions' collection by ObjectId
        result = await db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": update_dict}
        )
        
        # Check if session was found and updated
        if result.matched_count == 0:
            # Raise HTTP 404 error if session not found
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find updated document to return
        session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
        
        # Create ChatSessionResponse object from updated document
        response_obj = ChatSessionResponse(
            # Set patient name from document
            patient_name=session["patient_name"],
            # Set problem from document
            problem=session["problem"],
            # Set additional info from document
            additional_info=session.get("additional_info"),
            # Set AI response from document
            ai_response=session["ai_response"],
            # Set timestamp from document
            timestamp=session["timestamp"],
            # Convert ObjectId to string
            id=str(session["_id"]),
            # Set pinned status from document (default to False if not present)
            pinned=session.get("pinned", False)
        )
        
        # Return response object
        return response_obj
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Error updating session {session_id}: {str(e)}")
        # Raise HTTP 500 error
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")

# DELETE endpoint to delete a chat session
@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Deletes a specific chat session by its ID.
    """
    try:
        # Get database instance
        db = get_database()
        # Check if database connection exists
        if db is None:
            # Raise HTTP 500 error if database is not connected
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate that session_id is a valid ObjectId format
        if not ObjectId.is_valid(session_id):
            # Raise HTTP 400 error for invalid ID format
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        # Delete document from 'chat_sessions' collection by ObjectId
        result = await db.chat_sessions.delete_one({"_id": ObjectId(session_id)})
        
        # Check if session was found and deleted
        if result.deleted_count == 0:
            # Raise HTTP 404 error if session not found
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Return success message
        return {"message": "Session deleted successfully", "id": session_id}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        # Raise HTTP 500 error
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
