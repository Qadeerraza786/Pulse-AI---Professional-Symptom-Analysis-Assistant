"""
AI service for generating medical responses using Groq API.
"""
# Import AsyncOpenAI client for making async API calls
from openai import AsyncOpenAI
# Import logging module for application logging
import logging
# Import configuration variables for Groq API
from app.core.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS
# Import text processing utility to clean markdown formatting
from app.utils.text_processing import clean_markdown_formatting

# Create logger instance for this module
logger = logging.getLogger(__name__)

# System prompt that defines Pulse AI's persona and behavior
# This prompt instructs the AI on how to respond as a medical professional
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

# Initialize Groq (OpenAI-compatible) client
# Check if API key is configured
if not GROQ_API_KEY:
    # Log error if API key is missing
    logger.error("GROQ_API_KEY environment variable is not set")
    # Raise ValueError to prevent application from starting without API key
    raise ValueError("GROQ_API_KEY environment variable is required")

# Create AsyncOpenAI client instance with Groq configuration
openai_client = AsyncOpenAI(
    # Set API key from environment variable
    api_key=GROQ_API_KEY,
    # Set base URL to Groq API endpoint
    base_url=GROQ_BASE_URL,
)

# Async function to generate medical response from user message
async def generate_medical_response(user_message: str) -> str:
    """
    Generates a medical response using Groq API.
    
    Args:
        user_message: The patient's message/question
        
    Returns:
        Cleaned AI response text
        
    Raises:
        Exception: If API call fails
    """
    # Wrap API call in try-except for error handling
    try:
        # Make async API call to Groq (OpenAI-compatible) API
        response = await openai_client.chat.completions.create(
            # Specify model to use (from config)
            model=GROQ_MODEL,
            # Provide conversation messages
            messages=[
                # System message with AI instructions
                {"role": "system", "content": SYSTEM_PROMPT},
                # User message with patient input
                {"role": "user", "content": user_message}
            ],
            # Set temperature for response creativity (from config)
            temperature=AI_TEMPERATURE,
            # Set maximum tokens for response length (from config)
            max_tokens=AI_MAX_TOKENS
        )
        
        # Extract AI response text from API response
        # Access first choice's message content
        ai_response_text = response.choices[0].message.content
        # Clean markdown formatting from response using utility function
        ai_response_text = clean_markdown_formatting(ai_response_text)
        # Log successful response generation
        logger.info("AI response generated successfully")
        # Return cleaned response text
        return ai_response_text
        
    # Catch any exceptions during API call
    except Exception as e:
        # Log error with details
        logger.error(f"Error calling Groq API: {str(e)}")
        # Raise new exception with descriptive message
        raise Exception(f"Error generating AI response: {str(e)}")
