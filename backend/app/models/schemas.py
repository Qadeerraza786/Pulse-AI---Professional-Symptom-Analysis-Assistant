"""
Pydantic models for data validation and serialization.
"""
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId

# Custom validator for MongoDB ObjectId to work with Pydantic v2
class PyObjectId(str):
    """
    Custom class to handle MongoDB ObjectId in Pydantic models.
    """
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")

# Pydantic model for patient input request
class PatientInput(BaseModel):
    """
    Schema for patient input data with validation rules.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True
    )
    
    name: str = Field(..., min_length=1, description="Patient's full name")
    problem: str = Field(..., min_length=1, description="Primary medical problem or symptom")
    message: Optional[str] = Field(None, description="Additional details or context about the problem")

# Pydantic model for AI response
class AIResponse(BaseModel):
    """
    Schema for AI-generated medical response.
    """
    response: str = Field(..., description="AI-generated medical diagnosis and recommendations")

# Pydantic model for complete chat session stored in database
class ChatSession(BaseModel):
    """
    Schema for chat session data stored in MongoDB.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    patient_name: str = Field(..., description="Name of the patient")
    problem: str = Field(..., description="Primary medical problem or symptom")
    additional_info: Optional[str] = Field(None, description="Additional context or details")
    ai_response: str = Field(..., description="AI's medical diagnosis and recommendations")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")
    pinned: Optional[bool] = Field(default=False, description="Whether this chat is pinned")

# Pydantic model for API response containing chat session data
class ChatSessionResponse(BaseModel):
    """
    Schema for API response when returning chat session data.
    """
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: str}
    )
    
    patient_name: str = Field(..., description="Name of the patient")
    problem: str = Field(..., description="Primary medical problem or symptom")
    additional_info: Optional[str] = Field(None, description="Additional context or details")
    ai_response: str = Field(..., description="AI's medical diagnosis and recommendations")
    timestamp: datetime = Field(..., description="Session creation timestamp")
    id: str = Field(..., description="Unique session identifier")
    pinned: Optional[bool] = Field(default=False, description="Whether this chat is pinned")

# Pydantic model for chat session update request
class ChatSessionUpdate(BaseModel):
    """
    Schema for updating a chat session (rename, pin, etc.).
    """
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True
    )
    
    problem: Optional[str] = Field(None, description="New problem/name for the chat")
    pinned: Optional[bool] = Field(None, description="Pin status for the chat")
