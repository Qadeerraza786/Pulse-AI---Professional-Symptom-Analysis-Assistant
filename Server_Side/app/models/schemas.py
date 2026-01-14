"""
Pydantic models for data validation and serialization.
"""
# Import BaseModel from Pydantic for creating data models
from pydantic import BaseModel, Field
# Import ConfigDict from Pydantic for model configuration
from pydantic import ConfigDict
# Import Optional from typing for optional fields
from typing import Optional
# Import datetime for timestamp fields
from datetime import datetime
# Import ObjectId from bson for MongoDB document IDs
from bson import ObjectId

# Custom validator for MongoDB ObjectId to work with Pydantic v2
# This class extends str to handle ObjectId conversion
class PyObjectId(str):
    """
    Custom class to handle MongoDB ObjectId in Pydantic models.
    """
    # Class method to get Pydantic core schema for validation
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        # Import core_schema from pydantic_core
        from pydantic_core import core_schema
        # Return a plain validator function that uses cls.validate
        return core_schema.no_info_plain_validator_function(cls.validate)

    # Class method to validate ObjectId values
    @classmethod
    def validate(cls, v):
        # Check if value is already an ObjectId instance
        if isinstance(v, ObjectId):
            # Convert ObjectId to string
            return str(v)
        # Check if value is a string and is a valid ObjectId format
        if isinstance(v, str) and ObjectId.is_valid(v):
            # Return the string as-is
            return v
        # Raise ValueError if value is not a valid ObjectId
        raise ValueError("Invalid ObjectId")

# Pydantic model for patient input request
# This model validates incoming patient data from API requests
class PatientInput(BaseModel):
    """
    Schema for patient input data with validation rules.
    """
    # Configure model behavior
    model_config = ConfigDict(
        # Allow populating fields by both field name and alias
        populate_by_name=True,
        # Use enum values instead of enum objects
        use_enum_values=True
    )
    
    # Patient name field - required, minimum 1 character
    name: str = Field(..., min_length=1, description="Patient's full name")
    # Medical problem field - required, minimum 1 character
    problem: str = Field(..., min_length=1, description="Primary medical problem or symptom")
    # Additional message field - optional, can be None
    message: Optional[str] = Field(None, description="Additional details or context about the problem")

# Pydantic model for AI response
# This model represents AI-generated medical responses
class AIResponse(BaseModel):
    """
    Schema for AI-generated medical response.
    """
    # AI response text field - required
    response: str = Field(..., description="AI-generated medical diagnosis and recommendations")

# Pydantic model for complete chat session stored in database
# This model represents the full chat session document in MongoDB
class ChatSession(BaseModel):
    """
    Schema for chat session data stored in MongoDB.
    """
    # Configure model behavior
    model_config = ConfigDict(
        # Allow populating fields by both field name and alias
        populate_by_name=True,
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Custom JSON encoder for ObjectId (convert to string)
        json_encoders={ObjectId: str}
    )
    
    # Document ID field - optional, uses "_id" alias for MongoDB
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    # Patient name field - required
    patient_name: str = Field(..., description="Name of the patient")
    # Medical problem field - required
    problem: str = Field(..., description="Primary medical problem or symptom")
    # Additional info field - optional, can be None
    additional_info: Optional[str] = Field(None, description="Additional context or details")
    # AI response field - required
    ai_response: str = Field(..., description="AI's medical diagnosis and recommendations")
    # Timestamp field - defaults to current UTC time if not provided
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")
    # Pinned status field - optional, defaults to False
    pinned: Optional[bool] = Field(default=False, description="Whether this chat is pinned")

# Pydantic model for API response containing chat session data
# This model is used when returning chat sessions to clients
class ChatSessionResponse(BaseModel):
    """
    Schema for API response when returning chat session data.
    """
    # Configure model behavior
    model_config = ConfigDict(
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Custom JSON encoder for datetime (convert to string)
        json_encoders={datetime: str}
    )
    
    # Patient name field - required
    patient_name: str = Field(..., description="Name of the patient")
    # Medical problem field - required
    problem: str = Field(..., description="Primary medical problem or symptom")
    # Additional info field - optional, can be None
    additional_info: Optional[str] = Field(None, description="Additional context or details")
    # AI response field - required
    ai_response: str = Field(..., description="AI's medical diagnosis and recommendations")
    # Timestamp field - required
    timestamp: datetime = Field(..., description="Session creation timestamp")
    # Session ID field - required, as string
    id: str = Field(..., description="Unique session identifier")
    # Pinned status field - optional, defaults to False
    pinned: Optional[bool] = Field(default=False, description="Whether this chat is pinned")

# Pydantic model for chat session update request
# This model is used for partial updates (PATCH requests)
class ChatSessionUpdate(BaseModel):
    """
    Schema for updating a chat session (rename, pin, etc.).
    """
    # Configure model behavior
    model_config = ConfigDict(
        # Allow populating fields by both field name and alias
        populate_by_name=True,
        # Use enum values instead of enum objects
        use_enum_values=True
    )
    
    # Problem field - optional, for renaming chats
    problem: Optional[str] = Field(None, description="New problem/name for the chat")
    # Pinned status field - optional, for pinning/unpinning chats
    pinned: Optional[bool] = Field(None, description="Pin status for the chat")
