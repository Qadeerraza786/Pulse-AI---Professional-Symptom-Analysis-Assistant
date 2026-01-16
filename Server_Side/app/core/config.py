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
# Set temperature for AI responses (0.1 = deterministic, precise doctor-like behavior)
AI_TEMPERATURE = 0.1
# Set maximum tokens for AI response (600 tokens = enough for thorough clinical questions and guidance)
AI_MAX_TOKENS = 600
# Set top p for AI response (0.9 = allows slight variation in phrasing, keeping responses natural)
AI_TOP_P = 0.9
# Set frequency penalty for AI response (1.0 = avoids repeated questions)
AI_FREQUENCY_PENALTY = 1.0
# Set presence penalty for AI response (0.7 = encourages asking missing information only)
AI_PRESENCE_PENALTY = 0.7
# Set stop sequences to end response at correct point (prevents model from continuing beyond intended response)
AI_STOP_SEQUENCES = ["\n\nPatient:", "\n\nUser:", "\n\n---", "END_OF_RESPONSE"]