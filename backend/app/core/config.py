"""
Configuration settings for the application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "pulse_ai"

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000"
]

# AI Configuration
AI_TEMPERATURE = 0.3
AI_MAX_TOKENS = 400
