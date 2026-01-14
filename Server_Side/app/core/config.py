"""
Configuration settings for the application.
"""
# Import os module to access environment variables
import os
# Import load_dotenv function to load .env file
from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
load_dotenv()

# Groq API Configuration
# Get GROQ_API_KEY from environment variables (required for AI service)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Set base URL for Groq API (OpenAI-compatible endpoint)
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
# Set model name for Groq API (Llama 3.3 70B Versatile model)
GROQ_MODEL = "llama-3.3-70b-versatile"

# MongoDB Configuration
# Get MongoDB connection URI from environment, default to localhost if not set
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# Set database name for the application
DATABASE_NAME = "pulse_ai"

# CORS Configuration - list of allowed origins for cross-origin requests
ALLOWED_ORIGINS = [
    # Allow requests from React development server on port 3000
    "http://localhost:3000",
    # Allow requests from Vite development server on port 5173
    "http://localhost:5173",
    # Allow requests from localhost using IP address
    "http://127.0.0.1:3000"
]

# AI Configuration
# Set temperature for AI responses (0.3 = more focused, less creative)
AI_TEMPERATURE = 0.3
# Set maximum tokens for AI response (400 tokens = ~300 words)
AI_MAX_TOKENS = 400
